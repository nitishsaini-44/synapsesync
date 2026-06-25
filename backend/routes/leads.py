"""
routes/leads.py
────────────────
Lead listing endpoint with server-side pagination.

Fixes:
- M11: pagination via ?page= and ?limit= query params (no more client-side slicing)
- M2:  uses serialize_leads() — no inline datetime conversion
- H6:  logging replaces print()
- L1:  uses flask.g.user_id
"""
import logging
from flask import Blueprint, request, jsonify, g
from backend.database.db import get_all_leads
from backend.utils.auth_middleware import token_required
from backend.utils.serializers import serialize_leads

logger = logging.getLogger(__name__)

leads_bp = Blueprint("leads", __name__)


@leads_bp.route("/leads", methods=["GET"])
@token_required
def get_leads():
    category = request.args.get("category", "all")
    page     = max(1, int(request.args.get("page",  1)))
    limit    = min(100, max(1, int(request.args.get("limit", 40))))
    offset   = (page - 1) * limit

    try:
        leads = get_all_leads(g.user_id, category_filter=category, limit=limit, offset=offset)
        return jsonify({
            "message": "Leads fetched successfully.",
            "data":    serialize_leads(list(leads)),
            "page":    page,
            "limit":   limit,
        }), 200
    except Exception:
        logger.exception("Error fetching leads for user %s", g.user_id)
        return jsonify({"error": "Failed to fetch leads."}), 500
