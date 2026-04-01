import fitz  # PyMuPDF for PDF
from docx import Document
from PIL import Image
import pytesseract
import io

def extract_from_pdf(file_bytes: bytes) -> str:
    text = ""
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text.strip()

def extract_from_docx(file_bytes: bytes) -> str:
    doc = Document(io.BytesIO(file_bytes))
    return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])

def extract_from_image(file_bytes: bytes) -> str:
    image = Image.open(io.BytesIO(file_bytes))
    return pytesseract.image_to_string(image).strip()

def extract_text(file_bytes: bytes, filename: str) -> str:
    ext = filename.lower().split(".")[-1]
    if ext == "pdf":
        return extract_from_pdf(file_bytes)
    elif ext in ["docx", "doc"]:
        return extract_from_docx(file_bytes)
    elif ext in ["png", "jpg", "jpeg", "tiff", "bmp", "webp"]:
        return extract_from_image(file_bytes)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
