"""Matplotlib charts embedded as base64 PNG in the HTML assignment report."""

from __future__ import annotations

import base64
import io
from collections import Counter
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Wedge

BRAND = "#d93900"
POS = "#22c55e"
NEU = "#64748b"
NEG = "#ef4444"
BG = "#fafafa"
GRID = "#e2e8f0"

plt.rcParams.update(
    {
        "figure.facecolor": BG,
        "axes.facecolor": "#ffffff",
        "axes.edgecolor": GRID,
        "axes.labelcolor": "#334155",
        "axes.titleweight": "bold",
        "axes.titlesize": 11,
        "axes.labelsize": 9,
        "xtick.color": "#475569",
        "ytick.color": "#475569",
        "grid.color": GRID,
        "grid.alpha": 0.6,
        "font.family": "sans-serif",
        "font.sans-serif": ["Segoe UI", "DejaVu Sans", "Arial"],
    }
)


def _fig_to_data_uri(fig: plt.Figure) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=140, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    encoded = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def _empty_chart(title: str, message: str = "Insufficient data") -> str:
    fig, ax = plt.subplots(figsize=(6.5, 3.2))
    ax.set_axis_off()
    ax.text(0.5, 0.55, title, ha="center", va="center", fontsize=12, fontweight="bold")
    ax.text(0.5, 0.35, message, ha="center", va="center", fontsize=10, color="#64748b")
    return _fig_to_data_uri(fig)


def chart_sentiment_distribution(result: dict[str, Any]) -> str:
    pcts = result.get("summary", {}).get("sentiment_percentages", {})
    labels = ["Positive", "Neutral", "Negative"]
    keys = ["positive", "neutral", "negative"]
    values = [float(pcts.get(k, 0)) for k in keys]
    if sum(values) <= 0:
        return _empty_chart("Sentiment distribution")

    colors = [POS, NEU, NEG]
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels,
        colors=colors,
        autopct=lambda p: f"{p:.1f}%" if p > 0 else "",
        startangle=90,
        pctdistance=0.78,
        wedgeprops={"width": 0.45, "edgecolor": "white", "linewidth": 2},
    )
    for t in autotexts:
        t.set_fontsize(9)
        t.set_fontweight("bold")
    ax.set_title("Sentiment distribution (ensemble)")
    centre = plt.Circle((0, 0), 0.35, fc="white")
    ax.add_artist(centre)
    total = result.get("summary", {}).get("total_posts", 0)
    ax.text(0, 0, f"{total}\nposts", ha="center", va="center", fontsize=10, fontweight="bold")
    return _fig_to_data_uri(fig)


def chart_vader_lr_comparison(posts: list[dict]) -> str:
    if not posts:
        return _empty_chart("VADER vs Logistic Regression")

    labels = ["positive", "neutral", "negative"]
    vader = Counter(str(p.get("vader_label", "neutral")) for p in posts)
    lr = Counter(str(p.get("lr_label", "neutral")) for p in posts)

    x = np.arange(len(labels))
    width = 0.35
    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    ax.bar(x - width / 2, [vader.get(l, 0) for l in labels], width, label="VADER", color="#3b82f6")
    ax.bar(x + width / 2, [lr.get(l, 0) for l in labels], width, label="TF-IDF + LR", color=BRAND)
    ax.set_xticks(x)
    ax.set_xticklabels([l.title() for l in labels])
    ax.set_ylabel("Post count")
    ax.set_title("Classifier comparison (before ensemble vote)")
    ax.legend(frameon=False, loc="upper right")
    ax.yaxis.grid(True, linestyle="--")
    ax.set_axisbelow(True)
    return _fig_to_data_uri(fig)


