"""Delete all duplicate images in a directory."""
from argparse import Namespace
from collections.abc import Iterator
from multiprocessing import Pool
from pathlib import Path
from typing import Final
from warnings import warn

import numpy as np
from PIL import Image
from tqdm import tqdm

from .utils import SSIM_THRESH, dhash, ssim

PROC_LIMIT: Final = 8  # upper limit on number of processes
EXTENSIONS: Final = {"jpg", "jpeg", "png", "webp"}
HASH_BITS: Final = 16  # bits for the image hash


def load_img(
    path: Path, /, *, hash_bits: int = HASH_BITS
) -> tuple[Path, bytes, int] | None:
    """Load the image given the path and return the image info.

    The info for each image is a tuple containing the input path, the hash of
    the image, and the no. of pixels in the image.

    If the path is an invalid image, None is returned instead.

    Args:
        path: Path to the image to be loaded
        hash_bits: Bits to be used for the image hash

    Returns:
        The input path
        The image hash
        The no. of pixels in the image
    """
    try:
        img = Image.open(path)
    except OSError:
        tqdm.write(f"Invalid image: {path}")
        return None  # Ignore it, as the image is invalid

    img = np.array(img)
    img_hash = dhash(img, bits=hash_bits)
    pixels = np.prod(img.shape)
    return path, img_hash, pixels


def group_by_hash(
    info: Iterator[tuple[Path, bytes, int]],
    /,
) -> dict[bytes, list[Path]]:
    """Group list of image info tuples into a dict with hashes as keys.

    The dictionary values contain image paths, sorted by the no. of pixels in
    the image, then the path.
    """
    temp_dict: dict[bytes, list[tuple[int, Path]]] = {}
    info_dict: dict[bytes, list[Path]] = {}

    for path, img_hash, size in info:
        if img_hash in temp_dict:
            temp_dict[img_hash].append((size, path))
        else:
            temp_dict[img_hash] = [(size, path)]

    for key in temp_dict:
        temp_dict[key].sort(reverse=True)
        info_dict[key] = list(map(lambda tup: tup[1], temp_dict[key]))

    return info_dict


def get_dup(
    info: list[Path], /, *, ssim_thresh: float = SSIM_THRESH
) -> tuple[dict[Path, Path], int]:
    """Get duplicate images by comparing with SSIM.

    The input must be a list of image paths. This must be sorted by the no. of
    pixels in the image.

    Args:
        info: The input list of image paths
        ssim_thresh: The value of SSIM above which images will be considered as
            duplicates

    Returns:
        A dict where the key is the path of the duplicate image, and the value
            is the path of the original
        The total no. of pairs compared (used for the progress bar)
    """
    duplicates = {}

    for i, first in enumerate(info):
        if first in duplicates:
            continue

        for j in range(i + 1, len(info)):
            second = info[j]
            if second in duplicates:
                continue

            img1 = Image.open(first)
            img2 = Image.open(second)
            if ssim(img1, img2) > SSIM_THRESH:
                duplicates[second] = first

    return duplicates, len(info) * (len(info) - 1) // 2


def main(args: Namespace) -> None:
    """Run the main program.

    Arguments:
        args: The object containing the commandline arguments
    """
    file_list = args.dir.expanduser().glob("**/*" if args.recursive else "*")
    imgs = [
        item
        for item in file_list
        if item.is_file()
        and item.name[0] != "."
        and item.suffix[1:].lower() in EXTENSIONS
    ]
    if len(imgs) < 2:
        warn(f'No. of images in directory "{args.dir}" less than 2')
        return

    # Limit the max possible processes
    total_proc = min(max(args.processes, 0), PROC_LIMIT)

    with Pool(total_proc) as pool:
        # Use a progressbar for the info loading.
        # Unordered map is used as order is unnecessary.
        # Invalid images are returned as None, so filter them.
        info = filter(
            lambda i: i is not None,
            tqdm(
                pool.imap_unordered(load_img, imgs),
                desc="Loading",
                total=len(imgs),
            ),
        )
        # This is where the loading occurs, so keep it in the pool context
        info_dict = group_by_hash(info)

    # Used for the progress bar
    total = sum(
        map(lambda arr: len(arr) * (len(arr) - 1) // 2, info_dict.values())
    )

    to_delete = {}
    with Pool(total_proc) as pool, tqdm(
        desc="Processing", total=total
    ) as pbar:
        for dup, comp in pool.imap_unordered(get_dup, info_dict.values()):
            pbar.update(comp)  # update by total comparisons made
            to_delete.update(dup)

    if len(to_delete) == 0:
        print("No duplicates found")
        return

    if args.dry_run:
        print("DUPLICATE --> ORIGINAL")
        for img, cause in to_delete.items():
            if args.recursive:
                print(img, "-->", cause)
            else:
                print(img.name, "-->", cause.name)

        response = input("Delete duplicates? (y/N): ")
        if response.strip().lower() != "y":
            return

    for dup_path in to_delete:
        dup_path.unlink()
    print(f"Deleted {len(to_delete)} duplicate(s)")
