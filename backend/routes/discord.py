from flask import Blueprint, jsonify, request
from backend.services.discord_service import validate_webhook
from backend.utils.encryption import encrypt_data
from backend.database.db import update_user_settings
from backend.utils.auth_middleware import token_required

discord_bp = Blueprint('discord', __name__)

@discord_bp.route('/discord/save', methods=['POST'])
@token_required
def save_discord_webhook():
    data = request.json
    webhook_url = data.get('webhook_url')
    
    if not webhook_url:
        return jsonify({"error": "Webhook URL is required"}), 400
        
    # 1. Validate Webhook
    if not validate_webhook(webhook_url):
        return jsonify({"error": "Invalid Discord Webhook URL"}), 400
        
    try:
        # 2. Encrypt Webhook URL
        encrypted_url = encrypt_data(webhook_url)
        
        # 3. Save to user settings
        # We assume update_user_settings handles discord_webhook correctly
        update_user_settings(request.user_id, discord_webhook=encrypted_url)
        
        return jsonify({
            "message": "Discord webhook connected successfully!"
        }), 200
    except Exception as e:
        print(f"Error saving discord webhook: {e}")
        return jsonify({"error": "Failed to save Discord webhook"}), 500
