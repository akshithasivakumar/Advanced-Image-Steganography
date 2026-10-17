from PIL import Image

from security.decrypt import decrypt_message


def decode_image(file_path, password, loading_window=None):
    with Image.open(file_path) as encoded_image:
        encoded_image = encoded_image.convert("RGB")
        pixels = list(encoded_image.getdata())

    binary_secret = "".join(
        format(channel, "08b")[-1]
        for pixel in pixels
        for channel in pixel
    )

    secret_bytes = bytearray()
    for i in range(0, len(binary_secret), 8):
        byte = binary_secret[i:i + 8]
        if len(byte) < 8:
            break
        secret_bytes.append(int(byte, 2))

    # Safety check: limit payload size to prevent memory exhaustion
    if len(secret_bytes) > 1000000:  # 1 MB limit
        raise ValueError("Extracted payload exceeds maximum size limit (1 MB).")

    secret_message = secret_bytes.decode("utf-8", errors="ignore")
    secret_message = secret_message.split("\n", 1)[0]

    if not secret_message:
        raise ValueError("No hidden message found in the selected image.")

    try:
        original_message = decrypt_message(password, secret_message)
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Decryption failed: {str(e)}")

    return original_message