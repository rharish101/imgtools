#!/usr/bin/env python3
"""Compute the difference hash (d-hash) of an image."""
from argparse import Namespace
from binascii import hexlify

import numpy as np
from PIL import Image

from .utils import dhash


def main(args: Namespace) -> None:
    """Run the main program.

    Arguments:
        args: The object containing the commandline arguments
    """
    for img_name in args.images:
        try:
            img = Image.open(img_name)
        except OSError as err:
            print(err)  # includes the file name
            continue

        img_hash_bin = dhash(np.array(img), bits=args.bits)
        # bytes => str (in hex)
        img_hash = hexlify(img_hash_bin).decode()
        print(f"{img_hash}  {img_name}")