def chart_crisis_score(result: dict[str, Any]) -> str:
    crisis = result.get("crisis", {})
    score = int(crisis.get("crisis_score", 0))
    level = str(crisis.get("risk_level", "Low"))
    components = crisis.get("components", {})
    if not components:
        return _empty_chart("Crisis intelligence score")

    level_colors = {
        "Low": "#22c55e",
        "Medium": "#eab308",
        "High": "#f97316",
        "Critical": "#ef4444",
    }
    accent = level_colors.get(level, BRAND)

    fig, (ax_gauge, ax_comp) = plt.subplots(
        1,
        2,
        figsize=(8.5, 3.2),
        gridspec_kw={"width_ratios": [1, 1.35], "wspace": 0.5},
    )

    # --- Speedometer gauge (compact, hub at baseline) ---
    ax_gauge.set_aspect("equal")
    ax_gauge.set_xlim(-1.1, 1.1)
    ax_gauge.set_ylim(-0.42, 0.95)
    ax_gauge.axis("off")

    radius = 0.78
    band = 0.16
    zones = [
        (0, 30, "#dcfce7"),
        (30, 60, "#fef9c3"),
        (60, 80, "#ffedd5"),
        (80, 100, "#fee2e2"),
    ]
    for lo, hi, fill in zones:
        theta2 = 180 - lo * 1.8
        theta1 = 180 - hi * 1.8
        ax_gauge.add_patch(
            Wedge(
                (0, 0),
                radius,
                theta1,
                theta2,
                width=band,
                facecolor=fill,
                edgecolor="#ffffff",
                linewidth=1.2,
            )
        )

    track = np.linspace(np.pi, 0, 200)
    ax_gauge.plot(
        radius * np.cos(track),
        radius * np.sin(track),
        color="#94a3b8",
        linewidth=1.5,
        zorder=3,
    )

    needle_rad = np.pi * (1 - score / 100)
    ax_gauge.annotate(
        "",
        xy=(0.68 * radius * np.cos(needle_rad), 0.68 * radius * np.sin(needle_rad)),
        xytext=(0, 0),
        arrowprops=dict(arrowstyle="-|>", color=accent, lw=2.2, mutation_scale=11),
        zorder=4,
    )
    ax_gauge.scatter(
        [0],
        [0],
        s=48,
        color="#1e293b",
        zorder=5,
        edgecolors="#ffffff",
        linewidths=1.2,
    )

    ax_gauge.text(0, 0.88, "Crisis score", ha="center", fontsize=11, fontweight="bold", color="#334155")
    ax_gauge.text(0, -0.1, str(score), ha="center", fontsize=26, fontweight="bold", color=accent)
    ax_gauge.text(0, -0.3, f"/ 100  ·  {level} risk", ha="center", fontsize=9, color="#64748b")

    # --- Component bars (sorted, thicker, fixed x-scale) ---
    items = sorted(
        [(k.replace("_", " ").title(), float(v)) for k, v in components.items()],
        key=lambda x: x[1],
        reverse=True,
    )
    names = [item[0] for item in items]
    vals = [item[1] for item in items]
    color_map = {
        "Negative Sentiment": NEG,
        "Risk Keywords": "#f97316",
        "Engagement": "#eab308",
        "Trend Spike": "#8b5cf6",
    }
    bar_colors = [color_map.get(name, "#64748b") for name in names]

    y = np.arange(len(names))
    ax_comp.barh(y, vals, color=bar_colors, height=0.58, edgecolor="#ffffff", linewidth=0.8)
    ax_comp.set_yticks(y)
    ax_comp.set_yticklabels(names, fontsize=9)
    ax_comp.set_xlim(0, 25)
    ax_comp.set_xlabel("Points contributed (max 40 / 25 / 20 / 15)", fontsize=8)
    ax_comp.set_title("Score components", fontsize=11, fontweight="bold", pad=6)
    ax_comp.invert_yaxis()
    ax_comp.spines["top"].set_visible(False)
    ax_comp.spines["right"].set_visible(False)
    ax_comp.xaxis.grid(True, linestyle="--", alpha=0.65)
    ax_comp.set_axisbelow(True)
    for i, v in enumerate(vals):
        ax_comp.text(
            min(v + 0.4, 24),
            i,
            f"{v:.1f}",
            va="center",
            fontsize=9,
            color="#334155",
        )

    fig.subplots_adjust(left=0.05, right=0.98, top=0.9, bottom=0.14)
    return _fig_to_data_uri(fig)


