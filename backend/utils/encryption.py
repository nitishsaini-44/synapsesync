from cryptography.fernet import Fernet
from flask import current_app

def encrypt_data(data: str) -> str:
    if not data:
        return None
    fernet_key = current_app.config.get('FERNET_KEY')
    if not fernet_key:
        raise ValueError("FERNET_KEY is missing from configuration")
    f = Fernet(fernet_key.encode())
    return f.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data: str) -> str:
    if not encrypted_data:
        return None
    fernet_key = current_app.config.get('FERNET_KEY')
    if not fernet_key:
        raise ValueError("FERNET_KEY is missing from configuration")
    f = Fernet(fernet_key.encode())
    return f.decrypt(encrypted_data.encode()).decode()
