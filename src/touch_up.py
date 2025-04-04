from PIL import Image, ImageFile
import math
import colorsys
import logging
import os
import numpy as np
import argparse
from pathlib import Path
import matplotlib.pyplot as plt

LOGGER = logging.getLogger(__name__)

def trim_edge(image: ImageFile, depth = 15, ratio = 0.5):
    """
        This should be done before upscaling
        Some cards will have a sliver of white pixels on the border that we want to remove
        * Assuming this is the only use-case and it goes from white to black
        Should also remove all alpha border
    """
    width, height = image.size

    image_array = np.array(list(image.getdata())).reshape((height,width,-1))

    edge_index = ["left", "right", "top", "bottom"]
    modified_alpha = [False,False,False,False]
    modified_edge = [False,False,False,False]

    # First trim any alpha channel off the side
    if image_array.shape[2] >3:
        # Test case: u_cirion02s_Art_Folder.png
        
        # Left side
        while image_array[height//2,0,3] < 255:
            image_array = image_array[:,1:,...]
            width -= 1
            modified_alpha[0] = True
        # Right Side
        while image_array[height//2,-1,3] < 255:
            image_array = image_array[:,:-1,...]
            width -= 1
            modified_alpha[1] = True
        # Top Side
        while image_array[0,width//2,3] < 255:
            image_array = image_array[1:,...]
            height -= 1
            modified_alpha[2] = True
        # Bottom Side
        while image_array[-1,width//2,3] < 255:
            image_array = image_array[:-1,...]
            height -= 1
            modified_alpha[3] = True

    # Left Side
    value_gradient = [int(colorsys.rgb_to_hsv(*list((point.ravel()[:3]/255)))[2]*255) for point in image_array[height//2,0:depth]]
    if all([value < 10 for value in value_gradient[-int(depth*ratio):]]):
        while not math.isclose(value_gradient[0], 0.0):
            value_gradient = value_gradient[1:]
            image_array = image_array[:,1:,...]
            width -= 1
            modified_edge[0] = True

    # Right Side
    value_gradient = [int(colorsys.rgb_to_hsv(*list((point.ravel()[:3]/255)))[2]*255) for point in image_array[height//2,-depth:]]
    if all([value < 10 for value in value_gradient[:int(depth*ratio)]]):
        while not math.isclose(value_gradient[-1], 0.0):
            value_gradient = value_gradient[:-1]
            image_array = image_array[:,:-1,...]
            width -= 1
            modified_edge[1] = True
    
    # Top Side
    value_gradient = [int(colorsys.rgb_to_hsv(*list((point.ravel()[:3]/255)))[2]*255) for point in image_array[0:depth,width//2]]
    if all([value < 10 for value in value_gradient[-int(depth*ratio):]]):
        while not math.isclose(value_gradient[0], 0.0):
            value_gradient = value_gradient[1:]
            image_array = image_array[1:,...]
            height -= 1
            modified_edge[2] = True
    # Bottom Side
    value_gradient = [int(colorsys.rgb_to_hsv(*list((point.ravel()[:3]/255)))[2]*255) for point in image_array[-depth:,width//2]]
    if all([value < 10 for value in value_gradient[:int(depth*ratio)]]):
        while not math.isclose(value_gradient[-1], 0.0):
            value_gradient = value_gradient[:-1]
            image_array = image_array[:-1,...]
            height -= 1
            modified_edge[3] = True

    if any(modified_edge):
        LOGGER.warning("Modified Edges: " + ",".join([edge_index[i] for i, truth in enumerate(modified_edge) if truth]) + f"of {image.filename}")
    if any(modified_alpha):
        LOGGER.warning("Modified alpha: " + ",".join([edge_index[i] for i, truth in enumerate(modified_alpha) if truth]) + f"of {image.filename}")
    
    return Image.fromarray(np.uint8(image_array)), any(modified_alpha+modified_edge)


if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument("image_dir", type=Path, help="Folder with downloaded images to touch up")
    parser.add_argument("--output_dir", type=Path)
    args = parser.parse_args()


    if args.output_dir is None:
        args.output_dir = args.image_dir/"touchuped"
    if not args.output_dir.exists():
        args.output_dir.mkdir(exist_ok=True)

    for image in args.image_dir.iterdir():
        if image.is_file():
            image_path = image
            img = Image.open(image_path)
            try:
                trimed_edges, modified = trim_edge(img)
            except Exception as e:
                LOGGER.error(f"Failed to touch-up {image}")
                continue
            if not modified:
                LOGGER.debug(str(image)+" was not modified")
                continue
            trimed_edges.save(args.output_dir/image.name)
    