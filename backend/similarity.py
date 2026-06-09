from typing import TypedDict

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


class SimilarPair(TypedDict):
    post_a_id: str
    post_b_id: str
    similarity: float


_embedder = None
_embedder_tried = False


def _get_embedder():
    global _embedder, _embedder_tried
    if _embedder_tried:
        return _embedder
    _embedder_tried = True
    try:
        from sentence_transformers import SentenceTransformer

        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    except Exception:
        _embedder = None
    return _embedder


def _tfidf_vectors(texts: list[str]):
    from sklearn.feature_extraction.text import TfidfVectorizer

    vec = TfidfVectorizer(max_features=2000, ngram_range=(1, 2))
    return vec.fit_transform(texts).toarray()


def embed_texts(texts: list[str]) -> np.ndarray:
    model = _get_embedder()
    if model is not None and texts:
        return np.array(model.encode(texts, show_progress_bar=False))
    if not texts:
        return np.zeros((0, 0))
    return _tfidf_vectors(texts)


def top_similar_pairs(
    posts: list[dict], *, top_k: int = 5, threshold: float = 0.55
) -> list[SimilarPair]:
    if len(posts) < 2:
        return []
    texts = [p.get("clean_text", "") for p in posts]
    vectors = embed_texts(texts)
    if vectors.size == 0:
        return []
    sim = cosine_similarity(vectors)
    pairs: list[SimilarPair] = []
    for i in range(len(posts)):
        for j in range(i + 1, len(posts)):
            score = float(sim[i, j])
            if score >= threshold:
                pairs.append(
                    {
                        "post_a_id": posts[i].get("id", str(i)),
                        "post_b_id": posts[j].get("id", str(j)),
                        "similarity": round(score, 3),
                    }
                )
    pairs.sort(key=lambda x: -x["similarity"])
    return pairs[:top_k]
