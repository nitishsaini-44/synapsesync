import requests
from flask import Blueprint, request, jsonify, current_app
from backend.services.openai_service import classify_lead
from backend.database.db import insert_lead, get_user_by_email
from backend.utils.auth_middleware import token_required, api_key_required

classify_bp = Blueprint('classify', __name__)

@classify_bp.route('/classify', methods=['POST'])
@token_required
def classify():
    data = request.json
    message = data.get('message')
    
    if not message:
        return jsonify({"error": "Message is required"}), 400

    # 1. Call OpenAI
    ai_result = classify_lead(message)
    
    # 2. Extract data
    summary = ai_result.get('summary', '')
    category = ai_result.get('category', 'support')
    urgency = ai_result.get('priority', 'low') # mapping priority to urgency field
    
    # 3. Store in DB
    try:
        new_lead = insert_lead(request.user_id, message, category, summary, urgency)
        if new_lead and 'created_at' in new_lead:
             new_lead['created_at'] = new_lead['created_at'].isoformat()
             
        # 4. Trigger n8n Workflow (Webhook)
        try:
            n8n_url = current_app.config.get('N8N_WEBHOOK_URL')
            # Assuming n8n webhook is at /webhook/lead
            webhook_url = f"{n8n_url}/webhook/lead"
            
            payload = {
                "id": new_lead['id'],
                "message": message,
                "category": category,
                "urgency": urgency,
                "summary": summary
            }
            # Fire and forget (timeout=2)
            requests.post(webhook_url, json=payload, timeout=2)
        except Exception as e:
            print(f"Failed to trigger n8n: {e}")
            # Non-blocking, continue
             
        return jsonify({
            "message": "Classification successful",
            "data": new_lead
        }), 200
        
    except Exception as e:
        print(f"DB Insert Error: {e}")
        return jsonify({"error": "Failed to save to database"}), 500

@classify_bp.route('/webhook/email_lead', methods=['POST'])
@api_key_required
def webhook_email_lead():
    """Endpoint for n8n to send incoming emails to."""
    data = request.json
    message = data.get('message')
    
    if not message:
        return jsonify({"error": "Message is required"}), 400

    # Retrieve the admin user's ID
    admin_email = current_app.config.get('ADMIN_USER_EMAIL')
    if not admin_email:
        return jsonify({"error": "ADMIN_USER_EMAIL not configured on server"}), 500
        
    user = get_user_by_email(admin_email)
    if not user:
        return jsonify({"error": f"Admin user {admin_email} not found in database"}), 404
        
    # 1. Call OpenAI
    ai_result = classify_lead(message)
    
    # 2. Extract data
    summary = ai_result.get('summary', '')
    category = ai_result.get('category', 'support')
    urgency = ai_result.get('priority', 'low') 
    
    # 3. Store in DB
    try:
        new_lead = insert_lead(user['id'], message, category, summary, urgency)
        if new_lead and 'created_at' in new_lead:
             new_lead['created_at'] = new_lead['created_at'].isoformat()
             
        # 4. Trigger n8n Workflow (Webhook) to send to Discord
        try:
            n8n_url = current_app.config.get('N8N_WEBHOOK_URL')
            webhook_url = f"{n8n_url}/webhook/lead"
            
            payload = {
                "id": new_lead['id'],
                "message": message,
                "category": category,
                "urgency": urgency,
                "summary": summary
            }
            # Fire and forget
            requests.post(webhook_url, json=payload, timeout=2)
        except Exception as e:
            print(f"Failed to trigger n8n: {e}")
             
        return jsonify({
            "message": "Email classified successfully",
            "data": new_lead
        }), 200
        
    except Exception as e:
        print(f"DB Insert Error: {e}")
        return jsonify({"error": "Failed to save to database"}), 500
