from io import BytesIO

from PIL import Image


def bytes_from_file(path: str) -> bytes:
    with open(path, "rb") as file:
        return file.read(-1)


def image_from_bytes(image_bytes: bytes) -> Image:
    stream = BytesIO(image_bytes)
    return Image.open(stream)


def image_to_bytes(image: Image) -> bytes:
    buf = BytesIO()
    image.save(buf, format='JPEG')
    return buf.getvalue()


def image_to_file(image: Image, path: str):
    with open(path, "wb") as file:
        image.save(file, format="JPEG")


def downscale_image(b_image: bytes, max_size: int = 1000) -> bytes:
    image = image_from_bytes(b_image)
    max_dimension: int = image.size[0] if image.size[0] > image.size[1] else image.size[1]
    if max_dimension <= max_size:
        return b_image
    resize_factor = max_size / max_dimension
    downscaled_image: Image = image.resize([int(x * resize_factor) for x in image.size])
    return image_to_bytes(downscaled_image)


class Notifier:

    def __init__(self):
        pass

    def notify(self, user_data: dict, message_data: dict):
        pass


class CliNotifier(Notifier):

    def notify(self, user_data: dict, message_data: dict):
        print(user_data, message_data)


if __name__ == '__main__':
    img = bytes_from_file("image.jpg")
    downscale_image(img)
