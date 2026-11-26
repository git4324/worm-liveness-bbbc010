"""Plot six randomly selected wells, with both TIFF channels side by side."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from study import FIG, SEED, display_range, image_pairs, labels, read_image


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    chosen = labels().groupby("group").sample(n=3, random_state=SEED)
    pairs = {row.well: (bf, fluorescence) for row, bf, fluorescence, _ in image_pairs()}
    fig, axes = plt.subplots(2, 6, figsize=(14, 4.7), layout="constrained")
    fig.suptitle("BBBC010 example wells · treatment labels")
    for row_index, (_, group) in enumerate(chosen.groupby("group")):
        for i, row in enumerate(group.itertuples(index=False)):
            for j, (path, channel) in enumerate(zip(pairs[row.well], ["Brightfield", "TRITC"])):
                ax = axes[row_index, 2 * i + j]
                image = read_image(path)
                ax.imshow(image, cmap="gray", **display_range(image))
                ax.set_title(f"{row.well} {row.group}\n{channel}", fontsize=9)
                ax.axis("off")
    fig.savefig(FIG / "examples.png", dpi=145)
    plt.close(fig)


if __name__ == "__main__":
    main()

