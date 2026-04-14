# 📄 AI-Powered Document Analysis & Extraction
try here https://ai-document-extracter-and-analyzer.onrender.com/

> **Intelligent Document Processing System** — Extracts, analyzes, and summarizes content from PDF, DOCX, and image files using AI.(Working on it - solution may vary)

Built for **GUVI Hackathon 2026 — Intern Hiring Challenge**

---

## 🎯 Overview

An enterprise-grade document intelligence API that automatically processes documents through a **4-layer AI pipeline** to extract meaningful insights — summaries, entities, sentiment, keywords, and 25+ structured data fields.


---

## 🏗️ Architecture

```
                    ┌─────────────────┐
                    │   Client/UI     │
                    │  (index.html)   │
                    └────────┬────────┘
                             │ POST /analyze
                    ┌────────▼────────┐
                    │    FastAPI       │
                    │   (main.py)     │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Text Extraction │
                    │ (extractors.py) │
                    │ PDF│DOCX│Image  │
                    └────────┬────────┘
                             │
              ┌──────────────▼──────────────┐
              │      AI Pipeline            │
              │    (ai_pipeline.py)         │
              │                             │
              │  Layer 0: Groq LLM ────────►│ Best quality
              │  Layer 1: spaCy NLP ───────►│ Fallback
              │  Layer 2: YAKE + textstat ─►│ Keywords/stats
              │  Layer 3: Regex patterns ──►│ Always runs
              └─────────────────────────────┘
```

### 4-Layer Cascading Pipeline

| Layer | Engine | Purpose | Reliability |
|-------|--------|---------|-------------|
| **Layer 0** | Groq Llama 3.3 70B | Summary, entities, sentiment, insights | Primary AI |
| **Layer 1** | spaCy NER | Named entity recognition fallback | High |
| **Layer 2** | YAKE + textstat | Keyword extraction + readability | High |
| **Layer 3** | Regex patterns | Emails, phones, URLs, dates, money | Always works |

If Groq fails → spaCy takes over → If spaCy fails → Regex still works. **Zero single points of failure.**

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Python 3.10+, FastAPI, Uvicorn |
| **AI/LLM** | Groq API (Llama 3.3 70B Versatile) |
| **NLP** | spaCy (en_core_web_sm), YAKE, textstat, langdetect |
| **PDF Processing** | PyMuPDF (fitz) |
| **DOCX Processing** | python-docx |
| **OCR** | Tesseract via pytesseract |
| **Frontend** | Vanilla HTML/CSS/JavaScript |
| **Authentication** | Bearer token via API key |

---

## 📂 Project Structure

```
├── main.py              # FastAPI server, /analyze endpoint
├── ai_pipeline.py       # Master pipeline orchestrator (4 layers)
├── llm_engine.py        # Groq Llama 3.3 70B integration
├── nlp_engine.py        # spaCy NER, YAKE keywords, sentiment, stats
├── extractors.py        # PDF/DOCX/Image text extraction
├── frontend/
│   └── index.html       # Web UI dashboard
├── requirements.txt     # Python dependencies
├── .env                 # API keys (not committed)
└── README.md
```

---

## 🚀 Setup Instructions

### Prerequisites

