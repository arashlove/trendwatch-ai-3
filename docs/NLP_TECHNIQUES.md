# TrendWatch AI — Project & NLP reference

This document explains **what the repository does**, **how to run it step by step**, and **every NLP technique** implemented — where it runs, what it does, and how outputs flow through the system.

---

## What this repo is

**TrendWatch AI** is a Reddit **brand-monitoring** Devvit web app (Assignment Use Case 2: social media intelligence). It:

- Pulls **live Reddit posts** from a subreddit (no Reddit Data API keys required in the app).
- Surfaces **top keywords**, **sentiment**, **trends**, **crisis risk**, and **briefings** for a topic or whole subreddit.
- Runs a **lightweight preview** inside Reddit (Steps 1–2).
- Runs the **full NLP assignment pipeline** on your PC via Python FastAPI (Step 3 → local upload).

The app is built for **Devvit Web** (React iframe + Hono/tRPC server on Reddit) with an optional **Python backend** for rubric-grade analysis and a printable HTML report with Matplotlib charts.

---

## Repository layout

```text
trendwatch-ai-3/
├── src/
│   ├── client/          React UI (game.html dashboard, splash inline view)
│   ├── server/          Devvit Hono API + NLP preview pipeline
│   │   └── nlp/         TypeScript NLP (collect, sentiment, trends, crisis…)
│   └── shared/          Shared TypeScript types
├── backend/             Python FastAPI — full NLP + HTML report
│   ├── main.py          /upload, /report, /health
│   ├── pipeline.py      Full analysis entry
│   ├── agent.py         ReAct orchestration
│   ├── demo_report.py   HTML report template
│   └── report_charts.py Matplotlib charts for report sections
├── docs/
│   └── NLP_TECHNIQUES.md   This file
├── devvit.json          Devvit app config & entrypoints
└── package.json         npm scripts (dev, build, deploy)
```

| Part | Tech | Runs where |
|------|------|------------|
| Dashboard UI | React 19, Tailwind, Recharts | Reddit iframe (`game.html`) |
| Devvit API | Hono, `/api/trendwatch/*` | Reddit serverless |
| Full NLP | FastAPI, spaCy, sklearn, VADER, MiniLM | Your machine (`localhost:8000`) |

---

## How to run

### Devvit app (required)

```powershell
npm install
npx devvit login          # once
npm run dev               # playtest on Reddit
```

Open the app in Reddit playtest (expanded view = full dashboard).

### Python backend (for full assignment report)

```powershell
cd backend
python -m venv venv
.\venv\Scripts\pip install -r requirements.txt
.\run.ps1                 # http://127.0.0.1:8000
```

Optional: copy `backend/.env.example` → `backend/.env` and set `OPENAI_API_KEY` for LLM briefing and LLM-as-judge (otherwise rule-based fallback is used).

---

## User workflow — Steps 1, 2, 3

The dashboard (`src/client/game.tsx`) is a three-step flow:

### Step 1 — Find keywords

**Button:** *Find keywords*

**Inputs:**

| Field | Meaning |
|-------|---------|
| Keyword | Optional filter on title/body; leave blank to analyse all recent posts |
| Subreddit | e.g. `technology` or `all` |
| Scan limit | How many recent posts to fetch (100–1000) |
| Post limit | Max matched posts to keep (10–500) |

**What happens:** Devvit server calls `GET /api/trendwatch/collect` → fetches posts via Reddit API → extracts **top 10 keywords** → returns summaries + `export_posts` (full JSON for Python).

**You see:** Data source banner, keyword list, post count.

---

### Step 2 — Run analysis (in-app preview)

**Button:** *Run analysis* (enabled after Step 1)

**What happens:** `GET /api/trendwatch/analyze` runs the **TypeScript preview pipeline** on the same parameters: lexicon sentiment, trends, crisis score, keyword-based topics, rule-based briefing, Recharts in the iframe.

**You see:** Overview cards, sentiment chart, crisis panel, trend timeline, topic cards, high-impact posts, insight briefing.

