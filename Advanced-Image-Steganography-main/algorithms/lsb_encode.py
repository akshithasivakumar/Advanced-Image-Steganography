from PIL import Image

from security.encrypt import encrypt_message


def encode_image(image_path, output_path, message, password):

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

    index = 0

    for i, pixel in enumerate(pixels):

        if index >= len(binary_secret):
            break

        r, g, b = pixel

        r = format(r, "08b")
        g = format(g, "08b")
        b = format(b, "08b")

        if index < len(binary_secret):
            r = r[:-1] + binary_secret[index]
            index += 1

        if index < len(binary_secret):
            g = g[:-1] + binary_secret[index]
            index += 1

        if index < len(binary_secret):
            b = b[:-1] + binary_secret[index]
            index += 1

        pixels[i] = (
            int(r, 2),
            int(g, 2),
            int(b, 2)
        )

    encoded_image = Image.new("RGB", (width, height))
    encoded_image.putdata(pixels)

    try:
        encoded_image.save(output_path)
    except (IOError, OSError) as e:
        raise IOError(f"Failed to save image to {output_path}: {str(e)}")
    except Exception as e:
        raise Exception(f"Image save failed: {str(e)}")