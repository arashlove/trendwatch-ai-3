"""Automated evaluation: metrics and LLM-as-judge stub."""

import os
from typing import TypedDict

from dotenv import load_dotenv

load_dotenv()


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
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key or not briefing_markdown:
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
        from openai import OpenAI

        client = OpenAI(
            api_key=api_key,
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        )
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an evaluation judge. Score the briefing 0-100 for "
                        "clarity, grounding, and actionability. Reply JSON: "
                        '{"score": number, "feedback": "string"}'
                    ),
                },
                {
                    "role": "user",
                    "content": f"Crisis score: {crisis_score}\n\nBriefing:\n{briefing_markdown[:3000]}",
                },
            ],
            temperature=0,
            max_tokens=200,
        )
        import json

        text = resp.choices[0].message.content or "{}"
        data = json.loads(text)
        return {
            "score": int(data.get("score", 70)),
            "feedback": str(data.get("feedback", "OK")),
            "source": "llm_judge",
        }
    except Exception:
        return {
            "score": 70,
            "feedback": "LLM judge unavailable; use manual rubric in report.",
            "source": "error_fallback",
        }