def chart_trends_timeline(trends: dict[str, Any]) -> str:
    timeline = trends.get("timeline", [])
    timeline = [t for t in timeline if t.get("date") != "unknown"]
    if not timeline:
        return _empty_chart("Trend timeline")

    dates = [t["date"][5:] if len(t["date"]) >= 5 else t["date"] for t in timeline]
    posts = [t.get("post_count", 0) for t in timeline]
    neg_pct = [float(t.get("negative_ratio", 0)) * 100 for t in timeline]
    risk = [t.get("risk_keyword_count", 0) for t in timeline]

    fig, ax1 = plt.subplots(figsize=(7.5, 4))
    x = np.arange(len(dates))
    ax1.bar(x, posts, color="#cbd5e1", label="Post volume", width=0.65)
    ax1.set_ylabel("Posts per day")
    ax1.set_xticks(x)
    ax1.set_xticklabels(dates, rotation=45, ha="right", fontsize=8)
    ax1.set_title("Volume, negative sentiment & risk keywords over time")

    ax2 = ax1.twinx()
    ax2.plot(x, neg_pct, color=NEG, marker="o", linewidth=2, label="Negative %")
    ax2.plot(x, risk, color=BRAND, marker="s", linewidth=1.8, linestyle="--", label="Risk keywords")
    ax2.set_ylabel("Negative % / risk count")
    ax2.set_ylim(bottom=0)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", frameon=False, fontsize=8)
    ax1.grid(True, axis="y", linestyle="--", alpha=0.5)
    ax1.set_axisbelow(True)
    fig.tight_layout()
    return _fig_to_data_uri(fig)


def chart_topics(topics: list[dict]) -> str:
    if not topics:
        return _empty_chart("Topic clusters")

    labels = [f"T{t.get('topic_id', i)+1}" for i, t in enumerate(topics[:8])]
    sizes = [t.get("size", 0) for t in topics[:8]]
    sentiments = [str(t.get("average_sentiment", "neutral")) for t in topics[:8]]
    sent_colors = {"positive": POS, "neutral": NEU, "negative": NEG}
    colors = [sent_colors.get(s, NEU) for s in sentiments]

    fig, ax = plt.subplots(figsize=(7, max(3.5, len(labels) * 0.45)))
    y = np.arange(len(labels))
    ax.barh(y, sizes, color=colors, height=0.6)
    ax.set_yticks(y)
    full_labels = [
        f"{labels[i]} — {topics[i].get('label', '')[:28]}"
        for i in range(len(labels))
    ]
    ax.set_yticklabels(full_labels, fontsize=8)
    ax.set_xlabel("Posts in cluster")
    ax.set_title("Topic clusters (embedding + KMeans) — colour = dominant sentiment")
    ax.xaxis.grid(True, linestyle="--")
    ax.set_axisbelow(True)
    for i, v in enumerate(sizes):
        ax.text(v + 0.2, i, str(v), va="center", fontsize=8)
    fig.tight_layout()
    return _fig_to_data_uri(fig)


def chart_entities(entities: list[dict]) -> str:
    if not entities:
        return _empty_chart("Named entities (NER)")

    items = entities[:12]
    names = [str(e.get("entity", ""))[:32] for e in items]
    counts = [e.get("count", 0) for e in items]

    fig, ax = plt.subplots(figsize=(7, max(3.5, len(names) * 0.4)))
    y = np.arange(len(names))
    ax.barh(y, counts, color="#6366f1", height=0.6)
    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel("Mentions across corpus")
    ax.set_title("Top named entities (spaCy / NLTK NER)")
    ax.xaxis.grid(True, linestyle="--")
    ax.set_axisbelow(True)
    fig.tight_layout()
    return _fig_to_data_uri(fig)


