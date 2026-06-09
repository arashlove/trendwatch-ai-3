from typing import Literal, TypedDict

from classification import SentimentClassifier
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

SentimentLabel = Literal["positive", "neutral", "negative"]

_analyzer = SentimentIntensityAnalyzer()


class SentimentResult(TypedDict):
    sentiment: SentimentLabel
    sentiment_score: float
    vader_label: SentimentLabel
    vader_compound: float
    lr_label: SentimentLabel
    lr_confidence: float
    ensemble_method: str


def _label_from_compound(compound: float) -> SentimentLabel:
    if compound >= 0.05:
        return "positive"
    if compound <= -0.05:
        return "negative"
    return "neutral"


def _ensemble_vote(vader: SentimentLabel, lr: SentimentLabel) -> SentimentLabel:
    if vader == lr:
        return vader
    if vader == "neutral":
        return lr
    if lr == "neutral":
        return vader
    return "neutral"


def analyze_sentiment(text: str, lr: dict | None = None) -> SentimentResult:
    scores = _analyzer.polarity_scores(text or "")
    compound = scores["compound"]
    vader_label = _label_from_compound(compound)
    lr_label = lr.get("lr_label", "neutral") if lr else "neutral"
    lr_conf = lr.get("lr_confidence", 0.0) if lr else 0.0
    final = _ensemble_vote(vader_label, lr_label)
    return {
        "sentiment": final,
        "sentiment_score": round(compound, 3),
        "vader_label": vader_label,
        "vader_compound": round(compound, 3),
        "lr_label": lr_label,
        "lr_confidence": lr_conf,
        "ensemble_method": "majority_vote_vader_lr",
    }


def enrich_posts_with_sentiment(posts: list[dict]) -> list[dict]:
    texts = [p.get("clean_text", "") for p in posts]
    clf = SentimentClassifier()
    clf.fit(texts)
    lr_preds = clf.predict(texts)
    enriched: list[dict] = []
    for post, lr in zip(posts, lr_preds):
        result = analyze_sentiment(post.get("clean_text", ""), lr)
        enriched.append({**post, **result})
    return enriched


def sentiment_distribution(posts: list[dict]) -> dict:
    counts = {"positive": 0, "neutral": 0, "negative": 0}
    for post in posts:
        label = post.get("sentiment", "neutral")
        if label in counts:
            counts[label] += 1
    total = len(posts) or 1
    return {
        "counts": counts,
        "percentages": {k: round(v / total * 100, 1) for k, v in counts.items()},
        "total": len(posts),
    }
