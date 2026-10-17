import base64

from cryptography.fernet import Fernet, InvalidToken

from security.password_manager import derive_fernet_key


def decrypt_message(password, payload):
    if not password:
        raise ValueError("Password is required.")

    if not payload:
        raise ValueError("No hidden message found in the selected image.")

    if ":" not in payload:
        raise ValueError("Invalid encrypted payload format.")

    salt_b64, token_b64 = payload.split(":", 1)

    try:
        salt = base64.urlsafe_b64decode(salt_b64.encode("utf-8"))
        token = base64.urlsafe_b64decode(token_b64.encode("utf-8"))
    except Exception as exc:
        raise ValueError("Invalid encrypted payload format.") from exc

    key = derive_fernet_key(password, salt)
    f = Fernet(key)

    try:
        return f.decrypt(token).decode("utf-8")
    except InvalidToken as exc:
        raise ValueError("Invalid password. The password does not match the encrypted message.") from exc