import os
from fastapi import FastAPI, File, UploadFile, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from extractors import extract_text
from ai_pipeline import run_pipeline

load_dotenv()
API_KEY = os.getenv("API_KEY", "mysecretapikey123")

app = FastAPI(title="DocAI - Document Analysis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def verify_key(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    # Accept both "Bearer KEY" and just "KEY"
    key = authorization.replace("Bearer ", "").strip()
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")

@app.get("/")
def root():
    return FileResponse("frontend/index.html")

@app.get("/health")
def health():
    return {"status": "ok", "message": "DocAI is running"}

@app.post("/analyze")
async def analyze_document(
    file: UploadFile = File(...),
    authorization: str = Header(None)
):
    import traceback
    try:
        verify_key(authorization)
        file_bytes = await file.read()
        filename = file.filename or "document"

        if not filename:
            raise HTTPException(status_code=400, detail="No filename provided")

        try:
            text = extract_text(file_bytes, filename)
        except Exception as e:
            print(f"[ERROR] Extraction: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Text extraction failed: {str(e)}")

        if not text or len(text.strip()) < 10:
            raise HTTPException(status_code=422, detail="Could not extract readable text")

        try:
            # Pass filename so stats work correctly
            result = run_pipeline(text, filename)
        except Exception as e:
            print(f"[ERROR] Pipeline: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"AI pipeline failed: {str(e)}")

        return {
            "filename": filename,
            "extracted_text_length": len(text),
            "extracted_text_preview": text[:500],        # NEW: preview of extracted text
            "summary": result["summary"],
            "entities": result["entities"],
            "sentiment": result["sentiment"],
            "keywords": result["keywords"],              # NEW
            "document_stats": result["document_stats"],  # NEW
            "document_classification": result["document_classification"],  # NEW
            "language": result["language"]               # NEW
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Unexpected: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# NEW: Warmup endpoint (call this before judge testing)
@app.get("/warmup")
def warmup():
    try:
        sample = "Apple Inc was founded by Steve Jobs in California. The company had an amazing year."
        run_pipeline(sample, "warmup.txt")
        return {"status": "warmed up", "models": "ready"}
    except Exception as e:
        return {"status": "warmup failed", "error": str(e)}

# Serve frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")
