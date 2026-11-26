"""A fixed, explainable brightfield foreground baseline."""
from scipy import ndimage as ndi
from skimage.filters import threshold_otsu
from skimage.measure import label
from skimage.morphology import binary_closing, disk, remove_small_objects


def segment(image):
    # Compare a lightly smoothed pixel to its surroundings to reduce shading.
    smooth = ndi.gaussian_filter(image.astype("float32"), sigma=1)
    background = ndi.gaussian_filter(smooth, sigma=12)
    darkness = background - smooth
    foreground = darkness > threshold_otsu(darkness)
    foreground = binary_closing(foreground, disk(3))
    foreground = ndi.binary_fill_holes(foreground)
    return remove_small_objects(label(foreground), max_size=79) > 0


def overlap(predicted, reference):
    shared = (predicted & reference).sum()
    union = (predicted | reference).sum()
    total = predicted.sum() + reference.sum()
    return 2 * shared / total if total else 1.0, shared / union if union else 1.0