def chart_risk_keywords(risk_keywords: list[dict]) -> str:
    if not risk_keywords:
        return _empty_chart("Risk keyword frequency")

    items = risk_keywords[:15]
    words = [str(r.get("keyword", "")) for r in items]
    counts = [r.get("count", 0) for r in items]

    fig, ax = plt.subplots(figsize=(6.5, max(3.5, len(words) * 0.35)))
    y = np.arange(len(words))
    ax.barh(y, counts, color=NEG, height=0.62, alpha=0.85)
    ax.set_yticks(y)
    ax.set_yticklabels(words, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel("Occurrences")
    ax.set_title("Brand-risk lexicon matches (regex IE)")
    ax.xaxis.grid(True, linestyle="--")
    ax.set_axisbelow(True)
    fig.tight_layout()
    return _fig_to_data_uri(fig)


def chart_high_impact(posts: list[dict]) -> str:
    if not posts:
        return _empty_chart("High-impact posts")

    items = posts[:10]
    titles = [
        (str(p.get("title", ""))[:36] + "…")
        if len(str(p.get("title", ""))) > 36
        else str(p.get("title", ""))
        for p in items
    ]
    scores = [float(p.get("impact_score", 0)) for p in items]
    colors = [
        NEG if p.get("sentiment") == "negative" else POS if p.get("sentiment") == "positive" else NEU
        for p in items
    ]

    fig, ax = plt.subplots(figsize=(7.5, max(3.8, len(titles) * 0.42)))
    y = np.arange(len(titles))
    ax.barh(y, scores, color=colors, height=0.6)
    ax.set_yticks(y)
    ax.set_yticklabels(titles, fontsize=7)
    ax.invert_yaxis()
    ax.set_xlabel("Impact score (engagement × sentiment weight)")
    ax.set_title("High-impact posts")
    ax.xaxis.grid(True, linestyle="--")
    ax.set_axisbelow(True)
    fig.tight_layout()
    return _fig_to_data_uri(fig)


def chart_similar_pairs(similar_pairs: list[dict], posts_by_id: dict[str, dict]) -> str:
    if not similar_pairs:
        return _empty_chart("Semantic similarity pairs")

    labels: list[str] = []
    scores: list[float] = []
    for pair in similar_pairs[:8]:
        if not isinstance(pair, dict):
            continue
        a = posts_by_id.get(str(pair.get("post_a_id", "")), {})
        b = posts_by_id.get(str(pair.get("post_b_id", "")), {})
        title_a = str(a.get("title", pair.get("post_a_id", "?")))[:22]
        title_b = str(b.get("title", pair.get("post_b_id", "?")))[:22]
        labels.append(f"{title_a} ↔ {title_b}")
        scores.append(float(pair.get("similarity", 0)))

    if not scores:
        return _empty_chart("Semantic similarity pairs")

    fig, ax = plt.subplots(figsize=(7.5, max(3.5, len(labels) * 0.45)))
    y = np.arange(len(labels))
    ax.barh(y, scores, color="#0ea5e9", height=0.55)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=7)
    ax.invert_yaxis()
    ax.set_xlim(0, 1.05)
    ax.set_xlabel("Cosine similarity (MiniLM embeddings)")
    ax.set_title("Most similar post pairs")
    ax.axvline(0.55, color="#94a3b8", linestyle=":", linewidth=1, label="Threshold")
    ax.xaxis.grid(True, linestyle="--")
    ax.set_axisbelow(True)
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    return _fig_to_data_uri(fig)


