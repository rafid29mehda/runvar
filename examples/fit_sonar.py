import csv
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.tree import DecisionTreeClassifier

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "sonar.csv"
OUT = ROOT / "sonar_scores.csv"


def load() -> tuple[np.ndarray, np.ndarray]:
    with DATA.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    names = [f"f{i}" for i in range(1, 61)]
    features = [[float(row[name]) for name in names] for row in rows]
    labels = [1 if row["label"] == "M" else 0 for row in rows]
    return np.array(features), np.array(labels)


def accuracy(model, features, labels, test) -> float:
    predicted = model.predict(features[test])
    return float((predicted == labels[test]).mean())


def main() -> None:
    features, labels = load()
    written: list[tuple[str, str, str, float]] = []
    for split_seed in range(10):
        splitter = StratifiedShuffleSplit(n_splits=1, test_size=0.25, random_state=split_seed)
        train, test = next(splitter.split(features, labels))
        models = (
            ("logreg", LogisticRegression(max_iter=1000, random_state=0)),
            ("tree", DecisionTreeClassifier(max_depth=3, random_state=0)),
        )
        for system, model in models:
            model.fit(features[train], labels[train])
            written.append((system, "split", str(split_seed), accuracy(model, features, labels, test)))
    splitter = StratifiedShuffleSplit(n_splits=1, test_size=0.25, random_state=0)
    train, test = next(splitter.split(features, labels))
    for model_seed in range(10):
        models = (
            ("logreg", LogisticRegression(max_iter=1000, random_state=model_seed)),
            ("tree", DecisionTreeClassifier(max_depth=3, random_state=model_seed)),
        )
        for system, model in models:
            model.fit(features[train], labels[train])
            written.append((system, "seed", str(model_seed), accuracy(model, features, labels, test)))
    with OUT.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["system", "factor", "level", "score"])
        writer.writerows(written)


if __name__ == "__main__":
    main()
