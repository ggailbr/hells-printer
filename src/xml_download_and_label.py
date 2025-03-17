import xml.etree.ElementTree as ET
import argparse
import requests
from pathlib import Path
import typing

from card_format import Card, DraftableCard


def download_image(image_url: str, card_name: str, save_folder: Path):
    """Downloads an image from a URL and saves it locally with the card name."""
    response = requests.get(image_url, stream=True)
    if response.status_code == 200:
        image_path = save_folder / f"{card_name}.jpg"
        with open(image_path, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print(f"Downloaded: {image_path}")
    else:
        print(f"Failed to download {card_name} from {image_url}")


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

    for card in card_list:
        name = card.find("name").text.replace("/", "_")  # Replace invalid characters
        layout = card.find("prop/layout")
        image_link = card.find("set").attrib.get("picURL")

        if image_link:
            download_image(image_link, name, save_folder)

        if layout is not None:
            cards["draftable_cards"].append(
                DraftableCard(name, image_link, layout.text)
            )
        else:
            cards["tokens"].append(
                Card(name, image_link)
            )

    return cards["draftable_cards"], cards["tokens"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("xml_file", type=Path, help="Path to the Cockatrice XML file")
    parser.add_argument("save_folder", type=Path, help="Folder to save card images")
    args = parser.parse_args()

    parse_xml_into_cards(args.xml_file, args.save_folder)
