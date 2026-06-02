from flask import Blueprint, request, jsonify
from backend.services.openai_service import summarize_message
from backend.database.db import insert_lead
from backend.utils.auth_middleware import token_required

summarize_bp = Blueprint('summarize', __name__)

@summarize_bp.route('/summarize', methods=['POST'])
@token_required
def summarize():
    data = request.json
    message = data.get('message')
    
    if not message:
        return jsonify({"error": "Message is required"}), 400

    # 1. Call OpenAI
    ai_result = summarize_message(message)
    
    # 2. Extract data
    summary = ai_result.get('summary', '')
    category = ai_result.get('category', 'support')
    urgency = ai_result.get('urgency', 'low')
    
    # 3. Store in DB
    try:
        new_lead = insert_lead(request.user_id, message, category, summary, urgency)
        
        # Convert datetime for JSON
        if new_lead and 'created_at' in new_lead:
             new_lead['created_at'] = new_lead['created_at'].isoformat()
             
        return jsonify({
            "message": "Summarization successful",
            "data": new_lead
        }), 200
        
    except Exception as e:
        print(f"DB Insert Error: {e}")
        return jsonify({"error": "Failed to save to database"}), 500