This is **not** the full Python pipeline — it is a fast demo suitable inside Reddit.

---

### Step 3 — Copy report data (full NLP)

**Button:** *Copy report data* (needs ≥5 posts from Step 1)

**What happens:** Report JSON (`query`, `subreddit`, `posts[]`) is copied to the clipboard. Reddit’s sandbox blocks file downloads and localhost calls, so this **copy → paste** bridge is used.

**You see:** Toast confirmation and instructions with upload URL.

**Then on your PC:**

1. Open **`http://127.0.0.1:8000/upload`** in a normal browser tab (not Reddit).
2. Paste the JSON (Ctrl+V) → **Run full NLP report**.
3. Python runs the full agent pipeline and returns a **printable HTML report** with Matplotlib charts (sentiment, crisis, trends, topics, NER, risk, agent trace, evaluation).

---

## End-to-end data flow (diagram)

```text
┌─────────────────────────────────────────────────────────────┐
│  REDDIT PLAYTEST — Devvit app (src/)                        │
│                                                             │
│  Step 1: Collect posts + top 10 keywords                    │
│  Step 2: Lightweight TS NLP + charts (preview)              │
│  Step 3: Copy JSON to clipboard                             │
└──────────────────────────┬──────────────────────────────────┘
                             │  paste JSON (same machine)
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  LOCAL PC — Python FastAPI (backend/)                       │
│                                                             │
│  POST /upload  →  full NLP pipeline  →  HTML + charts      │
└─────────────────────────────────────────────────────────────┘
```

---

## Architecture overview (NLP tiers)

TrendWatch uses a **hybrid two-tier** design:

| Tier | Location | Purpose |
|------|----------|---------|
| **In-app preview** | `src/server/nlp/` (TypeScript on Devvit) | Live Reddit collection, keyword discovery, lightweight charts inside the Reddit iframe |
| **Full assignment report** | `backend/` (Python FastAPI on your PC) | Rubric-grade NLP: spaCy, VADER, TF-IDF+LR, embeddings, RAG, LLM briefing, printable HTML with Matplotlib charts |

**Pipeline summary**

1. Devvit **Step 1** collects posts via the Reddit API (`reddit.getNewPosts` / `getBestPosts`).
2. Devvit **Step 2** runs the TypeScript preview pipeline on the same posts.
3. Devvit **Step 3** copies post JSON to clipboard; you paste it at `http://127.0.0.1:8000/upload`.
4. Python runs the full agent pipeline and returns an HTML report with embedded charts.

---

## Technique matrix (rubric mapping)

| Technique | Tier | Module | Category |
|-----------|------|--------|----------|
| Text preprocessing | Both | `preprocessing.py` / `preprocessing.ts` | Basic |
| Tokenization & stopwords | Both | `preprocessing.py`, `keywords.ts` | Basic |
| Stemming & lemmatization | Python | `preprocessing.py` (NLTK Porter + WordNet) | Basic |
| Regex information extraction | Both | `extraction.py` / `crisis.ts` | Basic |
| Named entity recognition (NER) | Python | `ner_pos.py` (spaCy / NLTK fallback) | Basic |
| Part-of-speech tagging | Python | `ner_pos.py` | Basic |
| Lexicon sentiment | Devvit | `sentiment.ts` | Basic |
| VADER sentiment | Python | `sentiment.py` | Basic |
| TF-IDF + Logistic Regression | Python | `classification.py` | Basic |
| Sentiment ensemble | Python | `sentiment.py` | Advanced |
| Term-frequency keywords | Devvit | `keywords.ts` | Basic |
| Embedding topic clustering | Python | `topics.py` + `similarity.py` | Advanced |
| Temporal trend analysis | Both | `trends.py` / `trends.ts` | Basic |
| Crisis scoring | Both | `crisis.py` / `crisis.ts` | Advanced |
| Cosine similarity pairs | Python | `similarity.py` | Advanced |
| RAG retrieval | Python | `rag.py` | Advanced |
| Foundation LLM briefing | Python | `llm_report.py` | Advanced |
| Chain-of-thought prompting | Python | `llm_report.py` | Advanced |
| Prompt engineering | Python | `llm_report.py` | Advanced |
| LLM-as-judge evaluation | Python | `evaluation.py` | Advanced |
| ReAct agent orchestration | Python | `agent.py` | Advanced |
| Ethics disclaimers | Both | `llm_report.py` / `briefing.ts` | Advanced |

