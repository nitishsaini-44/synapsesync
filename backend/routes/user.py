from flask import Blueprint, jsonify, request
from backend.database.db import get_user_by_id, update_user_settings
from backend.utils.auth_middleware import token_required
from backend.services.gmail_service import refresh_access_token, watch_inbox
from backend.utils.encryption import decrypt_data
from flask import current_app

user_bp = Blueprint('user', __name__)

@user_bp.route('/user/settings', methods=['GET'])
@token_required
def get_settings():
    try:
        user = get_user_by_id(request.user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
            
        return jsonify({
            "data": {
                "name": user['name'],
                "email": user['email'],
                "google_email": user['google_email'],
                "is_gmail_connected": bool(user['google_refresh_token']),
                "discord_webhook": user['discord_webhook'],
                "automation_enabled": user['automation_enabled']
            }
        }), 200
    except Exception as e:
        print(f"Error fetching settings: {e}")
        return jsonify({"error": "Failed to fetch settings"}), 500

@user_bp.route('/user/settings', methods=['PUT'])
@token_required
def update_settings():
    data = request.json
    discord_webhook = data.get('discord_webhook')
    automation_enabled = data.get('automation_enabled')
    
    try:
        user = update_user_settings(request.user_id, discord_webhook, automation_enabled)
        
        # If enabling automation, register the push watch
        if automation_enabled:
            topic_name = current_app.config.get('GOOGLE_PUBSUB_TOPIC')
            encrypted_rt = user.get('google_refresh_token')
            if topic_name and encrypted_rt:
                try:
                    rt = decrypt_data(encrypted_rt)
                    token_data = refresh_access_token(rt)
                    access_token = token_data.get('access_token')
                    if access_token:
                        watch_inbox(access_token, topic_name)
                        print(f"Successfully renewed push watch for user {request.user_id}")
                except Exception as e:
                    print(f"Failed to renew watch on settings update: {e}")

        return jsonify({
            "message": "Settings updated successfully",
            "data": {
                "discord_webhook": user['discord_webhook'],
                "automation_enabled": user['automation_enabled']
            }
        }), 200
    except Exception as e:
        print(f"Error updating settings: {e}")
        return jsonify({"error": "Failed to update settings"}), 500
