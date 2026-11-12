
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter


def extract_text_from_image(uploaded_file):

    try:
        uploaded_file.seek(0)

        image = Image.open(uploaded_file)

        # Convert image to RGB
        image = image.convert("RGB")

        # Improve image readability
        image = ImageEnhance.Contrast(image).enhance(1.5)
        image = ImageEnhance.Sharpness(image).enhance(1.5)

        # OCR extraction
        extracted_text = pytesseract.image_to_string(
            image,
            config="--psm 6"
        )

        if not extracted_text.strip():
            return ""

        return extracted_text.strip()

    except Exception as error:

        raise RuntimeError(
            f"Image OCR failed: {error}"
        )
      