- Python 3.10 or higher
- Tesseract OCR installed ([Download](https://github.com/tesseract-ocr/tesseract))
- Groq API key (free at [console.groq.com](https://console.groq.com))

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/shrutikeshri2021/ai_document_extracter_and_analyzer.git
cd ai_document_extracter_and_analyzer

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download spaCy model
python -m spacy download en_core_web_sm

# 5. Configure environment
# Create a .env file with:
GROQ_API_KEY=gsk_your_key_here
API_KEY=mysecretapikey123
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe

# 6. Start the server
python -m uvicorn main:app --reload --port 8000
```

### Verify Installation

```bash
# Health check
curl http://localhost:8000/health

# Warmup (loads all AI models)
curl http://localhost:8000/warmup
```

---

## 📡 API Reference

### `POST /analyze`

Analyzes a document and returns structured AI-generated insights.

**Headers:**
```
Authorization: Bearer mysecretapikey123
Content-Type: multipart/form-data
```

**Request:**
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Authorization: Bearer mysecretapikey123" \
  -F "file=@document.pdf"
```

**Response (JSON):**
```json
{
  "filename": "document.pdf",
  "summary": "AI-generated summary of the document...",
  "entities": [
    {"text": "John Smith", "label": "PERSON"},
    {"text": "Google", "label": "ORG"},
    {"text": "New York", "label": "LOCATION"},
    {"text": "$5 million", "label": "MONEY"}
  ],
  "sentiment": {
    "label": "positive",
    "score": 0.85,
    "explanation": "Document contains 8 positive indicators vs 2 negative"
  },
  "keywords": [
    {"word": "revenue", "score": 0.95},
    {"word": "growth", "score": 0.88}
  ],
  "key_phrases": ["record-breaking revenue", "market expansion"],
  "main_topics": ["Financial Performance", "Strategic Growth"],
  "insights": ["Revenue grew 23% year-over-year..."],
  "classification": {
    "category": "Financial",
    "document_type": "Report",
    "confidence": 0.87
  },
  "language": {"language": "English", "confidence": 0.92},
  "risk_assessment": {"level": "low", "reasons": []},
  "document_score": 92,
  "document_stats": {
    "word_count": 320,
    "sentence_count": 18,
    "reading_time_minutes": 2,
    "complexity": "Moderate"
  },
  "ai_powered": true
}
```

### `GET /health`
Returns server status.

### `GET /warmup`
Pre-loads AI models for faster first analysis.

### Supported File Types

| Format | Extension | Method |
|--------|-----------|--------|
| PDF | `.pdf` | PyMuPDF text extraction |
| Word | `.docx`, `.doc` | python-docx parsing |
| Images | `.png`, `.jpg`, `.jpeg`, `.tiff`, `.bmp`, `.webp` | Tesseract OCR |

---

## ✨ Features

### Core Analysis (Scored)
- **AI Summary** — 2-4 sentence contextual summary via Llama 3.3 70B
- **Entity Extraction** — People, organizations, locations, dates, money, percentages
- **Sentiment Analysis** — Positive/negative/neutral with confidence score and explanation

### Extended Analysis
- Keyword extraction (YAKE + frequency analysis)
- Key phrase identification
- Document classification (Financial, Legal, Medical, Tech, etc.)
- Language detection (12+ languages)
- Risk assessment (low/medium/high with reasons)
- Compliance issue detection
- Readability scoring (Flesch-Kincaid)
- Document quality score (0-100)
- Contact extraction (emails, phones, URLs)
- Reading time estimation

### Frontend Dashboard
- Modern dark-themed responsive UI
- Drag-and-drop file upload
- Real-time analysis visualization
- Color-coded entity tags
- Animated sentiment bar
- Keyword frequency charts
- Risk and compliance indicators

---

## 🧪 How Sentiment Analysis Works

The sentiment engine uses a **3-layer approach**:

1. **Word-boundary matching** — Regex `\bword\b` prevents false positives (e.g., "effective" inside "ineffectiveness")
2. **Negation detection** — "reduce effectiveness" correctly flips positive to negative
3. **Sentence-level weighting** — Counts positive vs negative sentences for overall tone
4. **Contrast word handling** — Words after "however", "but", "although", "nevertheless" get extra weight

This avoids common pitfalls like always returning "neutral" or misclassifying mixed-tone documents.

---

## 🔒 Authentication

All API requests require a Bearer token:

```
Authorization: Bearer mysecretapikey123
```

The API key is configured via the `API_KEY` environment variable.

---

## 📋 Known Limitations

- OCR accuracy depends on image quality and resolution
- Groq API has rate limits on free tier (30 requests/minute)
- spaCy `en_core_web_sm` is a small model — larger models would improve NER accuracy
- Very short documents (< 20 words) may produce limited analysis
- Scanned PDFs without embedded text require OCR fallback

---

## 🤖 AI Tools Used

| Tool | Purpose |
|------|---------|
| **Groq API (Llama 3.3 70B)** | Primary AI engine for summarization, entity extraction, sentiment analysis, and insights generation |
| **spaCy (en_core_web_sm)** | Named Entity Recognition (NER) fallback and sentence tokenization |
| **YAKE** | Unsupervised keyword extraction |
| **textstat** | Readability scoring (Flesch-Kincaid) |
| **langdetect** | Language identification |
| **Tesseract OCR** | Optical Character Recognition for image-based documents |
| **Google Gemini (Antigravity)** | Used for code development assistance, debugging, and documentation |

---

## 👩‍💻 Author

**Shruti Keshri**  
GUVI Hackathon 2026 — AI-Powered Document Analysis & Extraction Track

---

## 📄 License

This project was built for the GUVI Hackathon 2026 Intern Hiring Challenge.
