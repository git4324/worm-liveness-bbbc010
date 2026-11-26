# Application notes

Use these as evidence and draft wording. Say which parts you personally reran, inspected, changed or explained, and describe any coding assistance accurately.

## Two-sentence summary

This Python project compares explainable image features with a small neural network for distinguishing ampicillin-treated from untreated wells in 100 pairs of microscopy images from one BBBC010 plate. The feature classifiers reached 100% held-out-well accuracy and the CNN reached 99.3%, but outside-well pixels alone reached 95% and the treatment-level labels leave individual worm viability unverified.

## Activities list

- Reproduced a Python workflow for pairing microscopy channels, segmenting worm-shaped foreground and measuring region shape and fluorescence.
- Compared logistic regression, a random forest and a small CNN using the same well-level splits, then tested sensitivity to flipped training labels.
- Audited the TIFF channel tags and tested for background shortcuts before interpreting the one-plate classification scores.

## Three results or lessons for a motivation statement

- The foreground mask averaged 0.720 Dice. Looking at overlays showed where a single numerical score hid a concrete problem. The baseline often missed worms close to the well rim.
- A classifier using only pixels outside the visible wells reached 95% accuracy. That made the 100% feature result a starting point for asking what the images reveal about treatment and plate position.
- With 30% of training treatment labels flipped, mean accuracy was 91.3% for logistic regression and 95.7% for the CNN. The experiment showed sensitivity to simulated errors in assigning treatment, while the real fraction of live or dead worms within each well remained unknown.
