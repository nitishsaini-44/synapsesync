from flask import Blueprint, jsonify, request, current_app, redirect
from backend.services.gmail_service import exchange_code_for_token, get_profile_email, watch_inbox
from backend.utils.encryption import encrypt_data
from backend.database.db import update_google_tokens
from backend.utils.auth_middleware import token_required
import urllib.parse
import jwt

oauth_bp = Blueprint('oauth', __name__)

@oauth_bp.route('/google/connect', methods=['GET'])
@token_required
def google_connect():
    """Returns the Google OAuth 2.0 authorization URL."""
    client_id = current_app.config.get('GOOGLE_CLIENT_ID')
    redirect_uri = current_app.config.get('GOOGLE_REDIRECT_URI')
    
    if not client_id or not redirect_uri:
        return jsonify({"error": "Google OAuth is not configured on the server."}), 500
        
    scope = "https://www.googleapis.com/auth/gmail.readonly"
    
    # Extract the token to pass as state parameter
    auth_header = request.headers.get('Authorization')
    token = auth_header.split(" ")[1] if auth_header else ""
    
    auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"response_type=code&"
        f"scope={urllib.parse.quote(scope)}&"
        "access_type=offline&"
        "prompt=consent&"
        f"state={token}"
    )
    
    return jsonify({"url": auth_url}), 200

@oauth_bp.route('/google/callback', methods=['GET'])
def google_callback():
    """Handles Google OAuth redirect, exchanges code, and redirects to frontend."""
    code = request.args.get('code')
    state_token = request.args.get('state')
    
    frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5173')
    frontend_redirect = f"{frontend_url}/integrations"
    
    if not code or not state_token:
        return redirect(f"{frontend_redirect}?error=missing_parameters")
        
    try:
        # Decode the state token to get user_id
        secret = current_app.config['SECRET_KEY']
        decoded = jwt.decode(state_token, secret, algorithms=["HS256"])
        user_id = decoded.get('user_id')
        
        if not user_id:
            return redirect(f"{frontend_redirect}?error=invalid_state")
            
        # Exchange code for token
        token_data = exchange_code_for_token(code)
        access_token = token_data.get('access_token')
        refresh_token = token_data.get('refresh_token')
        
        if not access_token:
            return redirect(f"{frontend_redirect}?error=token_exchange_failed")
            
        # Get user's Google email
        google_email = get_profile_email(access_token)
        
        # Encrypt and save refresh token
        encrypted_rt = encrypt_data(refresh_token) if refresh_token else None
        update_google_tokens(user_id, google_email, encrypted_rt)
        
        # Subscribe to Push Notifications
        topic_name = current_app.config.get('GOOGLE_PUBSUB_TOPIC')
        if topic_name:
            try:
                watch_inbox(access_token, topic_name)
                print(f"Successfully registered push watch for {google_email}")
            except Exception as e:
                print(f"Failed to register watch for {google_email}: {e}")
        
        return redirect(f"{frontend_redirect}?status=success")
        
    except jwt.ExpiredSignatureError:
        return redirect(f"{frontend_redirect}?error=session_expired")
    except jwt.InvalidTokenError:
        return redirect(f"{frontend_redirect}?error=invalid_token")
    except Exception as e:
        print(f"OAuth Callback Error: {e}")
        return redirect(f"{frontend_redirect}?error=server_error")
