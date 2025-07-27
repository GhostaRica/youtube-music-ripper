import os
import tempfile
import requests
from PIL import Image

def download_thumbnail(thumbnail_url: str) -> str:
    response = requests.get(thumbnail_url, stream=True)
    if not response.ok:
        raise Exception(f"Failed to download thumbnail: {response.status_code}")

    suffix = os.path.splitext(thumbnail_url)[-1] or ".jpg"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        for chunk in response.iter_content(1024):
            tmp_file.write(chunk)
        tmp_path = tmp_file.name

    crop_thumbnail_to_square(tmp_path)

    if suffix == ".webp":
        tmp_path = convert_webp_to_jpeg(tmp_path)

    return tmp_path

def crop_thumbnail_to_square(path: str):
    img = Image.open(path)
    width, height = img.size
    min_dim = min(width, height)
    left = (width - min_dim) // 2
    top = (height - min_dim) // 2
    right = (width + min_dim) // 2
    bottom = (height + min_dim) // 2
    img_cropped = img.crop((left, top, right, bottom))
    img_cropped.save(path)

def convert_webp_to_jpeg(image_path: str) -> str:
    with Image.open(image_path) as img:
        rgb_image = img.convert("RGB")
        jpeg_path = image_path.rsplit('.', 1)[0] + ".jpg"
        rgb_image.save(jpeg_path, format="JPEG")
    return jpeg_path
