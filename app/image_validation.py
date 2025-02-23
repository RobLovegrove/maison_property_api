from PIL import Image
from io import BytesIO


def validate_image(image_data):
    """Validate image size and dimensions"""
    try:
        # Check file size (max 5MB)
        if len(image_data) > 5 * 1024 * 1024:
            return False, "Image size exceeds 5MB limit"

        # Check dimensions
        img = Image.open(BytesIO(image_data))
        width, height = img.size
        if width > 4096 or height > 4096:
            return False, "Image dimensions exceed 4096x4096 limit"

        return True, None

    except Exception as e:
        return False, f"Invalid image: {str(e)}"
