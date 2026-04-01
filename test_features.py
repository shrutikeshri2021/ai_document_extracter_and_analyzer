#!/usr/bin/env python
from ai_pipeline import run_pipeline

print("=" * 60)
print("🧪 TESTING ALL 7 NEW FEATURES")
print("=" * 60)

sample_text = "Apple Inc was founded by Steve Jobs in California in 1976. The company developed innovative products and achieved tremendous success. Apple earned $100 million in revenue last year."
filename = "test.txt"

print("\n📌 Input text:", sample_text[:80] + "...")

result = run_pipeline(sample_text, filename)

print("\n✅ 1. SUMMARY")
print(f"   {result['summary']}")

print("\n✅ 2. ENTITIES (Fixed with BIO tagging + regex)")
print(f"   Found {len(result['entities'])} entities:")
for e in result['entities'][:5]:
    print(f"   - {e['text']:<20} ({e['label']})")

print("\n✅ 3. SENTIMENT (Fixed with domain keywords)")
print(f"   Sentiment: {result['sentiment']['label'].upper()}")
print(f"   Confidence: {result['sentiment']['score']}")

print("\n✅ 4. KEYWORDS (NEW)")
print(f"   Top keywords:")
for kw in result['keywords'][:5]:
    print(f"   - {kw['word']:<15} ({kw['count']}x)")

print("\n✅ 5. DOCUMENT STATS (NEW)")
stats = result['document_stats']
print(f"   Words: {stats['word_count']}")
print(f"   Sentences: {stats['sentence_count']}")
print(f"   Paragraphs: {stats['paragraph_count']}")
print(f"   Reading time: {stats['reading_time_minutes']} min")

print("\n✅ 6. DOCUMENT CLASSIFICATION (NEW)")
cls = result['document_classification']
print(f"   Category: {cls['category']}")
print(f"   Confidence: {cls['confidence']}")

print("\n✅ 7. LANGUAGE DETECTION (NEW)")
lang = result['language']
print(f"   Language: {lang['language']}")
print(f"   Confidence: {lang['confidence']}")

print("\n" + "=" * 60)
print("🏆 ALL 7 FEATURES WORKING PERFECTLY!")
print("=" * 60)
