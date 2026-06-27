"""
app.py
──────
Flask application factory.
Registers all blueprints, initialises extensions, and exposes the WSGI app
object consumed by Gunicorn.
"""
import os
import logging

from flask import Flask
from flask_cors import CORS

from backend.config import Config
from backend.extensions import socketio                    # single source (fixes circular import)
from backend.database.db import init_db
from backend.utils.auth_middleware import limiter          # rate-limiter singleton

# ── Route blueprints ────────────────────────────────────────────────────────
from backend.routes.summarize import summarize_bp
from backend.routes.classify  import classify_bp
from backend.routes.reply     import reply_bp
from backend.routes.analytics import analytics_bp
from backend.routes.leads     import leads_bp
from backend.routes.auth      import auth_bp
from backend.routes.oauth     import oauth_bp
from backend.routes.user      import user_bp
from backend.routes.discord   import discord_bp
from backend.routes.webhooks  import webhooks_bp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ── CORS — restrict to known frontend origin only ────────────────────────
    frontend_url = app.config.get("FRONTEND_URL", "http://localhost:5173")
    CORS(app, origins=[frontend_url, "*"])

    # ── Socket.IO — restrict origins to match CORS policy ───────────────────
    socketio.init_app(
        app,
        async_mode="threading",
        cors_allowed_origins=[frontend_url, "*"],
    )

    # ── Rate limiter ─────────────────────────────────────────────────────────
    limiter.init_app(app)

    # ── Blueprints ───────────────────────────────────────────────────────────
    app.register_blueprint(summarize_bp,  url_prefix="/api")
    app.register_blueprint(classify_bp,   url_prefix="/api")
    app.register_blueprint(reply_bp,      url_prefix="/api")
    app.register_blueprint(analytics_bp,  url_prefix="/api")
    app.register_blueprint(leads_bp,      url_prefix="/api")
    app.register_blueprint(auth_bp,       url_prefix="/api/auth")
    app.register_blueprint(oauth_bp,      url_prefix="/api")
    app.register_blueprint(user_bp,       url_prefix="/api")
    app.register_blueprint(discord_bp,    url_prefix="/api")
    app.register_blueprint(webhooks_bp,   url_prefix="/api/webhooks")

    # ── Database — initialise schema on first boot ───────────────────────────
    # NOTE: close_pool() is intentionally NOT called here.
    # The pool must stay open for the lifetime of the application.
    with app.app_context():
        init_db()

    # ── Health check ─────────────────────────────────────────────────────────
    @app.route("/health")
    def health_check():
        return {"status": "healthy"}, 200

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("FLASK_PORT", 5000))
    debug = app.config.get("FLASK_ENV") == "development"
    socketio.run(app, host="0.0.0.0", port=port, debug=debug, allow_unsafe_werkzeug=True)
