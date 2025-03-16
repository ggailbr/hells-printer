import xml.etree.ElementTree as ET
import argparse
from pathlib import Path
import typing


from card_format import Card, DraftableCard


def parse_xml_into_cards(xml_path: typing.Union[Path,str]) -> tuple[list[DraftableCard], list[Card]]:
    """
    Parses supplied Cockatrice XML into draftable and token cards
    """

    xml_tree = ET.parse(args.xml_file)
    xml_root = xml_tree.getroot()
    card_list = xml_root.find("cards")
    cards = {
        "draftable_cards": [],
        "tokens": []
    }
    for card in card_list:
        name = card.find("name").text
        layout = card.find("prop/layout")
        image_link = card.find("set").attrib["picURL"]
        if layout is not None:
            # Tokens don't have a layout as far as I can tell
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
    parser.add_argument("xml_file", type=Path)
    args = parser.parse_args()