from typing import TypedDict

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from similarity import _get_embedder


class RetrievedPost(TypedDict):
    id: str
    title: str
    snippet: str
    sentiment: str
    score: float


def _corpus_and_query_vectors(texts: list[str], query: str) -> tuple[np.ndarray, np.ndarray]:
    model = _get_embedder()
    combined = texts + [query]
    if model is not None and combined:
        all_vec = np.array(model.encode(combined, show_progress_bar=False))
        return all_vec[:-1], all_vec[-1:].reshape(1, -1)
    vec = TfidfVectorizer(max_features=2000, ngram_range=(1, 2))
    matrix = vec.fit_transform(combined)
    return matrix[:-1].toarray(), matrix[-1].toarray()


def retrieve(
    posts: list[dict],
    query: str,
    *,
    top_k: int = 5,
) -> list[RetrievedPost]:
    if not posts:
        return []
    texts = [p.get("clean_text", "") for p in posts]
    corpus_vecs, q_vec = _corpus_and_query_vectors(texts, query)
    if corpus_vecs.size == 0:
        return []
    sims = cosine_similarity(q_vec, corpus_vecs)[0]
    indices = np.argsort(sims)[::-1][:top_k]
    results: list[RetrievedPost] = []
    for idx in indices:
        post = posts[int(idx)]
        text = post.get("clean_text", "")[:280]
        results.append(
            {
                "id": str(post.get("id", idx)),
                "title": post.get("title", ""),
                "snippet": text,
                "sentiment": post.get("sentiment", "neutral"),
                "score": round(float(sims[int(idx)]), 3),
            }
        )
    return results
