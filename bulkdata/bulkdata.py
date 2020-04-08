"""Main module."""

from .abc import BulkDataCard, BulkDataDeck
from .format import DefaultFormat
from .card import Card
from .deck import Deck


class BulkData:
    """Facade class that simplifies the interface to the package
    """
    def __init__(self, format=None):
        self._format = format or DefaultFormat()

    def Card(self, *args, **kwargs):
        return Card(*args, format=self._format, **kwargs)

    def Deck(self, *args, **kwargs):
        return Deck(*args, format=self._format, **kwargs)

    def make_card(self, name, fields, format=None):
        format = format or self._format
        card = Card(name, format=format)
        card.set_raw_fields(fields)
        return card

    def make_deck(self, card_tuples, format=None, header=None):
        format = format or self._format
        cards = []
        for name, fields in card_tuples:
            cards.append(self.make_card(name, fields, format=format))
        return Deck(cards, format=format, header=header)

    def loads(self, bd_str, format=None):
        format = format or self._format
        header, card_tuples = self._format.read_deck(bd_str)
        if not header:
            if len(card_tuples) == 1:
                return self.make_card(*card_tuples[0], format=format)

        return self.make_deck(card_tuples, format=format, header=header)

    def load(self, fp, format=None):
        format = format or self._format
        return self.loads(fp.read(), format)

    def dumps(self, bd_obj, format=None):
        format = format or self._format
        if isinstance(bd_obj, BulkDataCard):
            return self._format.write_card(bd_obj, format)
        elif isinstance(bd_obj, BulkDataDeck):
            return self._format.write_deck(bd_obj, format)
        else:
            raise TypeError("Unable to dumps object of type {}", type(bd_obj))

    def dump(self, bd_obj, fp, format=None):
        format = format or self._format
        fp.write(self.dumps(bd_obj, format))
