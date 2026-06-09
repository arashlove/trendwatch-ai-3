# TrendWatch AI — Charts & figures reference

Use this document when writing your assignment report. It lists **every visual output** produced by the repository: interactive charts in the Devvit app (Step 2) and static figures in the Python full report (Step 3 → `/upload`).

For project workflow and NLP techniques, see [`NLP_TECHNIQUES.md`](./NLP_TECHNIQUES.md).

---

## Summary table

| # | Figure name | Type | Where it appears | When generated | Library |
|---|-------------|------|------------------|----------------|---------|
| F1 | Top 10 keywords list | Ranked list | Devvit app — Step 1 | After *Find keywords* | React UI |
| F2 | Overview metric cards | KPI cards | Devvit app — Step 2 | After *Run analysis* | React UI |
| F3 | Sentiment pie chart | Pie chart | Devvit app — Step 2 | After *Run analysis* | Recharts |
| F4 | Sentiment bar chart | Bar chart | Devvit app — Step 2 | After *Run analysis* | Recharts |
| F5 | Crisis assessment panel | Score + bullet list | Devvit app — Step 2 | After *Run analysis* | React UI |
| F6 | Trend timeline | Composed chart (bars + line) | Devvit app — Step 2 | After *Run analysis* | Recharts |
| F7 | Topic cards | Card grid | Devvit app — Step 2 | After *Run analysis* | React UI |
| F8 | High-impact posts list | Ranked list | Devvit app — Step 2 | After *Run analysis* | React UI |
| F9 | Insight briefing | Text report | Devvit app — Step 2 | After *Run analysis* | React UI |
| F10 | Crisis gauge & components | Gauge + horizontal bars | Full HTML report §2 | After `/upload` | Matplotlib |
| F11 | Sentiment donut | Donut chart | Full HTML report §3 | After `/upload` | Matplotlib |
| F12 | VADER vs LR comparison | Grouped bar chart | Full HTML report §3 | After `/upload` | Matplotlib |
| F13 | Trend timeline (full) | Dual-axis combo chart | Full HTML report §4 | After `/upload` | Matplotlib |
| F14 | Topic cluster sizes | Horizontal bar chart | Full HTML report §5 | After `/upload` | Matplotlib |
| F15 | Top named entities | Horizontal bar chart | Full HTML report §6 | After `/upload` | Matplotlib |
| F16 | Risk keyword frequency | Horizontal bar chart | Full HTML report §7 | After `/upload` | Matplotlib |
| F17 | Similar post pairs | Horizontal bar chart | Full HTML report §7 | After `/upload` | Matplotlib |
| F18 | High-impact posts | Horizontal bar chart | Full HTML report §7 | After `/upload` | Matplotlib |
| F19 | Agent pipeline trace | Process diagram | Full HTML report §10 | After `/upload` | Matplotlib |
| F20 | Evaluation (agreement + judge) | Pie + progress bar | Full HTML report §10 | After `/upload` | Matplotlib |
| T1–T8 | Report data tables | Tables | Full HTML report §2–§10 | After `/upload` | HTML/CSS |

---

## Part A — Devvit in-app outputs (Steps 1 & 2)

These appear inside the Reddit playtest dashboard. Capture them with **screenshots** or screen recording for your report (the iframe does not export PNG files directly).

### Step 1 — After *Find keywords*

#### F1 — Top 10 keywords

| Property | Detail |
|----------|--------|
| **Component** | `TopKeywordsPanel.tsx` |
| **Visual type** | Ordered list (ranked table) |
| **Shows** | Keyword rank, term, number of posts containing it, total mention count |
| **Data source** | Term frequency after stopword removal on collected posts |
| **Report caption suggestion** | *Figure 1: Top 10 keywords extracted from r/{subreddit} (N posts scanned).* |

---

### Step 2 — After *Run analysis*

#### F2 — Overview metric cards

| Property | Detail |
|----------|--------|
| **Component** | `OverviewCards.tsx` |
| **Visual type** | Six KPI cards in a grid |
| **Metrics** | Total posts, positive %, neutral %, negative %, crisis score (0–100), risk level (Low/Medium/High/Critical) |
| **Report caption suggestion** | *Figure 2: Summary metrics from the in-app preview pipeline.* |

