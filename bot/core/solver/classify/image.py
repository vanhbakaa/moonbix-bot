from PIL import Image
import requests
from io import BytesIO

async def process_image(url):
    square_size = 110

    try:
        response = requests.get(url)
        image = Image.open(BytesIO(response.content))

        cropped_images = []

        for row in range(3):
            for col in range(3):
                x_min = col * square_size
                y_min = row * square_size
                x_max = x_min + square_size
                y_max = y_min + square_size

                # Crop the image
                cropped_image = image.crop((x_min, y_min, x_max, y_max))
                cropped_images.append(cropped_image)

        return cropped_images

    except Exception as err:
        return str(err)
