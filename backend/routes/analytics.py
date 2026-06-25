"""
routes/analytics.py
────────────────────
Analytics endpoint.

Fixes:
- L1:  uses flask.g.user_id
- H6:  logging replaces bare exception string leakage
"""
import logging
from flask import Blueprint, jsonify, g
from backend.services.analytics_service import get_dashboard_stats
from backend.utils.auth_middleware import token_required

logger = logging.getLogger(__name__)

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/analytics", methods=["GET"])
@token_required
def analytics():
    try:
        stats = get_dashboard_stats(g.user_id)
        return jsonify({"message": "Analytics fetched successfully.", "data": stats}), 200
    except Exception:
        logger.exception("Error in /analytics for user %s", g.user_id)
        return jsonify({"error": "Failed to fetch analytics."}), 500
