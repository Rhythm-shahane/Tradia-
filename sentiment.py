from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

# Load FinBERT
tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
finbert = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

# Analyze list of headlines
def analyze_sentiment(headlines):
    return finbert(headlines)

# Compute an average sentiment score
def sentiment_score(results):
    score_map = {"POSITIVE": 1, "NEUTRAL": 0, "NEGATIVE": -1}
    total = 0
    count = 0
    for r in results:
        label = r["label"].upper()
        if label in score_map:
            total += score_map[label] * r["score"]
            count += 1
    return total / count if count > 0 else 0
