"""Evaluate measured features and check for alternative signals."""
import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance
from sklearn.model_selection import StratifiedGroupKFold

from evaluation import forest, load_features, logistic, save_scores, score, well_splits
from study import OUT, SEED, image_pairs, labels, read_image


def outside_well_features():
    # Left/right strips sit far outside the visible well in the example images.
    # Their brightness and noise can reveal acquisition differences.
    rows = []
    for _, bf, fluorescence, _ in image_pairs():
        values = []
        for path in (bf, fluorescence):
            image = read_image(path)
            for strip in (image[:, :64], image[:, -64:]):
                values.extend([np.median(strip), np.std(strip)])
        rows.append(values)
    return pd.DataFrame(rows)


def main():
    wells, x, y = load_features()
    geometry = x.drop(columns="median_mean_fluorescence")
    intensity = x[["median_mean_fluorescence"]]
    outside = outside_well_features()
    results, audit, importances = [], [], []
    for repeat, fold, train, test in well_splits(wells, y):
        info = dict(repeat=repeat, fold=fold)
        seed = SEED + 10 * repeat + fold
        for name, model in (("Logistic regression", logistic()), ("Random forest", forest(seed))):
            model.fit(x.iloc[train], y[train])
            probabilities = model.predict_proba(x.iloc[test])[:, 1]
            results.append(dict(model=name, **info, **score(y[test], probabilities)))
            importance = permutation_importance(model, x.iloc[test], y[test],
                                                scoring="roc_auc", n_repeats=12, random_state=seed)
            for feature, drop in zip(x.columns, importance.importances_mean):
                importances.append(dict(model=name, **info, feature=feature, auc_drop=drop))
        for name, values in (("Geometry and count", geometry),
                             ("Fluorescence intensity only", intensity),
                             ("Outside-well strips only", outside)):
            model = logistic().fit(values.iloc[train], y[train])
            probabilities = model.predict_proba(values.iloc[test])[:, 1]
            audit.append(dict(model=name, **info, **score(y[test], probabilities)))

    columns = labels().column.to_numpy()
    # Hold out entire columns to check for memorizing exact column-level cues.
    splitter = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=SEED)
    for fold, (train, test) in enumerate(splitter.split(x, y, columns), start=1):
        assert not set(columns[train]) & set(columns[test])
        model = logistic().fit(x.iloc[train], y[train])
        probabilities = model.predict_proba(x.iloc[test])[:, 1]
        audit.append(dict(model="All features, held-out columns", repeat=1, fold=fold,
                          **score(y[test], probabilities)))
    save_scores(results, "feature_cv")
    save_scores(audit, "artifact_checks")
    pd.DataFrame(importances).to_csv(OUT / "feature_importance.csv", index=False)
    print(pd.DataFrame(importances).groupby(["model", "feature"]).auc_drop.mean()
          .sort_values(ascending=False).round(3).to_string())


if __name__ == "__main__":
    main()

