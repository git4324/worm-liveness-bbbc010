# Can Simple Measurements Tell Treated Worm Wells from Untreated Ones?

*A computational image-analysis project using the BBBC010 C. elegans dataset*

## Why I started this

My school experiment on C. elegans taught me how to run an experiment and test it with statistics, but it also showed me how much of biology depends on what you can measure from images. I wanted to learn how researchers turn a microscope picture into numbers a computer can work with. So in November 2026 I started this project to teach myself image analysis in Python. I'm still a beginner, and I used an AI coding assistant to help me write and debug code, but I chose the question, read the results, and wrote up what they mean and what they don't.

## The question

Can simple, explainable measurements of worm shape and fluorescence separate wells treated with the antibiotic ampicillin from untreated wells? And how does that compare with a small neural network that learns straight from the pixels?

## The data

I used BBBC010, a public collection from the Broad Bioimage Benchmark Collection, contributed by Fred Ausubel and released under CC0, which means anyone can use it freely. It has 100 wells from one 384-well plate. For each well there are two 16-bit TIFF images at 696 × 520 pixels. The mask files hold 100 corrected foreground masks, which are human-drawn outlines of where the worms are, plus 1,407 outlines of individual worms.

Each filename carries a well ID like A13, and the matching mask is named A13_binary.png. All 199 TIFF stage labels I could check agreed with the filenames. Columns 1–12 gave 52 ampicillin-treated wells, which mostly contain live worms. Columns 13–24 gave 48 untreated wells, which mostly contain dead worms.

This is the most important limit of the whole project: these are treatment labels for entire wells, not labels for individual worms. A single well can hold both live and dead worms, and I don't know the true health of any individual worm.

## A detail I checked before trusting the images

The dataset page says the channels are brightfield and GFP. But the TIFF metadata tags in the version 2 download identify all 100 "w1" images as TRITC fluorescence, and 99 of the "w2" images as transmitted light (ordinary brightfield). The last w2 file, from well A24, has no tag, so I paired it by filename. I used w2 as my brightfield image and called the other channel TRITC. I checked this because a project that mislabels its own channels can't be trusted, and I'd rather catch a mismatch early than build on it.

## What I saw by eye

In six randomly chosen wells, many treated worms look curved, while straight, rod-like shapes were more common in the untreated wells. Some treated worms look straight too, so shape alone isn't a clean rule. Each picture also freezes a single moment, so measuring movement would need a series of images over time. I adjusted the contrast separately for each panel so shapes are easier to see, which means brightness shouldn't be compared across panels.

## What I trained, in plain language

I trained three models on the same task: given a new well's image measurements or pixels, predict whether it was treated with ampicillin or left untreated.

**Logistic regression** is one of the simplest models in machine learning. It gives each measurement a weight, adds them up, and turns the total into a probability of "treated." It learned these weights from one row of nine measurements per well: the number of segmented regions, plus the median of eight region features. Those features are area, perimeter, major and minor axis length (how long and how wide a fitted ellipse is), eccentricity (how stretched out the shape is), solidity (its area divided by the area of the smallest convex shape that encloses it), elongation (long axis divided by short axis), and mean TRITC fluorescence intensity inside each region. I used scikit-learn, a widely used Python library that includes standard models like this one. A "region" can be a single worm, a fragment of one, or several touching worms, which is a real weakness of my segmentation.

**A random forest** builds many decision trees, each asking a series of yes/no questions about the measurements, and averages their predicted probabilities. Mine used 150 trees on the same nine measurements. Forests can pick up more complicated patterns than logistic regression, but they are harder to explain.

**A small convolutional neural network (CNN)** looks at the images directly instead of at my hand-picked measurements. A CNN slides small filters across an image to detect edges and shapes, then stacks those into higher-level patterns. I built mine with PyTorch, an open-source library for building and training neural networks. Mine took whole-well images, contrast-scaled separately and resized to 96 × 128 pixels. It started from random weights in each cross-validation fold and trained for 16 epochs, where one epoch is one full pass through the training images, running on a regular computer processor, no special graphics card needed. It has 5,177 parameters, which are the adjustable numbers it learns. For perspective, that is tiny, since modern image models have millions or billions.

## How I tested honestly

