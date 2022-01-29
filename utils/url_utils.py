import io

from PIL import Image
from requests import get


def download_image(url) -> bytes:
    data = get(url, timeout=10).content
    return Image.open(io.BytesIO(data))
