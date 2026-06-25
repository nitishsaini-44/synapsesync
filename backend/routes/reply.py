"""
routes/reply.py
────────────────
Generate AI reply endpoint.

Fixes:
- L1:  uses flask.g (no direct request mutation)
- H6:  proper JSON parsing with silent=True
"""
import logging
from flask import Blueprint, request, jsonify
from backend.services.ai_service import generate_reply
from backend.utils.auth_middleware import token_required

logger = logging.getLogger(__name__)

reply_bp = Blueprint("reply", __name__)


@reply_bp.route("/generate-reply", methods=["POST"])
@token_required
def reply():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON."}), 400

    message  = (data.get("message") or "").strip()
    category = data.get("category")

    if not message:
        return jsonify({"error": "A 'message' field is required."}), 400

    if len(message) > 50_000:
        return jsonify({"error": "Message is too large. Maximum 50,000 characters."}), 400

    ai_result = generate_reply(message, category)
    return jsonify({"message": "Reply generated successfully.", "data": ai_result}), 200
