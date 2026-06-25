"""
routes/classify.py
───────────────────
Manual classify endpoint.

Fixes:
- H6:  logging replaces print()
- M4:  reads 'urgency' key (was 'priority') from ai_service — key name unified
- M2:  uses serialize_lead() — no inline datetime conversion
- L1:  uses flask.g.user_id instead of request.user_id
"""
import logging

from flask import Blueprint, request, jsonify, g
from backend.services.ai_service import classify_lead
from backend.database.db import insert_lead
from backend.utils.auth_middleware import token_required
from backend.utils.serializers import serialize_lead
from backend.utils.email_cleaner import clean_email_body

logger = logging.getLogger(__name__)

classify_bp = Blueprint("classify", __name__)


@classify_bp.route("/classify", methods=["POST"])
@token_required
def classify():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON."}), 400

    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"error": "A 'message' field is required."}), 400

    if len(message) > 50_000:
        return jsonify({"error": "Message is too large. Maximum 50,000 characters."}), 400

    cleaned   = clean_email_body(message)
    ai_result = classify_lead(cleaned)

    summary  = ai_result.get("summary", "")
    category = ai_result.get("category", "support")
    urgency  = ai_result.get("urgency", "low")     # unified key (M4)

    try:
        new_lead = insert_lead(g.user_id, cleaned, category, summary, urgency)
        lead_out = serialize_lead(dict(new_lead)) if new_lead else None  # shared helper (M2)

        return jsonify({"message": "Classification successful.", "data": lead_out}), 200

    except Exception:
        logger.exception("DB insert error in /classify for user %s", g.user_id)
        return jsonify({"error": "Failed to save classification to database."}), 500