---

## Devvit in-app preview (`src/server/nlp/`)

These run inside Reddit’s serverless environment. They are **fast and dependency-light** but intentionally simpler than the Python pipeline.

### 1. Reddit post collection

**File:** `redditCollect.ts`

- Fetches recent posts from a subreddit using Devvit’s `reddit` API.
- Optional keyword filter: scans post titles/bodies locally (no Reddit search API).
- Returns matched posts plus `export_posts` (full payloads for Python).

### 2. Preprocessing

**File:** `preprocessing.ts`

- Combines title + body.
- Lowercases, strips URLs and punctuation.
- Produces `cleanedText` for downstream steps.

### 3. Lexicon-based sentiment

**File:** `sentiment.ts`

- Counts hits against fixed **positive** and **negative** word lists.
- Computes a score in `[-1, 1]` and labels `positive` / `neutral` / `negative`.
- No ML model — suitable for quick preview only.

### 4. Risk keyword extraction

**File:** `crisis.ts` (`extractRiskKeywords`)

- Matches tokens against a brand-risk lexicon (`scam`, `boycott`, `lawsuit`, etc.).
- Used in crisis scoring and high-impact ranking.

### 5. Top keywords (TF-style)

**File:** `keywords.ts`

- Tokenizes cleaned text, removes English stopwords.
- Ranks terms by document frequency and total occurrences.
- Excludes query tokens when a search keyword is set.

### 6. Pseudo-entities

**File:** `keywords.ts` (`extractTopEntities`)

- Extracts `@mentions` and `#hashtags` via regex (not true NER).

### 7. Topic labels (keyword overlap)

**File:** `topics.ts`

- Groups posts that contain each top keyword.
- Labels topics by dominant keyword; picks highest-engagement representative post.
- **Not** embedding clustering — that is Python-only.

### 8. Trend detection

**File:** `trends.ts`

- Buckets posts by UTC date.
- Computes daily post count, negative count, negative ratio, risk keyword count.
- Flags a **spike** when the latest day’s negative ratio exceeds the average by 25+ points (with ≥3 posts that day).

### 9. Crisis intelligence score

**File:** `crisis.ts`

Weighted 0–100 score from:

| Component | Max points | Logic |
|-----------|------------|-------|
| Negative ratio | 40 | `% negative posts × 40` |
| Risk keywords | 25 | Keyword density capped at 1.0 × 25 |
| High-impact negative | 20 | Negative posts with score+comments ≥ 50 |
| Trend spike | 10 | Binary if spike detected |

Risk levels: Low (0–30), Medium (31–60), High (61–80), Critical (81–100).

### 10. Rule-based briefing

**File:** `briefing.ts`

- Template executive summary from crisis score, keywords, and trends.
- Recommended actions scale with risk level.
- Includes ethics notice (no LLM).

---

## Python full pipeline (`backend/`)

Runs locally after you paste Devvit-collected JSON. Orchestrated by `agent.py` in ReAct-style steps.

### Pipeline order

```
collect → preprocess → extract → NER/POS → sentiment → topics → trends → crisis → RAG → briefing → similarity pairs
```

### 1. Preprocessing

**File:** `preprocessing.py`

| Step | Method |
|------|--------|
| HTML/URL removal | Regex |
| Normalization | Lowercase, strip non-alphanumeric |
| Tokenization | NLTK `word_tokenize` |
| Stemming | Porter stemmer |
| Lemmatization | WordNet lemmatizer |
| Optional stopword removal | NLTK English stopwords |

Output fields: `clean_text`, `tokens`, `stemmed_tokens`, `lemmatized_tokens`.

