"""Shared paths and loaders for one well per row."""
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image
from tifffile import TiffFile, imread

DATA = Path("data")
OUT = Path("outputs")
FIG = OUT / "figures"
SEED = 42


def visible_files(folder, pattern):
    # Skip archive bookkeeping such as __MACOSX and .svn.
    return sorted(
        p for p in folder.rglob(pattern)
        if not any(part.startswith(".") or part == "__MACOSX"
                   for part in p.relative_to(folder).parts)
    )


def inventory():
    images = visible_files(DATA / "BBBC010_v2_images", "*.tif")
    masks = visible_files(DATA / "BBBC010_v1_foreground", "*_binary.png")
    return images, masks


def labels():
    return pd.read_csv(DATA / "labels.csv").sort_values("well").reset_index(drop=True)


def image_pairs():
    images, masks = inventory()
    by_name = {path.name: path for path in images}
    by_well = {path.name.split("_")[0]: path for path in masks}
    fluorescence = {path.name.split("_")[6]: path for path in images if "_w1_" in path.name}
    for row in labels().itertuples(index=False):
        yield row, by_name[row.filename], fluorescence[row.well], by_well[row.well]


def read_mask(path):
    with Image.open(path) as image:
        return np.asarray(image.convert("L")) > 0


def read_image(path):
    return imread(path)


def display_range(image):
    return dict(zip(("vmin", "vmax"), np.percentile(image, [1, 99])))



def illumination(path):
    with TiffFile(path) as tif:
        tag = tif.pages[0].tags.get("UIC1tag")
        if tag is None:
            return None, "missing", None
        metadata = tag.value
    return metadata["StageLabel"][0], metadata["Name"], metadata["wavelength"]
