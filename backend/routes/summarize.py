from flask import Blueprint, request, jsonify
from backend.services.ai_service import summarize_message
from backend.database.db import insert_lead
from backend.utils.auth_middleware import token_required

import re
import html

summarize_bp = Blueprint('summarize', __name__)

def clean_html(raw_html):
    if not raw_html:
        return ""
    # Decode HTML entities
    text = html.unescape(raw_html)
    # Remove style and script tags completely
    text = re.sub(r'<style.*?</style>', ' ', text, flags=re.IGNORECASE|re.DOTALL)
    text = re.sub(r'<script.*?</script>', ' ', text, flags=re.IGNORECASE|re.DOTALL)
    # Remove all other HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

@summarize_bp.route('/summarize', methods=['POST'])
@token_required
def summarize():
    data = request.json
    raw_message = data.get('message')
    
    if not raw_message:
        return jsonify({"error": "Message is required"}), 400

    # Clean the message
    message = clean_html(raw_message)
    
    # If it was just HTML structural tags with no text, fallback to raw_message
    if not message.strip():
        message = raw_message

    # 1. Call AI
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
