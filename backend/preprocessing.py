"""Text preprocessing: tokenization, normalization, stemming, lemmatization."""

import re
from typing import TypedDict

import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import word_tokenize

_NLTK_RESOURCES = [
    ("tokenizers/punkt", "punkt"),
    ("tokenizers/punkt_tab", "punkt_tab"),
    ("corpora/stopwords", "stopwords"),
    ("corpora/wordnet", "wordnet"),
    ("taggers/averaged_perceptron_tagger", "averaged_perceptron_tagger"),
    ("taggers/averaged_perceptron_tagger_eng", "averaged_perceptron_tagger_eng"),
]


def _ensure_nltk() -> None:
    for path, name in _NLTK_RESOURCES:
        try:
            nltk.data.find(path)
        except LookupError:
            nltk.download(name, quiet=True)


_ensure_nltk()

_stemmer = PorterStemmer()
_lemmatizer = WordNetLemmatizer()
_stop = set(stopwords.words("english"))

_URL_RE = re.compile(r"https?://\S+|www\.\S+")
_HTML_RE = re.compile(r"<[^>]+>")
_NON_WORD_RE = re.compile(r"[^a-zA-Z0-9#@_\s]+")


class ProcessedText(TypedDict):
    raw: str
    normalized: str
    tokens: list[str]
    stemmed_tokens: list[str]
    lemmatized_tokens: list[str]


def clean_text(text: str) -> str:
    if not text:
        return ""
    t = _HTML_RE.sub(" ", text)
    t = _URL_RE.sub(" ", t)
    t = t.lower().strip()
    t = _NON_WORD_RE.sub(" ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def preprocess_text(text: str, *, remove_stopwords: bool = False) -> ProcessedText:
    raw = text or ""
    normalized = clean_text(raw)
    tokens = word_tokenize(normalized) if normalized else []
    filtered = [t for t in tokens if t not in _stop] if remove_stopwords else tokens
    stemmed = [_stemmer.stem(t) for t in filtered]
    lemmatized = [_lemmatizer.lemmatize(t) for t in filtered]
    return {
        "raw": raw,
        "normalized": normalized,
        "tokens": tokens,
        "stemmed_tokens": stemmed,
        "lemmatized_tokens": lemmatized,
    }


def prepare_posts(posts: list[dict]) -> list[dict]:
    prepared: list[dict] = []
    for post in posts:
        title = post.get("title", "") or ""
        body = post.get("selftext", post.get("body", "")) or ""
        combined = f"{title} {body}".strip()
        processed = preprocess_text(combined)
        prepared.append(
            {
                **post,
                "combined_text": combined,
                "clean_text": processed["normalized"],
                "tokens": processed["tokens"],
                "stemmed_tokens": processed["stemmed_tokens"],
                "lemmatized_tokens": processed["lemmatized_tokens"],
            }
        )
    return prepared
