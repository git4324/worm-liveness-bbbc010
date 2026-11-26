"""Measure sensitivity to randomly corrupted training treatment labels."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from evaluation import load_features, logistic, score, well_splits
from small_cnn import load_pixels, predict
from study import FIG, OUT, SEED

RATES = (0.0, 0.1, 0.2, 0.3)


def plot(summary):
    fig, ax = plt.subplots(figsize=(7, 4.3), layout="constrained")
    for model, color in [("Logistic regression", "#007d75"), ("Small CNN", "#bb5323")]:
        row = summary.loc[model]
        ax.errorbar(row.index * 100, row["mean"], yerr=row["std"], color=color,
                    marker="o", capsize=4, label=model)
    ax.set(title="Sensitivity to flipped training labels",
           xlabel="Training treatment labels flipped (%)",
           ylabel="Accuracy on unchanged test labels", xticks=[0, 10, 20, 30], ylim=(0, 1.04))
    ax.legend(frameon=False)
    ax.text(0.02, 0.04, "Mean ± SD across 15 folds from three seeded repeats",
            transform=ax.transAxes, fontsize=9)
    fig.savefig(FIG / "label_noise.png", dpi=150)
    plt.close(fig)


def main():
    wells, x, y = load_features()
    pixels = load_pixels(wells)
    rows = []
    for repeat, fold, train, test in well_splits(wells, y):
        seed = SEED + 10 * repeat + fold
        # One random ordering per fold makes the flips nested across noise levels.
        order = np.random.default_rng(seed + 1000).permutation(len(train))
        for rate in RATES:
            corrupted = y[train].copy()
            count = round(rate * len(train))
            corrupted[order[:count]] ^= 1
            model = logistic().fit(x.iloc[train], corrupted)
            feature_probs = model.predict_proba(x.iloc[test])[:, 1]
            cnn_probs = predict(pixels, train, test, corrupted, seed)
            for name, probs in (("Logistic regression", feature_probs), ("Small CNN", cnn_probs)):
                rows.append(dict(model=name, repeat=repeat, fold=fold, rate=rate,
                                 flip_seed=seed + 1000, flipped=count, **score(y[test], probs)))
        print(f"Finished noise levels for repeat {repeat}, fold {fold}", flush=True)
    table = pd.DataFrame(rows)
    table.to_csv(OUT / "label_noise.csv", index=False)
    summary = table.groupby(["model", "rate"]).accuracy.agg(["mean", "std"])
    print(summary.round(3).to_string())
    plot(summary)


if __name__ == "__main__":
    main()

