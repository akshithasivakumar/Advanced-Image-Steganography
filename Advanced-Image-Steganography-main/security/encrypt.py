import base64

from cryptography.fernet import Fernet

from security.password_manager import derive_fernet_key, generate_salt


def encrypt_message(password, message):
    if not password:
        raise ValueError("Password is required.")

    if not message:
        raise ValueError("Message is empty.")

    salt = generate_salt()
    key = derive_fernet_key(password, salt)
    f = Fernet(key)
    encrypted_message = f.encrypt(message.encode("utf-8"))

    salt_b64 = base64.urlsafe_b64encode(salt).decode("utf-8")
    token_b64 = base64.urlsafe_b64encode(encrypted_message).decode("utf-8")

    return f"{salt_b64}:{token_b64}"