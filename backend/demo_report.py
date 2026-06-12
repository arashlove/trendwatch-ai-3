from __future__ import annotations

import html
import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import quote

from report_charts import chart_img, generate_all_charts

SOURCE_LABELS = {
    "reddit_praw": "Live Reddit (PRAW API credentials)",
    "reddit_public_api": "Live Reddit (public search API)",
    "reddit_devvit_import": "Live Reddit (imported from Devvit app)",
    "reddit_devvit_new": "Live Reddit (Devvit new posts)",
    "reddit_devvit_best": "Live Reddit (Devvit front-page best)",
    "reddit_unavailable": "Reddit fetch unavailable",
    "unknown": "Unknown source",
}

TECHNIQUE_LABELS = {
    "preprocessing": "Preprocessing (tokenize, stem, lemmatize, URL removal)",
    "ner": "Named entity recognition (spaCy / NLTK)",
    "pos_tagging": "Part-of-speech tagging",
    "tfidf_logistic_regression": "TF-IDF + Logistic Regression classification",
    "sentiment_ensemble": "Sentiment ensemble (VADER + LR majority vote)",
    "embedding_clustering": "Embedding-based topic clustering (KMeans)",
    "regex_extraction": "Regex information extraction (hashtags, mentions, risk lexicon)",
    "temporal_trends": "Temporal trend analysis (daily volume & negative ratio)",
    "foundation_llm": "Foundation LLM (OpenAI-compatible briefing)",
    "rag": "Retrieval-augmented generation (top-k posts)",
    "prompt_engineering": "Prompt engineering (structured analyst template)",
    "chain_of_thought": "Chain-of-thought prompting",
    "llm_as_judge": "LLM-as-judge / automated evaluation",
    "ensemble_methods": "Ensemble methods (sentiment + multi-signal crisis)",
    "agentic_react": "Agentic ReAct-style orchestration",
    "ethics_disclaimer": "Ethics & fairness disclaimers",
}

