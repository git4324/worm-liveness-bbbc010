# BBBC010 project explainer

The project asks whether a computer can tell which wells got ampicillin from two pictures of each well. The labels come from plate columns and record **treatment**. Treated wells contain mostly live worms and untreated wells contain mostly dead worms. The images provide no confirmed live/dead label for an individual worm.

## 0. Save the project with Git

Git stores snapshots called commits. The project uses a branch called `main`. The `data/` folder stays on your computer and GitHub can show the code, small result tables and plots. The download script gets the same source data for someone who clones the project.

1. What does a commit save?
2. Why is `data/` in `.gitignore`?
3. What does pushing do?

## 1. Download, inspect and label

`00_download.py` downloads the three official ZIPs. `01_explore.py` checks the real TIFFs, reads their acquisition tags, matches files by well and writes `data/labels.csv`. Each well has two images and a human-corrected foreground mask. The file called `A01_binary.png` matches the well token `A01` in both TIFFs. The digits give the column. The tags identify `w2` as transmitted light and `w1` as TRITC fluorescence in the downloaded release. One `w2` file lacks the tag and was paired using its filename.

1. Which files belong to well `A13`, and what is its label?
2. What evidence identifies the two imaging channels?
3. What can the label tell you about one particular worm?

## 2. Look at both pictures

`01_examples.py` uses a fixed seed to pick three wells per group and saves both views of each. Many worm outlines curve in the treated examples. Many untreated worm outlines look like rods. A single frame shows posture. Measuring motion would require multiple frames at different times. The display stretches contrast separately for each panel, so use `features.csv` to compare measured intensities.

1. Why look at example images before measuring them?
2. Which shape differences can you see?
3. What extra data would you need to measure motion?

## 3. Find worm pixels

`02_segment.py` calls `segmentation.py` to smooth the transmitted-light image, estimate background, trim the rim and mark pixels that are dark relative to their surroundings. A threshold chosen by Otsu's method splits low and high darkness values. Closing bridges short gaps, hole filling closes enclosed holes and the size filter removes tiny specks. The script compares the resulting mask with the corrected mask. Dice averaged 0.720 and IoU averaged 0.573. The low-scoring examples show missed worms along the rim.

1. Why subtract the smoothed background?
2. What do Dice and IoU measure?
3. Why do the paper's 81% and 94% answer a different question?

## 4. Turn regions into numbers

`03_features.py` uses `regionprops` to measure each connected group of marked pixels. It records region count and the median of each measurement per well. The major and minor axes are the long and short axes of an ellipse fitted to a region. Elongation divides the two. Solidity compares the area with the area of the smallest convex shape that encloses the region. The fluorescence summary takes the median of the mean TRITC intensity measured within each region. A segmented region may be a fragment or several touching worms. In the distribution plot, each curve gives the fraction of wells at or below a value.

1. What does a large elongation value mean?
2. Why use medians to summarize regions?
3. Why can one region contain multiple worms?

## 5. Classify wells and check what the models could learn

`04_classify.py` trains logistic regression and random forests with helpers in `evaluation.py`. Logistic regression combines scaled measurements into a treatment score. The forest combines votes from decision trees. One fold trains on 80 wells and tests on the other 20. Three repeats give 15 folds. Accuracy counts correct predictions, balanced accuracy averages the two groups' correct-prediction rates, and ROC AUC measures how well the scores rank treated wells above untreated wells. A confusion matrix counts correct and incorrect group predictions.

Both models scored 100% on this plate. A model using only pixels outside the wells reached 95%. This is a warning that whole-well results may reflect image background and plate position as well as worm appearance. Permutation importance shuffles one feature in a test fold to see how much AUC falls. The strongest drops were small and related features can substitute for one another.

1. Why keep both channels and all regions from a well in the same fold?
2. What does 95% accuracy from outside-well pixels tell you?
3. What does permutation importance measure?

## 6. Let a small network learn from pixels

`05_cnn.py` trains the network in `small_cnn.py` on the same splits. A convolution scans small patches for patterns. The network combines patterns across the resized image and produces a treatment score. It uses both channels, so it can see image patterns the hand-measured models omit, including background. The CNN reached 99.3% accuracy, with two treated wells called untreated across the three repeats. The models share the same one-plate limitation.

1. What does the CNN receive as input?
2. Why use the same splits across models?
3. What would an independent plate add to the comparison?

## 7. Flip some training labels

`06_noise.py` switches 0%, 10%, 20% or 30% of training wells to the opposite group, then fits a fresh logistic model and CNN. It uses the same flips for both models and evaluates each on the original test labels. At 30% flips, accuracy fell to 91.3% for logistic regression and 95.7% for the CNN. This simulates errors in the treatment labels. A correctly labeled treated well can still contain a mixture of live and dead worms.

1. Which labels are flipped?
2. Why keep each test label unchanged?
3. How does this experiment differ from the biological label ambiguity?

## 8. Explain what the results support

The README records the data, methods, results, reproduction commands and limits. `APPLICATION_NOTES.md` gives wording you can adapt once you have rerun and explained the analysis yourself. Focus on the measured results, the channel check, and how the outside-well control changed the interpretation.

1. What outcome did the study measure?
2. Which limitation matters most for applying the results elsewhere?
3. What result would you mention alongside the 100% accuracy?

## Answer key

| Step | 1 | 2 | 3 |
| --- | --- | --- | --- |
| 0 | A snapshot of staged project files. | The script retrieves the large source files as needed. | It publishes local commits to a remote repository. |
| 1 | Both `A13` TIFFs and `A13_binary.png`. Column 13 is untreated. | The TIFF tags and the matching well tokens. | The well's treatment group. That leaves individual viability unverified. |
| 2 | To check what the channels and worm shapes look like and spot artifacts. | More curved outlines in treated examples and more rods in untreated examples. | A time series of the same well. |
| 3 | It reduces the effect of uneven illumination. | Overlap between predicted and corrected foreground pixels. | The paper scored individual worms after separating clusters. |
| 4 | The region is long relative to its width. | One extremely large or small region has less influence. | Worms can touch or overlap, so their pixels connect. |
| 5 | Otherwise the model could see part of the test well during training. | The background itself carries treatment-group information. | The loss in test AUC when a feature's values are shuffled across wells. |
| 6 | Two resized images per well. | It gives models the same train and test wells. | A check of whether the result carries to new images and imaging conditions. |
| 7 | Only the training wells' treatment labels. | All runs should be scored against the same targets. | Random flips change the recorded group. The biological ambiguity comes from mixed viability within a well. |
| 8 | Prediction of the well's treatment group and overlap with foreground masks. | The whole dataset comes from a plate where treatment follows column. | Outside-well pixels alone yielded 95%, showing a possible shortcut. |
