"""
Due to some of the cards listed in the `Naughty List`, the easiest solution outside of just manual 
intervention was to patch the XML file. This file applies the hardcoded patches to the XML needed to
allow it to process properly.
"""
import xml.etree.ElementTree as ET
import argparse
from pathlib import Path

# Installed Libs
import git

CARDS_TO_PATCH = {
    "HLC": {
        "Sensory Overload" : [
            "picURL", "https://cdn.discordapp.com/attachments/765660673467351062/765662528029589514/https_cdn.discordapp.com_attachments_759189671665467443_759437526477570108_https_api.deepai.org_job-.jpg?ex=67ea490c&is=67e8f78c&hm=95a062734bbd63533329ad634d6eab2d939d51d52faef5615524a153d939e595&"
        ],
        "Sun Whitan" : [
            "picURL", "https://cdn.discordapp.com/attachments/765660673467351062/765662959858614312/https_cdn.discordapp.com_attachments_699985664992739409_699993256230125579_w1zku441fam41.jpg?ex=67ea4972&is=67e8f7f2&hm=75a19e670b8f2a8f4283bab59221639932f6540a33871895c47dc7537ae2367f&"
        ]
    }
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("xml_file", type=Path, help="Path to the Cockatrice XML file to be patched")
    args = parser.parse_args()

    repo = git.Repo(search_parent_directories=True)
    sha = repo.head.object.hexsha

    xml_tree = ET.parse(args.xml_file)
    xml_root = xml_tree.getroot()
    hc_set = xml_root.find("sets").find("set")
    if (found_sha := hc_set.find("patched")) is not None and found_sha.text == str(sha):
        print(f"{args.xml_file} already patched, returning")

    patches = CARDS_TO_PATCH[hc_set.find("name").text]
    card_list = xml_root.find("cards")

    card_names = list(patches.keys())
    for patch in patches:
        for card in card_list:
            if (card_name := card.find("name").text) in card_names:
                patch = patches[card_name]
                if patch[0] == "picURL":
                    card.find("set").attrib["picURL"] = patch[1]
    if hc_set.find("patched") is None:
        mark = ET.Element("patched")
        mark.text = str(sha)
        hc_set.append(mark)
    else:
        hc_set.find("patched").text = str(sha)

    xml_tree.write(args.xml_file)