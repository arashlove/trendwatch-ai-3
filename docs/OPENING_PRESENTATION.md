# TrendWatch AI System Demo + Supporting Reddit NLP Prototype

**COMP8420 Use Case 2: Social Media Intelligent Platform**

*Main system: TrendWatch AI live Reddit/Devvit + FastAPI backend*
*Supporting work: Kaggle-based Reddit NLP prototype by Sharon and Rajath*

---

## Why two implementations?

|                        | **TrendWatch AI** (main report system)                                      | **Kaggle Reddit prototype** (supporting work)                                     |
| ---------------------- | --------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| **Purpose**            | End-to-end live Reddit brand monitoring and crisis reporting                | Separate offline Reddit NLP experimentation and dashboard prototype               |
| **Data**               | Live Reddit posts collected through Devvit and exported as JSON             | Static Reddit/Kaggle-style dataset                                                |
| **Backend/UI**         | Devvit Web app + local Python FastAPI backend + printable report            | dashboard workflow                                                       |
| **Main outputs**       | Crisis score, sentiment, topics, risk signals, briefing, evaluation, report | Model comparison, sentiment experiments, crisis-detection tests, visual dashboard |
| **Role in submission** | Primary system demonstrated in the report and video                         | experiments on offline data                            |

The final report results are based on TrendWatch AI. The Kaggle prototype is included separately to show additional implementation work on Reddit NLP, evaluation, crisis detection, and dashboard visualisation.

## TrendWatch AI — architecture

```text
┌─────────────────────────────────────────┐
│  REDDIT (Devvit Web)                    │
│  Step 1  Scan subreddit → keywords      │
│  Step 2  Filter by brand/topic keyword  │
│  Step 3  Export matched posts as JSON   │
└──────────────────┬──────────────────────┘
                   │ paste JSON
                   ▼
┌─────────────────────────────────────────┐
│  PYTHON (FastAPI localhost:8000)        │
│  Preprocess → NER/POS → Sentiment       │
│  Topics → Trends → Crisis → RAG → Report│
└─────────────────────────────────────────┘
```

* Hybrid design separates Reddit-native collection from heavier Python NLP processing.
* Reproducible workflow: the same exported JSON can regenerate the backend report.
* Main output: printable report with charts, crisis score, briefing, evaluation, and agent trace.


## NLP pipeline in the main system

**Basic NLP**

* Preprocessing
* Regex risk extraction
* NER + POS tagging
* VADER sentiment
* TF-IDF + Logistic Regression
* Temporal trend analysis

**Advanced NLP / LLM-related components**

* Sentiment ensemble
* Embedding-based topic clustering
* Semantic similarity
* RAG-grounded briefing
* ReAct-style agent trace
* Automated evaluation
* Multi-signal crisis scoring


## Supporting Kaggle Reddit prototype

* Separate static Reddit dataset prototype developed by Sharon and Rajath.
* Explores offline Reddit NLP experiments, model comparison, crisis detection, and dashboard visualisation.
* Includes techniques such as traditional classifiers, RoBERTa sentiment inference, RAG-style retrieval, multilingual analysis, and dashboard outputs.
* Included as supporting contribution evidence, not as the source of the final TrendWatch AI case-study results.
