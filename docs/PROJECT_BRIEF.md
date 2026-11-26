# Can Simple Image Features Tell Treated from Untreated Worm Wells?

## Summary

I started this project in November 2026 to learn how to analyze microscope images with Python. I used BBBC010, a public dataset of *C. elegans* worms, to ask whether simple measurements of shape and fluorescence could tell which wells received ampicillin. I compared two models that use those measurements with a small neural network that learns from the images directly. I also tested how both approaches held up when some of their training labels were deliberately changed.

## Research question

Which measurements help separate treated from untreated wells, and how well do simple feature-based models do compared with a small neural network?

## Data

BBBC010 contains 100 wells from one 384-well plate, with two microscope images per well. The TIFF tags identify the channels as brightfield and TRITC fluorescence. The dataset also includes human-corrected masks that mark worm pixels. [BBBC010 dataset](https://bbbc.broadinstitute.org/BBBC010)

The treated wells mostly contain live worms, and the untreated wells mostly contain dead worms. The label comes from the well's plate column and records whether it received ampicillin. Each well can contain a mix of live and dead worms, and the viability of individual worms is unknown.

## Methods

1. I used a Python workflow to predict which pixels in each brightfield image belonged to worms. The script smooths the image, finds pixels that are darker than their surroundings, and cleans up the mask. I compared the predicted masks with the corrected masks using Dice, a measure of pixel overlap.
2. The script measured the size, shape, and fluorescence of each connected region, then summarized those measurements for each well. A connected region can contain a whole worm, part of a worm, or several touching worms.
3. Logistic regression and a random forest were trained on the well measurements. A small convolutional neural network (CNN) trained from scratch on the two images per well. All three models used the same splits, with 80 wells for training and 20 for testing in each fold.
4. To see how training-label errors changed the results, I compared logistic regression and the CNN after randomly flipping 0%, 10%, 20%, or 30% of the training labels. The test labels stayed the same.

## Results

| Model | Test accuracy, mean ± SD | ROC AUC, mean ± SD |
| --- | ---: | ---: |
| Logistic regression | 100.0% ± 0.0 percentage points | 1.000 ± 0.000 |
| Random forest | 100.0% ± 0.0 percentage points | 1.000 ± 0.000 |
| Small CNN | 99.3% ± 1.8 percentage points | 1.000 ± 0.000 |

The biggest surprise was that a model using only pixels **outside the wells** reached 95% accuracy. The image background carried information about treatment group even where the corrected masks showed no worms. That makes it hard to tell how much of the high accuracy came from worm appearance.

When 30% of the training labels were flipped, accuracy fell to 91.3% for logistic regression and 95.7% for the CNN. The CNN lost less accuracy at that setting on this plate.

### What the segmentation overlays show

The masks averaged **0.720 Dice** across the 100 wells, with a standard deviation of **0.107**. In the overlay for untreated well **B13**, which scored **0.299 Dice**, several worm shapes near the rim appear blue. Those are pixels the corrected mask marked as worms that the script missed. Trimming the rim helps remove the well boundary, but it can also remove worms close to that boundary. Mean Dice was **0.775 for treated wells** and **0.661 for untreated wells**, so the quality of the masks could affect the comparison between groups. [Segmentation overlays](../outputs/figures/segmentation_overlays.png)

## Why this matters and what I would try next

Microscope images can show clear differences by eye, but turning those differences into reliable measurements takes more than getting a high accuracy score. In this project, the overlays showed where the segmentation failed, and the background test showed that the images carried clues beyond the worms themselves.

The experiment used one plate, where treatment followed column position, and each test fold had only 20 wells. I would first test whether a narrower rim trim recovers more worm pixels in wells like B13 without adding too many pixels from the well boundary. Then I would test the classifiers on a second plate with treatments spread across different columns. The published benchmark scores individual worms after separating overlapping worms, while this project's Dice scores measure foreground pixel overlap across each well. [Wählby et al., 2012](https://pmc.ncbi.nlm.nih.gov/articles/PMC3433711/)

## AI use

I wrote the original project brief and used OpenAI Codex to help revise it. Codex also helped write and run the Python analysis, generate the figures, and draft and revise the repository documentation.
