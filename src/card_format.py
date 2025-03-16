import dataclasses

@dataclasses.dataclass
class Card:
    name: str
    image: str

@dataclasses.dataclass
class DraftableCard(Card):
    layout: str