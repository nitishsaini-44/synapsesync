from flask import Blueprint, request, jsonify
from backend.services.openai_service import generate_reply
from backend.utils.auth_middleware import token_required

reply_bp = Blueprint('reply', __name__)

@reply_bp.route('/generate-reply', methods=['POST'])
@token_required
def reply():
    data = request.json
    message = data.get('message')
    category = data.get('category')
    
    if not message:
        return jsonify({"error": "Message is required"}), 400

    # Call OpenAI
    ai_result = generate_reply(message, category)
    
    return jsonify({
        "message": "Reply generated successfully",
        "data": ai_result
    }), 200
