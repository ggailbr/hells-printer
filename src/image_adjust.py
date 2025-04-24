# usage: ./image_adjust.py -s <source_path> -d <dest_path>
# -<source_path> must have "draftable" and "tokens" folders with card images
# both inputs are optional, default src and dest are provided below

# BASICS:
# - This program takes downloaded images and splits and/or rotates them to be portrait MTG cards
# - Splitting logic - SPLIT IF:
#         - card is <split> layout and image is landscape
#              - if the card (when rotated to portrait) would be the right size, do not split
#                   - attempts to account for <layout> incorrectness (Fuse, adventure, etc.)
#
# - After splitting, cards are rotated to portrait if needed and saved in dest_path/draftable. By 
#   default, dest_path is <hells-printer\adjusted>. Default source_path is <hells-printer\downloads>
#
# - Script is intended to be run after the xml_download_and_label.py script has placed cards in
#   the <hells-printer\downloads> folder. Should be run from the \src directory 

# KNOWN ISSUES:
# - for HC1, the tokens need basically no adjustment or splitting. Currently, this code
#   does nothing to tokens, and simply copies the tokens folder from the source to destination
#
# - The code currently completely deletes the destination folder if it already exists, which is 
#   inefficient but simpler. THE SOURCE AND DESTINATION SHOULD ONLY CONTAIN A <draftable> AND 
#   <tokens> DIRECTORY WITH THE APPROPRIATE IMAGES. ANY OTHER FILES RISK BEING DELETED
#
# - Splitting logic is known to be flawed. It is important to check that all cards that were split
#   should've been split, and vice versa


import sys
import ast
import os
import argparse
from pathlib import Path
from PIL import Image
import shutil
import touch_up

#default directories
source_path = Path('../downloads').resolve()
dest_path = Path('../adjusted').resolve()

# constants
RATIO = 744/1039 # portrait card size (~0.71591)
RATIO_ERROR = 0.005 # margin of error for ratio checking

def check_ratio(image: Image) -> bool:
    w, h = image.size
    if RATIO-RATIO_ERROR <= w/h <= RATIO+RATIO_ERROR:
         return True
    else:
         return False

def adjust(src: Path, dst: Path, type: str):
     src = src/type
     dst = dst/type

     # tokens seem to need little processing... for now just copy source directory
     if type == 'tokens':
          if dst.exists():
               shutil.rmtree(dst)
          try:
               dst = (dst/'..').resolve()
               shutil.copytree(src, dst/type)
               print('Tokens copied from ' +str(src) + ' to ' +str(dst))
          except:
               print('Error copying tokens from '+str(src) + ' to ' +str(dst))
          return
          
     # if we are here... processing draftable cards
     warning_list = []
     split_list = []
     maybe_list = []
     dst.mkdir(parents=True, exist_ok=True)

     for card in src.iterdir():
          split_halves = {}
          save_path = card
          portrait = True

          # open card image and extract EXIF
          try:
               current = Image.open(card)
          except:
               print('error with '+str(card))
               return
          w, h = current.size
          cur_meta = ast.literal_eval((dict(current.getexif()))[37510])
          #print(cur_meta)

          # card orientation
          if(w > h): portrait = False

          # if card is horizontal and <split> the split into two portrait halves
          # otherwise, don't split
          if(cur_meta['layout'] == 'split' and (not portrait)):
               if not check_ratio(current.rotate(90, expand=1)):
                    split_list.append(cur_meta['name'])

                    midpoint = w // 2
                    left = current.crop((0, 0, midpoint, h))
                    right = current.crop((midpoint, 0, w, h))

                    split_halves['left'] = left
                    split_halves['right'] = right
                    print('Splitting card: '+card.name)
               else:
                    maybe_list.append(cur_meta['name'])
                    current = current.rotate(90, expand=1)
                    print('Skipping over a <split> card: '+card.name)
                    portrait = True
          else:
               if not portrait:
                    current = current.rotate(90, expand=1)
                    print('Rotated card: '+card.name)
                    portrait = True

          save_path = dst/card.name
          if not split_halves: # split didn't occur
               if not check_ratio(current):
                    print('Ratio incorrect on: '+cur_meta['name'])
                    warning_list.append(cur_meta['name'])
               if save_path.exists() and save_path.is_file():
                    save_path.unlink()
               current.save(save_path)
          else: #there are two halves to deal with
               l_save_path = save_path.with_suffix('').resolve()
               l_save_path = save_path.with_name(l_save_path.name + '_1.png')

               r_save_path = save_path.with_suffix('').resolve()
               r_save_path = save_path.with_name(r_save_path.name + '_2.png')

               if l_save_path.exists() and l_save_path.is_file():
                    l_save_path.unlink()
               split_halves['left'].save(l_save_path, format='png')
               if r_save_path.exists() and r_save_path.is_file():
                    r_save_path.unlink()
               split_halves['right'].save(r_save_path, format='png')

     print('THESE CARDS HAD SUS RATIOS AND SHOULD BE REVIEWED:')
     print(warning_list)
     print('THESE CARDS WERE SPLIT AND SHOULD BE REVIEWED:')
     print(split_list)
     print('THESE CARDS MAYBE SHOULD HAVE BEEN SPLIT BUT WERE NOT: ')
     print(maybe_list)

               





def main():
     global source_path
     global dest_path

     parser = argparse.ArgumentParser()
     parser.add_argument('-s', '--source', type=Path, help='Path to images to be adjusted (draftable and tokens)')
     parser.add_argument('-d', '--dest', type=Path, help='Directory to save split/adjusted images')
     args = parser.parse_args()

     if args.source is not None:
          source_path = args.source
     if args.dest is not None:
          dest_path = args.dest

     print('Attempting to adjust from '+str(source_path)+' to '+str(dest_path))
     if (not (source_path/"draftable").exists()) or (not (source_path/"tokens").exists()):
          print('Source directory needs to have \"draftable\" and \"tokens\" folders')
          return
     

     adjust(source_path, dest_path, 'draftable')
     adjust(source_path, dest_path, 'tokens')

     # then run (but need to make trimmed directory first)
     # python .\touch_up.py ..\adjusted\draftable\ --output-dir ..\trimmed\draftable\ --max-processes 16
     # python .\touch_up.py ..\adjusted\tokens\ --output-dir ..\trimmed\tokens\ --max-processes 16

     # then run
     # python .\upscale.py



if __name__ == '__main__':
     main()