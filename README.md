# DocAI — AI-Powered Document Analysis & Extraction

## Live URL
https://your-app.onrender.com

## API Key
mysecretapikey123

## Setup Instructions
1. Clone the repo
2. Run `pip install -r requirements.txt`
3. Install Tesseract: `sudo apt-get install tesseract-ocr` (Linux/Render) or download from https://github.com/UB-Mannheim/tesseract/wiki (Windows)
4. Create `.env` with your `HF_API_KEY` and `API_KEY`
5. Run: `uvicorn main:app --reload`

## Architecture
- **FastAPI** backend with async file handling
- **PyMuPDF** for PDF text extraction
- **python-docx** for DOCX parsing
- **Tesseract OCR** via pytesseract for images
- **HuggingFace Inference API** for AI models:
  - Summarization: `facebook/bart-large-cnn`
  - NER: `dslim/bert-base-NER`
  - Sentiment: `distilbert-base-uncased-finetuned-sst-2-english`

## API Usage
```
POST /analyze
Header: Authorization: <api_key>
Body: multipart/form-data with `file` field
```

### Response Format
```json
{
  "filename": "document.pdf",
  "extracted_text_length": 1234,
  "summary": "AI-generated summary of the document...",
  "entities": [
    {"text": "Apple", "label": "ORG"},
    {"text": "Steve Jobs", "label": "PER"},
    {"text": "California", "label": "LOC"}
  ],
  "sentiment": {
    "label": "positive",
    "score": 0.95
  }
}
```

## File Support
- PDF (.pdf)
- Word Documents (.docx, .doc)
- Images (.png, .jpg, .jpeg, .tiff, .bmp, .webp)

## AI Tools Used
- Claude (Anthropic) — code architecture guidance
- GitHub Copilot — code completion assistance
- HuggingFace — inference APIs for NLP models

## Deployment on Render

1. Push your project to GitHub (add `.env` to `.gitignore`)
2. Go to https://render.com → Sign up with GitHub
3. Click New → Web Service → Connect your repo
4. Set these settings:
   - **Build Command**: `pip install -r requirements.txt && apt-get install -y tesseract-ocr`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables**: 
     - `HF_API_KEY` = your HuggingFace token
     - `API_KEY` = your secret API key

5. Click Deploy — your live URL will be `https://your-app.onrender.com`

## Testing Locally
```bash
# Start the server
uvicorn main:app --reload

# Test health endpoint
curl http://localhost:8000/health

# Test document analysis
curl -X POST http://localhost:8000/analyze \
  -H "Authorization: mysecretapikey123" \
  -F "file=@test.pdf"
```

## Key Features
✅ Drag-and-drop file upload  
✅ Automatic text extraction from PDFs, DOCX, and images  
✅ AI-powered summarization  
✅ Named Entity Recognition (NER)  
✅ Sentiment analysis  
✅ Beautiful, responsive dark-mode UI  
✅ Fast async processing  
✅ API authentication with custom API keys  

## Troubleshooting

**HuggingFace API timeouts**: Add a `/warmup` endpoint that pre-loads models on startup.

**Missing Tesseract**: Install it before running the app. The app will fail on image uploads without it.

**API Key errors**: Make sure your `.env` file has the correct `HF_API_KEY` from HuggingFace.

**CORS issues**: Already configured to accept requests from all origins.
