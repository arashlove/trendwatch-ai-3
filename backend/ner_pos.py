"""Named Entity Recognition and Part-of-Speech tagging."""

from typing import TypedDict

_nlp = None
_spacy_load_attempted = False


def _load_spacy():
    """Load spaCy model if pre-installed. Never download during HTTP requests."""
    global _nlp, _spacy_load_attempted
    if _spacy_load_attempted:
        return _nlp
    _spacy_load_attempted = True
    try:
        import spacy

        _nlp = spacy.load("en_core_web_sm")
    except Exception:
        _nlp = None
    return _nlp


class NerPosResult(TypedDict):
    entities: list[dict]
    pos_tags: list[dict]
    engine: str


def _ner_pos_nltk(text: str) -> NerPosResult:
    import nltk
    from nltk import pos_tag, word_tokenize
    from nltk.tree import Tree

    from preprocessing import _ensure_nltk

    _ensure_nltk()
    for resource in ("maxent_ne_chunker", "maxent_ne_chunker_tab"):
        try:
            nltk.data.find(f"chunkers/{resource}")
        except LookupError:
            nltk.download(resource, quiet=True)

    tokens = word_tokenize(text[:2000]) if text else []
    tagged = pos_tag(tokens)
    pos_tags = [{"token": w, "pos": p} for w, p in tagged[:40]]
    entities: list[dict] = []
    try:
        from nltk import ne_chunk

        tree = ne_chunk(tagged)
        for chunk in tree:
            if isinstance(chunk, Tree):
                label = chunk.label()
                name = " ".join(c[0] for c in chunk.leaves())
                entities.append({"text": name, "label": label})
    except LookupError:
        entities = []
    return {"entities": entities[:20], "pos_tags": pos_tags, "engine": "nltk"}


def analyze_ner_pos(text: str) -> NerPosResult:
    if not text:
        return {"entities": [], "pos_tags": [], "engine": "none"}
    nlp = _load_spacy()
    if nlp is not None:
        doc = nlp(text[:3000])
        entities = [
            {"text": ent.text, "label": ent.label_}
            for ent in doc.ents[:20]
        ]
        pos_tags = [
            {"token": tok.text, "pos": tok.pos_}
            for tok in doc
            if tok.is_alpha
        ][:40]
        return {"entities": entities, "pos_tags": pos_tags, "engine": "spacy"}
    return _ner_pos_nltk(text)


def enrich_posts_with_ner(posts: list[dict]) -> list[dict]:
    corpus_entities: dict[str, int] = {}
    enriched: list[dict] = []
    for post in posts:
        text = post.get("clean_text") or post.get("combined_text", "")
        result = analyze_ner_pos(text)
        for ent in result["entities"]:
            key = f"{ent['text']} ({ent['label']})"
            corpus_entities[key] = corpus_entities.get(key, 0) + 1
        enriched.append({**post, "ner_pos": result})
    top_entities = [
        {"entity": k, "count": v}
        for k, v in sorted(corpus_entities.items(), key=lambda x: -x[1])[:15]
    ]
    return enriched, top_entities
