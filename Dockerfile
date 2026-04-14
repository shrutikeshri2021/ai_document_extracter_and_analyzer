# Use Python 3.10-slim as requested
FROM python:3.10-slim

# Install system dependencies including Tesseract
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm

# Copy entire application
COPY . .

# Environment variables for Render's dynamic port
ENV PORT=10000
ENV HOST=0.0.0.0

# Start command using main.py which honors the PORT environment variable
CMD ["python", "main.py"]
