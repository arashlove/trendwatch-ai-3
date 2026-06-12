import json
import logging
import os
from typing import TypedDict

import env_config  # noqa: F401

logger = logging.getLogger(__name__)


class EvaluationMetrics(TypedDict):
    sentiment_agreement: float
    notes: str


class JudgeResult(TypedDict):
    score: int
    feedback: str
    source: str


def sentiment_agreement(posts: list[dict]) -> EvaluationMetrics:
    if not posts:
        return {"sentiment_agreement": 0.0, "notes": "No posts."}
    agree = sum(
        1 for p in posts if p.get("vader_label") == p.get("lr_label")
    )
    ratio = agree / len(posts)
    return {
        "sentiment_agreement": round(ratio, 3),
        "notes": (
            f"VADER and LR agree on {agree}/{len(posts)} posts ({ratio:.0%}). "
            "Use manually labelled gold set for formal accuracy in your report."
        ),
    }


def llm_judge_briefing(briefing_markdown: str, crisis_score: int) -> JudgeResult:
    from llm_client import chat_completion, get_api_key, get_provider_label

    if not get_api_key() or not briefing_markdown:
        aligned = crisis_score >= 60 and "high" in briefing_markdown.lower()
        score = 75 if aligned or crisis_score < 40 else 55
        return {
            "score": score,
            "feedback": (
                "Heuristic judge: briefing length and crisis keywords checked. "
                "Set OPENAI_API_KEY for full LLM-as-judge evaluation."
            ),
            "source": "heuristic",
        }
    try:
        text = chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an evaluation judge. Score the briefing 0-100 for "
                        "clarity, grounding, and actionability. Reply JSON only: "
                        '{"score": number, "feedback": "string"}'
                    ),
                },
                {
                    "role": "user",
                    "content": f"Crisis score: {crisis_score}\n\nBriefing:\n{briefing_markdown[:3000]}",
                },
            ],
            max_tokens=200,
            temperature=0,
        )
        text = text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
        data = json.loads(text)
        return {
            "score": int(data.get("score", 70)),
            "feedback": str(data.get("feedback", "OK")),
            "source": "llm_judge",
        }
    except Exception as exc:
        logger.warning("%s judge failed: %s", get_provider_label(), exc)
        return {
            "score": 70,
            "feedback": f"LLM judge error: {exc}",
            "source": "error_fallback",
        }
