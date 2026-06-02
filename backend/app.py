from flask import Flask
from flask_cors import CORS
from backend.config import Config
from backend.database.db import init_db

# Import route blueprints
from backend.routes.summarize import summarize_bp
from backend.routes.classify import classify_bp
from backend.routes.reply import reply_bp
from backend.routes.analytics import analytics_bp
from backend.routes.leads import leads_bp
from backend.routes.notify import notify_bp
from backend.routes.auth import auth_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS for all domains
    CORS(app)

    # Register Blueprints
    app.register_blueprint(summarize_bp, url_prefix='/api')
    app.register_blueprint(classify_bp, url_prefix='/api')
    app.register_blueprint(reply_bp, url_prefix='/api')
    app.register_blueprint(analytics_bp, url_prefix='/api')
    app.register_blueprint(leads_bp, url_prefix='/api')
    app.register_blueprint(notify_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    # Initialize Database
    with app.app_context():
        init_db()

    @app.route('/health')
    def health_check():
        return {"status": "healthy"}, 200

    return app

app = create_app()

if __name__ == '__main__':
    import os
    port = int(os.environ.get("FLASK_PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=(app.config['FLASK_ENV'] == 'development'))
