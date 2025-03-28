import xml.etree.ElementTree as ET
import argparse
from pathlib import Path
import typing
import tqdm
import requests
from PIL import Image
from io import BytesIO

from card_format import Card, DraftableCard, TokenCard


def download_image(card: Card, save_folder: Path):
    """Downloads an image from a URL and saves it locally with the card name."""
    save_folder.mkdir(exist_ok=True)
    response = requests.get(card.image,  stream=True)
    if response.status_code == 200:
        image_path = save_folder / f"{card.name}.jpg"
        image_bytes = BytesIO()
        for chunk in response.iter_content(1024):
            image_bytes.write(chunk)
        image_bytes.seek(0)
        final_image = Image.open(image_bytes)
        exif = final_image.getexif()
        exif[0x9286] = str(card)
        final_image.save(str(save_folder/''.join([a for a in card.name.replace(' ','_').replace("//", "_OR_") if a.isalnum() or a == "_" ]))+".png",exif=exif)
        print(f"Downloaded: {save_folder/card.name.replace(' ','_')}.png")
    else:
        print(f"Failed to download {card.name} from {card.image}")


def parse_xml_into_cards(xml_path: typing.Union[Path, str], save_folder: Path) -> tuple[list[DraftableCard], list[Card]]:
    """
    Parses supplied Cockatrice XML into draftable and token cards.
    Also downloads card images.
    """
    xml_tree = ET.parse(xml_path)
    xml_root = xml_tree.getroot()
    card_list = xml_root.find("cards")
    cards = {
        "draftable_cards": [],
        "tokens": []
    }

    save_folder.mkdir(parents=True, exist_ok=True)  # Ensure the save directory exists

    # A little inefficient, but doing two passes to only grab tokens that hold references to cards needed
    for card in card_list:
        name = card.find("name").text.replace("/", "_")  # Replace invalid characters
        layout = card.find("prop/layout")
        image_link = card.find("set").attrib.get("picURL")
        if layout is not None:
            cards["draftable_cards"].append(
                DraftableCard(name, image_link, layout.text)
            )
    
    # Find all tokens that have a reverse related to a card currently parsed
    # This isn't exact and still requires some manual inspection to remove actual mtg tokens you may not need
    for card in card_list:
        name = card.find("name").text.replace("/", "_")  # Replace invalid characters
        layout = card.find("prop/layout")
        image_link = card.find("set").attrib.get("picURL")
        if layout is None:
            related_cards = card.findall("reverse-related")
            if len(related_cards) == 0:
                continue
            related_list = []
            for related in related_cards:
                if related.text in cards["draftable_cards"]:
                    related_list.append(related.text)
            if len(related_list) > 0:
                cards["tokens"].append(
                        TokenCard(name, image_link, related_list)
                    )

    return cards["draftable_cards"], cards["tokens"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("xml_file", type=Path, help="Path to the Cockatrice XML file")
    parser.add_argument("--save_folder", type=Path, help="Folder to save card images", default=Path(__file__).parent.parent/"downloads")
    args = parser.parse_args()

    draftable_cards, tokens = parse_xml_into_cards(args.xml_file, args.save_folder)
    for draftable_card in draftable_cards:
        download_image(draftable_card, args.save_folder/"draftable")
    for token in tokens:
        download_image(token, args.save_folder/"tokens")
    
    
