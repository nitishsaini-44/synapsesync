"""
routes/webhooks.py
───────────────────
Google Cloud Pub/Sub push notification receiver.

Fixes:
- H6:  logging replaces print()
- The circular import from `backend.tasks` inside the function is retained as a
  necessary pattern — importing at module-level would create a circular dependency.
  It is documented here for maintainability.
"""
import base64
import json
import logging

from flask import Blueprint, request, jsonify
from backend.database.db import get_user_by_google_email

logger = logging.getLogger(__name__)

webhooks_bp = Blueprint("webhooks", __name__)


@webhooks_bp.route("/gmail", methods=["POST"])
def gmail_webhook():
    """
    Receives Google Pub/Sub push notifications when a user's Gmail receives an email.

    Always returns 200 OK — returning 4xx would cause Google to retry aggressively.
    Processing happens asynchronously via Celery so this endpoint returns instantly.
    """
    try:
        envelope = request.get_json(silent=True)
        if not envelope:
            return jsonify({"status": "error", "reason": "no JSON payload"}), 200

        message = envelope.get("message")
        if not message or not isinstance(message, dict):
            return jsonify({"status": "error", "reason": "missing message field"}), 200

        data_b64 = message.get("data")
        if not data_b64:
            return jsonify({"status": "error", "reason": "no data in message"}), 200

        # Decode the base64 Pub/Sub envelope
        data_str = base64.b64decode(data_b64).decode("utf-8")
        data     = json.loads(data_str)

        google_email = data.get("emailAddress")
        if not google_email:
            return jsonify({"status": "ignored", "reason": "no emailAddress in payload"}), 200

        user = get_user_by_google_email(google_email)
        if not user:
            logger.debug("Webhook received for unregistered email: %s", google_email)
            return jsonify({"status": "ignored", "reason": "user not found"}), 200

        if not user.get("automation_enabled"):
            return jsonify({"status": "ignored", "reason": "automation disabled"}), 200

        # Delayed import to avoid circular dependency (tasks imports celery_worker which imports app)
        from backend.tasks import process_email_task  # noqa: PLC0415
        process_email_task.delay(user["id"])

        logger.info("Dispatched Celery task for %s (user_id=%s)", google_email, user["id"])
        return jsonify({"status": "success"}), 200

    except Exception:
        # Return 200 even on error — prevents Google from retrying indefinitely
        logger.exception("Error handling Gmail webhook")
        return jsonify({"status": "error"}), 200
