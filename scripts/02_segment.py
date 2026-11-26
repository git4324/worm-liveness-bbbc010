"""Score predicted foreground and show the three best and worst wells."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np
import pandas as pd

from segmentation import overlap, segment
from study import FIG, OUT, display_range, image_pairs, read_image, read_mask


def overlay(ax, image, predicted, reference):
    ax.imshow(image, cmap="gray", **display_range(image))
    colors = np.zeros((*image.shape, 4))
    colors[predicted & reference] = (0.15, 0.82, 0.58, 0.73)
    colors[predicted & ~reference] = (1.0, 0.50, 0.10, 0.80)
    colors[reference & ~predicted] = (0.34, 0.64, 1.0, 0.85)
    ax.imshow(colors)
    ax.axis("off")


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    rows, layers = [], {}
    for row, bf, _, mask in image_pairs():
        image = read_image(bf)
        predicted = segment(image)
        reference = read_mask(mask)
        dice, iou = overlap(predicted, reference)
        rows.append(dict(well=row.well, group=row.group, dice=dice, iou=iou))
        layers[row.well] = (image, predicted, reference)
    scores = pd.DataFrame(rows)
    scores.to_csv(OUT / "segmentation_scores.csv", index=False)
    print(scores[["dice", "iou"]].describe().round(3).to_string())
    print(scores.groupby("group")[["dice", "iou"]].mean().round(3).to_string())
    ranked = scores.sort_values(["dice", "well"])
    extremes = pd.concat([ranked.tail(3).iloc[::-1], ranked.head(3)])
    fig, axes = plt.subplots(2, 3, figsize=(12, 7), layout="constrained")
    fig.suptitle("Foreground segmentation · three highest and three lowest Dice")
    for ax, row in zip(axes.flat, extremes.itertuples(index=False)):
        overlay(ax, *layers[row.well])
        ax.set_title(f"{row.well} · {row.group} · Dice {row.dice:.2f}")
    legend = [Patch(color=color, label=label) for color, label in
              [("#26d194", "Overlap"), ("#ff801a", "Extra pixels"), ("#57a3ff", "Missed pixels")]]
    fig.legend(handles=legend, loc="outside lower center", ncol=3)
    fig.savefig(FIG / "segmentation_overlays.png", dpi=140)
    plt.close(fig)


if __name__ == "__main__":
    main()
