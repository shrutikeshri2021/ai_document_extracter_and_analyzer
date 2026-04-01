import os, re, requests
from collections import Counter
from dotenv import load_dotenv

load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")
HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}

IGNORE_WORDS = {
    "the","a","an","and","or","but","in","on","at","to","for","of","with",
    "by","from","is","are","was","were","be","been","have","has","had",
    "do","does","did","will","would","could","should","may","might","must",
    "can","still","however","moreover","this","that","these","those","it",
    "its","not","no","so","if","as","up","we","he","she","they","our",
    "their","my","your","his","her","##","[CLS]","[SEP]","i","you","new"
}

def hf_post(url, payload, retries=3):
    for attempt in range(retries):
        try:
            r = requests.post(url, headers=HEADERS, json=payload, timeout=60)
            if r.status_code == 503:
                import time; time.sleep(10)
                continue
            r.raise_for_status()
            return r.json()
        except Exception as e:
            if attempt == retries - 1:
                raise e
    return None

# ─── 1. SUMMARIZATION ────────────────────────────────────────────────
def summarize(text: str) -> str:
    try:
        selected = text[:1500] + " " + text[-1500:] if len(text) > 3000 else text
        url = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
        result = hf_post(url, {
            "inputs": selected,
            "parameters": {"max_length": 150, "min_length": 50, "do_sample": False}
        })
        if isinstance(result, list) and result:
            return result[0].get("summary_text", "").strip()
    except:
        pass
    # Fallback: first 3 sentences
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return " ".join(sentences[:3]) if sentences else text[:300]

# ─── 2. ENTITY EXTRACTION (FIXED) ────────────────────────────────
def extract_entities(text: str) -> list:
    entities = []
    seen = set()

    # Method 1: HuggingFace BERT NER
    try:
        url = "https://api-inference.huggingface.co/models/dslim/bert-base-NER"
        result = hf_post(url, {"inputs": text[:1000]})
        if isinstance(result, list):
            current_entity = ""
            current_label = ""
            for item in result:
                word = item.get("word", "").replace("##", "").strip()
                label = item.get("entity", "")
                score = item.get("score", 0)
                
                # Only take high-confidence predictions
                if score < 0.7:
                    continue
                    
                # Handle B- and I- prefixes (BIO tagging)
                if label.startswith("B-"):
                    if current_entity and current_entity.lower() not in IGNORE_WORDS:
                        clean = current_entity.strip()
                        if clean not in seen and len(clean) > 1:
                            seen.add(clean)
                            entities.append({"text": clean, "label": current_label})
                    current_entity = word
                    current_label = label[2:]  # Remove B-
                elif label.startswith("I-") and current_entity:
                    current_entity += " " + word
                else:
                    if current_entity and current_entity.lower() not in IGNORE_WORDS:
                        clean = current_entity.strip()
                        if clean not in seen and len(clean) > 1:
                            seen.add(clean)
                            entities.append({"text": clean, "label": current_label})
                    current_entity = ""
                    current_label = ""
            
            # Don't forget the last entity
            if current_entity and current_entity.lower() not in IGNORE_WORDS:
                clean = current_entity.strip()
                if clean not in seen and len(clean) > 1:
                    seen.add(clean)
                    entities.append({"text": clean, "label": current_label})
    except:
        pass

    # Method 2: Regex fallback (always runs to catch what BERT misses)
    # Emails
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    for e in emails:
        if e not in seen:
            seen.add(e); entities.append({"text": e, "label": "EMAIL"})

    # Phone numbers
    phones = re.findall(r'\b(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b', text)
    for p in phones:
        if p not in seen:
            seen.add(p); entities.append({"text": p.strip(), "label": "PHONE"})

    # Dates
    dates = re.findall(r'\b(?:\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4})\b', text)
    for d in dates:
        if d not in seen:
            seen.add(d); entities.append({"text": d.strip(), "label": "DATE"})

    # Money
    money = re.findall(r'\$[\d,]+(?:\.\d{2})?|\b\d+(?:,\d{3})*(?:\.\d+)?\s*(?:million|billion|USD|EUR|INR)\b', text, re.IGNORECASE)
    for m in money:
        if m not in seen:
            seen.add(m); entities.append({"text": m.strip(), "label": "MONEY"})

    # Percentages
    percents = re.findall(r'\b\d+(?:\.\d+)?%', text)
    for p in percents:
        if p not in seen:
            seen.add(p); entities.append({"text": p, "label": "PERCENT"})

    # URLs
    urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', text)
    for u in urls[:3]:
        if u not in seen:
            seen.add(u); entities.append({"text": u, "label": "URL"})

    return entities[:20]  # Return up to 20 entities

# ─── 3. SENTIMENT ANALYSIS (FIXED) ───────────────────────────────────
def analyze_sentiment(text: str) -> dict:
    label = "neutral"
    score = 0.5

    try:
        url = "https://api-inference.huggingface.co/models/distilbert-base-uncased-finetuned-sst-2-english"
        result = hf_post(url, {"inputs": text[:512]})
        
        if isinstance(result, list) and len(result) > 0:
            # Handle nested list [[{...}]] or flat list [{...}]
            scores_list = result[0] if isinstance(result[0], list) else result
            
            if scores_list:
                best = max(scores_list, key=lambda x: x.get("score", 0))
                raw_label = best.get("label", "").upper()
                score = float(best.get("score", 0.5))
                
                if raw_label in ["POSITIVE", "LABEL_1"]:
                    label = "positive"
                elif raw_label in ["NEGATIVE", "LABEL_0"]:
                    label = "negative"
                else:
                    label = "neutral"
    except:
        pass

    # Keyword boost for domain accuracy
    text_lower = text.lower()
    neg_words = ["breach","attack","vulnerability","malware","hack","failure","loss",
                 "decline","risk","threat","crisis","problem","issue","error","fail",
                 "lawsuit","penalty","fine","layoff","bankrupt","deficit"]
    pos_words = ["growth","success","profit","award","innovation","breakthrough",
                 "improvement","excellent","outstanding","achievement","record","gain",
                 "expansion","positive","strong","leading","best","top","winner"]
    
    neg_count = sum(1 for w in neg_words if w in text_lower)
    pos_count = sum(1 for w in pos_words if w in text_lower)
    
    if neg_count > pos_count + 1:
        label = "negative"
        score = min(score + neg_count * 0.05, 0.97)
    elif pos_count > neg_count + 1:
        label = "positive"
        score = min(score + pos_count * 0.05, 0.97)

    return {"label": label, "score": round(score, 2)}