#### F3 — Sentiment pie chart

| Property | Detail |
|----------|--------|
| **Component** | `SentimentChart.tsx` (upper chart) |
| **Visual type** | Pie chart |
| **Library** | Recharts `PieChart` |
| **Shows** | Share of posts labelled positive (green), neutral (grey), negative (red) |
| **NLP method** | Lexicon-based sentiment (TypeScript preview — not VADER) |
| **Report caption suggestion** | *Figure 3: Sentiment distribution (lexicon classifier, in-app preview).* |

#### F4 — Sentiment bar chart

| Property | Detail |
|----------|--------|
| **Component** | `SentimentChart.tsx` (lower chart) |
| **Visual type** | Vertical bar chart |
| **Library** | Recharts `BarChart` |
| **Shows** | Absolute post counts per sentiment label |
| **Report caption suggestion** | *Figure 4: Sentiment counts by class (in-app preview).* |

#### F5 — Crisis assessment panel

| Property | Detail |
|----------|--------|
| **Component** | `CrisisPanel.tsx` |
| **Visual type** | Large score + colour-coded risk level + bullet reasons |
| **Shows** | Crisis score 0–100, risk tier, human-readable reasons (negative ratio, risk keywords, high-impact posts, spike) |
| **Report caption suggestion** | *Figure 5: Crisis intelligence score and contributing factors (rule-based fusion).* |

#### F6 — Trend timeline

| Property | Detail |
|----------|--------|
| **Component** | `TrendTimeline.tsx` |
| **Visual type** | Composed chart: grouped bars + line on dual Y-axes |
| **Library** | Recharts `ComposedChart` |
| **Series** | Blue bars = daily post count; red bars = daily negative count; orange line = negative % (right axis) |
| **Also shows** | Summary chips: total posts, peak day, average negative %; spike message text |
| **Report caption suggestion** | *Figure 6: Temporal trend of post volume and negative sentiment ratio by day.* |

#### F7 — Topic cards

| Property | Detail |
|----------|--------|
| **Component** | `TopicCards.tsx` |
| **Visual type** | Card grid (not a chart — qualitative figure) |
| **Shows** | Topic label, post count, dominant sentiment, related keywords, link to representative post |
| **NLP method** | Keyword-overlap grouping (preview — not embedding clustering) |
| **Report caption suggestion** | *Figure 7: Topic groups derived from top keywords (in-app preview).* |

#### F8 — High-impact posts list

| Property | Detail |
|----------|--------|
| **Component** | `HighImpactPosts.tsx` |
| **Visual type** | Scrollable ranked list |
| **Shows** | Post title, author, subreddit, sentiment, impact score, matched risk keywords |
| **Impact formula** | `(score + 2 × comments) × sentiment weight` |
| **Report caption suggestion** | *Figure 8: Top high-engagement posts ranked by impact score.* |

#### F9 — Insight briefing

| Property | Detail |
|----------|--------|
| **Component** | `InsightReport.tsx` |
| **Visual type** | Structured text report (not a chart) |
| **Sections** | Executive summary, main concerns, recommended actions, ethics notice, technique lists (in-app vs full Python) |
| **Report caption suggestion** | *Figure 9: Rule-based executive briefing (in-app preview, no LLM).* |

---

## Part B — Full HTML report figures (Step 3 → `/upload`)

Generated by `backend/report_charts.py` (Matplotlib) and embedded in `backend/demo_report.py`. Open the report in a browser → **Print / Save as PDF** to export all figures at once.

**How to generate:** Step 1 in Reddit → Step 3 *Copy report data* → paste at `http://127.0.0.1:8000/upload` → **Run full NLP report**.

---

### Section 2 — Crisis intelligence

#### F10 — Crisis gauge & score components

| Property | Detail |
|----------|--------|
| **Function** | `chart_crisis_score()` |
| **Visual type** | Semi-circular gauge + horizontal bar chart |
| **Left panel** | Needle gauge: crisis score /100 and risk level label |
| **Right panel** | Points contributed by: negative sentiment, risk keywords, engagement, trend spike |
| **Report caption suggestion** | *Figure 10: Crisis intelligence score (gauge) and weighted component breakdown.* |

---

