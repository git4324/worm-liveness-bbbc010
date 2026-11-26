"""Shared splits, feature models and metrics for comparable experiments."""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix, roc_auc_score
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from study import OUT, SEED, labels

FOLDS = 5
REPEATS = 3
METRICS = ["accuracy", "balanced_accuracy", "roc_auc"]


def load_features():
    table = pd.read_csv(OUT / "features.csv").sort_values("well").reset_index(drop=True)
    if table.well.duplicated().any() or not table[["well", "group"]].equals(labels()[["well", "group"]]):
        raise ValueError("Features must match the label table, with exactly one row per well.")
    targets = (table.group == "treated").astype(int).to_numpy()
    return table.well.to_numpy(), table.drop(columns=["well", "group"]), targets


def well_splits(wells, targets):
    # Each sample represents one well, with both channels already paired.
    splitter = RepeatedStratifiedKFold(n_splits=FOLDS, n_repeats=REPEATS, random_state=SEED)
    for index, (train, test) in enumerate(splitter.split(wells, targets)):
        assert not set(wells[train]) & set(wells[test])
        yield index // FOLDS + 1, index % FOLDS + 1, train, test


def logistic():
    return make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), LogisticRegression())


def forest(seed):
    return make_pipeline(SimpleImputer(strategy="median"),
                         RandomForestClassifier(n_estimators=150, min_samples_leaf=2,
                                                random_state=seed, n_jobs=1))


def score(targets, probabilities):
    predictions = probabilities >= 0.5
    tn, fp, fn, tp = confusion_matrix(targets, predictions, labels=[0, 1]).ravel()
    return dict(accuracy=accuracy_score(targets, predictions),
                balanced_accuracy=balanced_accuracy_score(targets, predictions),
                roc_auc=roc_auc_score(targets, probabilities),
                tn=tn, fp=fp, fn=fn, tp=tp)


def save_scores(rows, stem):
    table = pd.DataFrame(rows)
    table.to_csv(OUT / f"{stem}.csv", index=False)
    grouped = table.groupby("model", sort=False)
    summary = grouped[METRICS].agg(["mean", "std"])
    print(summary.round(3).to_string())
    print("Confusion totals (each well appears once per repeat):")
    print(grouped[["tn", "fp", "fn", "tp"]].sum().to_string())