TECHNIQUE_META: dict[str, dict[str, str]] = {
    "preprocessing": {
        "module": "preprocessing.py",
        "detail": "Merges title and selftext, removes URLs/HTML, lowercases, tokenizes with NLTK, then stems (Porter) and lemmatizes (WordNet). Output field: clean_text.",
        "section": "All downstream sections",
    },
    "ner": {
        "module": "ner_pos.py",
        "detail": "spaCy en_core_web_sm extracts ORG/PRODUCT/DATE entities; NLTK ne_chunk fallback if spaCy is unavailable. Corpus-level entity counts in §6.",
        "section": "§6 Named entities",
    },
    "pos_tagging": {
        "module": "ner_pos.py",
        "detail": "POS tags per token (spaCy or NLTK) stored on each post for linguistic analysis alongside NER.",
        "section": "§6 (with entities)",
    },
    "tfidf_logistic_regression": {
        "module": "classification.py",
        "detail": "TF-IDF (1–2 grams, max 5000 features) + Logistic Regression trained with weak VADER labels on the current corpus. Produces lr_label per post.",
        "section": "§3 Classifier comparison chart",
    },
    "sentiment_ensemble": {
        "module": "sentiment.py",
        "detail": "VADER compound thresholds combined with LR via majority vote; VADER+LR disagreement resolves to neutral. Final label drives crisis and trends.",
        "section": "§3 Sentiment donut + classifier bars",
    },
    "embedding_clustering": {
        "module": "topics.py, similarity.py",
        "detail": "Sentence-BERT MiniLM embeddings (TF-IDF fallback) clustered with KMeans; cluster labels from top keywords. Also powers semantic similarity pairs in §7.",
        "section": "§5 Topic clusters",
    },
    "regex_extraction": {
        "module": "extraction.py",
        "detail": "Regex pulls #hashtags, u/mentions, and ~30-term risk lexicon (exploit, lawsuit, boycott, …). Counts feed crisis scoring and §7 tables.",
        "section": "§7 Risk keywords",
    },
    "temporal_trends": {
        "module": "trends.py",
        "detail": "Aggregates posts by day: volume, negative ratio, risk-keyword count. Detects sentiment spikes vs corpus average for crisis component.",
        "section": "§4 Trend timeline",
    },
    "foundation_llm": {
        "module": "llm_report.py",
        "detail": "OpenAI-compatible chat API generates structured markdown briefing (Executive Summary, Concerns, Actions). Active when OPENAI_API_KEY is set.",
        "section": "§1 Executive briefing",
    },
    "rag": {
        "module": "rag.py",
        "detail": "Embeds post clean_text + query; cosine top-k retrieval supplies evidence snippets to the briefing prompt so outputs stay grounded in real posts.",
        "section": "§1 (context for briefing)",
    },
    "prompt_engineering": {
        "module": "llm_report.py",
        "detail": "Fixed analyst system prompt and markdown section template (## Executive Summary, ## Main Concerns, …) constrain LLM output format.",
        "section": "§1 briefing structure",
    },
    "chain_of_thought": {
        "module": "llm_report.py",
        "detail": "System prompt instructs step-by-step reasoning on sentiment, topics, and risk before the structured briefing sections are written.",
        "section": "§1 (LLM path)",
    },
    "llm_as_judge": {
        "module": "evaluation.py, benchmark_sentiment.py",
        "detail": "Optional LLM scores briefing clarity 0–100; heuristic judge without API key. Gold-set benchmark (data/sentiment_gold.json) reports Accuracy/P/R/F1 for VADER, LR, ensemble.",
        "section": "§10 Evaluation charts",
    },
    "ensemble_methods": {
        "module": "sentiment.py, crisis.py",
        "detail": "Two ensembles: (1) VADER+LR sentiment vote; (2) crisis score fuses negative %, risk keywords, high-engagement negatives, and trend spike (max 40+25+20+15 pts).",
        "section": "§2 Crisis gauge + §3 sentiment",
    },
    "agentic_react": {
        "module": "agent.py, pipeline.py",
        "detail": "ReAct-style loop logs thought → action → observation for collect, preprocess, extract, NER, sentiment, topics, trends, crisis, RAG, briefing. See trace table below.",
        "section": "§10 Agent trace (F19)",
    },
    "ethics_disclaimer": {
        "module": "llm_report.py, demo_report.py",
        "detail": "ETHICS_FOOTER appended to every briefing; §11 states public-data-only use, decision-support limits, and model bias caveats.",
        "section": "§11 Ethics",
    },
}


def _esc(value: Any) -> str:
    if value is None:
        return ""
    return html.escape(str(value))


def _technique_list(keys: list[str]) -> str:
    items: list[str] = []
    for key in keys:
        label = TECHNIQUE_LABELS.get(key, key.replace("_", " "))
        meta = TECHNIQUE_META.get(key, {})
        module = meta.get("module", "—")
        detail = meta.get("detail", "")
        section = meta.get("section", "")
        items.append(
            f'<li class="technique-item">'
            f"<strong>{_esc(label)}</strong>"
            f'<code class="technique-module">{_esc(module)}</code>'
            f'<p class="muted">{_esc(detail)}</p>'
            f'<p class="technique-ref">Output: {_esc(section)}</p>'
            f"</li>"
        )
    return "".join(items)


def _pct_bar(label: str, pct: float, color: str) -> str:
    width = max(0, min(100, float(pct)))
    return (
        f'<div class="bar-row"><span class="bar-label">{_esc(label)}</span>'
        f'<div class="bar-track"><div class="bar-fill {color}" style="width:{width}%"></div></div>'
        f'<span class="bar-pct">{width:.1f}%</span></div>'
    )


def _list_items(items: list[str]) -> str:
    if not items:
        return "<p><em>None identified.</em></p>"
    return "<ul>" + "".join(f"<li>{_esc(x)}</li>" for x in items if x) + "</ul>"


