from PIL import Image, ImageFile
import math
import colorsys
import logging
import multiprocessing
import os
import traceback
import numpy as np
import argparse
from pathlib import Path
import functools
import matplotlib.pyplot as plt

LOGGER = logging.getLogger(__name__)

def trim_edge(image: ImageFile, depth = 10, ratio = 0.5):
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
    if image_array.shape[2] > 3:
        # Test case: u_cirion02s_Art_Folder.png
        
        # Left side
        while all(point < 255 for point in image_array[:,0,3]):
            image_array = image_array[:,1:,...]
            width -= 1
            modified_alpha[0] = True
        # Right Side
        while all(point < 255 for point in image_array[:,-1,3]):
            image_array = image_array[:,:-1,...]
            width -= 1
            modified_alpha[1] = True
        # Top Side
        while all(point < 255 for point in image_array[0,:,3]):
            image_array = image_array[1:,...]
            height -= 1
            modified_alpha[2] = True
        # Bottom Side
        while all(point < 255 for point in image_array[-1,:,3]):
            image_array = image_array[:-1,...]
            height -= 1
            modified_alpha[3] = True

    image_array = image_array[:,:,:3]
    threshold = 128

    # Left Side
    value_gradient = [int(colorsys.rgb_to_hsv(*list((point.ravel()[:3]/255)))[2]*255) for point in image_array[height//2,0:depth]]
    if all([value < threshold for value in value_gradient[-int(depth*ratio):]]):
        while all(int(colorsys.rgb_to_hsv(*list((point.ravel()[:3]/255)))[2]*255) > threshold for point in image_array[:,0]):
            value_gradient = value_gradient[1:]
            image_array = image_array[:,1:,...]
            width -= 1
            modified_edge[0] = True

    # Right Side
    value_gradient = [int(colorsys.rgb_to_hsv(*list((point.ravel()[:3]/255)))[2]*255) for point in image_array[height//2,-depth:]]
    if all([value < threshold for value in value_gradient[:int(depth*ratio)]]):
        while all(int(colorsys.rgb_to_hsv(*list((point.ravel()[:3]/255)))[2]*255) > threshold for point in image_array[:,-1]):
            value_gradient = value_gradient[:-1]
            image_array = image_array[:,:-1,...]
            width -= 1
            modified_edge[1] = True
    
    # Top Side
    value_gradient = [int(colorsys.rgb_to_hsv(*list((point.ravel()[:3]/255)))[2]*255) for point in image_array[0:depth,width//2]]
    if all([value < threshold for value in value_gradient[-int(depth*ratio):]]):
        while all(int(colorsys.rgb_to_hsv(*list((point.ravel()[:3]/255)))[2]*255) > threshold for point in image_array[0,:]):
            value_gradient = value_gradient[1:]
            image_array = image_array[1:,...]
            height -= 1
            modified_edge[2] = True
    # Bottom Side
    value_gradient = [int(colorsys.rgb_to_hsv(*list((point.ravel()[:3]/255)))[2]*255) for point in image_array[-depth:,width//2]]
    if all([value < threshold for value in value_gradient[:int(depth*ratio)]]):
        while all(int(colorsys.rgb_to_hsv(*list((point.ravel()[:3]/255)))[2]*255) > threshold for point in image_array[-1,:]):
            value_gradient = value_gradient[:-1]
            image_array = image_array[:-1,...]
            height -= 1
            modified_edge[3] = True

    if any(modified_edge):
        LOGGER.warning("Modified Edges: " + ",".join([edge_index[i] for i, truth in enumerate(modified_edge) if truth]) + f" of {image.filename}")
    if any(modified_alpha):
        LOGGER.warning("Modified alpha: " + ",".join([edge_index[i] for i, truth in enumerate(modified_alpha) if truth]) + f" of {image.filename}")
    return_image = Image.fromarray(np.uint8(image_array))
    return_image.filename = image.filename
    return return_image, any(modified_alpha+modified_edge)

def check_corner(image_values, image_array, top=True, right=True):
    height, width = image_values.shape[0:2]
    corner_range_w = [math.floor(width//2 * ratio) for ratio in (0.0, 0.11)]
    corner_range_h = [math.floor(height//2 * ratio) for ratio in (0.0, 0.08)]
    y_flipped = False
    x_flipped = False
    if top and right:
        cropped_image_values = image_values[:height//6, -width//6:,:]
        chunk = np.flip(cropped_image_values, axis=1)
        y_flipped = True
    if top and not right:
        cropped_image_values = image_values[:height//6, 0:width//6,:]
        chunk = cropped_image_values
    if not top and right:
        cropped_image_values = image_values[-height//6::, -width//6:,:]
        chunk = np.flip(np.flip(cropped_image_values, axis=1), axis=0)
        y_flipped = True
        x_flipped = True
    if not top and not right:
        cropped_image_values = image_values[-height//6:, 0:width//6,:]
        chunk = np.flip(cropped_image_values, axis=0)
        x_flipped = True

    horizontal_differences = np.abs(chunk[0,1:,2]-chunk[0,:-1,2])
    horizontal_transition_point = np.argmax(horizontal_differences)
    vertical_differences = np.abs(chunk[1:,0,2]-chunk[:-1,0,2])
    vertical_transition_point = np.argmax(vertical_differences)

    margin = 3
    # Check that the transition point is during 
    if horizontal_transition_point < corner_range_w[1] and horizontal_transition_point > corner_range_w[0] and np.max(horizontal_differences) > 30 and \
        vertical_transition_point < corner_range_h[1] and vertical_transition_point > corner_range_h[0] and np.max(vertical_differences) > 30 and chunk[0,0,2]  > 100:
        further_cropped = chunk[:vertical_transition_point + margin, :horizontal_transition_point + margin]
        sampled_hsv = further_cropped[further_cropped.shape[0]//2, further_cropped.shape[1]//2]

        for x in range(vertical_transition_point + margin):
            for y in range(horizontal_transition_point + margin):
                if further_cropped[x,y,2]  > max(sampled_hsv[2] + 30,0) and further_cropped[x,y,1] < 50:
                    target_x = x
                    target_y = y
                    if x_flipped:
                        target_x = -x - 1
                    if y_flipped:
                        target_y = -y - 1
                    image_array[target_x,target_y] = np.array([0,0,0])
        return True
    else:
        return False

def check_corners(image):
    width, height = image.size
    image_array = np.array(list(image.getdata())).reshape((height,width,-1))
    height, width = image_array.shape[0:2]
    image_values = np.asarray([np.asarray(colorsys.rgb_to_hsv(*list((point.ravel()/255))))*255 for point in image_array.ravel().reshape((-1,3))]).reshape((height, width, 3))
    corner_truth_list = ["TopRight", "BottomRight", "TopLeft", "BottomLeft"]
    modified_corners = [check_corner(image_values, image_array),
                        check_corner(image_values, image_array, False),
                        check_corner(image_values, image_array, right=False),
                        check_corner(image_values, image_array, False, False)]
    if any(modified_corners):
        LOGGER.warning("Modified corners: " + ",".join([corner_truth_list[i] for i, truth in enumerate(modified_corners) if truth]) + f" of {image.filename}")

    
    return_image = Image.fromarray(np.uint8(image_array))
    return_image.filename = image.filename
    return return_image, any(modified_corners)

def process_image(file_image):
    starting_filename = file_image.filename
    try:
        file_image, modified = trim_edge(file_image)
    except Exception as e:
        modified = False
        print(traceback.format_exception(e))
        LOGGER.error(f"Failed to trim {starting_filename}")
    try:
        file_image, corners = check_corners(file_image)
    except Exception as e:
        corners = False
        print(traceback.format_exception(e))
        LOGGER.error(f"Failed to corner {starting_filename}")
    # from edge_bleed import expand_for_bleed
    # file_image = expand_for_bleed(file_image)
    if not modified and not corners:
        LOGGER.debug(str(starting_filename)+" was not modified")

    file_image.filename = starting_filename
    return file_image

def process_image_file(image_path, args):
    if image_path.is_file():
        file_image = Image.open(image_path)
        # Thanks Halvesies for being 8 bit color specification...
        final_image = file_image.convert("RGBA")
        final_image.filename = file_image.filename
        try:
            final_image, modified = trim_edge(final_image)
        except Exception as e:
            modified = False
            print(traceback.format_exception(e))
            LOGGER.error(f"Failed to trim {image_path}")
        try:
            final_image, corners = check_corners(final_image)
        except Exception as e:
            corners = False
            print(traceback.format_exception(e))
            LOGGER.error(f"Failed to corner {image_path}")
        # from edge_bleed import expand_for_bleed
        # final_image = expand_for_bleed(final_image)
        if not modified and not corners:
            LOGGER.debug(str(image_path)+" was not modified")
        final_image.save(args.output_dir/image_path.name)

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
        args.output_dir.mkdir(exist_ok=True)

    if args.image_dir.is_dir():
        pool = multiprocessing.Pool(args.max_processes)
        multiprocess_image = functools.partial(process_image_file, args=args)
        pool.map(multiprocess_image, args.image_dir.iterdir())
        pool.close()
    else:
        process_image(args.image_dir, args)