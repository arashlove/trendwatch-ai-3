from collections import Counter
from typing import TypedDict

import numpy as np
from sklearn.cluster import KMeans

from similarity import embed_texts


class TopicResult(TypedDict):
    topic_id: int
    label: str
    size: int
    keywords: list[str]
    average_sentiment: str
    representative_post: dict | None


def _top_keywords(texts: list[str], n: int = 6) -> list[str]:
    words: list[str] = []
    for text in texts:
        for token in (text or "").split():
            if len(token) > 3 and token.isalpha():
                words.append(token)
    common = Counter(words).most_common(n)
    return [w for w, _ in common]


def _avg_sentiment(posts: list[dict]) -> str:
    labels = [p.get("sentiment", "neutral") for p in posts]
    counts = Counter(labels)
    return counts.most_common(1)[0][0] if counts else "neutral"


def detect_topics(posts: list[dict], *, n_clusters: int | None = None) -> list[TopicResult]:
    if len(posts) < 3:
        return []
    texts = [p.get("clean_text", "") for p in posts]
    k = n_clusters or min(5, max(2, len(posts) // 8))
    k = min(k, len(posts))
    vectors = embed_texts(texts)
    if vectors.size == 0:
        return []
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(vectors)
    topics: list[TopicResult] = []
    for cluster_id in range(k):
        cluster_posts = [p for p, lab in zip(posts, labels) if lab == cluster_id]
        if not cluster_posts:
            continue
        keywords = _top_keywords([p.get("clean_text", "") for p in cluster_posts])
        label = " / ".join(keywords[:3]) if keywords else f"Topic {cluster_id + 1}"
        rep = max(
            cluster_posts,
            key=lambda p: p.get("score", 0) + 2 * p.get("num_comments", 0),
        )
        topics.append(
            {
                "topic_id": cluster_id,
                "label": label.title(),
                "size": len(cluster_posts),
                "keywords": keywords,
                "average_sentiment": _avg_sentiment(cluster_posts),
                "representative_post": {
                    "id": rep.get("id"),
                    "title": rep.get("title"),
                    "sentiment": rep.get("sentiment"),
                    "permalink": rep.get("permalink"),
                },
            }
        )
    topics.sort(key=lambda t: -t["size"])
    return topics
