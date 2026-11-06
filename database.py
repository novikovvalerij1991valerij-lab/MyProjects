import os
from crypto_utils import encrypt_text, decrypt_text

FILE_NAME = "diary_secure.txt"
FINANCE_FILE = "finance_secure.txt"
HABITS_FILE = "habits_secure.txt"

def load_diary(key):
    """Загружает и расшифровывает дневник."""
    if not os.path.exists(FILE_NAME):
        return ""
    with open(FILE_NAME, "rb") as f:
        encrypted_data = f.read()
    return decrypt_text(encrypted_data, key)

def save_diary(text, key):
    """Шифрует и сохраняет дневник."""
    encrypted_data = encrypt_text(text, key)
    with open(FILE_NAME, "wb") as f:
        f.write(encrypted_data)

def load_finance(key):
    if not os.path.exists(FINANCE_FILE):
        return ""
    with open(FINANCE_FILE, "rb") as f:
        encrypted_data = f.read()
    return decrypt_text(encrypted_data, key)

def save_finance(text, key):
    encrypted_data = encrypt_text(text, key)
    with open(FINANCE_FILE, "wb") as f:
        f.write(encrypted_data)
        HABITS_FILE = "habits_secure.txt"

def load_habits(key):
    if not os.path.exists(HABITS_FILE):
        return ""
    with open(HABITS_FILE, "rb") as f:
        encrypted_data = f.read()
    return decrypt_text(encrypted_data, key)

def save_habits(text, key):
    encrypted_data = encrypt_text(text, key)
    with open(HABITS_FILE, "wb") as f:
        f.write(encrypted_data)