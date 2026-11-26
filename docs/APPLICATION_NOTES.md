# Talking about the project in an application

Use these as drafts. When you describe your own work, name the parts you personally ran, inspected or explained. A straightforward disclosure is “I used OpenAI Codex to write and run the Python analysis, make the figures, and help draft and revise the write-up.”

## Two-sentence project summary

I wanted to find out if a few measurements from microscope images could tell which wells had been treated with ampicillin, so this project compared logistic regression and a random forest with a small CNN trained on two images per well. The feature models reached 100% accuracy and the CNN reached 99.3% on held-out wells from one plate, but pixels outside the wells reached 95%, and the labels only tell us the treatment of each well.

## Three short activities-list points

- Python image analysis of 100 wells from a public roundworm microscopy dataset, with measurements of shape and fluorescence.
- Comparison of logistic regression, a random forest and a small CNN trained to predict well treatment, using the same test wells.
- Checked the channel names against the TIFF tags and looked for shortcuts by testing pixels outside the wells.

## Three things worth discussing in a motivation statement

- **A score can hide where a method fails.** The mask averaged 0.720 Dice. The overlays show that some worms near the rim were missed, which helped explain one weakness of the segmentation.
- **A high score can raise a better question.** The feature models reached 100%, and the background alone reached 95%. That makes me wonder how much the models learned about worm shape and how much came from the way the plate was imaged.
- **Label mistakes affected the two models differently.** When 30% of training labels were flipped, logistic regression fell to 91.3% and the CNN fell to 95.7%. This tests errors in recording treatment. The individual worms' live or dead status is still unknown.
