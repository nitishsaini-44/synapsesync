"""
routes/auth.py
──────────────
User registration and login endpoints.
Rate-limited to prevent brute-force / credential-stuffing attacks.
"""
import re
import logging
import datetime
import bcrypt
import jwt

from flask import Blueprint, request, jsonify, current_app
from backend.database.db import create_user, get_user_by_email
from backend.utils.auth_middleware import limiter

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)

# ── Input validation helpers ─────────────────────────────────────────────────

_EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

def _validate_register(data: dict) -> str | None:
    """Returns an error message string, or None if data is valid."""
    name     = (data.get("name") or "").strip()
    email    = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not name:
        return "Name is required."
    if len(name) > 100:
        return "Name must be 100 characters or fewer."
    if not email:
        return "Email is required."
    if not _EMAIL_RE.match(email):
        return "Please provide a valid email address."
    if not password:
        return "Password is required."
    if len(password) < 8:
        return "Password must be at least 8 characters."
    if len(password) > 128:
        return "Password must be 128 characters or fewer."
    return None


def _validate_login(data: dict) -> str | None:
    email    = (data.get("email") or "").strip()
    password = data.get("password") or ""
    if not email or not password:
        return "Email and password are required."
    return None


# ── Routes ───────────────────────────────────────────────────────────────────

@auth_bp.route("/register", methods=["POST"])
@limiter.limit("5 per minute")          # H2: rate limit — 5 registrations per IP per minute
def register():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON."}), 400

    error = _validate_register(data)
    if error:
        return jsonify({"error": error}), 400

    name     = data["name"].strip()
    email    = data["email"].strip().lower()    # Normalise email to lowercase
    password = data["password"]

    salt          = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    new_user = create_user(name, email, password_hash)
    if not new_user:
        return jsonify({"error": "An account with this email already exists."}), 409

    return jsonify({
        "message": "Registration successful.",
        "user": {
            "id":    new_user["id"],
            "name":  new_user["name"],
            "email": new_user["email"],
        },
    }), 201


@auth_bp.route("/login", methods=["POST"])
@limiter.limit("10 per minute")         # H2: rate limit — 10 login attempts per IP per minute
def login():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON."}), 400

    error = _validate_login(data)
    if error:
        return jsonify({"error": error}), 400

    email    = data["email"].strip().lower()
    password = data["password"]

    user = get_user_by_email(email)
    # Deliberate generic message — never reveal whether the email exists.
    if not user or not bcrypt.checkpw(
        password.encode("utf-8"), user["password_hash"].encode("utf-8")
    ):
        return jsonify({"error": "Invalid email or password."}), 401

    token = jwt.encode(
        {
            "user_id": user["id"],
            "email":   user["email"],
            "exp":     datetime.datetime.now(datetime.timezone.utc)
                       + datetime.timedelta(hours=24),
        },
        current_app.config["SECRET_KEY"],
        algorithm="HS256",
    )

    return jsonify({
        "message": "Login successful.",
        "token":   token,
        "user": {
            "id":    user["id"],
            "name":  user["name"],
            "email": user["email"],
        },
    }), 200
