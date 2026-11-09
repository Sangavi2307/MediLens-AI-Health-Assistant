
import streamlit as st
import pymupdf
import pytesseract

from PIL import Image
from io import BytesIO


def extract_text_from_pdf(uploaded_file):
    """
    Extract text from an uploaded PDF medical report.
    """

    try:
        file_bytes = uploaded_file.getvalue()

        if not file_bytes:
            return ""

        document = pymupdf.open(
            stream=file_bytes,
            filetype="pdf"
        )

        extracted_text = []

        for page_number, page in enumerate(document, start=1):
            page_text = page.get_text("text")

            if page_text.strip():
                extracted_text.append(
                    f"Page {page_number}\n{page_text}"
                )

        document.close()

        return "\n\n".join(extracted_text).strip()

    except Exception:
        st.error(
            "Unable to extract text from this PDF. "
            "Please check whether the file is valid."
        )
        return ""


def extract_text_from_image(uploaded_file):
    """
    Extract text from a medical report image using OCR.
    Supports PNG, JPG and JPEG images.
    """

    try:
        image_bytes = uploaded_file.getvalue()

        if not image_bytes:
            return ""

        image = Image.open(
            BytesIO(image_bytes)
        )

        image = image.convert("RGB")

        extracted_text = pytesseract.image_to_string(
            image,
            config="--psm 6"
        )

        return extracted_text.strip()

    except Exception:
        st.error(
            "Unable to read text from this image. "
            "Please upload a clear PNG or JPG image."
        )
        return ""


def extract_report_text(uploaded_file):
    """
    Automatically identify the uploaded file type
    and extract its text.
    """

    file_name = uploaded_file.name.lower()

    if file_name.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)

    elif file_name.endswith(
        (".png", ".jpg", ".jpeg")
    ):
        return extract_text_from_image(uploaded_file)

    else:
        st.warning(
            "Unsupported file format. "
            "Please upload a PDF, PNG or JPG file."
        )
        return ""
      
