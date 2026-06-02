from flask import Blueprint, request, jsonify
from backend.database.db import get_all_leads
from backend.utils.auth_middleware import token_required

leads_bp = Blueprint('leads', __name__)

@leads_bp.route('/leads', methods=['GET'])
@token_required
def get_leads():
    category = request.args.get('category', 'all')
    try:
        leads = get_all_leads(request.user_id, category)
        # Convert datetimes
        for lead in leads:
            if lead.get('created_at'):
                lead['created_at'] = lead['created_at'].isoformat()
                
        return jsonify({
            "message": "Leads fetched successfully",
            "data": leads
        }), 200
    except Exception as e:
        print(f"Error fetching leads: {e}")
        return jsonify({"error": "Failed to fetch leads"}), 500
