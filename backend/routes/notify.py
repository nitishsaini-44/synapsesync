from flask import Blueprint, request, jsonify
from backend.services.discord_service import DiscordService
from backend.services.openai_service import summarize_message, classify_lead, generate_reply
from backend.utils.auth_middleware import token_required

notify_bp = Blueprint('notify', __name__)

@notify_bp.route('/notify/discord', methods=['POST'])
@token_required
def notify_discord():
    data = request.get_json()
    
    if not data or 'message' not in data:
        return jsonify({"error": "Missing 'message' in request body"}), 400
        
    message = data['message']
    
    success, result_message = DiscordService.send_notification(message)
    
    if success:
        return jsonify({"message": result_message}), 200
    else:
        return jsonify({"error": result_message}), 500

@notify_bp.route('/notify/full_workflow', methods=['POST'])
@token_required
def notify_full_workflow():
    data = request.get_json()
    
    if not data or 'message' not in data:
        return jsonify({"error": "Missing 'message' in request body"}), 400
        
    message = data['message']
    
    # 1. Run all 3 AI services
    summary_result = summarize_message(message)
    classify_result = classify_lead(message)
    reply_result = generate_reply(message, category=classify_result.get('category'))
    
    # 2. Format the message
    discord_message = f"""**AI Workflow Processing Results:**

**1. Summary Result:**
- Summary: {summary_result.get('summary')}
- Category: {summary_result.get('category')}
- Urgency: {summary_result.get('urgency')}

**2. Classify Result:**
- Summary: {classify_result.get('summary')}
- Category: {classify_result.get('category')}
- Priority: {classify_result.get('priority')}

**3. Auto Reply Generated:**
{reply_result.get('reply')}
"""

    # 3. Send to Discord
    success, result_message = DiscordService.send_notification(discord_message)
    
    if success:
        return jsonify({"message": "Successfully sent full workflow to Discord!"}), 200
    else:
        return jsonify({"error": result_message}), 500
