import xml.etree.ElementTree as ET
import argparse
import copy
import itertools
from pathlib import Path

def add_card(card_path, slot, node):
    card = ET.SubElement(node, 'card')
    id = ET.SubElement(card, 'id')
    id.text = card_path
    slots = ET.SubElement(card, 'slots')
    slots.text = str(slot)


def make_order(card_list, order_size, card_back, card_stock="(S30) Standard Smooth", foil=False, save_path="order1.xml"):
    order = ET.Element('order')
    details = ET.SubElement(order, 'details')
    fronts = ET.SubElement(order, 'fronts')
    backs = ET.SubElement(order, 'backs')
    bracket = ET.SubElement(details, 'bracket')
    bracket.text = str(order_size)
    stock = ET.SubElement(details, 'stock')
    stock.text = card_stock
    foil = ET.SubElement(details, 'foil')
    foil.text = "true" if foil else "false"

    front_back_pairs = {}
    slot = -1
    for card in card_list:
        slot += 1
        card_slot = slot
        if "_1.png" in card or "_2.png" in card:
            if card[:-6] in front_back_pairs:
                card_slot = front_back_pairs[card[:-6]]
                slot -= 1
            else:
                front_back_pairs[card[:-6]] = slot

        if "_2.png" in card:
            add_card(card, card_slot, backs)
        else:
            add_card(card, card_slot, fronts)
    # while slot != order_size:
    #     slot += 1
    #     # Just repeat the last card until filled out
    #     add_card(card, slot, backs)
    quantity = ET.SubElement(details, 'quantity')
    quantity.text = str(slot+1)

    cardback = ET.SubElement(order, 'cardback')
    cardback.text = card_back
    ET.ElementTree(order).write(save_path)
        
def pack_cards(card_list, card_back_path, cardstock, foil, name):
        back_counts = len([path for path in card_list if path.__contains__("_2.png")])
        total = len(card_list)-back_counts
        orders = []
        cards_left = total
        while cards_left > 612:
            orders.append(612)
            cards_left -= 612
        if cards_left != 0:
            if cards_left in sizes_copy:
                orders.append(cards_left)
            else:
                # Find next largest order size
                sizes_copy.append(cards_left)
                sizes_copy.sort()
                orders.append(order_sizes[sizes_copy.index(cards_left)])
        

        list_idx = 0
        for idx, order in enumerate(orders):
            order_list = []
            for card_count in range(order):
                if list_idx >= len(card_list):
                    break
                card_name = card_list[list_idx]
                order_list.append(card_name)
                list_idx += 1
                if card_name.__contains__("_2.png") and card_name.replace("_2.png", "_1.png") in card_list:
                    order_list.append(card_name.replace("_2.png", "_1.png"))
                    card_list.remove(card_name.replace("_2.png", "_1.png"))
                if card_name.__contains__("_1.png") and card_name.replace("_1.png", "_2.png") in card_list:
                    order_list.append(card_name.replace("_1.png", "_2.png"))
                    card_list.remove(card_name.replace("_1.png", "_2.png"))
            make_order(order_list, order, card_back_path, cardstock, foil, f"{name}_order{order}_{idx}.xml")

order_sizes = [18, 36, 55, 72, 90, 108, 126, 144, 162, 180, 198, 216, 234, 396, 504, 612]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("image_folder", type=Path, help="Path to the folder with draftables and tokens folders")
    parser.add_argument("card_back", type=Path, help="Path to card back to be placed on cards")
    parser.add_argument("-c", "--cardstock", type=str, default="(S30) Standard Smooth", choices=["(S30) Standard Smooth", "(S33) Superior Smooth", "(M31) Linen", "(P10) Plastic"], help="The type of cardstock to use on MPCFill")
    parser.add_argument("--foil", action="store_true", help="If the cards should be foil")
    parser.add_argument("--seperate_tokens", action="store_true", help="If the orders should be broken up into draftable and tokens")
    parser.add_argument("--token_back", type=Path, help="Path to card back to be placed on tokens")
    args = parser.parse_args()
    
    sizes_copy = copy.copy(order_sizes)

    draftable_cards = [str(path.absolute()) for path in (args.image_folder/"draftable").iterdir() if str(path.absolute()).__contains__(".png") or str(path.absolute()).__contains__(".jpg")]
    token_cards = [str(path.absolute()) for path in (args.image_folder/"tokens").iterdir() if str(path.absolute()).__contains__(".png") or str(path.absolute()).__contains__(".jpg")]
    card_list = draftable_cards + token_cards
    
    if not args.seperate_tokens:
        pack_cards(card_list, str(args.card_back.absolute()),args.cardstock, args.foil, args.image_folder.name)
    else:
        pack_cards(draftable_cards, str(args.card_back.absolute()),args.cardstock, args.foil, args.image_folder.name+"_draftable")
        pack_cards(token_cards, str(args.card_back.absolute()) if args.token_back is None else str(args.token_back.absolute()),args.cardstock, args.foil, args.image_folder.name+"_tokens")
    
                