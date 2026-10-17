import base64
import os

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def generate_salt():
    return os.urandom(16)


def derive_fernet_key(password, salt):
    if not password:
        raise ValueError("Password is required.")

    if not salt:
        raise ValueError("Salt is required.")

    password_bytes = password.encode("utf-8")
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key_bytes = kdf.derive(password_bytes)

    return base64.urlsafe_b64encode(key_bytes)