def _table(headers: list[str], rows: list[list[Any]]) -> str:
    if not rows:
        return "<p><em>No data.</em></p>"
    head = "".join(f"<th>{_esc(h)}</th>" for h in headers)
    body = ""
    for row in rows:
        body += "<tr>" + "".join(f"<td>{_esc(cell)}</td>" for cell in row) + "</tr>"
    return f'<table class="data-table"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def _markdown_block(text: str) -> str:
    if not text.strip():
        return "<p><em>No LLM markdown generated.</em></p>"
    lines = text.strip().splitlines()
    out: list[str] = []
    for line in lines:
        if line.startswith("## "):
            out.append(f"<h4>{_esc(line[3:].strip())}</h4>")
        elif line.startswith("# "):
            out.append(f"<h3>{_esc(line[2:].strip())}</h3>")
        elif line.startswith("- "):
            out.append(f"<li>{_esc(line[2:].strip())}</li>")
        elif line.strip():
            out.append(f"<p>{_esc(line)}</p>")
    html_body = "".join(out)
    if "<li>" in html_body:
        html_body = re.sub(r"(<li>.*?</li>)+", r"<ul>\g<0></ul>", html_body, flags=re.DOTALL)
    return f'<div class="markdown-block">{html_body}</div>'


def render_demo_report(
    result: dict[str, Any],
    *,
    query: str,
    subreddit: str,
    limit: int,
    time_filter: str,
) -> str:
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    s = result.get("summary", {})
    briefing = result.get("briefing", {})
    crisis = result.get("crisis", {})
    trends = result.get("trends", {})
    techniques = result.get("techniques_used", {})
    evaluation = result.get("evaluation", {})
    agent = result.get("agent_trace", {})
    source = SOURCE_LABELS.get(
        str(result.get("data_source", "unknown")),
        _esc(result.get("data_source", "unknown")),
    )

    pcts = s.get("sentiment_percentages", {})
    sentiment_rows = [
        [d.get("label", ""), d.get("count", 0)]
        for d in result.get("sentiment_distribution", [])
    ]

    trend_rows = [
        [
            t.get("date", ""),
            t.get("post_count", 0),
            t.get("negative_count", 0),
            f"{float(t.get('negative_ratio', 0)) * 100:.1f}%",
            t.get("risk_keyword_count", 0),
        ]
        for t in trends.get("timeline", [])
    ]

    topic_blocks = ""
    for topic in result.get("topics", []):
        rep = topic.get("representative_post") or {}
        topic_blocks += f"""
        <article class="topic-card">
          <h4>Topic {topic.get("topic_id", "")}: {_esc(topic.get("label", ""))}</h4>
          <p>Size: {topic.get("size", 0)} · Avg sentiment: <strong>{_esc(topic.get("average_sentiment", ""))}</strong></p>
          <p>Keywords: {_esc(", ".join(topic.get("keywords", [])))}</p>
          <p class="muted">Representative: {_esc(rep.get("title", "—"))}</p>
        </article>
        """

    entity_rows = [
        [e.get("entity", ""), e.get("count", 0)]
        for e in result.get("top_entities", [])[:15]
    ]
    risk_rows = [
        [r.get("keyword", ""), r.get("count", 0)]
        for r in result.get("risk_keywords", [])[:20]
    ]
    impact_rows = [
        [
            (p.get("title", "")[:80] + "…")
            if len(str(p.get("title", ""))) > 80
            else p.get("title", ""),
            p.get("subreddit", ""),
            p.get("score", 0),
            p.get("num_comments", 0),
            p.get("sentiment", ""),
            ", ".join(p.get("risk_keywords", [])[:4]) or "—",
            round(float(p.get("impact_score", 0)), 2),
        ]
        for p in result.get("high_impact_posts", [])[:15]
    ]
    post_rows = [
        [
            (p.get("title", "")[:70] + "…")
            if len(str(p.get("title", ""))) > 70
            else p.get("title", ""),
            p.get("author", ""),
            p.get("sentiment", ""),
            p.get("vader_label", ""),
            p.get("lr_label", ""),
            ", ".join(p.get("risk_keywords", [])[:3]) or "—",
        ]
        for p in result.get("posts", [])[:30]
    ]

    posts_by_id: dict[str, dict] = {}
    for p in result.get("posts", []):
        pid = str(p.get("id", ""))
        if pid:
            posts_by_id[pid] = p
    for p in result.get("high_impact_posts", []):
        pid = str(p.get("id", ""))
        if pid and pid not in posts_by_id:
            posts_by_id[pid] = p

    similar_rows: list[list[Any]] = []
    for pair in result.get("similar_pairs", [])[:10]:
        if not isinstance(pair, dict):
            continue
        post_a = posts_by_id.get(str(pair.get("post_a_id", "")), {})
        post_b = posts_by_id.get(str(pair.get("post_b_id", "")), {})
        title_a = post_a.get("title") or pair.get("post_a_id", "?")
        title_b = post_b.get("title") or pair.get("post_b_id", "?")
        similar_rows.append(
            [
                str(title_a)[:55],
                str(title_b)[:55],
                pair.get("similarity", 0),
            ]
        )

    components = crisis.get("components", {})
    component_rows = [[k, round(float(v), 2)] for k, v in components.items()]

    basic = techniques.get("basic", [])
    advanced = techniques.get("advanced", [])
    if "temporal_trends" not in basic:
        basic = [*basic, "temporal_trends"]
    basic_list = _technique_list(basic)
    advanced_list = _technique_list(advanced)
    briefing_source = briefing.get("source", "unknown")
    if briefing_source == "llm_cot":
        briefing_source_note = "LLM-generated (OpenAI API — RAG + chain-of-thought)"
    elif briefing_source == "llm_error_fallback":
        briefing_source_note = (
            f"Rule-based fallback — OpenAI call failed: {briefing.get('llm_error', 'unknown error')}"
        )
    else:
        briefing_source_note = "Rule-based fallback (set OPENAI_API_KEY in backend/.env for LLM briefing)"

    steps = agent.get("steps", [])
    trace_rows = [
        [i + 1, step.get("thought", ""), step.get("action", ""), step.get("observation", "")]
        for i, step in enumerate(steps)
    ]

    sent_eval = evaluation.get("sentiment", {})
    judge = evaluation.get("briefing_judge", {})

    json_url = (
        f"/analyze?query={quote(query)}&subreddit={quote(subreddit)}"
        f"&limit={limit}&time_filter={quote(time_filter)}"
    )

    risk_class = {
        "Low": "risk-low",
        "Medium": "risk-med",
        "High": "risk-high",
        "Critical": "risk-crit",
    }.get(str(s.get("risk_level", "")), "")

    charts = generate_all_charts(result)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>TrendWatch AI Report — {_esc(query)}</title>
  <style>
    :root {{
      --brand: #d93900;
      --bg: #f8f9fa;
      --card: #fff;
      --text: #1a1a1a;
      --muted: #5c5c5c;
      --border: #e2e4e8;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      font-family: "Segoe UI", system-ui, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.55;
      margin: 0;
      padding: 0;
    }}
    .wrap {{ max-width: 960px; margin: 0 auto; padding: 1.5rem 1.25rem 3rem; }}
    header.report-header {{
      background: linear-gradient(135deg, #1a1a1a 0%, #3d2318 100%);
      color: #fff;
      padding: 2rem 1.25rem;
      margin-bottom: 1.5rem;
    }}
    header.report-header h1 {{ color: var(--brand); margin: 0 0 0.5rem; font-size: 1.75rem; }}
    header.report-header .meta {{ opacity: 0.9; font-size: 0.9rem; }}
    .badge {{
      display: inline-block;
      background: rgba(255,255,255,0.15);
      padding: 0.25rem 0.6rem;
      border-radius: 4px;
      margin: 0.25rem 0.25rem 0 0;
      font-size: 0.85rem;
    }}
    nav.toc {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 1rem 1.25rem;
      margin-bottom: 1.5rem;
    }}
    nav.toc ol {{ margin: 0.5rem 0 0; padding-left: 1.25rem; }}
    nav.toc a {{ color: var(--brand); }}
    section.card {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 1.25rem 1.5rem;
      margin-bottom: 1.25rem;
    }}
    section.card h2 {{
      color: var(--brand);
      font-size: 1.2rem;
      margin: 0 0 1rem;
      padding-bottom: 0.5rem;
      border-bottom: 2px solid var(--border);
    }}
    section.card h3 {{ font-size: 1rem; margin: 1rem 0 0.5rem; }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
      gap: 0.75rem;
      margin: 1rem 0;
    }}
    .metric {{
      background: var(--bg);
      border-radius: 6px;
      padding: 0.75rem;
      text-align: center;
    }}
    .metric .val {{ font-size: 1.5rem; font-weight: 700; }}
    .metric .lbl {{ font-size: 0.75rem; color: var(--muted); text-transform: uppercase; }}
    .crisis-big {{ font-size: 2rem; font-weight: 800; }}
    .risk-low {{ color: #15803d; }}
    .risk-med {{ color: #a16207; }}
    .risk-high {{ color: #c2410c; }}
    .risk-crit {{ color: #b91c1c; }}
    .data-table {{ width: 100%; border-collapse: collapse; font-size: 0.88rem; }}
    .data-table th, .data-table td {{
      border: 1px solid var(--border);
      padding: 0.45rem 0.6rem;
      text-align: left;
      vertical-align: top;
    }}
    .data-table th {{ background: var(--bg); }}
    .bar-row {{ display: flex; align-items: center; gap: 0.5rem; margin: 0.35rem 0; }}
    .bar-label {{ width: 4.5rem; font-size: 0.85rem; }}
    .bar-track {{ flex: 1; height: 1rem; background: #eee; border-radius: 4px; overflow: hidden; }}
    .bar-fill {{ height: 100%; }}
    .bar-fill.pos {{ background: #22c55e; }}
    .bar-fill.neu {{ background: #94a3b8; }}
    .bar-fill.neg {{ background: #ef4444; }}
    .bar-pct {{ width: 3rem; text-align: right; font-size: 0.85rem; }}
    .topic-card {{
      background: var(--bg);
      border-radius: 6px;
      padding: 0.75rem 1rem;
      margin: 0.5rem 0;
    }}
    .topic-card h4 {{ margin: 0 0 0.35rem; font-size: 0.95rem; }}
    .muted {{ color: var(--muted); font-size: 0.88rem; }}
    .two-col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }}
    .technique-list {{ list-style: none; padding: 0; margin: 0; }}
    .technique-item {{
      list-style: none;
      margin: 0 0 1rem;
      padding: 0.75rem 0.9rem;
      background: var(--bg);
      border-radius: 6px;
      border-left: 3px solid var(--brand);
    }}
    .technique-item strong {{ display: block; margin-bottom: 0.25rem; }}
    .technique-module {{
      font-size: 0.78rem;
      background: #fff;
      border: 1px solid var(--border);
      padding: 0.1rem 0.35rem;
      border-radius: 4px;
    }}
    .technique-ref {{ font-size: 0.8rem; color: var(--brand); margin: 0.35rem 0 0; }}
    .technique-intro {{
      background: #fff7ed;
      border: 1px solid #fed7aa;
      border-radius: 6px;
      padding: 0.85rem 1rem;
      margin-bottom: 1rem;
      font-size: 0.9rem;
    }}
    @media (max-width: 700px) {{ .two-col, .chart-grid {{ grid-template-columns: 1fr; }} }}
    .chart-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1rem;
      margin: 1rem 0;
    }}
    .chart-full {{ grid-column: 1 / -1; }}
    .chart-img {{
      width: 100%;
      height: auto;
      display: block;
      border: 1px solid var(--border);
      border-radius: 8px;
      background: #fff;
    }}
    .chart-caption {{
      font-size: 0.8rem;
      color: var(--muted);
      margin-top: 0.35rem;
    }}
    .toolbar {{
      position: sticky;
      top: 0;
      background: var(--card);
      border-bottom: 1px solid var(--border);
      padding: 0.5rem 1rem;
      display: flex;
      gap: 0.75rem;
      flex-wrap: wrap;
      z-index: 10;
    }}
    .toolbar a, .toolbar button {{
      font-size: 0.85rem;
      color: var(--brand);
      background: none;
      border: 1px solid var(--brand);
      border-radius: 4px;
      padding: 0.35rem 0.75rem;
      cursor: pointer;
      text-decoration: none;
    }}
    .toolbar button:hover, .toolbar a:hover {{ background: #fff5f2; }}
    @media print {{
      .toolbar {{ display: none; }}
      section.card {{ break-inside: avoid; }}
      body {{ background: #fff; }}
    }}
  </style>
</head>
<body>
  <div class="toolbar">
    <button type="button" onclick="window.print()">Print / Save as PDF</button>
    <a href="{json_url}">Download JSON</a>
    <a href="/">API home</a>
  </div>

  <header class="report-header">
    <div class="wrap">
      <h1>TrendWatch AI — Social Media Intelligence Report</h1>
      <p class="meta">
        <strong>Use Case 2:</strong> Brand monitoring on Reddit · Generated {generated}
      </p>
      <p class="meta">
        <span class="badge">Query: {_esc(query)}</span>
        <span class="badge">r/{_esc(subreddit)}</span>
        <span class="badge">Limit: {limit}</span>
        <span class="badge">Time: {_esc(time_filter)}</span>
        <span class="badge">Data: {_esc(source)}</span>
      </p>
    </div>
  </header>

  <div class="wrap">
    <nav class="toc card">
      <strong>Report contents (assignment sections)</strong>
      <ol>
        <li><a href="#briefing">Executive briefing (LLM / fallback)</a></li>
        <li><a href="#crisis">Crisis intelligence score</a></li>
        <li><a href="#overview">Overview & sentiment</a></li>
        <li><a href="#trends">Trend detection</a></li>
        <li><a href="#topics">Topic clusters</a></li>
        <li><a href="#entities">NER — top entities</a></li>
        <li><a href="#risk">Risk keywords & high-impact posts</a></li>
        <li><a href="#posts">Post-level analysis</a></li>
        <li><a href="#techniques">NLP techniques demonstrated</a></li>
        <li><a href="#agent">Agent trace & evaluation</a></li>
        <li><a href="#ethics">Ethics & limitations</a></li>
      </ol>
    </nav>

    <section id="briefing" class="card">
      <h2>1. Executive briefing</h2>
      <p class="muted">Source: <strong>{_esc(briefing.get("source", "unknown"))}</strong> · {_esc(briefing_source_note)}</p>
      {f'<p class="muted" style="color:#b91c1c">LLM error: {_esc(briefing.get("llm_error", ""))}</p>' if briefing.get("llm_error") else ""}
      <h3>Executive summary</h3>
      <p>{_esc(briefing.get("executive_summary", ""))}</p>
      <h3>Main concerns</h3>
      {_list_items(briefing.get("main_concerns", []))}
      <h3>Crisis explanation</h3>
      <p>{_esc(briefing.get("crisis_explanation", ""))}</p>
      <h3>Recommended actions</h3>
      {_list_items(briefing.get("recommended_actions", []))}
      <h3>Communication strategy</h3>
      <p>{_esc(briefing.get("communication_strategy", ""))}</p>
      <h3>Full LLM report (markdown)</h3>
      {_markdown_block(result.get("llm_report", ""))}
    </section>

    <section id="crisis" class="card">
      <h2>2. Crisis intelligence layer</h2>
      <div class="chart-grid">
        <div class="chart-full">
          {chart_img(charts["crisis"], alt="Crisis score gauge and component breakdown")}
        </div>
      </div>
      <p class="crisis-big {risk_class}">
        {_esc(s.get("crisis_score", 0))}/100 — {_esc(s.get("risk_level", ""))} risk
      </p>
      <p>Weighted fusion of negative sentiment, risk keywords, high-engagement negative posts, and trend spikes.</p>
      <h3>Score components</h3>
      {_table(["Component", "Points"], component_rows)}
      <h3>Reasons</h3>
      {_list_items(crisis.get("reasons", []))}
    </section>

    <section id="overview" class="card">
      <h2>3. Overview & sentiment analysis</h2>
      <div class="metrics">
        <div class="metric"><div class="val">{s.get("total_posts", 0)}</div><div class="lbl">Posts analysed</div></div>
        <div class="metric"><div class="val">{pcts.get("positive", 0)}%</div><div class="lbl">Positive</div></div>
        <div class="metric"><div class="val">{pcts.get("neutral", 0)}%</div><div class="lbl">Neutral</div></div>
        <div class="metric"><div class="val">{pcts.get("negative", 0)}%</div><div class="lbl">Negative</div></div>
      </div>
      <div class="chart-grid">
        <div>
          {chart_img(charts["overview_sentiment"], alt="Sentiment distribution donut chart")}
          <p class="chart-caption">Final labels after VADER + LR ensemble majority vote.</p>
        </div>
        <div>
          {chart_img(charts["overview_classifiers"], alt="VADER vs logistic regression comparison")}
          <p class="chart-caption">Independent classifier outputs before ensemble fusion.</p>
        </div>
      </div>
      <h3>Sentiment distribution (VADER + LR ensemble)</h3>
      {_pct_bar("Positive", pcts.get("positive", 0), "pos")}
      {_pct_bar("Neutral", pcts.get("neutral", 0), "neu")}
      {_pct_bar("Negative", pcts.get("negative", 0), "neg")}
      {_table(["Label", "Count"], sentiment_rows)}
      <p class="muted">
        Counts: positive={s.get("positive", 0)}, neutral={s.get("neutral", 0)}, negative={s.get("negative", 0)}
      </p>
    </section>

    <section id="trends" class="card">
      <h2>4. Trend detection</h2>
      <div class="chart-grid">
        <div class="chart-full">
          {chart_img(charts["trends"], alt="Trend timeline chart")}
          <p class="chart-caption">Daily post volume (bars), negative sentiment % (line), and risk keyword counts (dashed).</p>
        </div>
      </div>
      <p><strong>Spike detected:</strong> {"Yes" if trends.get("spike_detected") else "No"}
        — {_esc(trends.get("spike_message", ""))}</p>
      <p><strong>Average negative ratio:</strong> {float(trends.get("avg_negative_ratio", 0)) * 100:.1f}%</p>
      {_table(
        ["Date", "Posts", "Negative", "Neg %", "Risk keywords"],
        trend_rows,
      )}
    </section>

    <section id="topics" class="card">
      <h2>5. Topic clusters (embeddings + KMeans)</h2>
      <div class="chart-grid">
        <div class="chart-full">
          {chart_img(charts["topics"], alt="Topic cluster sizes chart")}
        </div>
      </div>
      {topic_blocks if topic_blocks else "<p><em>Not enough posts for clustering.</em></p>"}
    </section>

    <section id="entities" class="card">
      <h2>6. Named entities (NER)</h2>
      <div class="chart-grid">
        <div class="chart-full">
          {chart_img(charts["entities"], alt="Top named entities chart")}
        </div>
      </div>
      {_table(["Entity", "Mentions"], entity_rows)}
    </section>

    <section id="risk" class="card">
      <h2>7. Risk keywords & high-impact posts</h2>
      <div class="chart-grid">
        <div>
          {chart_img(charts["risk_keywords"], alt="Risk keyword frequency chart")}
        </div>
        <div>
          {chart_img(charts["similarity"], alt="Similar post pairs chart")}
        </div>
      </div>
      <div class="chart-grid">
        <div class="chart-full">
          {chart_img(charts["high_impact"], alt="High impact posts chart")}
        </div>
      </div>
      <div class="two-col">
        <div>
          <h3>Risk keyword frequency</h3>
          {_table(["Keyword", "Count"], risk_rows)}
        </div>
        <div>
          <h3>Similar post pairs (cosine similarity)</h3>
          {_table(["Post A", "Post B", "Similarity"], similar_rows)}
        </div>
      </div>
      <h3>High-impact posts</h3>
      {_table(
        ["Title", "Subreddit", "Score", "Comments", "Sentiment", "Risk terms", "Impact"],
        impact_rows,
      )}
    </section>

    <section id="posts" class="card">
      <h2>8. Post-level analysis (sample)</h2>
      <p class="muted">Showing up to 30 posts with VADER label, LR label, and extracted risk terms.</p>
      {_table(
        ["Title", "Author", "Ensemble", "VADER", "LR", "Risk terms"],
        post_rows,
      )}
    </section>

    <section id="techniques" class="card">
      <h2>9. NLP techniques demonstrated (rubric)</h2>
      <div class="technique-intro">
        <p><strong>All techniques below are implemented and executed in one pipeline run</strong>
        (<code>agent.py</code> → <code>pipeline.py</code>). This report used
        <strong>{_esc(briefing_source_note)}</strong> for §1.
        Advanced layers (RAG, ReAct trace, evaluation) are detailed in §10; ethics in §11.</p>
        <p class="muted">Run <code>backend/benchmark_sentiment.py</code> on
        <code>data/sentiment_gold.json</code> for human gold-set Accuracy / Precision / Recall / F1.</p>
      </div>
      <p>Minimum <strong>3 basic + 3 advanced</strong> — we demonstrate
        <strong>{len(basic)} basic</strong> and <strong>{len(advanced)} advanced</strong>
        with module mapping for audit and reproduction.</p>
      <div class="two-col">
        <div>
          <h3>Basic techniques</h3>
          <ul class="technique-list">{basic_list}</ul>
        </div>
        <div>
          <h3>Advanced techniques</h3>
          <ul class="technique-list">{advanced_list}</ul>
        </div>
      </div>
    </section>

    <section id="agent" class="card">
      <h2>10. Agent orchestration & evaluation</h2>
      <div class="chart-grid">
        <div>
          {chart_img(charts["agent"], alt="Agent pipeline trace chart")}
        </div>
        <div>
          {chart_img(charts["evaluation"], alt="Evaluation metrics chart")}
        </div>
      </div>
      <p><strong>Agent status:</strong> {_esc(agent.get("status", ""))}</p>
      <h3>ReAct-style trace</h3>
      {_table(["Step", "Thought", "Action", "Observation"], trace_rows)}
      <h3>Automated evaluation</h3>
      <p><strong>Sentiment agreement (VADER vs LR):</strong>
        {float(sent_eval.get("sentiment_agreement", 0)) * 100:.1f}% — {_esc(sent_eval.get("notes", ""))}</p>
      <p><strong>Briefing judge score:</strong> {judge.get("score", "—")}/100
        ({_esc(judge.get("source", ""))})</p>
      <p>{_esc(judge.get("feedback", ""))}</p>
    </section>

    <section id="ethics" class="card">
      <h2>11. Ethics, limitations & references</h2>
      <p>{_esc(briefing.get("ethics_notice", ""))}</p>
      <ul>
        <li>Public Reddit text only; no private user data.</li>
        <li>Crisis scores are decision-support estimates, not legal or PR advice.</li>
        <li>Sentiment models can misclassify sarcasm and domain-specific language.</li>
        <li>Gold-set benchmark: <code>backend/benchmark_sentiment.py</code> +
        <code>data/sentiment_gold.json</code> (20 labelled posts).</li>
        <li>Full NLP technique reference: <code>docs/NLP_TECHNIQUES.md</code></li>
      </ul>
      <p class="muted">
        TrendWatch AI · Devvit Web + Python FastAPI ·
        <a href="{json_url}">Raw JSON</a>
      </p>
    </section>
  </div>
</body>
</html>"""
