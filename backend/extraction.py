"""Rule-based information extraction: hashtags, mentions, risk keywords."""

import re
from typing import TypedDict

HASHTAG_RE = re.compile(r"#(\w+)", re.UNICODE)
MENTION_RE = re.compile(r"(?:u/|@)([A-Za-z0-9_-]+)")

RISK_KEYWORDS = frozenset(
    {
        "boycott",
        "scam",
        "fraud",
        "unsafe",
        "lawsuit",
        "broken",
        "refund",
        "delay",
        "angry",
        "disappointed",
        "terrible",
        "complaint",
        "cancel",
        "fake",
        "privacy",
        "leak",
        "discrimination",
        "exploit",
        "hate",
        "toxic",
        "recall",
        "injury",
        "misleading",
    }
)


class ExtractionResult(TypedDict):
    hashtags: list[str]
    mentions: list[str]
    risk_keywords: list[str]
    risk_keyword_count: int


def extract_from_text(text: str) -> ExtractionResult:
    lower = (text or "").lower()
    hashtags = list(dict.fromkeys(HASHTAG_RE.findall(text or "")))
    mentions = list(dict.fromkeys(MENTION_RE.findall(text or "")))
    found = [kw for kw in RISK_KEYWORDS if kw in lower]
    return {
        "hashtags": hashtags,
        "mentions": mentions,
        "risk_keywords": found,
        "risk_keyword_count": len(found),
    }


def enrich_posts(posts: list[dict]) -> list[dict]:
    enriched: list[dict] = []
    for post in posts:
        text = post.get("combined_text", post.get("title", ""))
        ext = extract_from_text(text)
        enriched.append({**post, **ext})
    return enriched


def aggregate_risk_keywords(posts: list[dict]) -> list[dict]:
    counts: dict[str, int] = {}
    for post in posts:
        for kw in post.get("risk_keywords", []):
            counts[kw] = counts.get(kw, 0) + 1
    return [
        {"keyword": k, "count": v}
        for k, v in sorted(counts.items(), key=lambda x: -x[1])
    ]
