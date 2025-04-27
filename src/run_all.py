# Build-in Libs
import xml.etree.ElementTree as ET
import argparse
from pathlib import Path
import multiprocessing
import logging
import functools

# Installed Libs
import requests
from PIL import Image

# Custom Files
from card_format import Card, DraftableCard, TokenCard
from xml_download_and_label import parse_xml_into_cards, download_image
from image_adjust import adjust_cards
from touch_up import process_image
from upscale import upscale_img
from edge_bleed import expand_for_bleed

LOGGER = logging.Logger(__name__)


def run_full_processesing(card: Image, save_folder):
    adjusted_imgs, _ = adjust_cards(card)
    for img in adjusted_imgs:
        touched_up_img = process_image(img)
        # If you change True to False, it will try to use AI upscaling
        #   This is considerably slower, but does help with really low
        #   resolution cards. It is also decently broken, so I would 
        #   recommend doing without first then rerunning for cards
        #   that look bad
        upscaled_img = upscale_img(touched_up_img, True)
        bleed_img = expand_for_bleed(upscaled_img)
        bleed_img.save(save_folder/bleed_img.filename)
    return


def process_draftable(draftable_card, save_folder:Path):
    downloaded_img = download_image(draftable_card, save_folder, save=False)
    if downloaded_img is None:
        # Already downloaded
        return
    run_full_processesing(downloaded_img, save_folder)

if __name__ == "__main__":
    LOGGER.setLevel(logging.INFO)
    
    parser = argparse.ArgumentParser()
    parser.add_argument("xml_file", type=Path, help="Path to the Cockatrice XML file")
    parser.add_argument("--save_folder", type=Path, help="Folder to save card images", default=Path(__file__).parent.parent/"downloads")
    parser.add_argument("--max_processes", type=int, default=8, help="The maximum number of processes to use when downloading and adjusting")
    args = parser.parse_args()
    args = parser.parse_args()

    (args.save_folder/"draftable").mkdir(parents=True, exist_ok=True)
    (args.save_folder/"tokens").mkdir(parents=True, exist_ok=True)

    draftable_cards, tokens = parse_xml_into_cards(args.xml_file, args.save_folder)
    
    LOGGER.info("Starting downloading and processing of cards")

    if args.max_processes > 1:
        pool = multiprocessing.Pool(args.max_processes)
        multiprocess_process = functools.partial(process_draftable, save_folder=args.save_folder/"draftable")
        pool.map(multiprocess_process, draftable_cards)
        pool.close()
    else:
        for draftable_card in draftable_cards:
            process_draftable(draftable_card, args.save_folder/"draftable")

    for token in tokens:
        downloaded_img = download_image(token, args.save_folder/"tokens")