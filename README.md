# TrendWatch AI

Reddit brand-monitoring and crisis-detection system for **COMP8420 Use Case 2: Social Media Intelligent Platform**.

TrendWatch AI collects live Reddit posts through a **Devvit Web** app inside Reddit, exports a post corpus as JSON, and runs a full **Python FastAPI** NLP pipeline locally to produce a printable HTML report with charts, crisis scoring, topic clusters, and an executive briefing.

## Architecture

```text
Reddit (Devvit)                    Local machine (FastAPI)
─────────────────                  ─────────────────────────
Step 1  Scan subreddit → keywords
Step 2  Filter by keyword
Step 3  Copy JSON  ──paste──►  /upload → NLP pipeline → HTML report
```

The Reddit iframe cannot call `localhost`, so the JSON copy/paste step is intentional.

## Tech stack

| Layer | Technologies |
|-------|----------------|
| Frontend | React 19, Tailwind CSS 4, Recharts |
| Devvit server | Hono, Devvit Reddit API |
| Python backend | FastAPI, NLTK, spaCy, VADER, scikit-learn, sentence-transformers, Matplotlib |

## Prerequisites

- **Node.js 22+**
- **Python 3.10+**
- Reddit developer account ([Devvit CLI](https://developers.reddit.com/))
- Optional: `OPENAI_API_KEY` for LLM briefing (rule-based fallback works without it)
- Optional: Reddit API credentials in `backend/.env` for standalone `/analyze` and `/demo` routes

## Running the app

You need **two terminals** — Devvit for live Reddit collection, FastAPI for the full NLP report.

### 1. Devvit app (Reddit UI)

```powershell
npm install
npm run login
npm run dev
```

Open the Reddit playtest URL from the CLI. In the expanded view:

1. **Find keywords** — choose a subreddit (e.g. `technology`) and scan posts
2. **Get keyword results** — filter by a brand keyword (e.g. `microsoft`)
3. **Copy report data** — export matched posts as JSON to the clipboard

### 2. Python backend (full NLP report)

```powershell
cd backend
.\run.ps1
```

Open **http://127.0.0.1:8000/upload**, paste the JSON from Step 3 (or upload a `.json` file), and click **Run full NLP report**.

The report includes sentiment analysis, NER, topic clustering, trend detection, crisis scoring, RAG briefing, agent trace, and evaluation charts. Use **Print / Save as PDF** in the browser to export.

### Quick test without Reddit

Paste a file from `data/` directly at `/upload`, for example `data/microsoft.json`.

## Data folder

The `data/` directory holds exported corpora and generated outputs for reproducible demos and evaluation.

| Path | Description |
|------|-------------|
| `data/*.json` | Exported post corpora from Devvit (`query`, `subreddit`, `posts[]`) — e.g. `microsoft.json`, `dog.json`, `nvidia.json` |
| `data/sentiment_gold.json` | 20 human-labelled posts for sentiment benchmark (VADER / LR / ensemble) |
| `data/reports/*.pdf` | Saved HTML reports (Print → PDF) from pipeline runs |

Example export shape:

```json
{
  "query": "microsoft",
  "subreddit": "technology",
  "posts": [
    {
      "id": "t3_…",
      "title": "…",
      "selftext": "…",
      "score": 109,
      "num_comments": 9,
      "created_utc": 1778343290
    }
  ]
}
```

Run the sentiment benchmark against the gold set:

```powershell
cd backend
.\venv\Scripts\python.exe benchmark_sentiment.py
```

## NPM commands

| Command | Description |
|---------|-------------|
| `npm run dev` | Start Devvit playtest on Reddit |
| `npm run build` | Build client and server |
| `npm run deploy` | Upload app to Reddit |
| `npm run type-check` | TypeScript check |
| `npm run lint` | ESLint |

## Backend API routes

| Route | Description |
|-------|-------------|
| `GET /upload` | Paste/upload UI |
| `POST /upload` | Generate HTML report from JSON |
| `POST /report` | Same as upload (programmatic JSON) |
| `GET /health` | Health check |
| `GET /analyze` | JSON analysis (fetches Reddit directly; needs API keys or public API) |
| `GET /demo` | HTML report from Reddit fetch |

## Documentation

| Document | Contents |
|----------|----------|
| [`docs/OPENING_PRESENTATION.md`](docs/OPENING_PRESENTATION.md) | Intro presentation |
| [`docs/VIDEO_SCRIPT_4MIN.md`](docs/VIDEO_SCRIPT_4MIN.md) | 4-minute demo script |
| [`docs/FULL_ASSIGNMENT_REPORT.md`](docs/FULL_ASSIGNMENT_REPORT.md) | Written report outline + case studies |
| [`docs/NLP_TECHNIQUES.md`](docs/NLP_TECHNIQUES.md) | NLP techniques reference |
| [`docs/CHARTS_AND_FIGURES.md`](docs/CHARTS_AND_FIGURES.md) | Report figures (F1–F20) |
| [`AGENTS.md`](AGENTS.md) | Devvit web development rules |

## Project layout

```text
src/client/     React UI (game.html — expanded dashboard)
src/server/     Devvit API routes (/api/trendwatch/collect, …)
backend/        FastAPI NLP pipeline + HTML report
data/           Exported JSON corpora, gold labels, PDF reports
docs/           Assignment report, video script, presentation
```

## License

BSD-3-Clause
