"""Traditional text classification: TF-IDF + Logistic Regression."""

from typing import Literal

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

SentimentLabel = Literal["positive", "neutral", "negative"]

_vader_lexicon: dict[str, float] | None = None


def _weak_labels(texts: list[str]) -> list[SentimentLabel]:
    """Weak supervision from VADER for training when no gold labels exist."""
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

    analyzer = SentimentIntensityAnalyzer()
    labels: list[SentimentLabel] = []
    for text in texts:
        scores = analyzer.polarity_scores(text or "")
        compound = scores["compound"]
        if compound >= 0.05:
            labels.append("positive")
        elif compound <= -0.05:
            labels.append("negative")
        else:
            labels.append("neutral")
    return labels


class SentimentClassifier:
    def __init__(self) -> None:
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            min_df=2,
        )
        self.model = LogisticRegression(max_iter=500)
        self._fitted = False

    def fit(self, texts: list[str]) -> None:
        if len(texts) < 5:
            self._fitted = False
            return
        labels = _weak_labels(texts)
        X = self.vectorizer.fit_transform(texts)
        self.model.fit(X, labels)
        self._fitted = True

    def predict(self, texts: list[str]) -> list[dict]:
        if not self._fitted or not texts:
            return [
                {
                    "lr_label": "neutral",
                    "lr_confidence": 0.0,
                }
                for _ in texts
            ]
        X = self.vectorizer.transform(texts)
        labels = self.model.predict(X)
        probas = self.model.predict_proba(X)
        classes = list(self.model.classes_)
        results: list[dict] = []
        for i, label in enumerate(labels):
            idx = classes.index(label)
            conf = float(np.max(probas[i]))
            results.append({"lr_label": label, "lr_confidence": round(conf, 3)})
        return results
