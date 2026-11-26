"""Compare a small CNN on the exact same well splits as the feature models."""
from evaluation import load_features, save_scores, score, well_splits
from small_cnn import architecture, load_pixels, predict
from study import SEED


def main():
    wells, _, y = load_features()
    pixels = load_pixels(wells)
    print("CNN trainable parameters:", sum(p.numel() for p in architecture().parameters()))
    results = []
    for repeat, fold, train, test in well_splits(wells, y):
        probabilities = predict(pixels, train, test, y[train], SEED + 10 * repeat + fold)
        metrics = score(y[test], probabilities)
        results.append(dict(model="Small CNN", repeat=repeat, fold=fold, **metrics))
        print(f"Repeat {repeat}, fold {fold}: accuracy {metrics['accuracy']:.2f}", flush=True)
    save_scores(results, "cnn_cv")


if __name__ == "__main__":
    main()

