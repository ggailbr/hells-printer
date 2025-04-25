from PIL import Image, ImageFile
import math
import os
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import logging
import multiprocessing
import argparse
import functools
card_w = 63
card_h = 88
margin = 3.175

LOGGER = logging.getLogger(__name__)

def expand_for_bleed(image: ImageFile) -> Image:
    """ Based on the width and height of the image, expands
        the last row/column of pixels to create a bleed. Does
        this blindly so it assumes it has been preprocessed as much 
        as you want before this

    """
    width, height = image.size
    bleed_pixels_h = math.ceil(margin/card_h * height)
    bleed_pixels_w = math.ceil(margin/card_w * width)
    image_array = np.array(list(image.getdata())).reshape((height,width,-1))[:,:,:3]
    top_bleed = np.tile(image_array[0,...].ravel(),reps=bleed_pixels_w).reshape((bleed_pixels_w,width,3))
    bottom_bleed = np.tile(image_array[-1,...].ravel(),reps=bleed_pixels_w).reshape((bleed_pixels_w,width,3))
    image_array = np.concatenate((top_bleed, image_array, bottom_bleed))
    height = image_array.shape[0]
    left_bleed =  np.repeat(image_array[:,0,...], repeats=bleed_pixels_h, axis=0).reshape((height,bleed_pixels_h,3))
    right_bleed = np.repeat(image_array[:,-1,...],repeats=bleed_pixels_h, axis=0).reshape((height,bleed_pixels_h,3))
    image_array = np.concatenate((left_bleed, image_array, right_bleed),axis=1)
    img_w_bleed = Image.fromarray(np.uint8(image_array))
    return img_w_bleed

def run_expand_for_bleed(image_file: Path, args):
    img = Image.open(image_file)
    expand_for_bleed(img).save(args.output_dir/image_file.name)

if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument("image_dir", type=Path, help="Folder with downloaded images to touch up")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--max-processes", type=int, default=8)
    args = parser.parse_args()


    if args.output_dir is None:
        args.output_dir = args.image_dir/"touchuped"
    if not args.output_dir.exists():
        args.output_dir.mkdir(parents=True, exist_ok=True)

    if args.image_dir.is_dir():
        pool = multiprocessing.Pool(args.max_processes)
        run_func = functools.partial(run_expand_for_bleed, args=args)
        pool.map(run_func, args.image_dir.iterdir())
        pool.close()
    else:
        run_expand_for_bleed(args.image_dir, args)