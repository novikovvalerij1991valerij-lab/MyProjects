import base64
import hashlib
from cryptography.fernet import Fernet

def get_key(password):
    """Превращает пароль в ключ шифрования."""
    key = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(key)

def encrypt_text(text, key):
    """Шифрует текст."""
    f_obj = Fernet(key)
    return f_obj.encrypt(text.encode("utf-8"))

def decrypt_text(encrypted_data, key):
    """Расшифровывает текст. Возвращает None, если пароль неверный."""
    try:
        f_obj = Fernet(key)
        return f_obj.decrypt(encrypted_data).decode("utf-8")
    except Exception:
        return None