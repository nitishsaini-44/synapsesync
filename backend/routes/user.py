"""
routes/user.py
───────────────
User settings endpoints.

Fixes:
- M12: request.json replaced with get_json(silent=True) + null guard
- H6:  print() replaced with logging
- L1:  uses flask.g.user_id instead of request.user_id
- Audit: returns is_discord_connected boolean instead of encrypted webhook value
"""
import logging
from flask import Blueprint, jsonify, request, current_app, g
from backend.database.db import get_user_by_id, update_user_settings
from backend.utils.auth_middleware import token_required
from backend.services.gmail_service import refresh_access_token, watch_inbox
from backend.utils.encryption import decrypt_data

logger = logging.getLogger(__name__)

user_bp = Blueprint("user", __name__)


@user_bp.route("/user/settings", methods=["GET"])
@token_required
def get_settings():
    try:
        user = get_user_by_id(g.user_id)
        if not user:
            return jsonify({"error": "User not found."}), 404

        return jsonify({
            "data": {
                "name":               user["name"],
                "email":              user["email"],
                "google_email":       user["google_email"],
                "is_gmail_connected": bool(user["google_refresh_token"]),
                # Return a boolean flag — never return the encrypted value to the frontend
                "discord_webhook":    bool(user["discord_webhook"]),
                "automation_enabled": user["automation_enabled"],
            }
        }), 200
    except Exception:
        logger.exception("Error fetching settings for user %s", g.user_id)
        return jsonify({"error": "Failed to fetch settings."}), 500


@user_bp.route("/user/settings", methods=["PUT"])
@token_required
def update_settings():
    data = request.get_json(silent=True)    # M12: null-safe JSON parsing
    if not data:
        return jsonify({"error": "Request body must be JSON."}), 400

    automation_enabled = data.get("automation_enabled")

    try:
        user = update_user_settings(g.user_id, automation_enabled=automation_enabled)

        # If enabling automation, renew the Gmail push watch
        if automation_enabled:
            topic_name   = current_app.config.get("GOOGLE_PUBSUB_TOPIC")
            encrypted_rt = user.get("google_refresh_token") if user else None
            if topic_name and encrypted_rt:
                try:
                    rt           = decrypt_data(encrypted_rt)
                    token_data   = refresh_access_token(rt)
                    access_token = token_data.get("access_token")
                    if access_token:
                        watch_inbox(access_token, topic_name)
                        logger.info("Renewed Gmail push watch for user %s", g.user_id)
                except Exception:
                    logger.warning(
                        "Failed to renew Gmail watch for user %s", g.user_id, exc_info=True
                    )

        return jsonify({
            "message": "Settings updated successfully.",
            "data": {
                "automation_enabled": user["automation_enabled"] if user else False,
            },
        }), 200

    except Exception:
        logger.exception("Error updating settings for user %s", g.user_id)
        return jsonify({"error": "Failed to update settings."}), 500
