import math
from typing import TypedDict

from trends import TrendSummary


class CrisisResult(TypedDict):
    crisis_score: int
    risk_level: str
    components: dict[str, float]
    reasons: list[str]


def _impact_score(post: dict) -> float:
    score = post.get("score", 0) or 0
    comments = post.get("num_comments", 0) or 0
    return math.log1p(score) + math.log1p(comments)


def high_impact_posts(posts: list[dict], *, limit: int = 5) -> list[dict]:
    ranked = sorted(posts, key=_impact_score, reverse=True)
    result: list[dict] = []
    for post in ranked[:limit]:
        result.append(
            {
                "id": post.get("id"),
                "title": post.get("title"),
                "author": post.get("author"),
                "subreddit": post.get("subreddit"),
                "score": post.get("score"),
                "num_comments": post.get("num_comments"),
                "sentiment": post.get("sentiment"),
                "risk_keywords": post.get("risk_keywords", []),
                "impact_score": round(_impact_score(post), 2),
                "permalink": post.get("permalink"),
            }
        )
    return result


def calculate_crisis_score(
    posts: list[dict], trends: TrendSummary
) -> CrisisResult:
    total = len(posts) or 1
    neg = sum(1 for p in posts if p.get("sentiment") == "negative")
    neg_pct = neg / total
    risk_total = sum(p.get("risk_keyword_count", 0) for p in posts)
    risk_norm = min(1.0, risk_total / (total * 2))
    neg_high_impact = [
        p for p in posts if p.get("sentiment") == "negative" and _impact_score(p) > 2
    ]
    engagement_ratio = len(neg_high_impact) / total
    trend_spike = 1.0 if trends.get("spike_detected") else 0.0
    if trends.get("avg_negative_ratio", 0) > 0:
        latest_ratio = 0.0
        tl = trends.get("timeline", [])
        if tl:
            latest_ratio = tl[-1].get("negative_ratio", 0)
        trend_spike = max(
            trend_spike,
            min(1.0, latest_ratio / trends["avg_negative_ratio"] - 1)
            if trends["avg_negative_ratio"] > 0
            else 0,
        )

    negative_component = neg_pct * 40
    risk_component = risk_norm * 25
    engagement_component = min(1.0, engagement_ratio * 5) * 20
    trend_component = min(1.0, trend_spike) * 15
    score = int(
        round(
            negative_component
            + risk_component
            + engagement_component
            + trend_component
        )
    )
    score = max(0, min(100, score))

    if score <= 30:
        level = "Low"
    elif score <= 60:
        level = "Medium"
    elif score <= 80:
        level = "High"
    else:
        level = "Critical"

    reasons: list[str] = []
    if neg_pct > 0.5:
        reasons.append(f"Negative sentiment is {neg_pct:.0%} of posts.")
    if risk_total > 0:
        reasons.append(f"Risk keywords appeared {risk_total} times across posts.")
    if neg_high_impact:
        reasons.append(
            f"{len(neg_high_impact)} high-engagement posts carry negative sentiment."
        )
    if trends.get("spike_detected"):
        reasons.append(trends.get("spike_message", "Trend spike detected."))
    if not reasons:
        reasons.append("Discussion appears within normal sentiment bounds.")

    return {
        "crisis_score": score,
        "risk_level": level,
        "components": {
            "negative_sentiment": round(negative_component, 1),
            "risk_keywords": round(risk_component, 1),
            "engagement": round(engagement_component, 1),
            "trend_spike": round(trend_component, 1),
        },
        "reasons": reasons,
    }
