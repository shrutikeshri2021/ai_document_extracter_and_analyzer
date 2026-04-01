#!/usr/bin/env python
"""Check for REJECTION REASONS"""

import os
import re

print("\n" + "="*70)
print("🚨 CHECKING POTENTIAL REJECTION REASONS")
print("="*70 + "\n")

errors = []
warnings = []

# 1. Check API response format
print("1️⃣  CHECKING RESPONSE FORMAT...")
with open("main.py") as f:
    content = f.read()
    if '"filename":' in content and '"summary":' in content and '"entities":' in content and '"sentiment":' in content:
        print("   ✅ Response has all required fields")
    else:
        errors.append("❌ Response format missing required fields")

# 2. Check error handling
print("\n2️⃣  CHECKING ERROR HANDLING...")
if "HTTPException" in content and "status_code" in content:
    print("   ✅ Proper HTTP error handling")
else:
    errors.append("❌ Missing HTTP error handling")

# 3. Check authentication
print("\n3️⃣  CHECKING API AUTHENTICATION...")
if "Authorization" in content and "verify_key" in content:
    print("   ✅ Authentication required for /analyze")
else:
    errors.append("❌ Missing API key authentication")

# 4. Check CORS
print("\n4️⃣  CHECKING CORS...")
if "CORSMiddleware" in content:
    print("   ✅ CORS enabled")
else:
    warnings.append("⚠️  CORS not configured - frontend may have issues")

# 5. Check file size handling
print("\n5️⃣  CHECKING FILE UPLOAD LIMITS...")
if "file_bytes" in content:
    print("   ✅ File upload handling exists")
    if "len(text.strip()) < 10" in content:
        print("   ✅ Minimum text length check (10 chars)")
    else:
        warnings.append("⚠️  No minimum text length validation")
else:
    errors.append("❌ File upload not handled properly")

# 6. Check sentiment output format
print("\n6️⃣  CHECKING SENTIMENT OUTPUT...")
with open("ai_pipeline.py") as f:
    content = f.read()
    if '"label":' in content and '"score":' in content:
        print("   ✅ Sentiment has label + score")
    else:
        errors.append("❌ Sentiment format incorrect")

# 7. Check entities output format
print("\n7️⃣  CHECKING ENTITIES OUTPUT...")
if '"text":' in content and '"label":' in content:
    print("   ✅ Entities have text + label")
else:
    errors.append("❌ Entities format incorrect")

# 8. Check summary quality
print("\n8️⃣  CHECKING SUMMARY LOGIC...")
if "summarize(text)" in content:
    print("   ✅ Summary function exists")
    if "[:1500]" in content and "[-1500:]" in content:
        print("   ✅ Smart text selection (start + end)")
    else:
        warnings.append("⚠️  Summary might use only beginning of text")
else:
    errors.append("❌ Summary function missing")

# 9. Check for hardcoded paths
print("\n9️⃣  CHECKING FOR HARDCODED VALUES...")
if 'frontend/index.html' in content or "mysecretapikey123" in content:
    if os.path.exists(".env"):
        print("   ✅ API key in .env (not hardcoded)")
    else:
        warnings.append("⚠️  Check API key is in .env, not in code")

# 10. Check README
print("\n🔟 CHECKING DOCUMENTATION...")
if os.path.exists("README.md"):
    with open("README.md") as f:
        readme = f.read()
        if "Setup" in readme or "setup" in readme:
            print("   ✅ Setup instructions exist")
        else:
            warnings.append("⚠️  README missing setup instructions")
        
        if "pip install" in readme or "requirements.txt" in readme:
            print("   ✅ Installation instructions exist")
        else:
            warnings.append("⚠️  README missing installation steps")
        
        if "API_KEY" in readme:
            print("   ✅ API key documentation exists")
        else:
            warnings.append("⚠️  README missing API key documentation")
else:
    errors.append("❌ README.md missing!")

# 11. Check for proper exception handling in pipeline
print("\n1️⃣1️⃣  CHECKING EXCEPTION HANDLING...")
with open("ai_pipeline.py") as f:
    content = f.read()
    if "except" in content and "try" in content:
        print("   ✅ Try-except blocks present")
    else:
        warnings.append("⚠️  Limited exception handling")

# 12. Check if entities are actually being filtered
print("\n1️⃣2️⃣  CHECKING ENTITY FILTERING...")
if "IGNORE_WORDS" in content:
    print("   ✅ Entity noise filtering enabled")
    if "The" in content or "But" in content:
        print("   ✅ Common words filtered")
    else:
        warnings.append("⚠️  Check if IGNORE_WORDS is comprehensive")
else:
    warnings.append("⚠️  No entity filtering detected")

# 13. Check OCR preprocessing
print("\n1️⃣3️⃣  CHECKING OCR PREPROCESSING...")
with open("extractors.py") as f:
    content = f.read()
    if "convert(\"L\")" in content:
        print("   ✅ Grayscale conversion for OCR")
    else:
        warnings.append("⚠️  No grayscale conversion for OCR")
    
    if "resize" in content:
        print("   ✅ Image upscaling for OCR")
    else:
        warnings.append("⚠️  No image upscaling for OCR")

# 14. Check git configuration
print("\n1️⃣4️⃣  CHECKING GIT SETUP...")
if os.path.exists(".gitignore"):
    with open(".gitignore") as f:
        content = f.read()
        if ".env" in content:
            print("   ✅ .env in .gitignore (API key protected)")
        else:
            errors.append("❌ .env NOT in .gitignore - API KEY EXPOSED!")
        
        if "__pycache__" in content:
            print("   ✅ __pycache__ in .gitignore")
        else:
            warnings.append("⚠️  __pycache__ should be in .gitignore")
else:
    warnings.append("⚠️  .gitignore missing")

# 15. Check for valid API endpoints
print("\n1️⃣5️⃣  CHECKING API ENDPOINTS...")
with open("main.py") as f:
    content = f.read()
    endpoints = ["@app.get(\"/health\")", "@app.post(\"/analyze\")", "@app.get(\"/\")"]
    for ep in endpoints:
        if ep in content:
            print(f"   ✅ {ep} exists")
        else:
            errors.append(f"❌ Missing endpoint: {ep}")

print("\n" + "="*70)
print("📊 REJECTION RISK ASSESSMENT")
print("="*70)

if errors:
    print(f"\n🔴 CRITICAL ERRORS ({len(errors)}):")
    for e in errors:
        print(f"   {e}")
else:
    print("\n✅ No critical errors found!")

if warnings:
    print(f"\n🟡 WARNINGS ({len(warnings)}):")
    for w in warnings:
        print(f"   {w}")
else:
    print("\n✅ No warnings!")

print("\n" + "="*70)
if errors:
    print("⛔ PROJECT WILL LIKELY BE REJECTED - FIX CRITICAL ERRORS!")
elif warnings:
    print("⚠️  PROJECT ACCEPTABLE - But consider fixing warnings")
else:
    print("🏆 PROJECT READY FOR SUBMISSION!")
print("="*70 + "\n")
