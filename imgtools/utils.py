"""Common utilities."""
from typing import Final

import numpy as np
from PIL import Image
from PIL.ImageFilter import BoxBlur

# Images will be resized to this before applying SSIM (must be larger than
# `WIN_SIZE`).
SSIM_SIZE: Final = (64, 64)
K1: Final = 0.01  # Algorithm parameter K1 (small constant, see the SSIM paper)
K2: Final = 0.03  # Algorithm parameter K2 (small constant, see the SSIM paper)
# The side-length of the sliding window used in comparison (must be odd)
WIN_SIZE: Final = 7
SSIM_THRESH: Final = 0.9  # SSIM threshold for marking as duplicate


def dhash(img: np.ndarray, bits: int = 64) -> bytes:
    """Compute d-hash of an image.

    Args:
        img: The input image as a 3D RGB image
        bits: The number of bits in the hash

    Returns:
        The d-hash of the image
    """
    width = int(np.sqrt(bits))
    if width ** 2 != bits:
        raise ValueError("Number of bits must be a perfect square")

    pillow = Image.fromarray(img)
    # Resize image to `width` x `width` with an extra column.
    # This extra column is added because the difference b/w two pixels is
    # calculated along rows. This results in differences one less than the no.
    # of columns in a row.
    pillow = pillow.convert("L").resize((width + 1, width), Image.BICUBIC)
    img = np.array(pillow)

    # Binarize the difference b/w two row-adjacent pixels
    diff = img[:, :-1] > img[:, 1:]
    # Flatten and pack the bools into bytes, ie 8 bools become one uint8 byte
    binary = np.packbits(diff)
    # Get the binary hash as a bytes string
    return binary.tobytes()


def _preprocess(
    img: Image.Image, size: tuple[int, int] = SSIM_SIZE
) -> np.ndarray:
    """Pre-process the image for SSIM.

    This converts into the following:
        * Grayscale
        * float64 in [0, 1]

    Args:
        img: The PIL image
        size: The size to which the image should be resized

    Returns:
        The pre-processed float64 ndarray image
    """
    img = img.convert("L")  # grayscale
    img = img.resize(SSIM_SIZE, resample=Image.BICUBIC)
    return np.array(img) / 255.0


def _filter(img: np.ndarray) -> np.ndarray:
    """Apply a uniform filter to the image.

    Args:
        img: The float64 grayscale image in [0, 1]

    Returns:
        The filtered float64 ndarray image in [0, 1]
    """
    grey = (img * 255).astype(np.uint8)
    orig = Image.fromarray(grey)
    filtered = orig.filter(BoxBlur(WIN_SIZE))
    return np.array(filtered) / 255.0


def ssim(img1: Image.Image, img2: Image.Image) -> float:
    """Compute the mean structural similarity index between two images.

    This code was adapted from the SSIM code in the scikit-image library:
    https://github.com/scikit-image/scikit-image/blob/master/skimage/metrics/_structural_similarity.py

    Arguments:
        img1, arr2: The input images of the same shape

    Returns:
        The mean structural similarity index over the image.
    """
    # Preprocess images for SSIM
    arr1 = _preprocess(img1)
    arr2 = _preprocess(img2)

    # Filter is already normalized by NP
    NP = WIN_SIZE ** 2
    cov_norm = NP / (NP - 1)  # sample covariance

    # Compute (weighted) means
    ux = _filter(arr1)
    uy = _filter(arr2)

    # Compute (weighted) variances and covariances
    uxx = _filter(arr1 * arr1)
    uyy = _filter(arr2 * arr2)
    uxy = _filter(arr1 * arr2)
    vx = cov_norm * (uxx - ux * ux)
    vy = cov_norm * (uyy - uy * uy)
    vxy = cov_norm * (uxy - ux * uy)

    C1 = K1 ** 2
    C2 = K2 ** 2

    A1 = 2 * ux * uy + C1
    A2 = 2 * vxy + C2
    B1 = ux ** 2 + uy ** 2 + C1
    B2 = vx + vy + C2
    D = B1 * B2
    S = (A1 * A2) / D

    # To avoid edge effects will ignore filter radius strip around edges
    pad = (WIN_SIZE - 1) // 2

    # Compute (weighted) mean of ssim
    mssim = S[pad:-pad, pad:-pad].mean()

    return mssim
