import base64
from io import BytesIO

from PIL import Image, UnidentifiedImageError
from pillow_heif import register_heif_opener


register_heif_opener()

MAX_IMAGE_DIMENSION = 1280
JPEG_QUALITY = 82


class ImageProcessingError(Exception):
    pass


def preprocess_image_for_openai(file_bytes: bytes, filename: str) -> str:
    try:
        with Image.open(BytesIO(file_bytes)) as image:
            # Force actual decode now so errors happen inside try block
            image.load()

            processed = image.convert("RGB")
            processed.thumbnail((MAX_IMAGE_DIMENSION, MAX_IMAGE_DIMENSION))

            buffer = BytesIO()
            processed.save(
                buffer,
                format="JPEG",
                quality=JPEG_QUALITY,
                optimize=True,
            )

    except UnidentifiedImageError as exc:
        raise ImageProcessingError(
            f'"{filename}" could not be processed for AI analysis. Use JPG, PNG, WEBP, HEIC, or HEIF images.'
        ) from exc

    except OSError as exc:
        raise ImageProcessingError(
            f'"{filename}" uses an image format that is not supported for AI preprocessing.'
        ) from exc

    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"