import random
from PIL import Image

from security.encrypt import encrypt_message
from security.decrypt import decrypt_message


def encode_image(image_path, output_path, message, password):
    """
    Random LSB encoding: Uses password-derived seed to shuffle pixel positions
    before embedding bits, providing an additional layer of security.
    """
    try:
        encrypted_message = encrypt_message(password, message)
    except Exception as exc:
        raise ValueError(f"Failed to encrypt message: {str(exc)}") from exc

    # Open image
    try:
        with Image.open(image_path) as image:
            image = image.convert("RGB")
            pixels = list(image.getdata())
            width, height = image.size
    except IOError as e:
        raise IOError(f"Failed to load image: {image_path}. {str(e)}")
    except Exception as e:
        raise Exception(f"Invalid or unsupported image format: {str(e)}")

    # Convert encrypted bytes to string
    secret_message = encrypted_message + "\n"

    binary_secret = "".join(
        format(ord(char), "08b")
        for char in secret_message
    )

    # Pad to multiple of 3
    while len(binary_secret) % 3 != 0:
        binary_secret += "0"

    max_bits = width * height * 3

    if len(binary_secret) > max_bits:
        raise ValueError(
            "Secret message is too long to fit in the image."
        )

    # Generate deterministic random seed from password
    # Use a simple hash of the password to create a reproducible seed
    seed = sum(ord(c) * (i + 1) for i, c in enumerate(password)) % (2**32)

    # Create list of all possible bit positions (pixel_index, channel_index)
    # channel_index: 0=R, 1=G, 2=B
    all_positions = [
        (pixel_idx, channel_idx)
        for pixel_idx in range(len(pixels))
        for channel_idx in range(3)
    ]

    # Shuffle positions using the deterministic seed
    random.seed(seed)
    random.shuffle(all_positions)

    # Select only the positions we need
    positions_to_use = all_positions[:len(binary_secret)]

    # Sort positions back by pixel index for easier processing
    # but remember the original shuffled order for embedding
    index = 0
    for pixel_idx, channel_idx in positions_to_use:
        r, g, b = pixels[pixel_idx]
        channels = [r, g, b]

        # Modify the specific channel
        channel_bin = format(channels[channel_idx], "08b")
        channels[channel_idx] = int(channel_bin[:-1] + binary_secret[index], 2)

        pixels[pixel_idx] = (channels[0], channels[1], channels[2])
        index += 1

    encoded_image = Image.new("RGB", (width, height))
    encoded_image.putdata(pixels)

    try:
        encoded_image.save(output_path)
    except (IOError, OSError) as e:
        raise IOError(f"Failed to save image to {output_path}: {str(e)}")
    except Exception as e:
        raise Exception(f"Image save failed: {str(e)}")


def decode_image(file_path, password, loading_window=None):
    """
    Random LSB decoding: Uses password-derived seed to determine which pixel
    positions contain the hidden data, then extracts and decrypts the message.
    """
    with Image.open(file_path) as encoded_image:
        encoded_image = encoded_image.convert("RGB")
        pixels = list(encoded_image.getdata())
        width, height = encoded_image.size

    # Generate deterministic random seed from password (same as encoding)
    seed = sum(ord(c) * (i + 1) for i, c in enumerate(password)) % (2**32)

    # Create list of all possible bit positions
    all_positions = [
        (pixel_idx, channel_idx)
        for pixel_idx in range(len(pixels))
        for channel_idx in range(3)
    ]

    # Shuffle positions using the same deterministic seed
    random.seed(seed)
    random.shuffle(all_positions)

    # We don't know the exact length of the hidden message, so we'll extract
    # bits until we find the newline terminator or hit a reasonable limit
    max_bits_to_extract = min(len(all_positions), 1000000)  # 1MB limit

    binary_secret = ""
    for i in range(max_bits_to_extract):
        if i >= len(all_positions):
            break
        pixel_idx, channel_idx = all_positions[i]
        if pixel_idx >= len(pixels):
            break

        r, g, b = pixels[pixel_idx]
        channel_value = [r, g, b][channel_idx]
        binary_secret += format(channel_value, "08b")[-1]

        # Check if we've found the newline terminator
        if len(binary_secret) >= 8:
            # Check every 8 bits for the newline character
            if len(binary_secret) % 8 == 0:
                last_byte = binary_secret[-8:]
                if chr(int(last_byte, 2)) == '\n':
                    break

    # Convert binary to bytes
    secret_bytes = bytearray()
    for i in range(0, len(binary_secret), 8):
        byte = binary_secret[i:i + 8]
        if len(byte) < 8:
            break
        secret_bytes.append(int(byte, 2))

    # Safety check: limit payload size
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