### Section 3 — Overview & sentiment

#### F11 — Sentiment donut chart

| Property | Detail |
|----------|--------|
| **Function** | `chart_sentiment_distribution()` |
| **Visual type** | Donut (ring) pie chart |
| **Shows** | Positive / neutral / negative percentages; centre label = total posts |
| **NLP method** | VADER + TF-IDF/LR **ensemble** (final labels) |
| **Report caption suggestion** | *Figure 11: Final sentiment distribution after VADER–LR ensemble voting.* |

#### F12 — VADER vs Logistic Regression comparison

| Property | Detail |
|----------|--------|
| **Function** | `chart_vader_lr_comparison()` |
| **Visual type** | Grouped vertical bar chart |
| **Shows** | Side-by-side post counts per class for VADER vs TF-IDF+LR **before** ensemble fusion |
| **Report caption suggestion** | *Figure 12: Comparison of independent sentiment classifiers prior to ensemble.* |

**Also in section 3:** CSS horizontal percentage bars and a count table (supplementary, not numbered as separate figures).

---

### Section 4 — Trend detection

#### F13 — Trend timeline (full pipeline)

| Property | Detail |
|----------|--------|
| **Function** | `chart_trends_timeline()` |
| **Visual type** | Dual-axis combo chart |
| **Bars** | Daily post volume (grey) |
| **Lines** | Negative sentiment % (red); risk keyword count per day (orange dashed) |
| **Report caption suggestion** | *Figure 13: Daily post volume, negative sentiment percentage, and risk keyword frequency.* |

**Also in section 4:** Trend data table (date, posts, negative count, negative %, risk keywords).

---

### Section 5 — Topic clusters

#### F14 — Topic cluster sizes

| Property | Detail |
|----------|--------|
| **Function** | `chart_topics()` |
| **Visual type** | Horizontal bar chart |
| **Shows** | Each cluster’s post count; bar colour = dominant cluster sentiment (green/grey/red) |
| **NLP method** | Sentence-BERT MiniLM embeddings + KMeans |
| **Also shows** | Topic cards with keywords and representative post (text, below chart) |
| **Report caption suggestion** | *Figure 14: Embedding-based topic clusters (KMeans on MiniLM vectors).* |

---

### Section 6 — Named entities

#### F15 — Top named entities

| Property | Detail |
|----------|--------|
| **Function** | `chart_entities()` |
| **Visual type** | Horizontal bar chart |
| **Shows** | Top 12 entities by corpus mention count |
| **NLP method** | spaCy NER (NLTK fallback) |
| **Report caption suggestion** | *Figure 15: Most frequently mentioned named entities (ORG, PERSON, GPE, etc.).* |

**Also in section 6:** Entity frequency table.

---

### Section 7 — Risk & high impact

#### F16 — Risk keyword frequency

| Property | Detail |
|----------|--------|
| **Function** | `chart_risk_keywords()` |
| **Visual type** | Horizontal bar chart (red) |
| **Shows** | Brand-risk lexicon matches (boycott, scam, lawsuit, …) |
| **Report caption suggestion** | *Figure 16: Frequency of brand-risk keywords detected by regex information extraction.* |

#### F17 — Similar post pairs

| Property | Detail |
|----------|--------|
| **Function** | `chart_similar_pairs()` |
| **Visual type** | Horizontal bar chart |
| **Shows** | Top post pairs by cosine similarity (MiniLM embeddings); dotted line at 0.55 threshold |
| **Report caption suggestion** | *Figure 17: Semantically similar post pairs (cosine similarity ≥ 0.55).* |

#### F18 — High-impact posts

| Property | Detail |
|----------|--------|
| **Function** | `chart_high_impact()` |
| **Visual type** | Horizontal bar chart |
| **Shows** | Top posts by impact score; colour = sentiment |
| **Report caption suggestion** | *Figure 18: High-impact posts ranked by engagement-weighted impact score.* |

**Also in section 7:** Tables for risk keywords, similar pairs, and high-impact post metadata.

---

### Section 10 — Agent & evaluation

#### F19 — Agent pipeline trace

