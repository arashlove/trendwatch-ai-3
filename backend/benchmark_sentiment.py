import json
from pathlib import Path
from typing import Literal, TypedDict

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
)

from classification import SentimentClassifier
from preprocessing import prepare_posts
from sentiment import _ensemble_vote, _label_from_compound
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

SentimentLabel = Literal["positive", "neutral", "negative"]
LABELS: list[SentimentLabel] = ["positive", "neutral", "negative"]


class ModelMetrics(TypedDict):
    accuracy: float
    precision: float
    recall: float
    f1: float
    notes: str


class BenchmarkResult(TypedDict):
    n_samples: int
    label_distribution: dict[str, int]
    models: dict[str, ModelMetrics]
    per_class: dict[str, dict[str, dict[str, float]]]


def _load_gold(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["posts"]


def _load_training_texts(data_dir: Path) -> list[str]:
    texts: list[str] = []
    for name in ("microsoft.json", "dog.json", "nvidia.json"):
        fp = data_dir / name
        if not fp.exists():
            continue
        payload = json.loads(fp.read_text(encoding="utf-8"))
        prepared = prepare_posts(payload.get("posts", []))
        texts.extend(p.get("clean_text", "") for p in prepared if p.get("clean_text"))
    return texts


def _macro_metrics(y_true: list[str], y_pred: list[str]) -> tuple[float, float, float, float]:
    return (
        round(accuracy_score(y_true, y_pred), 3),
        round(
            precision_score(y_true, y_pred, average="macro", zero_division=0, labels=LABELS),
            3,
        ),
        round(
            recall_score(y_true, y_pred, average="macro", zero_division=0, labels=LABELS),
            3,
        ),
        round(f1_score(y_true, y_pred, average="macro", zero_division=0, labels=LABELS), 3),
    )


def run_benchmark(
    gold_path: Path | None = None,
    data_dir: Path | None = None,
) -> BenchmarkResult:
    root = Path(__file__).resolve().parent.parent
    gold_path = gold_path or root / "data" / "sentiment_gold.json"
    data_dir = data_dir or root / "data"

    gold_posts = _load_gold(gold_path)
    prepared = prepare_posts(
        [
            {"id": p["id"], "title": p["title"], "selftext": p.get("selftext", "")}
            for p in gold_posts
        ]
    )
    y_true = [p["human_label"] for p in gold_posts]
    texts = [p.get("clean_text", "") for p in prepared]

    analyzer = SentimentIntensityAnalyzer()
    y_vader: list[str] = []
    for text in texts:
        compound = analyzer.polarity_scores(text or "")["compound"]
        y_vader.append(_label_from_compound(compound))

    train_texts = _load_training_texts(data_dir)
    clf = SentimentClassifier()
    clf.fit(train_texts)
    lr_preds = clf.predict(texts)
    y_lr = [p["lr_label"] for p in lr_preds]

    y_ensemble: list[str] = []
    for v, lr in zip(y_vader, y_lr):
        y_ensemble.append(_ensemble_vote(v, lr))

    acc_v, prec_v, rec_v, f1_v = _macro_metrics(y_true, y_vader)
    acc_l, prec_l, rec_l, f1_l = _macro_metrics(y_true, y_lr)
    acc_e, prec_e, rec_e, f1_e = _macro_metrics(y_true, y_ensemble)

    per_class: dict[str, dict[str, dict[str, float]]] = {}
    for name, y_pred in (
        ("vader", y_vader),
        ("logistic_regression", y_lr),
        ("ensemble", y_ensemble),
    ):
        report = classification_report(
            y_true, y_pred, labels=LABELS, output_dict=True, zero_division=0
        )
        per_class[name] = {
            label: {
                "precision": round(report[label]["precision"], 3),
                "recall": round(report[label]["recall"], 3),
                "f1": round(report[label]["f1-score"], 3),
            }
            for label in LABELS
        }

    dist: dict[str, int] = {"positive": 0, "neutral": 0, "negative": 0}
    for label in y_true:
        dist[label] += 1

    return {
        "n_samples": len(gold_posts),
        "label_distribution": dist,
        "models": {
            "vader": {
                "accuracy": acc_v,
                "precision": prec_v,
                "recall": rec_v,
                "f1": f1_v,
                "notes": "Lexicon baseline; headline idiom bias (kill/killing/dangerous).",
            },
            "logistic_regression": {
                "accuracy": acc_l,
                "precision": prec_l,
                "recall": rec_l,
                "f1": f1_l,
                "notes": "TF-IDF+LR weakly supervised on VADER labels from full corpus (~140 posts).",
            },
            "ensemble": {
                "accuracy": acc_e,
                "precision": prec_e,
                "recall": rec_e,
                "f1": f1_e,
                "notes": "Majority vote; VADER+LR disagree → neutral tie-break.",
            },
        },
        "per_class": per_class,
    }


def print_benchmark_table(result: BenchmarkResult) -> None:
    print(f"Gold set: n={result['n_samples']}  distribution={result['label_distribution']}\n")
    print(f"{'Model':<22} {'Accuracy':>8} {'Precision':>10} {'Recall':>8} {'F1':>8}")
    print("-" * 58)
    for key, label in (
        ("vader", "VADER"),
        ("logistic_regression", "Logistic Regression"),
        ("ensemble", "Ensemble"),
    ):
        m = result["models"][key]
        print(
            f"{label:<22} {m['accuracy']:>8.3f} {m['precision']:>10.3f} "
            f"{m['recall']:>8.3f} {m['f1']:>8.3f}"
        )
        print(f"  Notes: {m['notes']}")


if __name__ == "__main__":
    result = run_benchmark()
    print_benchmark_table(result)
