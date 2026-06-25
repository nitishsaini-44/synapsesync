"""
auth_middleware.py
──────────────────
Route decorators for JWT authentication, API-key auth, and internal-secret auth.
Uses flask.g (thread-safe request context) to store the resolved user_id.
"""
import logging
import jwt
from functools import wraps
from flask import request, jsonify, current_app, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

logger = logging.getLogger(__name__)

# ── Rate-limiter (shared instance, initialised with app in app.py) ────────────
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],           # No global default; limits are applied per-route.
    storage_uri="memory://",     # Falls back to in-process memory if REDIS_URL absent.
)


def token_required(f):
    """Verifies the Bearer JWT and writes user_id to flask.g."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]

        if not token:
            return jsonify({"error": "Authentication token is missing."}), 401

        try:
            data = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"],
            )
            g.user_id = data["user_id"]    # ← flask.g is thread-safe; avoids mutating request
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Authentication token has expired."}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid authentication token."}), 401
        except Exception:
            logger.exception("Unexpected error decoding JWT")
            return jsonify({"error": "Authentication error."}), 401

        return f(*args, **kwargs)

    return decorated
