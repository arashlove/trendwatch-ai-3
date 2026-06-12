# TrendWatch AI System Demo + Supporting Reddit NLP Prototype

**COMP8420 Use Case 2: Social Media Intelligent Platform**

*Main system: TrendWatch AI live Reddit/Devvit + FastAPI backend*  
*Supporting prototype: Kaggle Reddit NLP dashboard/evaluation*

---

## Why two systems?

| | **TrendWatch AI** (main) | **Kaggle prototype** (supporting) |
|---|--------------------------|-----------------------------------|
| **Purpose** | End-to-end brand monitoring on live Reddit | Offline NLP experiments & benchmarks |
| **Data** | Live posts via Devvit API | Kaggle / curated Reddit CSV |
| **UI** | Reddit iframe + HTML report | Dashboard |
| **Output** | Crisis score, briefing, printable report | Accuracy, F1, model comparison tables |
| **Role in assignment** | Primary implementation demo | Evidence for technique selection & evaluation |

The prototype informed our choice of VADER, TF-IDF+LR, and ensemble design in the main system.

---

## TrendWatch AI — architecture

```text
┌─────────────────────────────────────────┐
│  REDDIT (Devvit Web)                    │
│  Step 1  Scan subreddit → keywords      │
│  Step 2  Filter by brand keyword        │
│  Step 3  Export JSON                    │
└──────────────────┬──────────────────────┘
                   │ paste JSON
                   ▼
┌─────────────────────────────────────────┐
│  PYTHON (FastAPI localhost:8000)        │
│  Preprocess → NER → Sentiment ensemble  │
│  Topics → Trends → Crisis → RAG → Report│
└─────────────────────────────────────────┘
```

- Hybrid design: Reddit sandbox cannot call localhost — JSON bridge is intentional
- ≥3 basic + ≥3 advanced NLP techniques (report §9)
- Reproducible: paste `data/microsoft.json` anytime

---

## NLP pipeline (main system)

**Basic**
- Preprocessing (NLTK)
- NER + POS (spaCy)
- VADER sentiment
- TF-IDF + Logistic Regression
- Regex information extraction
- Temporal trend analysis

**Advanced**
- Sentiment ensemble
- Embedding topic clustering (MiniLM + KMeans)
- RAG-grounded briefing
- ReAct agent orchestration
- Crisis multi-signal fusion
- LLM-as-judge / gold-set evaluation

---

## Supporting prototype — Kaggle Reddit NLP

- Fixed Reddit dataset (Kaggle) for controlled experiments
- Compared VADER, LR, and ensemble before live integration
- Produced evaluation tables in our written report
- Supports technique justification — **not** the primary live demo
