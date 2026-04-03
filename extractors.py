import fitz
from docx import Document
from PIL import Image
import pytesseract
import io
import os
from dotenv import load_dotenv
load_dotenv()

# Fix Tesseract path for Windows
TESS_PATH = os.getenv("TESSERACT_PATH", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
if os.path.exists(TESS_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESS_PATH
else:
    # Try common locations
    for path in [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        r"C:\Users\Lenovo\AppData\Local\Tesseract-OCR\tesseract.exe",
    ]:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            break


def extract_from_pdf(file_bytes: bytes) -> str:
    text = ""
    try:
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text() + "\n"
    except Exception as e:
        raise ValueError(f"PDF extraction failed: {e}")
    return text.strip()


def extract_from_docx(file_bytes: bytes) -> str:
    try:
        doc = Document(io.BytesIO(file_bytes))
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)
    except Exception as e:
        raise ValueError(f"DOCX extraction failed: {e}")


def extract_from_image(file_bytes: bytes) -> str:
    try:
        image = Image.open(io.BytesIO(file_bytes))
        image = image.convert('L')
        image = image.resize((image.width * 2, image.height * 2), Image.Resampling.LANCZOS)
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        raise ValueError(f"Image OCR failed: {e}")


def extract_text(file_bytes: bytes, filename: str) -> str:
    ext = filename.lower().split(".")[-1]
    if ext == "pdf":
        return extract_from_pdf(file_bytes)
    elif ext in ["docx", "doc"]:
        return extract_from_docx(file_bytes)
    elif ext in ["png", "jpg", "jpeg", "tiff", "bmp", "webp"]:
        return extract_from_image(file_bytes)
    else:
        raise ValueError(f"Unsupported file type: .{ext}")
