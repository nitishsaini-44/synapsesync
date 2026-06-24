import threading
from flask import Blueprint, jsonify, request, current_app
from backend.database.db import get_active_users
from backend.services.automation_service import process_user_emails

internal_bp = Blueprint('internal', __name__)

def require_internal_secret(f):
    """Simple decorator to ensure requests come from trusted internal services (n8n)."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        expected_secret = current_app.config.get('APP_API_KEY')
        provided_secret = request.headers.get('X-Internal-Secret')
        if not provided_secret or provided_secret != expected_secret:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

@internal_bp.route('/users/active', methods=['GET'])
@require_internal_secret
def get_active_users_endpoint():
    """Returns a list of active users to the n8n Master Workflow."""
    try:
        users = get_active_users()
        return jsonify(users), 200
    except Exception as e:
        print(f"Error fetching active users: {e}")
        return jsonify({"error": "Server error"}), 500

def run_in_background(app, user_id):
    """Wrapper to run the email processor inside the Flask application context."""
    with app.app_context():
        try:
            process_user_emails(user_id)
        except Exception as e:
            print(f"Background thread error for user {user_id}: {e}")

@internal_bp.route('/process-user', methods=['POST'])
@require_internal_secret
def process_user_endpoint():
    """Triggered by n8n to process emails for a specific user."""
    data = request.json
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
        
    # We must pass the actual application object to the thread so it has the DB/Config context
    app = current_app._get_current_object()
    
    # Start the processing in a background thread
    thread = threading.Thread(target=run_in_background, args=(app, user_id))
    thread.daemon = True # Allows the server to exit even if threads are running
    thread.start()
    
    # Return 202 Accepted immediately so n8n finishes in milliseconds
    return jsonify({"message": f"Processing started in background for user {user_id}"}), 202
