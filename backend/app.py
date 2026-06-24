from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from backend.config import Config

socketio = SocketIO(cors_allowed_origins="*")
from backend.database.db import init_db

# Import route blueprints
from backend.routes.summarize import summarize_bp
from backend.routes.classify import classify_bp
from backend.routes.reply import reply_bp
from backend.routes.analytics import analytics_bp
from backend.routes.leads import leads_bp

from backend.routes.auth import auth_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS for all domains
    CORS(app)

    # Initialize SocketIO with app
    socketio.init_app(app, async_mode='threading')

    # Register Blueprints
    app.register_blueprint(summarize_bp, url_prefix='/api')
    app.register_blueprint(classify_bp, url_prefix='/api')
    app.register_blueprint(reply_bp, url_prefix='/api')
    app.register_blueprint(analytics_bp, url_prefix='/api')
    app.register_blueprint(leads_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    from backend.routes.oauth import oauth_bp
    from backend.routes.user import user_bp
    from backend.routes.discord import discord_bp
    from backend.routes.internal import internal_bp
    from backend.routes.webhooks import webhooks_bp
    app.register_blueprint(oauth_bp, url_prefix='/api')
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(discord_bp, url_prefix='/api')
    app.register_blueprint(internal_bp, url_prefix='/api')
    app.register_blueprint(webhooks_bp, url_prefix='/api/webhooks')

    # Initialize Database
    with app.app_context():
        init_db()
        from backend.database.db import close_pool
        close_pool()

    @app.route('/health')
    def health_check():
        return {"status": "healthy"}, 200

    return app

app = create_app()

if __name__ == '__main__':
    import os
    port = int(os.environ.get("FLASK_PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=(app.config['FLASK_ENV'] == 'development'))
