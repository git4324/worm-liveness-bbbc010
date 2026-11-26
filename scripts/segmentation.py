"""A fixed, explainable transmitted-light foreground baseline."""
from scipy import ndimage as ndi
from skimage.filters import threshold_otsu
from skimage.morphology import closing, disk, remove_small_objects


def segment(image):
    # Mask out the black surround and trim the sharp rim before thresholding.
    smooth = ndi.gaussian_filter(image.astype("float32"), sigma=1)
    background = ndi.gaussian_filter(smooth, sigma=12)
    inside = background > threshold_otsu(background)
    inside = ndi.binary_erosion(inside, structure=disk(10))
    darkness = background - smooth
    foreground = inside & (darkness > threshold_otsu(darkness[inside]))
    foreground = closing(foreground, disk(3))
    foreground = ndi.binary_fill_holes(foreground) & inside
    return remove_small_objects(foreground, max_size=79)


def overlap(predicted, reference):
    shared = (predicted & reference).sum()
    union = (predicted | reference).sum()
    total = predicted.sum() + reference.sum()
    return 2 * shared / total if total else 1.0, shared / union if union else 1.0
