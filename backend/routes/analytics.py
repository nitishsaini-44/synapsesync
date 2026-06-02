from flask import Blueprint, jsonify, request
from backend.services.analytics_service import get_dashboard_stats
from backend.utils.auth_middleware import token_required

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics', methods=['GET'])
@token_required
def analytics():
    try:
        stats = get_dashboard_stats(request.user_id)
        return jsonify({
            "message": "Analytics fetched successfully",
            "data": stats
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
