#usage: ./image_adjust.py -s <source_path> -d <dest_path>
# -<source_path> must have "draftable" and "tokens" folders with card images
# code will place outputs in <dest_path>/draftable and <dest_path>/tokens

# VERSION 1:
# - Code trusts the 'layout' field completely
#   - split layout is split down the middle, then saved as two portrait images
#   - normal layout is simply rotated if not portrait

# - Code does minimal dimension changes
#   - if not in the right ratio for a card, image is stretched or compressed into the shape

# - Code does DPI resizing
#   - If images resolution is < 744x1039 (aka < 300 DPI):
#       - images is upscaled with <> to 300 DPI and DPI metadata changed to 300

import sys
import ast
import os
import argparse
from pathlib import Path
from PIL import Image
from io import BytesIO

#default directories
source_path = Path('../downloads')
adj_path = Path('../adjusted')
dest_path = Path('../final')

card_types = ['draftable', 'tokens']


standard_dpi = 300 # required pixels/inch
# portrait card size
RATIO = 63/88
DPI = 300

ratio_mm = [63,88]
ratio_in = [2.48,3.46]
ratio_px = [744,1039] # for 300 dpi 

#for token in os.listdir(r'..\downloads\tokens'):
#    print(token)

def check_ratio(image: Image) -> bool:
    w, h = image.size
    if 0.710 <= w/h <= 0.720:
         return True
    else:
         return False

def adjust(src_path: Path, save_path: Path):
     warning_list = []
     split_list = []

     for card in src_path.iterdir():
        split = False
        new_cards = []

        # open card image and extract EXIF
        cur_card = Image.open(str(card))
        cur_w, cur_h = cur_card.size
        metadata = (dict(cur_card.getexif()))[37510]
        metadata = ast.literal_eval(metadata)
    
        # find card orientation
        if(cur_w > cur_h):
             portrait = False
        else:
             portrait = True

        # if horizontal and <split>, assume the two cards are actually portrait
        # if portrait and <split>, dont split
        if(metadata['layout'] == 'split' and (not portrait)):
             split_list.append(cur_card)
             split = True
             midpoint = cur_w // 2
             left_half = cur_card.crop((0, 0, midpoint, cur_h))
             right_half = cur_card.crop((midpoint, 0, cur_w, cur_h))
             #portrait = True


             left_meta = metadata
             left_meta['name'] = metadata['name'] + '_LEFT'
             left_exif = left_half.getexif()
             left_exif[0x9286] = str(left_meta)
             new_cards.append(left_half)
             left_path = save_path / left_meta['name']

             right_meta = metadata
             right_meta['name'] = metadata['name'] + '_RIGHT'
             right_exif = right_half.getexif()
             right_exif[0x9286] = str(right_meta)
             new_cards.append(right_half)
             right_path = save_path / right_meta['name']
        else:
             if not portrait:
                  cur_card = cur_card.rotate(90, expand=1)
             new_cards.append(cur_card)

          # new_cards now has either cur_card OR 2 halves of a card

        for index, card in enumerate(new_cards):
            if not check_ratio(card):
                 warning_list.append(card)
          
            if split:
                 if index == 0:
                      left_path = dest_path / left_meta['name']
                      card.save(left_path, exif=left_exif, format='png')
                 elif index == 1:
                      right_path = dest_path / right_meta['name']
                      card.save(right_path, exif=right_exif, format='png')
            else:
                 card.save(save_path / metadata['name'], format='png')

     print("These cards were split into two:")
     print(split_list)
     print("These cards didn't have the correct ratio and should be reviewed:")
     print(warning_list)
                 

         
        #saved adjusted cards

            

        # trim corners with gage

        # upscale

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source', type=Path, help='Path to images to be adjusted (draftable and tokens)')
    parser.add_argument('-d', '--dest', type=Path, help='Directory to save split+upscaled images')
    args = parser.parse_args()

    global source_path
    global dest_path

    if args.source is not None:
        source_path = args.source
    if args.dest is not None:
         dest_path = args.dest
      


    for element in card_types:
     start_path = source_path / element
     end_path = dest_path / element
     end_path.mkdir(parents=True, exist_ok=True)
     adjust(src_path=start_path, save_path=end_path)
    


             


if __name__ == '__main__':
     main()

# end result = image that only needs bleed. (dpi scaled)