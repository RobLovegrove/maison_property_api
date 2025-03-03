from PIL import Image
from io import BytesIO


def validate_image(image_data):
    """Validate image size and dimensions"""
    try:
        # Check file size (max 10MB)
        if len(image_data) > 10 * 1024 * 1024:
            return False, "Image size exceeds 10MB limit"

        # Check dimensions
        img = Image.open(BytesIO(image_data))
        width, height = img.size
        if width > 8192 or height > 8192:
            return False, "Image dimensions exceed 8192x8192 limit"

        return True, None

    except Exception as e:
        return False, f"Invalid image: {str(e)}"
