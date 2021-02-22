"""Compare two images using Multi-Scale SSIM."""
from argparse import Namespace

from PIL import Image

from .utils import ssim


def main(args: Namespace) -> None:
    """Run the main program.

    Arguments:
        args: The object containing the commandline arguments
    """
    img1 = Image.open(args.img1)
    img2 = Image.open(args.img2)
    ssim_val = ssim(img1, img2)

    if ssim_val < args.threshold:
        print(
            f"Images {args.img1} and {args.img2} differ with "
            f"SSIM={ssim_val:.3f}"
        )
        exit(-1)
