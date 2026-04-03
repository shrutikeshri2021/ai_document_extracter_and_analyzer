import os
import json
import re
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

GROQ_KEY = os.getenv("GROQ_API_KEY", "")
client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None


def analyze_with_llm(text: str) -> dict:
    """
    Use Groq Llama 3 70B to produce ALL analysis fields in one call.
    Returns comprehensive structured JSON.
    """
    if not client:
        print("[LLM] No Groq API key found, skipping LLM layer")
        return {}

    sample = text[:4500]

    prompt = f"""You are an expert document analyst. Analyze the document below and return ONLY valid JSON with NO markdown, NO explanation, NO code blocks.

Return exactly this JSON structure:

{{
  "summary": "Write 2-4 clear sentences summarizing the main content and purpose of this document",
  "sentiment": "positive",
  "sentiment_score": 0.82,
  "sentiment_explanation": "One sentence explaining why the tone is positive/negative/neutral",
  "entities": [
    {{"text": "Entity Name", "label": "PERSON"}},
    {{"text": "Company Name", "label": "ORG"}},
    {{"text": "New York", "label": "LOCATION"}},
    {{"text": "January 2024", "label": "DATE"}},
    {{"text": "$5 million", "label": "MONEY"}}
  ],
  "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5", "keyword6", "keyword7", "keyword8", "keyword9", "keyword10"],
  "key_phrases": ["important phrase one", "key phrase two", "phrase three"],
  "document_type": "Report",
  "main_topics": ["topic1", "topic2", "topic3"],
  "insights": [
    "First meaningful insight about this document",
    "Second insight about key findings or patterns",
    "Third insight about implications or recommendations"
  ],
  "risk_level": "low",
  "risk_reasons": [],
  "compliance_issues": [],
  "language": "English"
}}

RULES:
- sentiment must be exactly one of: positive, negative, neutral
- sentiment_score must be 0.0 to 1.0
- risk_level must be exactly one of: low, medium, high
- document_type must be one of: Report, Contract, Article, Email, Invoice, Academic, News, Resume, Legal, Financial, Medical, Technical, General
- entities: extract ALL real people, organizations, locations, dates, money amounts mentioned
- keywords: extract 10 most important single words from the document
- insights: write 3 genuinely useful observations, NOT generic statements
- If no compliance issues found, return empty array []
- Return ONLY the JSON object, nothing before or after it

DOCUMENT TO ANALYZE:
{sample}"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1500
        )

        raw = response.choices[0].message.content.strip()

        # Strip markdown code blocks if model adds them
        raw = re.sub(r'^```json\s*', '', raw)
        raw = re.sub(r'^```\s*', '', raw)
        raw = re.sub(r'\s*```$', '', raw)
        raw = raw.strip()

        # Find JSON object boundaries
        start = raw.find('{')
        end = raw.rfind('}') + 1
        if start >= 0 and end > start:
            raw = raw[start:end]

        result = json.loads(raw)
        print(f"[LLM] ✅ Groq analysis successful — {len(result.get('entities', []))} entities, sentiment={result.get('sentiment')}")
        return result

    except json.JSONDecodeError as e:
        print(f"[LLM] JSON parse error: {e}")
        print(f"[LLM] Raw output (first 300 chars): {raw[:300]}")
        return {}
    except Exception as e:
        print(f"[LLM] Error: {e}")
        return {}
