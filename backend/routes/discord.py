"""
routes/discord.py
──────────────────
Discord webhook save endpoint.

Fixes:
- M12: null-safe JSON parsing
- H6:  logging replaces print()
- L1:  uses flask.g.user_id
"""
import logging
from flask import Blueprint, jsonify, request, g
from backend.services.discord_service import validate_webhook
from backend.utils.encryption import encrypt_data
from backend.database.db import update_user_settings
from backend.utils.auth_middleware import token_required

logger = logging.getLogger(__name__)

discord_bp = Blueprint("discord", __name__)


@discord_bp.route("/discord/save", methods=["POST"])
@token_required
def save_discord_webhook():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON."}), 400

    webhook_url = (data.get("webhook_url") or "").strip()
    if not webhook_url:
        return jsonify({"error": "A 'webhook_url' field is required."}), 400

    # Validate the webhook against the Discord API
    if not validate_webhook(webhook_url):
        return jsonify({"error": "Invalid Discord webhook URL. Please check the URL and try again."}), 400

    try:
        encrypted_url = encrypt_data(webhook_url)
        update_user_settings(g.user_id, discord_webhook=encrypted_url)
        return jsonify({"message": "Discord webhook connected and saved successfully!"}), 200
    except Exception:
        logger.exception("Error saving Discord webhook for user %s", g.user_id)
        return jsonify({"error": "Failed to save Discord webhook."}), 500
