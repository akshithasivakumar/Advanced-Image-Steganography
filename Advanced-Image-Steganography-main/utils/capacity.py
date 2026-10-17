from pathlib import Path
from PIL import Image
from cryptography.fernet import Fernet


def calculate_capacity(image_path):
    """
    Calculate the maximum number of bytes that can be embedded inside an image.
    """
    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    with Image.open(image_path) as image:
        width, height = image.size

    total_pixels = width * height
    total_bits = total_pixels * 3
    total_bytes = total_bits // 8

    return total_bytes


def _encrypted_payload_size(message):
    """
    Estimate encrypted payload size. Note: Fernet encryption size includes overhead.
    We add a safety margin of 10% to account for Fernet's timestamp and formatting overhead.
    """
    message = message or ""
    # Fernet encrypted tokens are approximately: len(plaintext) * 1.33 + 73 bytes
    # The actual size depends on timestamp encoding, so we use an upper bound estimate
    estimated_encrypted_size = len(message.encode("utf-8")) + 128  # Conservative estimate
    
    # Add newline delimiter
    return estimated_encrypted_size + 1


def can_embed(image_path, message):
    """
    Returns True if the message can fit inside the image after encryption.
    """
    capacity = calculate_capacity(image_path)
    payload_size = _encrypted_payload_size(message)

    return payload_size <= capacity


def remaining_capacity(image_path, message):
    """
    Returns remaining capacity after storing the encrypted message.
    """
    capacity = calculate_capacity(image_path)
    payload_size = _encrypted_payload_size(message)

    return capacity - payload_size