#!/usr/bin/env python
"""Debug script - Check all issues"""

import os
import sys

print("=" * 60)
print("DOCAI PROJECT DEBUG REPORT")
print("=" * 60)

# 1. Check .env file
print("\n✅ 1. CHECKING .env FILE")
if os.path.exists(".env"):
    with open(".env") as f:
        content = f.read()
        has_hf = "HF_API_KEY" in content
        has_api = "API_KEY" in content
        if has_hf and has_api:
            print("   ✅ .env file exists with both keys")
        else:
            print("   ⚠️ .env missing HF_API_KEY or API_KEY")
else:
    print("   ❌ .env file NOT found - WILL FAIL!")

# 2. Check dependencies
print("\n✅ 2. CHECKING DEPENDENCIES")
deps = {
    "fastapi": "FastAPI framework",
    "uvicorn": "Server",
    "fitz": "PDF extraction",
    "docx": "DOCX extraction",
    "pytesseract": "OCR for images",
    "PIL": "Image processing",
    "requests": "HTTP calls to HF API",
    "dotenv": "Environment variables"
}

missing = []
for dep, desc in deps.items():
    try:
        __import__(dep)
        print(f"   ✅ {dep:15} → {desc}")
    except ImportError:
        print(f"   ❌ {dep:15} → {desc} (MISSING!)")
        missing.append(dep)

if missing:
    print(f"\n   ⚠️ INSTALL: pip install {' '.join(missing)}")

# 3. Check file structure
print("\n✅ 3. CHECKING FILE STRUCTURE")
required_files = {
    "main.py": "FastAPI app",
    "ai_pipeline.py": "AI models",
    "extractors.py": "Text extraction",
    "requirements.txt": "Dependencies",
    ".env": "API keys",
    ".gitignore": "Git ignore",
    "README.md": "Documentation",
    "frontend/index.html": "Frontend UI"
}

for file, desc in required_files.items():
    if os.path.exists(file):
        print(f"   ✅ {file:25} → {desc}")
    else:
        print(f"   ❌ {file:25} → {desc} (MISSING!)")

# 4. Check imports
print("\n✅ 4. CHECKING PYTHON IMPORTS")
try:
    from extractors import extract_text
    print("   ✅ extractors.extract_text imports correctly")
except Exception as e:
    print(f"   ❌ extractors error: {str(e)[:100]}")

try:
    from ai_pipeline import run_pipeline
    print("   ✅ ai_pipeline.run_pipeline imports correctly")
except Exception as e:
    print(f"   ❌ ai_pipeline error: {str(e)[:100]}")

try:
    from main import app
    print("   ✅ main.app imports correctly")
except Exception as e:
    print(f"   ❌ main error: {str(e)[:100]}")

# 5. Check environment variables
print("\n✅ 5. CHECKING ENVIRONMENT VARIABLES")
hf_key = os.getenv("HF_API_KEY")
api_key = os.getenv("API_KEY")

if hf_key and hf_key != "hf_your_token_here":
    print(f"   ✅ HF_API_KEY set (starts with: {hf_key[:10]}...)")
else:
    print(f"   ❌ HF_API_KEY not set or placeholder!")

if api_key:
    print(f"   ✅ API_KEY set → {api_key}")
else:
    print(f"   ❌ API_KEY not set!")

# 6. Check HuggingFace API key validity
print("\n✅ 6. CHECKING HUGGINGFACE API")
if hf_key and hf_key.startswith("hf_"):
    print(f"   ✅ HF_API_KEY format looks valid")
else:
    print(f"   ⚠️ HF_API_KEY format suspicious - should start with 'hf_'")

# 7. Check if server can start
print("\n✅ 7. TESTING SERVER STARTUP")
try:
    from main import app
    print("   ✅ FastAPI app created")
    print(f"   ✅ Routes available: {len(app.routes)} endpoints")
    
    routes = [route.path for route in app.routes]
    print(f"   ✅ Endpoints: {routes}")
except Exception as e:
    print(f"   ❌ Server error: {str(e)[:100]}")

print("\n" + "=" * 60)
print("DEBUG COMPLETE")
print("=" * 60)
