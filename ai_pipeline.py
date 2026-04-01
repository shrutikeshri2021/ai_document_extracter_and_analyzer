import os, requests, re
from dotenv import load_dotenv

load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")
HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}


def hf_post(url: str, payload: dict):
    response = requests.post(url, headers=HEADERS, json=payload)

    if response.status_code != 200:
        print("[DEBUG ERROR]:", response.text)
        return None

    return response.json()


# 🔥 SUMMARY
def summarize(text: str) -> str:
    text = text[:3000]

    url = "https://api-inference.huggingface.co/models/sshleifer/distilbart-cnn-12-6"

    result = hf_post(url, {
        "inputs": text,
        "parameters": {"max_length": 120, "min_length": 30}
    })

    if result and isinstance(result, list) and "summary_text" in result[0]:
        return result[0]["summary_text"]

    # ✅ fallback
    return text[:300]


# 🔥 ENTITIES
def extract_entities(text: str) -> list:
    text = text[:512]

    url = "https://api-inference.huggingface.co/models/Jean-Baptiste/roberta-large-ner-english"

    result = hf_post(url, {"inputs": text})

    entities = []
    seen = set()

    if result and isinstance(result, list):
        for item in result:
            word = item.get("word", "").replace("##", "")
            label = item.get("entity_group", item.get("entity", ""))

            if word and label and word not in seen:
                seen.add(word)
                entities.append({"text": word, "label": label})

    # ✅ fallback
    if not entities:
        words = re.findall(r'\b[A-Z][a-z]+\b', text)
        entities = [{"text": w, "label": "MISC"} for w in set(words[:5])]

    return entities


# 🔥 SENTIMENT
def analyze_sentiment(text: str) -> dict:
    text = text[:512]

    url = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment"

    result = hf_post(url, {"inputs": text})

    if result and isinstance(result, list):
        scores = result[0] if isinstance(result[0], list) else result
        best = max(scores, key=lambda x: x.get("score", 0))

        label = best.get("label", "neutral").lower()
        score = round(best.get("score", 0.5), 4)

        return {"label": label, "score": score}

    # ✅ fallback
    text_lower = text.lower()
    if "hate" in text_lower:
        return {"label": "negative", "score": 0.7}
    elif "good" in text_lower:
        return {"label": "positive", "score": 0.7}

    return {"label": "neutral", "score": 0.5}


# 🔥 PIPELINE
def run_pipeline(text: str) -> dict:
    return {
        "summary": summarize(text),
        "entities": extract_entities(text),
        "sentiment": analyze_sentiment(text)
    }