To avoid fooling myself, I used cross-validation, where the data is split into several chunks and each chunk takes a turn as the test set while the model trains on the rest. I split by well, so the model is never tested on a well it already saw. I ran the experiments with fixed random seeds, meaning the random choices are repeated the same way so someone else can reproduce my numbers. I report results as mean ± standard deviation across 15 folds from three seeded repeats, so you can see how much the numbers wobble rather than just one best case.

## How well segmentation worked

Here, segmentation means marking the pixels that look like worms. I scored the predicted foreground against the human-corrected masks using pixel-overlap measures, Dice and IoU, both of which run from 0 (no overlap) to 1 (perfect match). The [overlay figures](outputs/figures/segmentation_overlays.png) color the overlap, the extra pixels I included by mistake, and the pixels I missed.

Mean Dice was 0.720 ± 0.107, and mean IoU was 0.573 ± 0.123 across the 100 wells. In the lowest-scoring well, B13, the mask missed several worms near the rim.

I also want to be careful about the published benchmark. The published worm-by-worm segmentation scores use a different measure than my pixel-overlap scores, so I can't claim my numbers are better or worse than theirs.

## What happened when I scrambled the labels

Real biology has messy labels, so I flipped 0%, 10%, 20% and 30% of the training labels on purpose and measured accuracy on the unchanged test labels. Both the logistic regression and the CNN lost accuracy as more labels were flipped. At 20% flipped, logistic regression scored 97.0% ± 4.6 percentage points and the CNN scored 96.7% ± 4.5. At 30%, logistic regression dropped to 91.3% ± 8.1 while the CNN held at 95.7% ± 5.0, so in this experiment the CNN handled the most label damage better. A percentage point (pp) is just one point on a 100-point scale, so "± 8.1 pp" is a fairly wide wobble.

At 0% flipped, logistic regression scored 100.0% ± 0.0 percentage points, and the CNN scored 99.3% ± 1.8. At 10% flipped, they scored 99.7% ± 1.3 and 98.7% ± 3.0, respectively. The random forest scored 100.0% ± 0.0 in the original comparison. That comparison gave all three models a mean ROC AUC of 1.000 across the 15 folds. The label-flip test used logistic regression and the CNN.

This test shows how the models cope with mistakes in my training table. It does not tell me the real mix of live and dead worms in each well, which is still unknown.

## What I can honestly conclude

First, these models separated the two treatment groups on this one plate. But the near-perfect scores should make me more suspicious, not more excited. The background check and the column layout both suggest a model could be partly picking up on plate effects, like lighting or position, instead of worm biology. For that reason I count an independent plate as essential for finding out how well any of this generalizes. As a background test, I counted how many corrected masks mark worm pixels in the 64-pixel strips along the left and right edges, which are the regions used to test whether models were reading the background. None of the 100 corrected masks marked worm pixels in those strips, yet a model trained on the strips alone reached 95% accuracy.

Second, the data support predicting treatment at the level of whole wells, not the health of individual worms.

Third, the masks affect what the feature models can even see. Worms near the rim can go missing, and touching worms can merge into one region, which changes every measurement downstream.

## What I'd do next

The most useful next step is testing on a different plate, ideally one with per-worm live/dead labels, so I can see whether any of this holds outside one plate's quirks. After that, I'd like to try tracking movement across a series of images, since curvature alone is only one moment in time. I'd also want to check whether the models are leaning on background brightness instead of the worms.

## How to reproduce it

Everything runs from the project folder with pinned dependencies and fixed seeds. I ran it with Python 3.14.5 on an Apple Silicon Mac, so other computers may give slightly different numbers. The scripts print results as they run. Labels are in data/labels.csv, score tables are in outputs/, and plots are in outputs/figures/.

## Words I used, in one place

- **Segmentation:** outlining the objects of interest in an image.
- **Feature:** a measurement taken from an image, like area or elongation.
- **Dice / IoU:** overlap scores between my outline and the human outline.
- **Logistic regression, random forest:** classic models that predict a category from measurements.
- **CNN (convolutional neural network):** a model that learns patterns directly from pixels.
- **PyTorch:** a Python library for building and training neural networks.
- **scikit-learn:** a Python library of standard machine-learning tools.
- **Epoch, parameter:** one full pass through the training data; one adjustable number inside a model.
- **Cross-validation:** repeatedly splitting data into training and test sets to check a model fairly.
- **Seed:** a fixed starting point for random choices so results can be repeated.
- **Label noise:** wrong labels in the training data.
- **TRITC:** a red fluorescent dye channel used in microscopy.
- **CC0:** a license that lets anyone freely use the data.
