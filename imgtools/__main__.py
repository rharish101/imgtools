"""CLI for this module."""
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from pathlib import Path
from typing import Final

from . import diff, img_hash, rm_dup
from .utils import SSIM_THRESH

MODE_TO_TOOL: Final = {
    "hash": img_hash.main,
    "diff": diff.main,
    "rmdup": rm_dup.main,
}


parser = ArgumentParser(description="Collection of tools that work on images")
subparsers = parser.add_subparsers(
    dest="tool", help="the choice of the image tool"
)

dhash_parser = subparsers.add_parser(
    "hash",
    description="Compute the difference hash (d-hash) of an image",
    formatter_class=ArgumentDefaultsHelpFormatter,
)
dhash_parser.add_argument(
    "images",
    metavar="IMAGE",
    type=Path,
    nargs="+",
    help="path to the input image(s)",
)
dhash_parser.add_argument(
    "-b", "--bits", type=int, default=64, help="number of bits in the hash"
)

diff_parser = subparsers.add_parser(
    "diff", description="Compare two images using SSIM"
)
diff_parser.add_argument(
    "img1", metavar="IMAGE", type=Path, help="path to the first image"
)
diff_parser.add_argument(
    "img2", metavar="IMAGE", type=Path, help="path to the second image"
)
diff_parser.add_argument(
    "-t",
    "--threshold",
    type=float,
    default=SSIM_THRESH,
    help="threshold for SSIM",
)

dup_parser = subparsers.add_parser(
    "rmdup",
    description="Delete all duplicate images in a directory",
    formatter_class=ArgumentDefaultsHelpFormatter,
)
dup_parser.add_argument(
    "dir",
    metavar="DIR",
    type=Path,
    help="directory in which to remove duplicate images",
)
dup_parser.add_argument(
    "-d",
    "--dry-run",
    action="store_true",
    help="list duplicates and prompt before deleting",
)
dup_parser.add_argument(
    "-r",
    "--recursive",
    action="store_true",
    help="recurse into subdirectories",
)
dup_parser.add_argument(
    "-p",
    "--processes",
    default=4,
    type=int,
    help="number of parallel processes to use",
)

args = parser.parse_args()
MODE_TO_TOOL[args.tool](args)
