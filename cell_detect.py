"""
cell_detect.py - the "brain" of the Cell Counter.

One job: take an image file and return a list of (x, y) points,
one per cell it found. No window, no buttons - just detection.

It is imported and used by cell_main.py.
"""

import numpy as np
from PIL import Image
from scipy.ndimage import (
    white_tophat,
    gaussian_filter,
    maximum_filter,
    label,
    center_of_mass,
)

# ---- Tuning knobs (change these if the count comes out wrong) ----
CELL_SIZE = 15          # roughly how wide one cell is, in pixels
MIN_DISTANCE = 7        # smallest gap allowed between two cell centers
THRESHOLD_K = 2.0       # higher = stricter (fewer cells); lower = more cells
WHITE_MARGIN = 150      # brightness above this is the white border, not cells
MIN_DARK_FRACTION = 0.15  # less dark area than this = blank/title slide -> 0


def _brightness(rgb):
    """Brightness that keeps BOTH blue and white cells bright.
    For each pixel, take its strongest color channel."""
    return rgb.max(axis=2).astype(float)


def _crop_to_dark(gray):
    """Find the dark microscope rectangle and ignore the white border
    and the date label sitting out in the margin.

    Returns the (y0, x0) top-left offset of the crop and the cropped
    brightness image. If there is no clear margin, returns the whole image.
    """
    row_is_dark = gray.mean(axis=1) < WHITE_MARGIN   # rows that are mostly dark
    col_is_dark = gray.mean(axis=0) < WHITE_MARGIN   # columns that are mostly dark
    rows = np.where(row_is_dark)[0]
    cols = np.where(col_is_dark)[0]
    if len(rows) == 0 or len(cols) == 0:
        return 0, 0, gray
    y0, y1 = rows.min(), rows.max() + 1
    x0, x1 = cols.min(), cols.max() + 1
    return y0, x0, gray[y0:y1, x0:x1]


def find_cells(image_path):
    """Open an image and return a list of (x, y) cell centers, in the
    coordinates of the original full image."""
    rgb = np.asarray(Image.open(image_path).convert("RGB"))
    gray = _brightness(rgb)

    # Blank / title slides (a word like "Tamoxifen" on white) are mostly
    # bright, so they have almost no dark area. Skip them entirely.
    if (gray < WHITE_MARGIN).mean() < MIN_DARK_FRACTION:
        return []

    # 1. Crop away the white border + date label, and run the rest on
    #    the dark imaging rectangle only. Cropping first matters: it keeps
    #    the bright border out of the threshold math below.
    y0, x0, region = _crop_to_dark(gray)

    # 2. Top-hat: keep small bright blobs (cells), erase big bright areas
    #    and any smooth background glow.
    hat = white_tophat(region, size=CELL_SIZE * 2)

    # 3. Smooth a touch so grainy noise does not become fake cells.
    hat = gaussian_filter(hat, sigma=2)

    # 4. Brightness bar: only blobs clearly above the noise count.
    threshold = hat.mean() + THRESHOLD_K * hat.std()

    # 5. Peak finding: each local maximum becomes one cell. This is what
    #    splits two touching cells into two separate points.
    peak = maximum_filter(hat, size=MIN_DISTANCE)
    is_peak = (hat == peak) & (hat > threshold)

    # 6. Collapse each blob of peak pixels into one center, convert
    #    (row, col) -> (x, y), and add the crop offset back so the points
    #    line up with the full image the user sees.
    labels, count = label(is_peak)
    if count == 0:
        return []
    centers = center_of_mass(hat, labels, range(1, count + 1))
    return [(int(round(col + x0)), int(round(row + y0))) for row, col in centers]
