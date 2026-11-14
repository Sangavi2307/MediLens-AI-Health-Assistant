
"""
MediLens - Medical Report Text Extractor

Supports:
- Text-based PDF files
- Scanned PDF files using OCR
- PNG, JPG and JPEG images
- Multi-page PDF reports
"""

from io import BytesIO


# --------------------------------------------------
# STREAMLIT MESSAGE HELPER
# --------------------------------------------------

def show_error(message):
    try:
        import streamlit as st
        st.error(message)
    except Exception:
        pass


def show_warning(message):
    try:
        import streamlit as st
        st.warning(message)
    except Exception:
        pass


# --------------------------------------------------
# IMAGE OCR HELPER
# --------------------------------------------------

def _ocr_image(image):
    """Extract text from a PIL image using Tesseract OCR."""

    try:
        import pytesseract

        image = image.convert("RGB")

        text = pytesseract.image_to_string(
            image,
            config="--oem 3 --psm 6"
        )

        return text.strip()

    except ImportError:
        raise RuntimeError(
            "Pytesseract is missing. "
            "Add pytesseract to requirements.txt."
        )

    except Exception as error:
        raise RuntimeError(
            "Image OCR failed. Check that Tesseract OCR "
            "is installed and the image is readable. "
            + str(error)
        )


# --------------------------------------------------
# PDF EXTRACTION
# --------------------------------------------------

def extract_text_from_pdf(uploaded_file):
    """
    Extract text from a PDF.

    If the PDF contains scanned pages without selectable
    text, OCR is attempted on those pages.
    """

    document = None

    try:
        import pymupdf

        file_bytes = uploaded_file.getvalue()

        if not file_bytes:
            show_error("The uploaded PDF is empty.")
            return ""

        if not file_bytes.startswith(b"%PDF"):
            show_error("The uploaded file is not a valid PDF.")
            return ""

        document = pymupdf.open(
            stream=file_bytes,
            filetype="pdf"
        )

        extracted_pages = []

        for page_number, page in enumerate(
            document,
            start=1
        ):

            page_text = page.get_text("text").strip()

            # Use OCR if the PDF page is scanned.
            if not page_text:

                try:
                    pixmap = page.get_pixmap(
                        matrix=pymupdf.Matrix(2, 2),
                        alpha=False
                    )

                    image_bytes = pixmap.tobytes("png")

                    from PIL import Image

                    image = Image.open(
                        BytesIO(image_bytes)
                    )

                    page_text = _ocr_image(image)

                except Exception as ocr_error:
                    page_text = (
                        "[OCR could not read this page: "
                        + str(ocr_error)
                        + "]"
                    )

            if page_text:
                extracted_pages.append(
                    f"PAGE {page_number}\n{page_text}"
                )

        document.close()
        document = None

        result = "\n\n".join(extracted_pages).strip()

        if not result:
            show_warning(
                "No readable text was found in this PDF. "
                "Please upload a clearer report."
            )

        return result

    except ImportError:
        show_error(
            "PyMuPDF is not installed. "
            "Add pymupdf to requirements.txt."
        )
        return ""

    except Exception as error:
        show_error(
            "Unable to extract the PDF report: "
            + str(error)
        )
        return ""

    finally:
        if document is not None:
            try:
                document.close()
            except Exception:
                pass


# --------------------------------------------------
# IMAGE EXTRACTION
# --------------------------------------------------

def extract_text_from_image(uploaded_file):
    """
    Extract text from PNG, JPG or JPEG medical reports.
    """

    try:
        from PIL import Image, ImageOps

        image_bytes = uploaded_file.getvalue()

        if not image_bytes:
            show_error("The uploaded image is empty.")
            return ""

        image = Image.open(
            BytesIO(image_bytes)
        )

        image = ImageOps.exif_transpose(image)
        image = image.convert("RGB")

        extracted_text = _ocr_image(image)

        if not extracted_text:
            show_warning(
                "No readable text was found. "
                "Please upload a clearer image."
            )

        return extracted_text

    except ImportError:
        show_error(
            "Pillow is not installed. "
            "Add Pillow to requirements.txt."
        )
        return ""

    except Exception as error:
        show_error(
            "Unable to extract text from the image: "
            + str(error)
        )
        return ""


# --------------------------------------------------
# AUTOMATIC FILE DETECTION
# --------------------------------------------------

def extract_report_text(uploaded_file):
    """
    Automatically detect the file type and extract text.
    """

    if uploaded_file is None:
        show_warning("Please upload a medical report.")
        return ""

    file_name = getattr(
        uploaded_file,
        "name",
        ""
    ).lower()

    if file_name.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)

    if file_name.endswith(
        (".png", ".jpg", ".jpeg")
    ):
        return extract_text_from_image(uploaded_file)

    show_warning(
        "Unsupported file format. "
        "Upload a PDF, PNG, JPG or JPEG file."
    )

    return ""
