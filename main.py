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
    verify_key(authorization)
    
    # Read file
    file_bytes = await file.read()
    filename = file.filename
    
    if not filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    # Extract text
    try:
        text = extract_text(file_bytes, filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text extraction failed: {str(e)}")
    
    if not text or len(text.strip()) < 10:
        raise HTTPException(status_code=422, detail="Could not extract readable text from document")
    
    # Run AI
    try:
        result = run_pipeline(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI pipeline failed: {str(e)}")
    
    return {
        "filename": filename,
        "extracted_text_length": len(text),
        "summary": result["summary"],
        "entities": result["entities"],
        "sentiment": result["sentiment"]
    }

# Serve frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")