def chart_evaluation(result: dict[str, Any]) -> str:
    posts = result.get("posts", [])
    evaluation = result.get("evaluation", {})
    sent_eval = evaluation.get("sentiment", {})
    judge = evaluation.get("briefing_judge", {})

    fig, axes = plt.subplots(1, 2, figsize=(7.5, 3.6))

    if posts:
        agree = sum(1 for p in posts if p.get("vader_label") == p.get("lr_label"))
        disagree = len(posts) - agree
        axes[0].pie(
            [agree, disagree],
            labels=["Agree", "Disagree"],
            colors=["#22c55e", "#fbbf24"],
            autopct="%1.0f%%",
            startangle=90,
            wedgeprops={"edgecolor": "white", "linewidth": 2},
        )
        axes[0].set_title(f"VADER vs LR agreement\n({agree}/{len(posts)} posts)")
    else:
        axes[0].set_axis_off()
        axes[0].text(0.5, 0.5, "No post data", ha="center")

    judge_score = judge.get("score")
    if judge_score is not None:
        score = int(judge_score)
        axes[1].barh([0], [score], color=BRAND, height=0.4)
        axes[1].barh([0], [100 - score], left=[score], color="#e2e8f0", height=0.4)
        axes[1].set_xlim(0, 100)
        axes[1].set_yticks([])
        axes[1].set_xlabel("Score / 100")
        axes[1].set_title(f"Briefing quality ({judge.get('source', 'judge')})")
        axes[1].text(score / 2, 0, str(score), ha="center", va="center", fontweight="bold", color="white")
    else:
        axes[1].set_axis_off()
        axes[1].text(0.5, 0.5, "Judge unavailable", ha="center")

    fig.tight_layout()
    return _fig_to_data_uri(fig)


def chart_agent_pipeline(agent: dict[str, Any]) -> str:
    steps = agent.get("steps", [])
    if not steps:
        return _empty_chart("Agent pipeline")

    actions = [str(s.get("action", "")) for s in steps]
    y = np.arange(len(actions))

    fig, ax = plt.subplots(figsize=(7.5, max(3.5, len(actions) * 0.38)))
    ax.barh(y, [1] * len(actions), color=BRAND, height=0.55, alpha=0.25)
    ax.scatter([0.5] * len(actions), y, s=120, color=BRAND, zorder=3, edgecolors="white", linewidths=1.5)
    for i, step in enumerate(steps):
        ax.text(
            0.65,
            i,
            f"Step {i+1}: {actions[i]}",
            va="center",
            fontsize=8,
            fontweight="bold",
        )
        obs = str(step.get("observation", ""))[:55]
        if obs:
            ax.text(0.65, i - 0.22, obs, va="center", fontsize=7, color="#64748b")
    ax.set_yticks([])
    ax.set_xticks([])
    ax.set_xlim(0, 1)
    ax.invert_yaxis()
    ax.set_title("ReAct agent orchestration trace")
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.tight_layout()
    return _fig_to_data_uri(fig)


def generate_all_charts(result: dict[str, Any]) -> dict[str, str]:
    """Build chart images keyed by section id."""
    posts = result.get("posts", [])
    posts_by_id: dict[str, dict] = {}
    for p in posts:
        pid = str(p.get("id", ""))
        if pid:
            posts_by_id[pid] = p
    for p in result.get("high_impact_posts", []):
        pid = str(p.get("id", ""))
        if pid and pid not in posts_by_id:
            posts_by_id[pid] = p

    trends = result.get("trends", {})
    crisis = result.get("crisis", {})
    agent = result.get("agent_trace", {})

    return {
        "overview_sentiment": chart_sentiment_distribution(result),
        "overview_classifiers": chart_vader_lr_comparison(posts),
        "crisis": chart_crisis_score({**result, "crisis": crisis}),
        "trends": chart_trends_timeline(trends),
        "topics": chart_topics(result.get("topics", [])),
        "entities": chart_entities(result.get("top_entities", [])),
        "risk_keywords": chart_risk_keywords(result.get("risk_keywords", [])),
        "high_impact": chart_high_impact(result.get("high_impact_posts", [])),
        "similarity": chart_similar_pairs(result.get("similar_pairs", []), posts_by_id),
        "evaluation": chart_evaluation(result),
        "agent": chart_agent_pipeline(agent),
    }


def chart_img(data_uri: str, *, alt: str) -> str:
    return f'<img class="chart-img" src="{data_uri}" alt="{alt}" loading="lazy" />'
