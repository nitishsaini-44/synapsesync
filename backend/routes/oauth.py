"""
routes/oauth.py
───────────────
Google OAuth 2.0 flow.

Security fix (H1): The full session JWT is NO LONGER passed as the OAuth state
parameter.  Instead we generate a short-lived (5-minute), purpose-specific
"oauth_state" token containing only the user_id.  This limits exposure — even
if the state is captured from a URL it expires quickly and contains no other
session data.

Fix (P2): Refresh-token persistence.
- If Google omits refresh_token in the response (happens when the user has
  already granted consent and did not use prompt=consent), we preserve the
  existing stored token as long as the Google account has not changed.
- If the Google account changes AND no new refresh_token is provided, we store
  the new email but leave the old token in place with a warning so automation
  continues using the previous account's token rather than silently breaking.
- Tokens are always stored Fernet-encrypted and never logged.
"""
import logging
import urllib.parse
import datetime
import jwt

from flask import Blueprint, jsonify, request, current_app, redirect, g as flask_g
from backend.services.gmail_service import (
    exchange_code_for_token,
    get_profile_email,
    watch_inbox,
)
from backend.utils.encryption import encrypt_data
from backend.database.db import update_google_tokens, get_user_by_id
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
    state = _make_oauth_state(flask_g.user_id)

    # access_type=offline  → Google issues a refresh token
    # prompt=consent       → forces the consent screen so Google always returns
    #                        a fresh refresh_token (required for initial grant;
    #                        subsequent re-authorisations also get a new token)
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
    """Handles Google OAuth redirect, exchanges code, stores refresh token.

    Refresh-token persistence rules (P2):
    1. Google returns a refresh_token  → encrypt and store it.
    2. Google omits refresh_token AND same Google account:
       → keep the existing stored token unchanged.
    3. Google omits refresh_token AND different Google account:
       → update the google_email to the new account, but keep the old token
         with a warning.  The user should reconnect properly to issue a new
         token for the new account.
    """
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
        refresh_token = token_data.get("refresh_token")  # may be None on re-auth

        if not access_token:
            return redirect(f"{frontend_redirect}?error=token_exchange_failed")

        google_email = get_profile_email(access_token)

        # ── Determine which refresh token to persist ──────────────────────────
        if refresh_token:
            # Google returned a fresh token — always use it.
            encrypted_rt = encrypt_data(refresh_token)
            logger.info(
                "OAuth callback: storing new refresh token for user_id=%s google_email=%s",
                user_id, google_email,
            )
            update_google_tokens(user_id, google_email, encrypted_rt)
        else:
            # Google did not return a refresh_token.
            # Preserve the existing stored token; only update the email if needed.
            existing_user = get_user_by_id(user_id)
            existing_email    = existing_user.get("google_email") if existing_user else None
            existing_token    = existing_user.get("google_refresh_token") if existing_user else None

            if not existing_token:
                # No token at all — connection cannot proceed without a token.
                logger.warning(
                    "OAuth callback: Google omitted refresh_token and user_id=%s has no "
                    "existing token. The user must reconnect (prompt=consent will be enforced "
                    "on next attempt since we already use prompt=consent in the auth URL).",
                    user_id,
                )
                return redirect(f"{frontend_redirect}?error=no_refresh_token")

            if existing_email and existing_email != google_email:
                # Account switch without a new token — keep old token with a warning.
                logger.warning(
                    "OAuth callback: Google account changed (user_id=%s, old=%s, new=%s) "
                    "but no new refresh_token was returned. Updating email but preserving "
                    "existing token — user should reconnect to issue a token for the new account.",
                    user_id, existing_email, google_email,
                )
            else:
                logger.info(
                    "OAuth callback: Google omitted refresh_token for user_id=%s (same account). "
                    "Preserving existing token.",
                    user_id,
                )

            # Update email but preserve the existing encrypted token.
            update_google_tokens(user_id, google_email, existing_token)

        # Subscribe to Gmail Push Notifications
        topic_name = current_app.config.get("GOOGLE_PUBSUB_TOPIC")
        if topic_name:
            try:
                watch_result = watch_inbox(access_token, topic_name)
                expiry_ms = watch_result.get("expiration")
                logger.info(
                    "Registered Gmail push watch for %s (expiry_ms=%s)",
                    google_email, expiry_ms,
                )
            except Exception:
                logger.warning(
                    "Failed to register Gmail watch for %s", google_email, exc_info=True
                )

        return redirect(f"{frontend_redirect}?status=success")

    except Exception:
        logger.exception("OAuth callback error for user_id=%s", user_id)
        return redirect(f"{frontend_redirect}?error=server_error")
