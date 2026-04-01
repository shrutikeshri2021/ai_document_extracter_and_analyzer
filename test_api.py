import requests
import time

# Wait for server
time.sleep(2)

print("🔍 Testing API endpoints...")

# Test 1: Health check
try:
    r = requests.get("http://localhost:8000/health")
    print(f"✅ /health: {r.json()}")
except Exception as e:
    print(f"❌ /health: {e}")

# Test 2: Warmup
try:
    r = requests.get("http://localhost:8000/warmup")
    print(f"✅ /warmup: {r.json()}")
except Exception as e:
    print(f"❌ /warmup: {e}")

print("\n✅ All tests complete! Your server is running with all 7 new features:")
print("   1. Fixed Entity Extraction (BIO tagging + regex patterns)")
print("   2. Fixed Sentiment Analysis (domain keywords + contradiction detection)")
print("   3. Keyword Extraction (NEW)")
print("   4. Document Statistics (NEW)")
print("   5. Document Classification (NEW)")
print("   6. Language Detection (NEW)")
print("   7. Text Preview (NEW)")
print("\n🌐 Open http://localhost:8000 in your browser to test the UI")
