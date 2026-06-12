import os
from typing import Any

import env_config  # noqa: F401


def get_api_key() -> str:
    return (
        os.getenv("OPENAI_API_KEY", "").strip()
        or os.getenv("OPENROUTER_API_KEY", "").strip()
    )


def get_base_url() -> str:
    return os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").strip()


def get_model() -> str:
    return os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()


def is_openrouter() -> bool:
    return "openrouter.ai" in get_base_url()


def get_provider_label() -> str:
    return "openrouter" if is_openrouter() else "openai"


def create_client():
    from openai import OpenAI

    key = get_api_key()
    if not key:
        raise ValueError("OPENAI_API_KEY or OPENROUTER_API_KEY not set in backend/.env")

    default_headers: dict[str, str] | None = None
    if is_openrouter():
        referer = os.getenv("OPENROUTER_HTTP_REFERER", "http://localhost:8000")
        title = os.getenv("OPENROUTER_APP_TITLE", "TrendWatch AI")
        default_headers = {
            "HTTP-Referer": referer,
            "X-Title": title,
        }

    return OpenAI(
        api_key=key,
        base_url=get_base_url(),
        default_headers=default_headers,
    )


def _extra_body() -> dict[str, Any] | None:
    if os.getenv("OPENAI_REASONING", "").strip().lower() in ("1", "true", "yes"):
        return {"reasoning": {"enabled": True}}
    return None


def _temperature() -> float | None:
    raw = os.getenv("OPENAI_TEMPERATURE", "0.3").strip()
    if not raw:
        return None
    return float(raw)


def chat_completion(
    *,
    messages: list[dict[str, Any]],
    max_tokens: int = 900,
    temperature: float | None = None,
) -> str:
    client = create_client()
    kwargs: dict[str, Any] = {
        "model": get_model(),
        "messages": messages,
        "max_tokens": max_tokens,
    }
    temp = _temperature() if temperature is None else temperature
    if temp is not None:
        kwargs["temperature"] = temp
    extra = _extra_body()
    if extra:
        kwargs["extra_body"] = extra

    resp = client.chat.completions.create(**kwargs)
    content = resp.choices[0].message.content
    if not content:
        raise ValueError("LLM returned empty content")
    return content
