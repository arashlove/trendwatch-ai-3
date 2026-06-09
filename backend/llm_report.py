import os
from typing import TypedDict

from dotenv import load_dotenv

load_dotenv()

ETHICS_FOOTER = (
    "\n\n---\n*Ethics notice: Analysis uses public Reddit text. Sentiment and crisis "
    "scores are algorithmic estimates, not legal or PR advice. Models may reflect "
    "language bias; human review is required before brand actions.*"
)


class BriefingSections(TypedDict):
    executive_summary: str
    main_concerns: list[str]
    crisis_explanation: str
    recommended_actions: list[str]
    communication_strategy: str
    ethics_notice: str
    source: str


def _format_context(payload: dict) -> str:
    summary = payload.get("summary", {})
    topics = payload.get("topics", [])
    risks = payload.get("risk_keywords", [])
    crisis = payload.get("crisis", {})
    trends = payload.get("trends", {})
    retrieved = payload.get("rag_context", [])
    lines = [
        f"Query: {payload.get('query', 'N/A')}",
        f"Total posts: {summary.get('total_posts', 0)}",
        f"Sentiment: {summary.get('sentiment_percentages', {})}",
        f"Crisis score: {crisis.get('crisis_score')} ({crisis.get('risk_level')})",
        f"Crisis reasons: {crisis.get('reasons', [])}",
        f"Trend: {trends.get('spike_message', '')}",
        f"Top risk keywords: {risks[:8]}",
        f"Topics: {[t.get('label') for t in topics[:5]]}",
        "Retrieved posts (RAG):",
    ]
    for r in retrieved[:5]:
        lines.append(f"- [{r.get('sentiment')}] {r.get('title')}: {r.get('snippet', '')[:120]}")
    return "\n".join(lines)


COT_SYSTEM = """You are a social media intelligence analyst for brand monitoring.
Use chain-of-thought: first reason step-by-step about sentiment, topics, and risk,
then produce the final structured briefing. Base conclusions only on provided data."""


def _fallback_briefing(payload: dict) -> BriefingSections:
    summary = payload.get("summary", {})
    crisis = payload.get("crisis", {})
    topics = payload.get("topics", [])
    neg_pct = summary.get("sentiment_percentages", {}).get("negative", 0)
    topic_names = [t.get("label", "") for t in topics[:3]]
    return {
        "executive_summary": (
            f"TrendWatch AI analysed {summary.get('total_posts', 0)} Reddit posts. "
            f"Negative sentiment is {neg_pct}%. Crisis score is "
            f"{crisis.get('crisis_score', 0)}/100 ({crisis.get('risk_level', 'Low')})."
        ),
        "main_concerns": crisis.get("reasons", [])[:3] or ["No major concerns detected."],
        "crisis_explanation": " ".join(crisis.get("reasons", [])),
        "recommended_actions": [
            "Monitor high-impact negative threads daily.",
            "Prepare a factual FAQ for top complaint topics.",
            "Escalate to customer support if refund/delay keywords spike.",
        ],
        "communication_strategy": (
            f"Address emerging topics: {', '.join(topic_names) or 'general discussion'}. "
            "Use empathetic, transparent tone; avoid dismissive responses."
        ),
        "ethics_notice": ETHICS_FOOTER.strip(),
        "source": "rule_based_fallback",
    }


def _call_llm(context: str) -> str | None:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None
    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=api_key,
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        )
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        prompt = f"""{COT_SYSTEM}

DATA:
{context}

After your internal reasoning, respond in this exact markdown structure:
## Executive Summary
(2-3 sentences)
## Main Concerns
- (bullet 1)
- (bullet 2)
- (bullet 3)
## Crisis Explanation
(short paragraph)
## Recommended Actions
- (action 1)
- (action 2)
- (action 3)
## Communication Strategy
(short paragraph)
"""
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": COT_SYSTEM},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=900,
        )
        return resp.choices[0].message.content
    except Exception:
        return None


def _parse_llm_markdown(text: str) -> BriefingSections:
    sections = {
        "executive_summary": "",
        "main_concerns": [],
        "crisis_explanation": "",
        "recommended_actions": [],
        "communication_strategy": "",
    }
    current = None
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("## Executive"):
            current = "executive_summary"
            continue
        if line.startswith("## Main"):
            current = "main_concerns"
            continue
        if line.startswith("## Crisis"):
            current = "crisis_explanation"
            continue
        if line.startswith("## Recommended"):
            current = "recommended_actions"
            continue
        if line.startswith("## Communication"):
            current = "communication_strategy"
            continue
        if not line or not current:
            continue
        if current in ("main_concerns", "recommended_actions") and line.startswith("-"):
            sections[current].append(line.lstrip("- ").strip())
        elif current == "executive_summary":
            sections["executive_summary"] += (" " if sections["executive_summary"] else "") + line
        else:
            sections[current] += (" " if sections[current] else "") + line
    return {
        **sections,
        "ethics_notice": ETHICS_FOOTER.strip(),
        "source": "llm_cot",
    }


def generate_briefing(payload: dict) -> BriefingSections:
    context = _format_context(payload)
    raw = _call_llm(context)
    if raw:
        parsed = _parse_llm_markdown(raw)
        parsed["raw_markdown"] = raw + ETHICS_FOOTER
        return parsed
    fallback = _fallback_briefing(payload)
    fallback["raw_markdown"] = (
        f"## Executive Summary\n{fallback['executive_summary']}\n\n"
        f"## Main Concerns\n"
        + "\n".join(f"- {c}" for c in fallback["main_concerns"])
        + f"\n\n## Crisis Explanation\n{fallback['crisis_explanation']}\n\n"
        f"## Recommended Actions\n"
        + "\n".join(f"- {a}" for a in fallback["recommended_actions"])
        + f"\n\n## Communication Strategy\n{fallback['communication_strategy']}"
        + ETHICS_FOOTER
    )
    return fallback