| Property | Detail |
|----------|--------|
| **Function** | `chart_agent_pipeline()` |
| **Visual type** | Vertical process diagram (step markers + action labels) |
| **Shows** | ReAct-style steps: collect → preprocess → extract → NER → sentiment → topics → trends → crisis → RAG → briefing |
| **Report caption suggestion** | *Figure 19: ReAct agent orchestration trace for the full NLP pipeline.* |

#### F20 — Evaluation metrics

| Property | Detail |
|----------|--------|
| **Function** | `chart_evaluation()` |
| **Visual type** | Two-panel figure: pie chart + horizontal progress bar |
| **Left** | VADER vs LR agreement rate (% posts where labels match) |
| **Right** | LLM-as-judge briefing quality score /100 |
| **Report caption suggestion** | *Figure 20: Automated evaluation — classifier agreement and briefing judge score.* |

**Also in section 10:** Agent trace table (step, thought, action, observation).

---

## Part C — Report tables (for appendix)

These are **tabular figures** suitable for an appendix. All appear in the printable HTML report.

| Table ID | Report section | Contents |
|----------|----------------|----------|
| T1 | §2 Crisis | Score components (component name, points) |
| T2 | §3 Overview | Sentiment label vs post count |
| T3 | §4 Trends | Daily timeline (date, posts, negative, %, risk keywords) |
| T4 | §6 NER | Entity name, mention count |
| T5 | §7 Risk | Risk keyword, count |
| T6 | §7 Risk | Similar post pairs (titles, similarity score) |
| T7 | §7 Risk | High-impact posts (title, subreddit, score, comments, sentiment, risks, impact) |
| T8 | §8 Posts | Sample post-level analysis (title, author, ensemble/VADER/LR labels, risk terms) |
| T9 | §10 Agent | ReAct trace rows |
| T10 | §9 Techniques | Basic and advanced NLP techniques list (rubric mapping) |

---

## Part D — Suggested figure set for your written report

If your assignment asks for a **minimum number of figures**, this mapping works well:

| Assignment topic | Recommended figures |
|------------------|---------------------|
| Data collection & keywords | F1 |
| Sentiment analysis | F11, F12 (full pipeline); optionally F3–F4 (preview) |
| Trend / temporal analysis | F13 or F6 |
| Topic modelling | F14 (+ topic cards F7 for contrast) |
| NER | F15 |
| Crisis / risk monitoring | F10, F16, F18 |
| Semantic similarity | F17 |
| Agentic / advanced NLP | F19, F20 |
| Executive output | F9 (preview) + Section 1 briefing text in HTML report |

**Tip:** Use **Part B (Matplotlib)** figures for the graded NLP report — they reflect spaCy, VADER, LR, embeddings, and ensemble methods. Use **Part A** figures to show the live Reddit Devvit demo.

---

## How to export figures for submission

### In-app (Recharts)

1. Run `npm run dev` and complete Steps 1–2 in Reddit playtest.
2. Screenshot each panel (Windows: Win+Shift+S; macOS: Cmd+Shift+4).
3. Crop to the chart border; save as PNG.

### Full report (Matplotlib)

1. Start backend: `cd backend` → `.\run.ps1`
2. Complete Step 1 → Step 3 → paste JSON at `http://127.0.0.1:8000/upload`
3. In the HTML report, click **Print / Save as PDF** (toolbar) — all Matplotlib figures export in vector-friendly layout.
4. Alternatively: right-click any chart → save image (browser dependent), or extract pages from the PDF.

### File locations (source code)

| Output | Source file |
|--------|-------------|
| In-app charts | `src/client/components/SentimentChart.tsx`, `TrendTimeline.tsx` |
| In-app panels | `OverviewCards.tsx`, `CrisisPanel.tsx`, `TopKeywordsPanel.tsx`, etc. |
| Report charts | `backend/report_charts.py` |
| Report layout | `backend/demo_report.py` |

---

## Figure numbering note

The **F1–F20** IDs above are a suggested scheme for your write-up. Renumber to match your university template (e.g. Figure 4.1, Figure 4.2). The HTML report sections (§1–§11) follow the assignment report structure in `demo_report.py` and can be cited directly.

---

## Related documentation

- [`NLP_TECHNIQUES.md`](./NLP_TECHNIQUES.md) — What each technique does and which module implements it
- `backend/demo_report.py` — Full report section headings and table of contents
