"""TrendWatch AI — FastAPI NLP backend."""

import json

from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field, ValidationError

from demo_report import render_demo_report
from pipeline import run_analysis_on_posts, run_full_analysis
from reddit_client import search_reddit
from upload_page import render_upload_page

app = FastAPI(
    title="TrendWatch AI",
    description="Full NLP pipeline for Devvit hybrid reports",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ReportRequest(BaseModel):
    query: str = ""
    subreddit: str = "all"
    posts: list[dict] = Field(default_factory=list)


def _report_html(body: ReportRequest) -> str:
    if len(body.posts) < 5:
        raise HTTPException(status_code=400, detail="Need at least 5 posts")

    result = run_analysis_on_posts(
        body.posts,
        query=body.query,
        subreddit=body.subreddit,
    )
    return render_demo_report(
        result,
        query=body.query or "(all posts)",
        subreddit=body.subreddit,
        limit=len(body.posts),
        time_filter="devvit_import",
    )


@app.get("/", response_class=HTMLResponse)
def home():
    return HTMLResponse(render_upload_page())


@app.get("/upload", response_class=HTMLResponse)
def upload_form():
    return HTMLResponse(render_upload_page())


@app.get("/health")
def health():
    return {"status": "ok"}


def _parse_report_bytes(raw: bytes) -> ReportRequest:
    payload = json.loads(raw.decode("utf-8"))
    return ReportRequest.model_validate(payload)


@app.post("/upload", response_class=HTMLResponse)
async def upload_report(
    file: UploadFile | None = File(None),
    paste_json: str | None = Form(None),
):
    """Accept pasted or uploaded JSON from Devvit Step 3."""
    raw: bytes | None = None
    if file is not None and file.filename:
        raw = await file.read()
    elif paste_json and paste_json.strip():
        raw = paste_json.encode("utf-8")

    if raw is None:
        return HTMLResponse(
            render_upload_page(error="Paste JSON or choose a .json file."),
            status_code=400,
        )

    try:
        body = _parse_report_bytes(raw)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return HTMLResponse(
            render_upload_page(error="Invalid JSON — copy again from Step 3 in the Devvit app."),
            status_code=400,
        )
    except ValidationError as exc:
        return HTMLResponse(
            render_upload_page(error=f"Invalid report format: {exc.errors()[0]['msg']}"),
            status_code=400,
        )

    try:
        html = _report_html(body)
        return HTMLResponse(html)
    except HTTPException:
        raise
    except Exception as exc:
        return HTMLResponse(
            render_upload_page(error=str(exc)),
            status_code=500,
        )


@app.post("/report", response_class=HTMLResponse)
def report(body: ReportRequest):
    """Programmatic JSON POST (local tools only — not usable from reddit.com)."""
    try:
        html = _report_html(body)
        return HTMLResponse(html)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/search")
def search(
    query: str = Query(..., min_length=1),
    subreddit: str = "all",
    limit: int = Query(25, ge=5, le=100),
    time_filter: str = "month",
):
    posts = search_reddit(query, subreddit=subreddit, limit=limit, time_filter=time_filter)
    return {"query": query, "count": len(posts), "posts": posts}


@app.get("/analyze")
def analyze(
    query: str = Query(..., min_length=1),
    subreddit: str = "all",
    limit: int = Query(40, ge=10, le=100),
    time_filter: str = "month",
):
    try:
        return run_full_analysis(
            query, subreddit=subreddit, limit=limit, time_filter=time_filter
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/demo", response_class=HTMLResponse)
def demo(
    query: str = Query(..., min_length=1),
    subreddit: str = "all",
    limit: int = Query(40, ge=10, le=100),
    time_filter: str = "month",
):
    """Standalone HTML report (fetches Reddit directly — requires API keys or public API)."""
    try:
        result = run_full_analysis(
            query, subreddit=subreddit, limit=limit, time_filter=time_filter
        )
        html = render_demo_report(
            result,
            query=query,
            subreddit=subreddit,
            limit=limit,
            time_filter=time_filter,
        )
        return HTMLResponse(html)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