# ─── 4. KEYWORD EXTRACTION (NEW FEATURE) ─────────────────────────────
def extract_keywords(text: str) -> list:
    stop_words = IGNORE_WORDS | {
        "also","about","after","before","between","through","during","while",
        "than","more","most","very","just","only","even","both","each","few",
        "other","into","over","under","again","further","then","once","here",
        "there","when","where","why","how","all","any","both","each","more"
    }
    words = re.findall(r'\b[a-zA-Z][a-zA-Z]{2,}\b', text.lower())
    filtered = [w for w in words if w not in stop_words]
    freq = Counter(filtered)
    return [{"word": word, "count": count} for word, count in freq.most_common(10)]

# ─── 5. DOCUMENT STATISTICS (NEW FEATURE) ────────────────────────────
def get_document_stats(text: str, filename: str) -> dict:
    words = text.split()
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    word_count = len(words)
    reading_time = max(1, round(word_count / 200))  # 200 wpm average
    
    ext = filename.lower().split('.')[-1]
    doc_type_map = {
        "pdf": "PDF Document", "docx": "Word Document", "doc": "Word Document",
        "png": "Image (PNG)", "jpg": "Image (JPEG)", "jpeg": "Image (JPEG)",
        "tiff": "Image (TIFF)", "bmp": "Image (BMP)", "webp": "Image (WebP)"
    }
    
    return {
        "word_count": word_count,
        "sentence_count": len(sentences),
        "paragraph_count": len(paragraphs),
        "character_count": len(text),
        "reading_time_minutes": reading_time,
        "document_type": doc_type_map.get(ext, "Unknown"),
        "avg_words_per_sentence": round(word_count / max(len(sentences), 1), 1)
    }

# ─── 6. DOCUMENT CLASSIFICATION (NEW FEATURE) ────────────────────────
def classify_document(text: str) -> dict:
    text_lower = text.lower()
    
    categories = {
        "Legal": ["contract","agreement","clause","party","whereas","herein",
                  "jurisdiction","liability","indemnify","shall","attorney","court"],
        "Financial": ["revenue","profit","loss","balance","asset","liability",
                      "investment","dividend","fiscal","quarterly","annual report","ebitda"],
        "Medical": ["patient","diagnosis","treatment","medication","symptom","clinical",
                    "healthcare","physician","hospital","therapy","disease","prescription"],
        "Technology": ["software","algorithm","artificial intelligence","machine learning",
                       "cloud","api","database","cybersecurity","digital","innovation"],
        "Academic": ["research","methodology","hypothesis","conclusion","abstract",
                     "literature","study","analysis","experiment","findings","journal"],
        "News/Media": ["reported","according","journalist","article","press","statement",
                       "announced","spokesperson","media","coverage","published"],
        "HR/Employment": ["employee","salary","benefits","recruitment","performance",
                          "resignation","promotion","workplace","hire","onboarding"],
        "General": []
    }
    
    scores = {}
    for category, keywords in categories.items():
        if keywords:
            score = sum(1 for kw in keywords if kw in text_lower)
            scores[category] = score
    
    if not scores or max(scores.values()) == 0:
        return {"category": "General", "confidence": 0.5}
    
    best_category = max(scores, key=scores.get)
    total = sum(scores.values())
    confidence = round(scores[best_category] / total, 2) if total > 0 else 0.5
    
    return {"category": best_category, "confidence": min(confidence + 0.3, 0.99)}

# ─── 7. LANGUAGE DETECTION (NEW FEATURE) ─────────────────────────────
def detect_language(text: str) -> dict:
    sample = text[:200].lower()
    
    lang_patterns = {
        "Hindi": ["है","और","का","के","में","नहीं","यह","हैं"],
        "Spanish": ["el","la","los","las","que","con","por","para","una"],
        "French": ["le","la","les","des","que","dans","pour","avec","une"],
        "German": ["der","die","das","und","ist","mit","von","auf","ein"],
        "Arabic": ["في","من","على","إلى","هذا","التي","كان","أن"],
        "English": ["the","and","is","in","of","to","that","this","with"]
    }
    
    for lang, patterns in lang_patterns.items():
        if sum(1 for p in patterns if p in sample) >= 3:
            return {"language": lang, "confidence": 0.85}
    
    return {"language": "English", "confidence": 0.7}

# ─── 8. MAIN PIPELINE (RETURNS ALL FEATURES) ─────────────────────────
def run_pipeline(text: str, filename: str = "document") -> dict:
    return {
        "summary": summarize(text),
        "entities": extract_entities(text),
        "sentiment": analyze_sentiment(text),
        "keywords": extract_keywords(text),
        "document_stats": get_document_stats(text, filename),
        "document_classification": classify_document(text),
        "language": detect_language(text)
    }