import base64
from io import BytesIO

from PIL import Image, UnidentifiedImageError
from pillow_heif import register_heif_opener


register_heif_opener()

MAX_IMAGE_DIMENSION = 1280
JPEG_QUALITY = 82
STORAGE_IMAGE_MAX_DIMENSION = 2000
STORAGE_JPEG_QUALITY = 88


class ImageProcessingError(Exception):
    pass


def _load_normalized_image(
    file_bytes: bytes,
    filename: str,
    max_dimension: int,
    quality: int,
) -> bytes:
    try:
        with Image.open(BytesIO(file_bytes)) as image:
            # Force actual decode now so errors happen inside try block
            image.load()

            processed = image.convert("RGB")
            processed.thumbnail((max_dimension, max_dimension))

            buffer = BytesIO()
            processed.save(
                buffer,
                format="JPEG",
                quality=quality,
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

    return buffer.getvalue()


def preprocess_image_for_openai(file_bytes: bytes, filename: str) -> str:
    normalized_bytes = _load_normalized_image(
        file_bytes=file_bytes,
        filename=filename,
        max_dimension=MAX_IMAGE_DIMENSION,
        quality=JPEG_QUALITY,
    )
    encoded = base64.b64encode(normalized_bytes).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"


def preprocess_image_for_storage(file_bytes: bytes, filename: str) -> tuple[bytes, str]:
    normalized_bytes = _load_normalized_image(
        file_bytes=file_bytes,
        filename=filename,
        max_dimension=STORAGE_IMAGE_MAX_DIMENSION,
        quality=STORAGE_JPEG_QUALITY,
    )
    return normalized_bytes, "image/jpeg"
