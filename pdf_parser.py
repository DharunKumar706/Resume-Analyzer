import fitz
from langdetect import detect, LangDetectException


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract text from a PDF byte stream using PyMuPDF."""
    if not pdf_bytes:
        raise ValueError("Empty PDF content")

    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    except Exception as exc:
        raise ValueError("Unable to parse PDF. The file may be corrupted or not a PDF.") from exc

    text_parts = []
    for page in doc:
        page_text = page.get_text("text")
        if page_text:
            text_parts.append(page_text)

    if not text_parts:
        raise ValueError("No readable text was found inside the PDF.")

    return "\n".join(text_parts).strip()


def is_english_text(text: str) -> bool:
    """Detect whether the provided text is English."""
    if not text or len(text.strip()) < 20:
        return False
    try:
        language = detect(text)
        return language.startswith("en")
    except LangDetectException:
        return False
