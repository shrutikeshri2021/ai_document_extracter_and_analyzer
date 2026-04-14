import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Tesseract configuration for Render (Linux)
# On Render, tesseract is usually in /usr/bin/tesseract
if os.name == 'nt':
    TESS_PATH = os.getenv("TESSERACT_PATH", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
else:
    TESS_PATH = "/usr/bin/tesseract"

# API Configuration
API_KEY = os.getenv("API_KEY", "mysecretapikey123")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Server Configuration
HOST = "0.0.0.0"
PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
