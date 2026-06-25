"""
utils/encryption.py
────────────────────
Fernet AES-256 encryption/decryption helpers.

Fixes:
- Module-level Fernet singleton (created once, not per call)
- Added error handling on decrypt_data() — logs a warning on corrupted/wrong-key data
"""
import os
import logging
from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger(__name__)

# Module-level singleton — created once, reused for every call.
_fernet: Fernet | None = None


def _get_fernet() -> Fernet:
    global _fernet
    if _fernet is None:
        key = os.environ.get("FERNET_KEY", "")
        if not key:
            raise ValueError("FERNET_KEY environment variable is not set.")
        _fernet = Fernet(key.encode())
    return _fernet


def encrypt_data(plain_text: str) -> str:
    """Encrypts a plain-text string and returns the Fernet token as a UTF-8 string."""
    return _get_fernet().encrypt(plain_text.encode()).decode()


def decrypt_data(encrypted: str) -> str | None:
    """
    Decrypts a Fernet-encrypted string.
    Returns None (and logs a warning) if the token is invalid or was encrypted
    with a different key — rather than raising an unhandled exception.
    """
    try:
        return _get_fernet().decrypt(encrypted.encode()).decode()
    except InvalidToken:
        logger.warning(
            "decrypt_data: failed to decrypt token — invalid token or wrong FERNET_KEY."
        )
        return None
    except Exception:
        logger.exception("decrypt_data: unexpected error")
        return None
