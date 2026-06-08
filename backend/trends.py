"""Trend detection over time: volume, negative ratio, risk keywords."""

from collections import defaultdict
from datetime import datetime, timezone
from typing import TypedDict


class TrendPoint(TypedDict):
    date: str
    post_count: int
    negative_count: int
    negative_ratio: float
    risk_keyword_count: int


class TrendSummary(TypedDict):
    timeline: list[TrendPoint]
    spike_detected: bool
    spike_message: str
    avg_negative_ratio: float


def _parse_date(created_utc: float | int | None) -> str:
    if not created_utc:
        return "unknown"
    return datetime.fromtimestamp(float(created_utc), tz=timezone.utc).strftime(
        "%Y-%m-%d"
    )


def analyze_trends(posts: list[dict]) -> TrendSummary:
    by_date: dict[str, list[dict]] = defaultdict(list)
    for post in posts:
        day = _parse_date(post.get("created_utc"))
        by_date[day].append(post)

    timeline: list[TrendPoint] = []
    for day in sorted(by_date.keys()):
        day_posts = by_date[day]
        neg = sum(1 for p in day_posts if p.get("sentiment") == "negative")
        risk = sum(p.get("risk_keyword_count", 0) for p in day_posts)
        count = len(day_posts)
        timeline.append(
            {
                "date": day,
                "post_count": count,
                "negative_count": neg,
                "negative_ratio": round(neg / count, 3) if count else 0.0,
                "risk_keyword_count": risk,
            }
        )

    ratios = [t["negative_ratio"] for t in timeline if t["date"] != "unknown"]
    avg_ratio = sum(ratios) / len(ratios) if ratios else 0.0
    spike_detected = False
    spike_message = "No significant negative sentiment spike detected."
    if timeline:
        latest = [t for t in timeline if t["date"] != "unknown"]
        if latest:
            last = latest[-1]
            if avg_ratio > 0 and last["negative_ratio"] >= avg_ratio * 1.5:
                spike_detected = True
                spike_message = (
                    f"Negative sentiment ratio rose to {last['negative_ratio']:.0%} "
                    f"(average {avg_ratio:.0%}). Monitor closely."
                )

    return {
        "timeline": timeline,
        "spike_detected": spike_detected,
        "spike_message": spike_message,
        "avg_negative_ratio": round(avg_ratio, 3),
    }
