"""
routes/summarize.py
────────────────────
Manual summarise endpoint — used by the AI Assistant page.

M1: Removed the local clean_html() function; now uses clean_email_body()
from utils/email_cleaner.py — the single canonical implementation.
"""
import logging
from flask import Blueprint, request, jsonify, g
from backend.services.ai_service import summarize_message
from backend.utils.auth_middleware import token_required
from backend.utils.email_cleaner import clean_email_body

logger = logging.getLogger(__name__)

summarize_bp = Blueprint("summarize", __name__)


@summarize_bp.route("/summarize", methods=["POST"])
@token_required
def summarize_email():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON."}), 400

    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"error": "A 'message' field is required."}), 400

    if len(message) > 50_000:
        return jsonify({"error": "Message is too large. Maximum 50,000 characters."}), 400

    cleaned = clean_email_body(message)
    result  = summarize_message(cleaned)

    return jsonify({"message": "Summarization successful.", "data": result}), 200
