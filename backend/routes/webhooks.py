import base64
import json
from flask import Blueprint, request, jsonify
from backend.database.db import get_user_by_google_email
from backend.tasks import process_email_task

webhooks_bp = Blueprint('webhooks', __name__)

@webhooks_bp.route('/gmail', methods=['POST'])
def gmail_webhook():
    """
    Endpoint for Google Cloud Pub/Sub to push Gmail notifications.
    Google sends a POST request here when a user receives a new email.
    """
    try:
        envelope = request.json
        if not envelope:
            return jsonify({"error": "Bad Request: no JSON payload"}), 400

        # Validate Pub/Sub payload structure
        message = envelope.get('message')
        if not message or not isinstance(message, dict):
            return jsonify({"error": "Bad Request: missing message payload"}), 400

        # The data payload is base64 encoded by Google Pub/Sub
        data_b64 = message.get('data')
        if not data_b64:
            return jsonify({"error": "Bad Request: no data in message"}), 400

        # Decode the base64 data to get the JSON string
        data_str = base64.b64decode(data_b64).decode('utf-8')
        data = json.loads(data_str)

        google_email = data.get('emailAddress')
        if not google_email:
            # We must return 200 so Google doesn't retry infinitely
            return jsonify({"error": "No email address found in payload"}), 200

        # Look up the user by their Google email address
        user = get_user_by_google_email(google_email)
        if not user:
            print(f"Webhook received for unknown email: {google_email}")
            return jsonify({"status": "ignored", "reason": "user not found"}), 200

        # Check if automation is enabled for this user
        if not user.get('automation_enabled'):
            return jsonify({"status": "ignored", "reason": "automation disabled"}), 200

        user_id = user['id']

        # Dispatch the task to Celery
        process_email_task.delay(user_id)

        print(f"⚡ CELERY DISPATCH: Task pushed to Redis for {google_email}")
        
        # Always return 200 to acknowledge receipt of the push notification
        return jsonify({"status": "success", "message": "processing started"}), 200

    except Exception as e:
        print(f"Error handling Gmail Webhook: {e}")
        # Return 200 even on error to prevent Google from aggressively retrying
        return jsonify({"status": "error", "message": str(e)}), 200
