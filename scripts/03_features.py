"""Measure segmented regions, then summarize them per well."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from skimage.measure import label, regionprops

from segmentation import segment
from study import FIG, OUT, image_pairs, read_image

REGION_PROPERTIES = {
    "area": "area",
    "perimeter": "perimeter",
    "major_axis": "axis_major_length",
    "minor_axis": "axis_minor_length",
    "eccentricity": "eccentricity",
    "solidity": "solidity",
    "mean_fluorescence": "intensity_mean",
}


def well_features(mask, fluorescence):
    regions = regionprops(label(mask), intensity_image=fluorescence)
    measurements = []
    for region in regions:
        values = {name: getattr(region, attr) for name, attr in REGION_PROPERTIES.items()}
        values["elongation"] = region.axis_major_length / max(region.axis_minor_length, 1)
        measurements.append(values)
    # Use medians to reduce the influence of one very large merged region.
    medians = pd.DataFrame(measurements, columns=[*REGION_PROPERTIES, "elongation"]).median()
    return {"region_count": len(regions), **medians.add_prefix("median_").to_dict()}


def plot_distributions(table):
    fig, axes = plt.subplots(3, 3, figsize=(11, 8), layout="constrained")
    fig.suptitle("Per-well region features by treatment group")
    for ax, feature in zip(axes.flat, table.columns[2:]):
        for group, color in [("treated", "#007d75"), ("untreated", "#bb5323")]:
            values = table.loc[table.group == group, feature].dropna()
            ax.ecdf(values, label=group, color=color)
        ax.set_xlabel(feature.replace("_", " "))
        ax.set_ylabel("Fraction of wells")
    axes.flat[0].legend(frameon=False, fontsize=8)
    fig.savefig(FIG / "feature_distributions.png", dpi=140)
    plt.close(fig)


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    rows = []
    for row, bf, fluorescence, _ in image_pairs():
        features = well_features(segment(read_image(bf)), read_image(fluorescence))
        rows.append(dict(well=row.well, group=row.group, **features))
    table = pd.DataFrame(rows)
    table.to_csv(OUT / "features.csv", index=False)
    plot_distributions(table)
    print(f"{len(table)} wells; {(table.region_count == 0).sum()} with zero regions")
    print(table.groupby("group").median(numeric_only=True).round(3).to_string())


if __name__ == "__main__":
    main()
