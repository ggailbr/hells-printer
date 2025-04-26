#  usage: ./upscale.py -s <source_path> -d <dest_path>
# -<source_path> must have "draftable" and "tokens" folders with card images

# BASICS:
# - This program takes portrait MTG image files and upscaled them to 300 DPI (755,1039) if
#   they are smaller than that. Current upscaler: Resampling.BICUBIC from PIL
#
# - Script is intended to be run after the touch_up.py script has placed cards in
#   the <hells-printer\trimmed\draftable> and the <hells-printer\trimmed\tokens> folders. 
#   This script should be run from the \src directory 

# KNOWN ISSUES:
# - The code currently completely deletes the destination folder if it already exists, which is 
#   inefficient but simpler. THE SOURCE AND DESTINATION SHOULD ONLY CONTAIN A <draftable> AND 
#   <tokens> DIRECTORY WITH THE APPROPRIATE IMAGES. ANY OTHER FILES RISK BEING DELETED
#
# - Code only upscales cards that are too small. Cards that are big enough, but not the correct
#   ratio, are not fixed. However, this situation should be rare.
#
# - Images are currently squashed and stretched to fit the ratio of a portrait MTG card if they 
#   are not already the correct ratio. This combined with simple upscaler means some cards become
#   much lower quality after upscaling
#
# - Upscaling images as PNGs (which is how it is currently done) leads to rather large image files.
#   For HC1, the final <upscaled> folder has a size of 681MB for 841 Files

import shutil
import argparse
from PIL import Image
import logging
from pathlib import Path

DPI = 300 # desired DPI
RATIO = 63/88 # portrait card size (~0.71591)
RATIO_PX = (744,1039) # needed resolution for 300 DPI

#default directories
source_path = Path('../trimmed').resolve()
dest_path = Path('../upscaled').resolve()

LOGGER = logging.Logger(__name__)

def upscale_img(img: Image, pil_upscale: bool = True):
    upscaled = img
    w, h = img.size
    if w*h < 744*1039:
        LOGGER.info('Resizing card: ' + str(img.filename))
        if pil_upscale:
            upscaled = img.resize(RATIO_PX) # all upscaling happens right here
            upscaled.filename = img.filename
        else:
            raise NotImplementedError("Need to add AI upscaling")
    else:
       LOGGER.info('Skipping card: ' + str(img.filename))
       upscaled = img
    return upscaled


def upscale(src: Path, dest: Path, type: str):
    src = src/type
    dest = dest/type

    for card in src.iterdir():
        image = Image.open(card)
        upscaled = upscale_img(image)
        card_name = str(card.name)
        save_path = dest/card_name
        if save_path.exists() and save_path.is_file():
            save_path.unlink() # remove file if it already exists (replacement)
        upscaled.save(save_path)
    return

def main():
    global source_path
    global dest_path

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source', type=Path, help='Path to images to be adjusted (draftable and tokens)')
    parser.add_argument('-d', '--dest', type=Path, help='Directory to save split+upscaled images')
    args = parser.parse_args()

    if args.source is not None:
        source_path = args.source
    if args.dest is not None:
         dest_path = args.dest

    source_path.resolve()
    dest_path.resolve()

    if (not (source_path/"draftable").exists()) or (not (source_path/"tokens").exists()):
        print('Source directory needs to have \"draftable\" and \"tokens\" folders')
        return
    
    #if dest_path.exists():
    #    shutil.rmtree(dest_path)
    dest_path.mkdir(parents=True, exist_ok=True)
    (dest_path/'draftable').mkdir(parents=True, exist_ok=True)
    (dest_path/'tokens').mkdir(parents=True, exist_ok=True)

    upscale(source_path, dest_path, 'draftable')
    upscale(source_path, dest_path, 'tokens')

if __name__ == '__main__':
    main()
