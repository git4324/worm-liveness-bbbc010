# How the worm image project works

The question was simple. Can two pictures of a well tell us whether it got ampicillin? The answer on this plate was yes, but the background also gave away a lot. The labels came from plate columns and tell us which treatment each well received. Treated wells mostly contained live worms, and untreated wells mostly contained dead worms. Each well could contain a mix, and the data leave individual worm viability unknown.

OpenAI Codex helped write and run the Python code, make the plots and draft the explanations. The models actually trained in the experiment were logistic regression, a random forest and a small convolutional neural network (CNN).

## 0. Save a version with Git

A commit is a saved version of the code, write-up and results. The project lives on the `main` branch. Anyone who downloads it can use the first script to get the original data from BBBC.

1. What does a commit save?
2. Why is the `data/` folder ignored by Git?
3. What happens when you push a commit?

## 1. Figure out which files go together

`00_download.py` fetches the three ZIP files. `01_explore.py` checks the image files, matches them with the masks, and writes a label sheet called `data/labels.csv`. For example, both A01 images belong with `A01_binary.png`. The number in the well ID gives its column, which determines its treatment group.

The image tags settle a detail the website describes differently. In the downloaded data, `w2` is transmitted light and `w1` is TRITC fluorescence. One `w2` image had no tag, so its filename was used to pair it.

1. Which files belong to A13, and which group is it in?
2. How do you know which channel is which?
3. What does the A13 label tell you about an individual worm in that well?

## 2. Look at the images

`01_examples.py` picks three wells from each group using a fixed random seed, so the examples are the same whenever the script runs. In the figure, many worms in treated wells bend or curl. More worms in the untreated wells look straight. The figure adjusts contrast for each picture separately, so compare measured intensity in the feature table.

1. Why look at the pictures before writing the analysis?
2. What shape difference can you see in the examples?
3. What would you need to see whether a worm moved?

## 3. Mark the pixels that look like worms

`02_segment.py` uses `segmentation.py` to smooth the brightfield picture and estimate its background. It trims the rim and looks for pixels that are darker than their surroundings. Otsu's method picks the cutoff from the image values. A few cleanup steps connect short gaps, fill holes and remove tiny regions.

The script compares the predicted mask with the corrected mask. Dice averaged 0.720 and IoU averaged 0.573. Both numbers measure overlap and reach 1 when the masks agree exactly. In the low-scoring overlays, you can see worms that the script missed near the edge.

1. What problem does estimating the background help with?
2. What do Dice and IoU compare?
3. Why are the 81% and 94% from the published paper a separate result?

## 4. Describe the regions with numbers

`03_features.py` uses `regionprops` to measure each connected region. For example, the major and minor axes describe the length and width of an ellipse fitted to the region. Their ratio is elongation. Solidity compares a region's area with the area it would cover if you stretched a tight rubber band around it.

The script takes the median of each measurement across regions in a well and keeps a region count. For fluorescence, it first calculates mean intensity within each region and then takes the median across regions. One region can come from part of a worm or a group of touching worms. In each feature plot, the height of a curve tells you what fraction of wells are at or below a value.

1. What does higher elongation mean?
2. Why use a median instead of a mean to describe a typical region?
3. How can two worms end up in one region?

## 5. Train the models that use measurements

`04_classify.py` uses `evaluation.py` to train and test scikit-learn logistic regression and a random forest. Logistic regression learns weights for the nine measurements and combines them into a treatment score. The random forest learns 150 decision trees from the same measurements. Both predict whether a well got ampicillin.

In each fold, the models learn from 80 wells and are tested on the other 20. The analysis runs five folds three times, using new groupings for each repeat. Accuracy is the fraction of correct calls. Balanced accuracy gives equal weight to both groups. ROC AUC describes how well the model ranks treated wells above untreated wells. A confusion matrix shows which calls were right and which group the mistakes came from.

Both feature models reached 100% accuracy on this plate. Then a model using only brightness and pixel variation outside the wells reached 95%. That result makes it harder to tell how much of the high accuracy comes from the worms. The script also shuffles one feature at a time within the test wells to see how much ROC AUC drops. The largest drops were small, partly because related features can carry similar information.

1. Why should both pictures from a well stay together when splitting the data?
2. What did the outside-well test reveal?
3. How does shuffling a feature help you check its importance?

## 6. Train a small network that sees pictures

`05_cnn.py` trains the PyTorch CNN in `small_cnn.py`. It receives two resized images per well. Its filters learn patterns in small groups of pixels, and the network combines those patterns into a treatment score. It trains for 16 passes through the training data, starting with random weights in every fold. The CNN reached 99.3% accuracy on the same test wells as the feature models.

1. What goes into the CNN, and what does it predict?
2. Why compare the models using the same splits?
3. What could you learn by testing the models on a new plate?

## 7. Try training with some wrong labels

`06_noise.py` changes the treatment labels on 0%, 10%, 20% or 30% of the training wells. Logistic regression and the CNN receive the same changes, and the test labels stay fixed. With 30% flipped, logistic regression reached 91.3% and the CNN reached 95.7%. The experiment shows how the models react when the training table has mistakes. It leaves open how many live or dead worms are actually in each well.

1. Which labels were flipped?
2. Why keep the test labels fixed?
3. How is a flipped label different from a treated well containing some dead worms?

## 8. Explain the result in your own words

The README has the full results and the commands to rerun them. The application notes offer ways to describe the project. Try explaining the outside-well result before talking about the 100% accuracy. It matters because the models could find a treatment signal even in parts of the pictures without marked worms.

1. What exactly did the classifiers predict?
2. What makes it hard to know if they would work on another plate?
3. Which result would you mention alongside the 100% accuracy?

## Answer key

| Step | 1 | 2 | 3 |
| --- | --- | --- | --- |
| 0 | A snapshot of the staged files. | The script can download the large data files when needed. | The commit is sent to the remote repository. |
| 1 | The two A13 TIFFs and `A13_binary.png`. Column 13 is untreated. | The TIFF acquisition tags identify TRITC and transmitted light. The well ID pairs the files. | It tells you which treatment the well got. The worm's viability is unknown. |
| 2 | Seeing the images helps identify visible patterns and problems before choosing measurements. | Many treated outlines curve, and many untreated outlines look like rods. | Images of the same well captured at different times. |
| 3 | It helps account for uneven lighting. | Predicted foreground pixels and the corrected foreground pixels. | The paper checked individual worms after separating touching worms. |
| 4 | The region is longer relative to its width. | An unusually large or small value has less influence. | Touching or overlapping pixels can connect the worms. |
| 5 | It keeps the model from seeing a second view of a test well during training. | Background brightness or variation carries information about the group. | A drop in AUC shows how much the score depended on that measurement in this test. |
| 6 | Brightfield and TRITC images go in. A treatment score for the well comes out. | It gives every model the same test cases. | Whether the results carry over to an independent set of wells and imaging conditions. |
| 7 | Only the treatment labels in the training fold. | It gives each experiment the same target to score against. | A flip deliberately changes the recorded treatment. A treated well can contain dead worms even when its treatment label is correct. |
| 8 | Whether each well got ampicillin. | There is just one plate, and treatment follows column position. | The model trained on outside-well pixels reached 95%. |
