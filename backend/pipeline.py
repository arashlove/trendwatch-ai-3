from agent import run_analysis_agent
from crisis import calculate_crisis_score
from evaluation import llm_judge_briefing, sentiment_agreement
from extraction import enrich_posts
from llm_report import generate_briefing
from ner_pos import enrich_posts_with_ner
from preprocessing import prepare_posts
from rag import retrieve
from reddit_client import get_last_data_source, search_reddit, set_data_source
from sentiment import enrich_posts_with_sentiment, sentiment_distribution
from topics import detect_topics
from trends import analyze_trends


def _public_post(post: dict) -> dict:
    return {
        "id": post.get("id"),
        "title": post.get("title"),
        "author": post.get("author"),
        "subreddit": post.get("subreddit"),
        "score": post.get("score"),
        "num_comments": post.get("num_comments"),
        "sentiment": post.get("sentiment"),
        "sentiment_score": post.get("sentiment_score"),
        "vader_label": post.get("vader_label"),
        "lr_label": post.get("lr_label"),
        "risk_keywords": post.get("risk_keywords", []),
        "hashtags": post.get("hashtags", []),
        "mentions": post.get("mentions", []),
        "permalink": post.get("permalink"),
    }


def _format_analysis_response(
    *,
    query: str,
    subreddit: str,
    result: dict,
    trace: list,
) -> dict:
    dist = sentiment_distribution(result["posts"])
    crisis = result["crisis"]

    return {
        "query": query,
        "subreddit": subreddit,
        "data_source": get_last_data_source(),
        "summary": {
            "total_posts": len(result["posts"]),
            "positive": dist["counts"]["positive"],
            "neutral": dist["counts"]["neutral"],
            "negative": dist["counts"]["negative"],
            "sentiment_percentages": dist["percentages"],
            "crisis_score": crisis["crisis_score"],
            "risk_level": crisis["risk_level"],
        },
        "sentiment_distribution": [
            {"label": k, "count": v} for k, v in dist["counts"].items()
        ],
        "trends": result["trends"],
        "topics": result["topics"],
        "high_impact_posts": result["high_impact_posts"],
        "risk_keywords": result["risk_keywords"],
        "top_entities": result["top_entities"],
        "similar_pairs": result.get("similar_pairs", []),
        "crisis": crisis,
        "llm_report": result.get("llm_report", ""),
        "briefing": result.get("briefing", {}),
        "agent_trace": trace,
        "posts": [_public_post(p) for p in result["posts"][:30]],
        "evaluation": {
            "sentiment": sentiment_agreement(result["posts"]),
            "briefing_judge": llm_judge_briefing(
                result.get("llm_report", ""),
                crisis["crisis_score"],
            ),
        },
        "techniques_used": {
            "basic": [
                "preprocessing",
                "ner",
                "pos_tagging",
                "tfidf_logistic_regression",
                "sentiment_ensemble",
                "embedding_clustering",
                "regex_extraction",
            ],
            "advanced": [
                "foundation_llm",
                "rag",
                "prompt_engineering",
                "chain_of_thought",
                "llm_as_judge",
                "ensemble_methods",
                "agentic_react",
                "ethics_disclaimer",
            ],
        },
    }


def _run_agent_on_posts(posts: list[dict], query: str) -> tuple[dict, list]:
    def collect():
        return posts

    def rag_fn(posts_arg, q):
        return retrieve(posts_arg, q)

    return run_analysis_agent(
        collect_fn=collect,
        preprocess_fn=prepare_posts,
        extract_fn=enrich_posts,
        ner_fn=enrich_posts_with_ner,
        sentiment_fn=enrich_posts_with_sentiment,
        topics_fn=detect_topics,
        trends_fn=analyze_trends,
        crisis_fn=calculate_crisis_score,
        rag_fn=rag_fn,
        briefing_fn=generate_briefing,
        query=query,
    )


def run_analysis_on_posts(
    posts: list[dict],
    *,
    query: str,
    subreddit: str = "all",
) -> dict:
    if len(posts) < 5:
        raise ValueError("Need at least 5 posts for analysis")

    set_data_source("reddit_devvit_import")
    result, trace = _run_agent_on_posts(posts, query)
    return _format_analysis_response(
        query=query,
        subreddit=subreddit,
        result=result,
        trace=trace,
    )


def run_full_analysis(
    query: str,
    *,
    subreddit: str = "all",
    limit: int = 50,
    time_filter: str = "month",
) -> dict:
    posts = search_reddit(
        query,
        subreddit=subreddit,
        limit=limit,
        time_filter=time_filter,
    )
    if len(posts) < 5:
        raise ValueError(
            "Not enough Reddit posts returned. Configure REDDIT_CLIENT_ID in backend/.env "
            "or use the Devvit app to collect posts and POST /report."
        )

    result, trace = _run_agent_on_posts(posts, query)
    return _format_analysis_response(
        query=query,
        subreddit=subreddit,
        result=result,
        trace=trace,
    )
