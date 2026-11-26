"""Inspect the archive, prove the pairing, and write column-derived labels."""
from collections import Counter
from hashlib import sha256
import re

import numpy as np
import pandas as pd

from study import DATA, illumination, inventory, read_image, read_mask, visible_files

PATTERN = re.compile(r"1649_1109_0003_Amp5-1_B_20070424_([A-P]\d{2})_w([12])_[\w-]+\.tif")


def main():
    images, masks = inventory()
    raw_tiffs = list((DATA / "BBBC010_v2_images").rglob("*.tif"))
    instances = visible_files(DATA / "BBBC010_v1_foreground_eachworm", "*_ground_truth.png")
    print(f"TIFF-named files: {len(raw_tiffs)}; actual TIFFs: {len(images)}")
    print(f"Well foreground masks: {len(masks)}; individual outlines: {len(instances)}")
    paths = {}
    fingerprints = {1: set(), 2: set()}
    duplicate_counts = Counter()
    modes = Counter()
    for path in images:
        match = PATTERN.fullmatch(path.name)
        if match is None:
            raise ValueError(f"Unexpected filename: {path.name}")
        well, channel = match[1], int(match[2])
        if (well, channel) in paths:
            raise ValueError(f"Repeated channel in well {well}")
        paths[well, channel] = path
        stage_well, mode, wavelength = illumination(path)
        if stage_well is None:
            print("No acquisition tag; paired by filename:", path.name)
        else:
            assert stage_well == well, path
        modes[channel, mode, wavelength] += 1
        image = read_image(path)
        assert image.shape == (520, 696) and image.dtype == np.uint16, path
        digest = sha256(image.tobytes()).digest()
        duplicate_counts[channel] += digest in fingerprints[channel]
        fingerprints[channel].add(digest)
    wells = sorted({well for well, _ in paths})
    mask_by_well = {p.name.split("_")[0]: p for p in masks}
    assert len(wells) == len(masks) == 100
    assert set(wells) == set(mask_by_well) == {p.name.split("_")[0] for p in instances}
    assert all((well, channel) in paths for well in wells for channel in (1, 2))
    assert all(read_mask(p).shape == (520, 696) for p in masks)
    print("Filename tokens _<well>_w1_ and _<well>_w2_ match each <well>_binary.png.")
    print("TIFF metadata by filename channel:", dict(modes))
    assert modes == {(1, "TRITC", 600): 100, (2, "Tansmitted light", 0): 99, (2, "missing", None): 1}
    print("All available TIFF StageLabel tags match the filename well.")
    print("The page channel description conflicts with the v2 TIFF tags.")
    print("Using w2 transmitted light as brightfield and w1 as TRITC fluorescence.")
    print("Each image is 520 rows × 696 columns, uint16.")
    print("Exact pixel duplicates across wells:", dict(duplicate_counts))
    rows = []
    for well in wells:
        column = int(well[1:])
        assert 1 <= column <= 24
        group = "treated" if column <= 12 else "untreated"
        if well in {"A01", "A12", "A13", "A24"}:
            print(paths[well, 1].name, paths[well, 2].name,
                  mask_by_well[well].name, f"→ column {column}, {group}")
        rows.append(dict(filename=paths[well, 2].name, well=well, column=column, group=group))
    table = pd.DataFrame(rows)
    table.to_csv(DATA / "labels.csv", index=False)
    print("Wells per group:", table.group.value_counts().to_dict())
    print("These are treatment-level labels. Individual worm viability is unknown.")


if __name__ == "__main__":
    main()

