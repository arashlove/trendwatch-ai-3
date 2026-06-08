"""Agentic orchestration (ReAct-style): plan → act → observe steps."""

from typing import Callable, TypedDict


class AgentStep(TypedDict):
    thought: str
    action: str
    observation: str


class AgentTrace(TypedDict):
    steps: list[AgentStep]
    status: str


def run_analysis_agent(
    *,
    collect_fn: Callable[[], list[dict]],
    preprocess_fn: Callable[[list[dict]], list[dict]],
    extract_fn: Callable[[list[dict]], list[dict]],
    ner_fn: Callable[[list[dict]], tuple[list[dict], list[dict]]],
    sentiment_fn: Callable[[list[dict]], list[dict]],
    topics_fn: Callable[[list[dict]], list],
    trends_fn: Callable[[list[dict]], dict],
    crisis_fn: Callable[[list[dict], dict], dict],
    rag_fn: Callable[[list[dict], str], list],
    briefing_fn: Callable[[dict], dict],
    query: str,
) -> tuple[dict, AgentTrace]:
    steps: list[AgentStep] = []

    def step(thought: str, action: str, observation: str) -> None:
        steps.append({"thought": thought, "action": action, "observation": observation})

    step(
        "Need Reddit posts about the brand/topic.",
        "collect_posts",
        "Starting data collection.",
    )
    posts = collect_fn()
    step(
        f"Collected {len(posts)} posts.",
        "collect_posts",
        f"Received {len(posts)} posts.",
    )

    step("Raw text must be normalized for NLP.", "preprocess", "Running tokenizer pipeline.")
    posts = preprocess_fn(posts)
    step("Preprocessing complete.", "preprocess", f"{len(posts)} posts prepared.")

    step("Extract hashtags, mentions, risk keywords.", "extract", "Regex IE.")
    posts = extract_fn(posts)

    step("Run NER and POS for entity-aware monitoring.", "ner_pos", "spaCy/NLTK.")
    posts, top_entities = ner_fn(posts)

    step("Classify sentiment with VADER + LR ensemble.", "sentiment", "Ensemble vote.")
    posts = sentiment_fn(posts)

    step("Cluster topics with embeddings.", "topics", "KMeans clustering.")
    topics = topics_fn(posts)

    step("Compute temporal trends.", "trends", "Daily aggregation.")
    trends = trends_fn(posts)

    step("Score crisis risk from sentiment + engagement + trends.", "crisis", "Crisis formula.")
    crisis = crisis_fn(posts, trends)

    step("Retrieve relevant posts for grounded LLM briefing (RAG).", "rag", f"Query={query}")
    rag_context = rag_fn(posts, query)

    from extraction import aggregate_risk_keywords
    from sentiment import sentiment_distribution

    dist = sentiment_distribution(posts)
    from crisis import high_impact_posts

    payload = {
        "query": query,
        "posts": posts,
        "summary": {
            "total_posts": len(posts),
            "sentiment_counts": dist["counts"],
            "sentiment_percentages": dist["percentages"],
        },
        "topics": topics,
        "trends": trends,
        "crisis": crisis,
        "risk_keywords": aggregate_risk_keywords(posts),
        "top_entities": top_entities,
        "high_impact_posts": high_impact_posts(posts),
        "rag_context": rag_context,
    }

    step("Generate executive briefing with CoT LLM.", "briefing", "LLM or fallback.")
    briefing = briefing_fn(payload)
    payload["briefing"] = briefing
    payload["llm_report"] = briefing.get("raw_markdown", "")

    from similarity import top_similar_pairs

    payload["similar_pairs"] = top_similar_pairs(posts)

    trace: AgentTrace = {"steps": steps, "status": "completed"}
    return payload, trace
