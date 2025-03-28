import dataclasses

@dataclasses.dataclass
class Card:
    name: str
    image: str
    def __str__(self):
        return repr(self.__dict__)


@dataclasses.dataclass
class DraftableCard(Card):
    layout: str
    def __eq__(self, item):
        if isinstance(item, str):
            return item == self.name

@dataclasses.dataclass
class TokenCard(Card):
    reverse_related: list[str]