"""
config.py
─────────
Centralised configuration loaded from environment variables.
All required secrets raise ValueError on startup if missing — no silent weak defaults.
"""
import os
from dotenv import load_dotenv

# Load .env when running locally (no-op in Docker / Render where vars are injected)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))


def _require(key: str) -> str:
    """Return the env var value or raise a clear error at startup."""
    value = os.environ.get(key)
    if not value:
        raise ValueError(
            f"Required environment variable '{key}' is not set. "
            f"See .env.example for the full list of required variables."
        )
    return value


class Config:
    # ── Security ─────────────────────────────────────────────────────────────
    # SECRET_KEY MUST be set — no fallback to a weak default.
    SECRET_KEY = _require("SECRET_KEY")
    FERNET_KEY = _require("FERNET_KEY")

    # ── App behaviour ────────────────────────────────────────────────────────
    FLASK_ENV     = os.environ.get("FLASK_ENV", "production")
    FRONTEND_URL  = os.environ.get("FRONTEND_URL", "http://localhost:5173")

    # ── Database ─────────────────────────────────────────────────────────────
    POSTGRES_HOST     = _require("POSTGRES_HOST")
    POSTGRES_PASSWORD = _require("POSTGRES_PASSWORD")

    # ── Google OAuth ─────────────────────────────────────────────────────────
    GOOGLE_CLIENT_ID     = os.environ.get("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI  = os.environ.get(
        "GOOGLE_REDIRECT_URI", "http://localhost:5000/api/google/callback"
    )
    GOOGLE_PUBSUB_TOPIC = os.environ.get("GOOGLE_PUBSUB_TOPIC", "")

    # ── Celery / Redis ───────────────────────────────────────────────────────
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    
    _redis_url = REDIS_URL
    # Upstash uses rediss:// (TLS). Append ssl_cert_reqs=CERT_NONE for
    # compatibility — accepted risk documented here.
    if _redis_url.startswith("rediss://") and "ssl_cert_reqs" not in _redis_url:
        _redis_url += "?ssl_cert_reqs=CERT_NONE"

    CELERY_BROKER_URL     = _redis_url
    CELERY_RESULT_BACKEND = _redis_url
