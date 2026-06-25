"""
routes/oauth.py
───────────────
Google OAuth 2.0 flow.

Security fix (H1): The full session JWT is NO LONGER passed as the OAuth state
parameter.  Instead we generate a short-lived (5-minute), purpose-specific
"oauth_state" token containing only the user_id.  This limits exposure — even
if the state is captured from a URL it expires quickly and contains no other
session data.
"""
import logging
import urllib.parse
import datetime
import jwt

from flask import Blueprint, jsonify, request, current_app, redirect
from backend.services.gmail_service import (
    exchange_code_for_token,
    get_profile_email,
    watch_inbox,
)
from backend.utils.encryption import encrypt_data
from backend.database.db import update_google_tokens
from backend.utils.auth_middleware import token_required

logger = logging.getLogger(__name__)

oauth_bp = Blueprint("oauth", __name__)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _make_oauth_state(user_id: int) -> str:
    """
    Creates a short-lived (5 min) JWT used exclusively as the OAuth state
    parameter.  It contains only `user_id` and a `type` claim so it cannot
    be mistaken for — or used as — a session token.
    """
    return jwt.encode(
        {
            "user_id": user_id,
            "type":    "oauth_state",
            "exp":     datetime.datetime.now(datetime.timezone.utc)
                       + datetime.timedelta(minutes=5),
        },
        current_app.config["SECRET_KEY"],
        algorithm="HS256",
    )


def _decode_oauth_state(state: str) -> int | None:
    """
    Decodes and validates an oauth_state token.
    Returns the user_id or None if the token is invalid/expired.
    """
    try:
        data = jwt.decode(
            state,
            current_app.config["SECRET_KEY"],
            algorithms=["HS256"],
        )
        if data.get("type") != "oauth_state":
            return None
        return data.get("user_id")
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


# ── Routes ───────────────────────────────────────────────────────────────────

@oauth_bp.route("/google/connect", methods=["GET"])
@token_required
def google_connect():
    """Returns the Google OAuth 2.0 authorisation URL."""
    client_id    = current_app.config.get("GOOGLE_CLIENT_ID")
    redirect_uri = current_app.config.get("GOOGLE_REDIRECT_URI")

    if not client_id or not redirect_uri:
        return jsonify({"error": "Google OAuth is not configured on the server."}), 500

    scope = "https://www.googleapis.com/auth/gmail.readonly"

    # Use a short-lived, purpose-specific state token — NOT the session JWT.
    state = _make_oauth_state(g_user_id := __import__("flask").g.user_id)

    auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={client_id}&"
        f"redirect_uri={urllib.parse.quote(redirect_uri, safe='')}&"
        f"response_type=code&"
        f"scope={urllib.parse.quote(scope)}&"
        "access_type=offline&"
        "prompt=consent&"
        f"state={urllib.parse.quote(state)}"
    )

    return jsonify({"url": auth_url}), 200


@oauth_bp.route("/google/callback", methods=["GET"])
def google_callback():
    """Handles Google OAuth redirect, exchanges code, stores refresh token."""
    code        = request.args.get("code")
    state_token = request.args.get("state")

    frontend_url      = current_app.config.get("FRONTEND_URL", "http://localhost:5173")
    frontend_redirect = f"{frontend_url}/integrations"

    if not code or not state_token:
        return redirect(f"{frontend_redirect}?error=missing_parameters")

    # Validate the state token — short-lived oauth_state JWT only
    user_id = _decode_oauth_state(state_token)
    if not user_id:
        return redirect(f"{frontend_redirect}?error=invalid_or_expired_state")

    try:
        token_data    = exchange_code_for_token(code)
        access_token  = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")

        if not access_token:
            return redirect(f"{frontend_redirect}?error=token_exchange_failed")

        google_email = get_profile_email(access_token)
        encrypted_rt = encrypt_data(refresh_token) if refresh_token else None
        update_google_tokens(user_id, google_email, encrypted_rt)

        # Subscribe to Gmail Push Notifications
        topic_name = current_app.config.get("GOOGLE_PUBSUB_TOPIC")
        if topic_name:
            try:
                watch_inbox(access_token, topic_name)
                logger.info("Registered Gmail push watch for %s", google_email)
            except Exception:
                logger.warning(
                    "Failed to register Gmail watch for %s", google_email, exc_info=True
                )

        return redirect(f"{frontend_redirect}?status=success")

    except Exception:
        logger.exception("OAuth callback error for user_id=%s", user_id)
        return redirect(f"{frontend_redirect}?error=server_error")
