"""
AI Pipeline — Master orchestrator
LAYER 0: Groq Llama 3 70B (best quality, all 15 fields)
LAYER 1: spaCy + YAKE + textstat (NLP fallback)
LAYER 2: Regex patterns (always supplements)
"""

import re
import time
from dotenv import load_dotenv
load_dotenv()

from llm_engine import analyze_with_llm
from nlp_engine import process_text, clean_text


def run_pipeline(text: str, filename: str = "document") -> dict:
    """
    Master pipeline. Returns all fields required by main.py.
    Groq is tried first. If it fails or returns incomplete data,
    NLP layer fills in the gaps. Regex always supplements.
    """
    start = time.time()

    # ── Clean text first ─────────────────────────────
    text = clean_text(text)
    if not text or len(text) < 10:
        return _empty_result("Text too short after cleaning")

    # ── LAYER 0: Groq LLM ────────────────────────────
    llm = {}
    try:
        llm = analyze_with_llm(text)
    except Exception as e:
        print(f"[PIPELINE] LLM error: {e}")

    groq_ok = bool(llm and llm.get("summary"))
    print(f"[PIPELINE] Groq: {'✅ success' if groq_ok else '⚠️ fallback to NLP'}")

    # ── LAYER 1: NLP ─────────────────────────────────
    nlp = {}
    try:
        nlp = process_text(text, filename)
    except Exception as e:
        print(f"[PIPELINE] NLP error: {e}")

    nlp_ok = nlp.get("status") == "success"

    # ── MERGE: Groq wins, NLP fills gaps ─────────────
    duration = round(time.time() - start, 2)

    # Summary: Groq first
    summary = (llm.get("summary") or nlp.get("summary") or _fallback_summary(text))

    # Entities: Merge all sources
    seen = set()
    all_entities = []
    for e in (llm.get("entities") or []) + (nlp.get("entities") or []):
        k = e.get("text", "").lower().strip()
        if k and k not in seen and len(k) > 1:
            seen.add(k)
            all_entities.append(e)

    # Sentiment: Groq preferred (more context-aware)
    if llm.get("sentiment") in ("positive", "negative", "neutral"):
        sentiment = {
            "label": llm["sentiment"],
            "score": float(llm.get("sentiment_score", 0.75)),
            "explanation": llm.get("sentiment_explanation", "")
        }
    else:
        sentiment = nlp.get("sentiment") or {
            "label": "neutral", "score": 0.6, "explanation": "Could not determine sentiment"
        }

    # Keywords: Groq gives strings, NLP gives dicts — normalize both
    raw_kw = llm.get("keywords") or []
    nlp_kw = nlp.get("keywords") or []
    keywords = []
    seen_kw = set()
    for kw in raw_kw:
        word = kw if isinstance(kw, str) else kw.get("word", "")
        if word and word.lower() not in seen_kw:
            seen_kw.add(word.lower())
            keywords.append({"word": word, "score": round(0.9 - len(keywords) * 0.05, 2)})
    for kw in nlp_kw:
        word = kw.get("word", "") if isinstance(kw, dict) else kw
        if word and word.lower() not in seen_kw:
            seen_kw.add(word.lower())
            keywords.append(kw if isinstance(kw, dict) else {"word": word, "score": 0.5})
    keywords = keywords[:10]

    # Classification
    cls_nlp = nlp.get("document_classification") or {}
    doc_type = llm.get("document_type") or cls_nlp.get("category") or "General"
    classification = {
        "category": cls_nlp.get("category") or doc_type,
        "document_type": doc_type,
        "confidence": cls_nlp.get("confidence") or 0.75
    }

    # Language
    lang_nlp = nlp.get("language") or {}
    lang_llm = llm.get("language") or ""
    if lang_llm:
        language = {"language": lang_llm, "code": "en", "confidence": 0.9}
    else:
        language = lang_nlp if lang_nlp else {"language": "English", "code": "en", "confidence": 0.7}

    # Stats
    stats = nlp.get("document_stats") or {}
    stats["processing_time_seconds"] = duration

    # Risk
    risk = nlp.get("risk_assessment") or {"level": "low", "reasons": [], "score": 0}
    risk_level = risk.get("level", "low")

    # Insights: Groq wins (more intelligent), NLP as backup
    insights = llm.get("insights") or nlp.get("insights") or []

    # Key phrases + topics (Groq only)
    key_phrases = llm.get("key_phrases") or []
    main_topics = llm.get("main_topics") or []
    compliance_issues = llm.get("compliance_issues") or []
    risk_reasons = llm.get("risk_reasons") or risk.get("reasons") or []

    # Regex extras (emails, phones, URLs)
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    phones = re.findall(r'\b(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b', text)
    urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', text)

    # Document score
    doc_score = nlp.get("document_score") or 70

    # Sentiment distribution estimate
    sentiment_distribution = {
        "positive": round(sentiment["score"] if sentiment["label"] == "positive" else 1 - sentiment["score"], 2),
        "negative": round(sentiment["score"] if sentiment["label"] == "negative" else 0.1, 2),
        "neutral": round(0.3 if sentiment["label"] == "neutral" else 0.1, 2)
    }

    # Key sentences
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    key_sentences = [s.strip() for s in sentences if len(s.strip()) > 40][:5]

    # Readability
    complexity = stats.get("complexity") or "Moderate"
    reading_time = stats.get("reading_time_minutes") or 1

    return {
        # Core fields (hackathon scoring)
        "summary": summary,
        "entities": all_entities[:25],
        "sentiment": sentiment,

        # Extended features
        "keywords": keywords,
        "key_phrases": key_phrases,
        "main_topics": main_topics,
        "insights": insights,
        "document_stats": stats,
        "classification": classification,
        "language": language,
        "risk_level": risk_level,
        "risk_assessment": {
            "level": risk_level,
            "reasons": risk_reasons or risk.get("reasons", []),
            "score": risk.get("score", 0)
        },
        "document_score": doc_score,
        "compliance_issues": compliance_issues,

        # Convenience fields
        "emails": emails[:5],
        "phones": phones[:5],
        "urls": urls[:5],
        "sentiment_distribution": sentiment_distribution,
        "key_sentences": key_sentences,
        "complexity": complexity,
        "reading_time": reading_time,
        "preview": text[:500],
        "insight": insights[0] if insights else "Analysis complete.",

        # Status
        "ai_powered": groq_ok,
        "llm_status": "groq_llama3" if groq_ok else "nlp_fallback",
        "nlp_status": "spacy_active" if nlp_ok else "regex_only",
    }


def _fallback_summary(text: str) -> str:
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    return " ".join(sentences[:3]) if sentences else text[:300]


def _empty_result(reason: str) -> dict:
    return {
        "summary": reason, "entities": [], "sentiment": {"label": "neutral", "score": 0.5},
        "keywords": [], "key_phrases": [], "main_topics": [], "insights": [],
        "document_stats": {}, "classification": {"category": "General", "confidence": 0.5},
        "language": {"language": "English"}, "risk_level": "low",
        "risk_assessment": {"level": "low", "reasons": []},
        "document_score": 0, "compliance_issues": [], "emails": [], "phones": [],
        "urls": [], "sentiment_distribution": {}, "key_sentences": [],
        "complexity": "Unknown", "reading_time": 1, "preview": "",
        "insight": reason, "ai_powered": False,
        "llm_status": "error", "nlp_status": "error"
    }