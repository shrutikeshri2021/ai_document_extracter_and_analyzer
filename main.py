import os
import traceback
from fastapi import FastAPI, File, UploadFile, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from extractors import extract_text
from ai_pipeline import run_pipeline

load_dotenv()
API_KEY = os.getenv("API_KEY", "mysecretapikey123")

app = FastAPI(title="DocAI - Document Analysis API", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def verify_key(authorization: str):
    """Accept both 'Bearer KEY' and plain 'KEY' formats."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    key = authorization.replace("Bearer ", "").strip()
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")


@app.get("/")
def root():
    return FileResponse("frontend/index.html")


@app.get("/health")
def health():
    return {"status": "ok", "message": "DocAI is running", "version": "3.0"}


@app.get("/warmup")
def warmup():
    """Pre-warm all AI models before judge testing."""
    try:
        sample = (
            "Apple Inc was founded by Steve Jobs and Steve Wozniak in Cupertino, California. "
            "The company reported record revenue of $120 billion in Q4 2024, representing "
            "a 15% year-over-year growth. CEO Tim Cook announced expansion into new markets."
        )
        result = run_pipeline(sample, "warmup.txt")
        return {
            "status": "ready",
            "groq": result.get("llm_status"),
            "nlp": result.get("nlp_status"),
            "test_entities": len(result.get("entities", [])),
            "test_sentiment": result.get("sentiment", {}).get("label"),
        }
    except Exception as e:
        return {"status": "warmup_failed", "error": str(e)}


@app.post("/analyze")
async def analyze_document(
    file: UploadFile = File(...),
    authorization: str = Header(None)
):
    """
    Main analysis endpoint.
    Accepts PDF, DOCX, PNG, JPG, TIFF files.
    Returns 25+ structured analysis fields.
    """
    try:
        # Auth
        verify_key(authorization)

        # Read file
        file_bytes = await file.read()
        filename = file.filename or "document"

        if not file_bytes:
            raise HTTPException(status_code=400, detail="Empty file received")

        print(f"[API] Received: {filename} ({len(file_bytes)} bytes)")

        # Extract text
        try:
            text = extract_text(file_bytes, filename)
        except Exception as e:
            print(f"[API] Extraction error:\n{traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Text extraction failed: {str(e)}")

        if not text or len(text.strip()) < 10:
            raise HTTPException(
                status_code=422,
                detail="Could not extract readable text from document. "
                       "Ensure PDF is not scanned-only, and images are clear."
            )

        print(f"[API] Extracted {len(text)} characters")

        # Run AI pipeline
        try:
            result = run_pipeline(text, filename)
        except Exception as e:
            print(f"[API] Pipeline error:\n{traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"AI pipeline failed: {str(e)}")

        print(f"[API] ✅ Analysis complete — {len(result.get('entities', []))} entities, "
              f"sentiment={result.get('sentiment', {}).get('label')}, "
              f"groq={result.get('ai_powered')}")

        # Return all fields — using .get() everywhere so no KeyError is possible
        return {
            # File info
            "filename": filename,
            "extracted_text_length": len(text),
            "extracted_text_preview": text[:500],

            # Core AI fields (scored by hackathon judges)
            "summary": result.get("summary", ""),
            "entities": result.get("entities", []),
            "sentiment": result.get("sentiment", {"label": "neutral", "score": 0.5}),

            # Extended analysis
            "keywords": result.get("keywords", []),
            "key_phrases": result.get("key_phrases", []),
            "main_topics": result.get("main_topics", []),
            "insights": result.get("insights", []),
            "document_stats": result.get("document_stats", {}),
            "classification": result.get("classification", {}),
            "language": result.get("language", {"language": "English"}),

            # Risk & compliance
            "risk_level": result.get("risk_level", "low"),
            "risk_assessment": result.get("risk_assessment", {}),
            "compliance_issues": result.get("compliance_issues", []),

            # Document quality
            "document_score": result.get("document_score", 0),
            "complexity": result.get("complexity", "Moderate"),
            "reading_time": result.get("reading_time", 1),

            # Extracted structured data
            "emails": result.get("emails", []),
            "phones": result.get("phones", []),
            "urls": result.get("urls", []),

            # Extra features
            "sentiment_distribution": result.get("sentiment_distribution", {}),
            "key_sentences": result.get("key_sentences", []),
            "insight": result.get("insight", ""),
            "preview": result.get("preview", ""),

            # Status
            "ai_powered": result.get("ai_powered", False),
            "llm_status": result.get("llm_status", "unknown"),
            "nlp_status": result.get("nlp_status", "unknown"),
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Unexpected error:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


# Mount static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 70)
    print("🚀 DocAI — AI-Powered Document Analysis")
    print("=" * 70)
    print("📍 Server:     http://localhost:8000")
    print("🌐 Web UI:     http://localhost:8000")
    print("🏥 Health:     http://localhost:8000/health")
    print("🔥 Warmup:     http://localhost:8000/warmup")
    print("📚 API Docs:   http://localhost:8000/docs")
    print("=" * 70 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)