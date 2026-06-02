import os
from dotenv import load_dotenv

# Load environment variables from .env file (if present)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_secret_key')
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    N8N_WEBHOOK_URL = os.environ.get('N8N_WEBHOOK_URL', 'http://localhost:5678')
    DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL', '')
    APP_API_KEY = os.environ.get('APP_API_KEY', 'n8n_secure_key_123')
    ADMIN_USER_EMAIL = os.environ.get('ADMIN_USER_EMAIL', 'nitishsaini7055@gmail.com')
