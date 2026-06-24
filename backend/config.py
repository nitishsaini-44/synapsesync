import os
from dotenv import load_dotenv

# Load environment variables from .env file (if present)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_secret_key')
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL', '')
    APP_API_KEY = os.environ.get('APP_API_KEY')
    FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:5173')
    ADMIN_USER_EMAIL = os.environ.get('ADMIN_USER_EMAIL', 'nitishsaini7055@gmail.com')
    
    # Security
    FERNET_KEY = os.environ.get('FERNET_KEY')
    
    # Google OAuth
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    GOOGLE_REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT_URI', 'http://localhost:5000/api/google/callback')
    GOOGLE_PUBSUB_TOPIC = os.environ.get('GOOGLE_PUBSUB_TOPIC', 'projects/synapsesync-1234/topics/gmail-push')
    
    # Celery
    _redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    if _redis_url.startswith('rediss://') and 'ssl_cert_reqs' not in _redis_url:
        _redis_url += '?ssl_cert_reqs=CERT_NONE'
        
    CELERY_BROKER_URL = _redis_url
    CELERY_RESULT_BACKEND = _redis_url
