import os

import env_config  # noqa: F401
import httpx

_last_data_source = "unknown"

TIME_FILTER_MAP = {
    "hour": "hour",
    "day": "day",
    "week": "week",
    "month": "month",
    "year": "year",
    "all": "all",
}


def get_last_data_source() -> str:
    return _last_data_source


def set_data_source(source: str) -> None:
    global _last_data_source
    _last_data_source = source


def _normalize_submission(sub) -> dict:
    return {
        "id": sub.id,
        "title": sub.title,
        "selftext": getattr(sub, "selftext", "") or "",
        "author": str(sub.author) if sub.author else "[deleted]",
        "subreddit": str(sub.subreddit),
        "score": sub.score,
        "num_comments": sub.num_comments,
        "created_utc": sub.created_utc,
        "permalink": f"https://reddit.com{sub.permalink}",
        "url": sub.url,
    }


def _normalize_public_child(data: dict) -> dict:
    permalink = data.get("permalink", "") or ""
    if permalink and not permalink.startswith("http"):
        permalink = f"https://reddit.com{permalink}"
    return {
        "id": data.get("id", ""),
        "title": data.get("title", ""),
        "selftext": data.get("selftext", "") or "",
        "author": data.get("author", "[deleted]") or "[deleted]",
        "subreddit": data.get("subreddit", ""),
        "score": int(data.get("score", 0) or 0),
        "num_comments": int(data.get("num_comments", 0) or 0),
        "created_utc": int(data.get("created_utc", 0) or 0),
        "permalink": permalink,
        "url": data.get("url", ""),
    }


def search_reddit_public(
    query: str,
    *,
    subreddit: str = "all",
    limit: int = 50,
    time_filter: str = "month",
    sort: str = "relevance",
) -> list[dict]:
    user_agent = os.getenv("REDDIT_USER_AGENT", "trendwatch-ai/1.0")
    headers = {"User-Agent": user_agent}
    t = TIME_FILTER_MAP.get(time_filter.lower(), "month")
    results: list[dict] = []
    after: str | None = None
    max_pages = 5

    with httpx.Client(timeout=30.0, headers=headers, follow_redirects=True) as client:
        for _ in range(max_pages):
            if len(results) >= limit:
                break
            batch = min(100, limit - len(results))
            if subreddit and subreddit.lower() != "all":
                url = f"https://www.reddit.com/r/{subreddit}/search.json"
                params: dict[str, str] = {
                    "q": query,
                    "restrict_sr": "1",
                    "sort": sort,
                    "t": t,
                    "limit": str(batch),
                }
            else:
                url = "https://www.reddit.com/search.json"
                params = {
                    "q": query,
                    "sort": sort,
                    "t": t,
                    "limit": str(batch),
                }
            if after:
                params["after"] = after

            resp = client.get(url, params=params)
            resp.raise_for_status()
            payload = resp.json()
            children = payload.get("data", {}).get("children", [])
            if not children:
                break
            for child in children:
                data = child.get("data")
                if isinstance(data, dict):
                    results.append(_normalize_public_child(data))
            after = payload.get("data", {}).get("after")
            if not after:
                break

    return results[:limit]


def search_reddit(
    query: str,
    *,
    subreddit: str = "all",
    limit: int = 50,
    time_filter: str = "month",
    sort: str = "relevance",
) -> list[dict]:
    client_id = os.getenv("REDDIT_CLIENT_ID", "").strip()
    client_secret = os.getenv("REDDIT_CLIENT_SECRET", "").strip()
    user_agent = os.getenv("REDDIT_USER_AGENT", "trendwatch-ai/1.0")

    if client_id and client_secret:
        import praw

        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
        )
        sub = reddit.subreddit(subreddit)
        results: list[dict] = []
        search = sub.search(query, sort=sort, time_filter=time_filter, limit=limit)
        for submission in search:
            results.append(_normalize_submission(submission))
        set_data_source("reddit_praw")
        return results

    try:
        public = search_reddit_public(
            query,
            subreddit=subreddit,
            limit=limit,
            time_filter=time_filter,
            sort=sort,
        )
        if public:
            set_data_source("reddit_public_api")
            return public
    except Exception:
        pass

    set_data_source("reddit_unavailable")
    return []