### 2. Regex information extraction

**File:** `extraction.py`

- **Hashtags:** `#word` pattern
- **Mentions:** `u/username` and `@username`
- **Risk lexicon:** 30+ brand-crisis terms (boycott, fraud, recall, etc.)
- Aggregates corpus-wide risk keyword frequencies

### 3. NER and POS tagging

**File:** `ner_pos.py`

- **Primary:** spaCy `en_core_web_sm` — entities (ORG, PERSON, GPE, …) and POS tags.
- **Fallback:** NLTK `ne_chunk` + `pos_tag` if spaCy unavailable.
- Corpus-level **top entities** ranked by mention count.

### 4. VADER sentiment

**File:** `sentiment.py` + `vaderSentiment`

- Compound score in `[-1, 1]` from valence-aware lexicon.
- Thresholds: ≥0.05 positive, ≤−0.05 negative, else neutral.

### 5. TF-IDF + Logistic Regression

**File:** `classification.py`

- `TfidfVectorizer` (max 5000 features, unigrams + bigrams, min_df=2).
- `LogisticRegression` trained on **weak labels** from VADER (no gold labels required).
- Outputs `lr_label` and `lr_confidence` per post.

### 6. Sentiment ensemble

**File:** `sentiment.py`

- **Majority vote** between VADER and LR labels.
- If one is neutral, the other wins; if they disagree (pos vs neg), defaults to neutral.
- Final label stored as `sentiment`.

### 7. Embedding-based topic clustering

**Files:** `topics.py`, `similarity.py`

- **Embeddings:** Sentence-BERT `all-MiniLM-L6-v2` (falls back to TF-IDF vectors).
- **Clustering:** KMeans (`k = min(5, max(2, n/8))`).
- Topic label = top 3 keywords in cluster; colour in charts = dominant sentiment.

### 8. Trend detection

**File:** `trends.py`

Same structure as Devvit but uses Python ensemble sentiment labels.

- Spike if latest day’s negative ratio ≥ 1.5× historical average.

### 9. Crisis intelligence (Python variant)

**File:** `crisis.py`

| Component | Max points |
|-----------|------------|
| Negative sentiment | 40 |
| Risk keyword density | 25 |
| High-engagement negative posts | 20 |
| Trend spike | 15 |

Impact score uses `log1p(score) + log1p(comments)`.

### 10. Semantic similarity

**File:** `similarity.py`

- Pairwise cosine similarity on MiniLM embeddings.
- Returns top pairs above threshold 0.55 (max 5 pairs).
- Surfaces duplicate narratives or coordinated discussion themes.

### 11. RAG (retrieval-augmented generation)

**File:** `rag.py`

- Embeds all post texts + user query.
- Retrieves top-5 posts by cosine similarity to query.
- Snippets fed into LLM context for grounded briefing.

### 12. LLM briefing with chain-of-thought

**File:** `llm_report.py`

- **With `OPENAI_API_KEY`:** OpenAI-compatible chat completion (`gpt-4o-mini` default).
- System prompt instructs step-by-step reasoning before structured output.
- Parses markdown sections: Executive Summary, Main Concerns, Crisis Explanation, Recommended Actions, Communication Strategy.
- **Without API key:** Rule-based fallback using crisis reasons and topic labels.

### 13. Automated evaluation

**File:** `evaluation.py`

- **Sentiment agreement:** % of posts where VADER label == LR label.
- **LLM-as-judge:** Optional second LLM call scores briefing clarity/grounding 0–100; heuristic fallback without API key.

### 14. ReAct agent trace

**File:** `agent.py`

Records thought → action → observation for each pipeline stage:

`collect_posts → preprocess → extract → ner_pos → sentiment → topics → trends → crisis → rag → briefing`

Used in the HTML report agent section and evaluation charts.

---

## Full report HTML & charts

**Files:** `demo_report.py`, `report_charts.py`

The Python `/upload` endpoint renders a printable HTML report. **Matplotlib** generates PNG charts embedded as base64:

