# worm-liveness-bbbc010

Can simple, explainable image features separate ampicillin-treated (mostly live) from
untreated (mostly dead) C. elegans wells in the BBBC010 dataset?

## Data
BBBC010 (Broad Bioimage Benchmark Collection), 100 images from one 384-well plate, CC0.
Labels are by plate COLUMN (treatment level), not per worm, so label noise is built in.
Human-corrected foreground masks are provided for scoring segmentation.

## Status
- [ ] Download and explore data
- [ ] Segmentation scored against provided masks (Dice)
- [ ] Features + classifier (cross-validate by well)
- [ ] Small model + label-noise experiment
- [ ] Limits and write-up

## Run
    python -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    python scripts/00_download.py
    python scripts/01_explore.py

## Limits (keep updated)
Treatment-level labels are noisy. Published benchmark numbers (Wahlby 2012: 81% automatic
foreground, 94% corrected) are compared against only after checking they measure the same thing.
