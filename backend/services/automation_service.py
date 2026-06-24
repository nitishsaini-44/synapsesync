import traceback
from backend.database.db import get_user_by_id, is_lead_processed, insert_lead, update_last_message_id, update_user_settings
from backend.utils.encryption import decrypt_data
from backend.services.gmail_service import refresh_access_token, fetch_latest_messages
from backend.services.ai_service import classify_lead
from backend.services.discord_service import send_notification
from backend.utils.email_cleaner import clean_email_body
import concurrent.futures
from flask import current_app
from backend.app import socketio

def process_single_message(app, user, msg):
    """Worker function to process a single message."""
    user_id = user['id']
    with app.app_context():
        try:
            msg_id = msg['id']
            
            # 4. Prevent duplicate processing using gmail_message_id
            if is_lead_processed(msg_id):
                return False
                
            body_text = msg.get('body') or msg.get('snippet') or "Empty message"
            sender = msg.get('sender', 'Unknown')
            
            full_text = f"From: {sender}\n\n{body_text}"
            
            # 5. Clean HTML and Links
            cleaned_text = clean_email_body(full_text)
            
            # 6. Send clean message to Groq AI
            ai_result = classify_lead(cleaned_text)
            
            # 7. Receive category, urgency, summary
            category = ai_result.get('category', 'support')
            urgency = ai_result.get('priority', 'low')
            summary = ai_result.get('summary', 'No summary available')
            
            # 8. Store lead in PostgreSQL
            lead = insert_lead(
                user_id=user_id,
                message=cleaned_text,
                category=category,
                summary=summary,
                urgency=urgency,
                ai_reply=None,
                gmail_message_id=msg_id
            )
            
            # Prepare payload for WebSockets and Discord
            lead_data = dict(lead) if lead else {}
            if 'created_at' in lead_data and lead_data['created_at']:
                lead_data['created_at'] = lead_data['created_at'].isoformat()
                
            # Broadcast to real-time dashboard
            socketio.emit('new_lead', lead_data)
            
            # 9. Send Discord notification
            encrypted_webhook = user.get('discord_webhook')
            if encrypted_webhook:
                try:
                    webhook_url = decrypt_data(encrypted_webhook)
                    if webhook_url:
                        payload = {
                            "embeds": [
                                {
                                    "title": "🚨 New Lead Processed",
                                    "color": 0x3498db,
                                    "fields": [
                                        {
                                            "name": "📧 From",
                                            "value": sender,
                                            "inline": False
                                        },
                                        {
                                            "name": "📂 Category",
                                            "value": category.capitalize(),
                                            "inline": True
                                        },
                                        {
                                            "name": "⚡ Urgency",
                                            "value": urgency.capitalize(),
                                            "inline": True
                                        },
                                        {
                                            "name": "📝 Summary",
                                            "value": summary,
                                            "inline": False
                                        }
                                    ],
                                    "footer": {
                                        "text": "SynapseSync AI"
                                    }
                                }
                            ]
                        }
                        send_notification(webhook_url, payload)
                except Exception as e:
                    print(f"Error sending discord notification for user {user_id}: {e}")
                    
            # 10. Update last_message_id (thread-safe enough for our usecase)
            update_last_message_id(user_id, msg_id)
            return True
            
        except Exception as e:
            print(f"Error processing single message {msg.get('id')} for user {user_id}: {e}")
            traceback.print_exc()
            return False

def process_user_emails(user_id: int):
    """
    Core automation logic to fetch, classify, and store emails for a user,
    and send Discord notifications if configured.
    """
    user = get_user_by_id(user_id)
    if not user:
        print(f"User {user_id} not found.")
        return False
        
    encrypted_refresh_token = user.get('google_refresh_token')
    if not encrypted_refresh_token:
        print(f"User {user_id} has no connected Gmail.")
        return False
        
    try:
        # 1. Decrypt refresh token
        refresh_token = decrypt_data(encrypted_refresh_token)
        
        # 2. Generate access token
        try:
            token_data = refresh_access_token(refresh_token)
            access_token = token_data.get('access_token')
            if not access_token:
                raise ValueError("No access token returned")
        except Exception as e:
            print(f"Failed to refresh access token for user {user_id}: {e}")
            # Handle token refresh failure: Disable automation to prevent infinite failing loops
            update_user_settings(user_id, automation_enabled=False)
            print(f"Automation disabled for user {user_id} due to token failure.")
            return False
            
        # 3. Fetch latest Gmail messages
        last_message_id = user.get('last_message_id')
        messages = fetch_latest_messages(access_token, last_message_id=last_message_id, max_results=5)
        
        if not messages:
            return True # Nothing new to process
            
        # We want to process oldest first to update last_message_id sequentially
        messages.reverse()
        
        # Capture current app context to pass to threads
        app = current_app._get_current_object()
        
        # Process all fetched emails concurrently instead of sequentially
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(process_single_message, app, user, msg) for msg in messages]
            concurrent.futures.wait(futures)
            
        return True
    except Exception as e:
        print(f"Error processing emails for user {user_id}: {e}")
        traceback.print_exc()
        return False