| Section | Chart |
|---------|-------|
| Overview | Donut — sentiment distribution; grouped bar — VADER vs LR |
| Crisis | Gauge + horizontal bar — score components |
| Trends | Dual-axis — volume bars, negative % line, risk keyword line |
| Topics | Horizontal bar — cluster sizes (colour = sentiment) |
| NER | Horizontal bar — top entities |
| Risk | Horizontal bars — risk keywords, similar pairs, high-impact posts |
| Agent / evaluation | Pipeline trace + agreement pie + judge score bar |

Tables and text summaries remain below each chart for assignment write-ups.

---

## Environment & dependencies

### Devvit (automatic with `npm run dev`)

- No extra NLP models; pure TypeScript.

### Python (`backend/`)

```powershell
cd backend
python -m venv venv
.\venv\Scripts\pip install -r requirements.txt
.\run.ps1
```

Optional `.env` keys:

| Variable | Purpose |
|----------|---------|
| `OPENAI_API_KEY` | LLM briefing + LLM-as-judge |
| `OPENAI_MODEL` | Model name (default `gpt-4o-mini`) |
| `REDDIT_CLIENT_ID` / `SECRET` | Standalone `/demo` Reddit fetch only |

---

## Quick reference: which button runs what

| UI action | NLP tier | Output |
|-----------|----------|--------|
| Step 1 — Find keywords | Devvit collect + keywords | Top 10 keywords, post list |
| Step 2 — Run analysis | Devvit full preview pipeline | Charts in iframe, rule briefing |
| Step 3 — Copy report data | Export only | JSON clipboard |
| Paste at `/upload` | Python full pipeline | HTML report + Matplotlib charts |

---

## Limitations (document in your assignment)

- Devvit preview uses lexicon sentiment, not VADER/spaCy.
- TF-IDF+LR uses weak VADER labels — not gold-standard supervised training.
- Embedding models add latency; first run downloads MiniLM weights.
- LLM outputs require human review; ethics disclaimers are included by design.
- Reddit iframe cannot call localhost — full report requires copy/paste workflow.

---

## Source file index

| Path | Role |
|------|------|
| `src/server/nlp/redditCollect.ts` | Live Reddit fetch |
| `src/server/nlp/preprocessing.ts` | Devvit text cleaning + lexicon sentiment |
| `src/server/nlp/keywords.ts` | Keywords & pseudo-entities |
| `src/server/nlp/sentiment.ts` | Lexicon sentiment scorer |
| `src/server/nlp/trends.ts` | Daily trend buckets |
| `src/server/nlp/topics.ts` | Keyword-overlap topics |
| `src/server/nlp/crisis.ts` | Crisis score + risk lexicon |
| `src/server/nlp/briefing.ts` | Rule-based briefing |
| `src/server/nlp/pipeline.ts` | Devvit analyze orchestrator |
| `backend/agent.py` | ReAct agent orchestration |
| `backend/preprocessing.py` | NLTK preprocess |
| `backend/extraction.py` | Regex IE |
| `backend/ner_pos.py` | spaCy/NLTK NER+POS |
| `backend/classification.py` | TF-IDF + LR |
| `backend/sentiment.py` | VADER + ensemble |
| `backend/topics.py` | Embedding KMeans topics |
| `backend/trends.py` | Temporal trends |
| `backend/crisis.py` | Crisis scoring |
| `backend/similarity.py` | Embeddings + cosine pairs |
| `backend/rag.py` | Top-k retrieval |
| `backend/llm_report.py` | LLM / fallback briefing |
| `backend/evaluation.py` | Agreement + LLM judge |
| `backend/pipeline.py` | Python entry + response shape |
| `backend/demo_report.py` | HTML report renderer |
| `backend/report_charts.py` | Matplotlib chart generator |

---

## Related documentation

- [`CHARTS_AND_FIGURES.md`](./CHARTS_AND_FIGURES.md) — Every chart and figure output (F1–F20), suggested captions, and export instructions for your report
