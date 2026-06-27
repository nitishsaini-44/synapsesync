"""
services/automation_service.py
────────────────────────────────
Core email processing pipeline.

Fixes applied:
- H4:  Imports socketio from extensions.py (not app.py) — breaks circular import
- H6:  Uses logging instead of print()
- M3:  update_last_message_id() called ONCE after all futures complete (fixes race condition)
- M2:  Uses shared serialize_lead() helper (no inline datetime conversion)
"""
import logging
import traceback
import concurrent.futures

from flask import current_app

from backend.extensions import socketio                          # ← fixed circular import (H4)
from backend.database.db import (
    get_user_by_id,
    is_lead_processed,
    insert_lead,
    update_last_message_id,
    update_user_settings,
)
from backend.utils.encryption import encrypt_data, decrypt_data
from backend.services.gmail_service import refresh_access_token, fetch_latest_messages
from backend.services.ai_service import classify_lead
from backend.services.discord_service import send_notification, format_lead_notification
from backend.utils.email_cleaner import clean_email_body
from backend.utils.serializers import serialize_lead

logger = logging.getLogger(__name__)


def process_single_message(app, user: dict, msg: dict) -> str | None:
    """
    Processes one email message end-to-end.
    Returns the msg_id on success, or None if skipped/failed.
    This return value is used by the caller to safely track the last processed ID.
    """
    user_id = user["id"]
    with app.app_context():
        try:
            msg_id = msg["id"]

            # 1. Deduplication — skip if already stored
            if is_lead_processed(msg_id):
                return None

            body_text = msg.get("body") or msg.get("snippet") or "Empty message"
            sender    = msg.get("sender", "Unknown")
            full_text = f"From: {sender}\n\n{body_text}"

            # 2. Clean HTML / links for token efficiency
            cleaned_text = clean_email_body(full_text)

            # 3. AI classification
            ai_result = classify_lead(cleaned_text)
            category  = ai_result.get("category", "support")
            urgency   = ai_result.get("urgency", "low")      # unified key name (M4)
            summary   = ai_result.get("summary", "No summary available.")

            # 4. Persist lead
            lead = insert_lead(
                user_id=user_id,
                message=cleaned_text,
                category=category,
                summary=summary,
                urgency=urgency,
                ai_reply=None,
                gmail_message_id=msg_id,
            )

            # 5. Real-time dashboard update via WebSocket
            if lead:
                lead_data = serialize_lead(dict(lead))    # shared helper — no inline datetime (M2)
                socketio.emit("new_lead", lead_data)

            # 6. Discord notification (optional — best-effort, does not block email processing)
            encrypted_webhook = user.get("discord_webhook")
            if encrypted_webhook:
                try:
                    webhook_url = decrypt_data(encrypted_webhook)
                    if webhook_url:
                        payload = format_lead_notification(sender, category, urgency, summary)
                        send_notification(webhook_url, payload)
                except Exception:
                    logger.warning(
                        "Discord notification failed for user %s", user_id, exc_info=True
                    )

            return msg_id   # ← return processed ID so caller can track last_message_id (M3)

        except Exception:
            logger.error(
                "Error processing message %s for user %s",
                msg.get("id"), user_id,
                exc_info=True,
            )
            return None


def process_user_emails(user_id: int) -> bool:
    """
    Core automation pipeline: fetch → clean → classify → store → notify.
    """
    user = get_user_by_id(user_id)
    if not user:
        logger.warning("User %s not found.", user_id)
        return False

    encrypted_refresh_token = user.get("google_refresh_token")
    if not encrypted_refresh_token:
        logger.info("User %s has no connected Gmail.", user_id)
        return False

    try:
        # 1. Decrypt and refresh the access token
        refresh_token = decrypt_data(encrypted_refresh_token)
        try:
            token_data   = refresh_access_token(refresh_token)
            access_token = token_data.get("access_token")
            if not access_token:
                raise ValueError("No access token returned from Google.")
        except Exception:
            logger.error(
                "Failed to refresh access token for user %s — disabling automation.",
                user_id, exc_info=True,
            )
            update_user_settings(user_id, automation_enabled=False)
            return False

        # 2. Fetch up to 5 new INBOX messages since last_message_id
        last_message_id = user.get("last_message_id")
        messages = fetch_latest_messages(
            access_token, last_message_id=last_message_id, max_results=5
        )

        if not messages:
            return True     # nothing new

        # Process oldest first
        messages.reverse()

        app = current_app._get_current_object()

        # 3. Process all messages concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(process_single_message, app, user, msg): msg
                for msg in messages
            }
            processed_ids = []
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    processed_ids.append(result)

        # 4. Update last_message_id ONCE after all threads finish (fixes M3 race condition).
        #    Use the last message in the original reversed list (oldest-first) that succeeded.
        if processed_ids:
            # Find the chronologically last processed message from the original order.
            original_order = [m["id"] for m in messages]
            last_id = next(
                (mid for mid in reversed(original_order) if mid in processed_ids), None
            )
            if last_id:
                update_last_message_id(user_id, last_id)

        return True

    except Exception:
        logger.error(
            "Unhandled error processing emails for user %s", user_id, exc_info=True
        )
        return False
