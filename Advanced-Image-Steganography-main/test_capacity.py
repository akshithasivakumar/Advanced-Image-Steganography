from utils.capacity import *

image = "assets/test_image.png"

print(calculate_capacity(image))

print(can_embed(image, "Hello World"))

print(remaining_capacity(image, "Hello World"))