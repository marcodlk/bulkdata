"""The :mod:`~bulkdata.deck` module provides the 
:class:`~bulkdata.deck.Deck` class.
"""

from collections.abc import Sequence

from .card import Card
from .field import Field, write_field
from .util import islist, repr_list
from .parse import BDFParser


class Deck():
    """:class:`~bulkdata.deck.Deck` class allows the user
    to load and update bulk data files, loading the 
    bulk data cards into :class:`~bulkdata.card.Card`
    objects.

    :param cards: initialize the deck with these cards, 
                    defaults to ``None``.
    :param header: the header, which is prepended to the bulk
                    data section when dumping the deck, 
                    defaults to ``None``.
    """
    
    def __init__(self, cards=None, header=None):
        self._cards = cards or []
        self.header = header or ""
        
    def append(self, card):
        """Append a card to the deck.

        :param card: The card to append
        """
        self._cards.append(card)
        
    def extend(self, cards):
        """Extend deck cards with sequence of cards.

        :param cards: The sequence of cards
        """
        self._cards.extend(cards)
    
    def _iter(self, value):
        if islist(value):
            for each in value:
                yield each
        else:
            yield value
            
    def _iter_index_value(self, dict_):
        index = dict_["index"]
        value = dict_["value"]
        if islist(value):
            if not islist(index):
                raise TypeError("value is type {} but index is type {}"
                                .format(type(value), type(index)))
            for each_index, each_value in zip(index, value):
                yield each_index, each_value
        else:
            yield index, value
        
    def _matches_name(self, filter, card):
        try:
            return card.name == filter["name"]
        except KeyError:
            return True
        
    def _matches_fields(self, filter, card):
        filter_fields = filter.get("fields")
        if filter_fields:
            match = True
            for index, value in self._iter_index_value(filter_fields):
                try:
                    match *= (card.fields[index].value == value)
                except IndexError:
                    return False
            return match
        else:
            return True
        
    def _matches_contains(self, filter, card):
        filter_contains = filter.get("contains")
        if filter_contains:
            filter_contains = [
                value
                for value in self._iter(filter_contains)
            ]
            # loop through fields, popping off matches
            for field in card.fields:
                try:
                    filter_contains.remove(field.value)
                except ValueError:
                    continue
            # match if all `contains` values found
            match = len(filter_contains) == 0
            return match
        else:
            return True
        
    def _matches(self, filter, card):
        match = True
        match *= self._matches_name(filter, card)
        match *= self._matches_fields(filter, card)
        match *= self._matches_contains(filter, card)
        return match
    
    def _enumerate_find(self, filter=None):
        filter = filter or {}
        if filter:
            for i, card in enumerate(self._cards):
                if self._matches(filter, card):
                    yield i, card
        else:
            for i, card in enumerate(self._cards):
                yield i, card
    
    def _enumerate_find_one(self, filter=None):
        filter = filter or {}
        if filter:
            for i, card in enumerate(self._cards):
                if self._matches(filter, card):
                    return i, card
            return None, None
        else:
            try:
                return 0, self._cards[0]
            except IndexError:
                return None, None

    def _normalize_filter(self, filter):
        if filter is None:
            return {}
        elif isinstance(filter, str):
            return {"name": filter}
        else:
            return filter

    def find(self, filter=None):
        """Find cards matching the query denoted by *filter*.

        :type filter: dict, str
        :param filter: Specifies which cards to find.
        :return: A generator object iterating through every card
                 matching the filter.

        If *filter* is a ``dict``, there are three keywords that may
        be used.

        * **name**, ``str``: Filter for cards with matching *name*.

        * **fields**, ``dict``: Given an "index" and "field" member, filter
          cards where the field(s) at *index* index, has/have
          value *field*.

        * **contains**: Filter for cards containing a field that matches
          the *contains* value, or any *contains* value if *contains*
          is a list.

        The following code block is an example of using ``find`` with
        a filter dict:

        .. code-block:: python

            filter_ = {
                # name is ASET1
                "name": "ASET1",
                
                "fields": {
                    
                    # first field
                    "index": 0,
                    
                    # with value 3
                    "value": 3
                },
                
                # contains values 1 and "THRU"
                "contains": [1, "THRU"] 
            }

            card = next(deck.find(filter_))
            print(card)

        .. code-block:: none

            ASET1   3       1       THRU    8

        If *filter* is a ``str``, the filter will match cards
        with name matching *filter*.

        .. code-block:: python

            card = next(deck.find("AERO"))
            print(card)

        .. code-block:: none

            AERO    3       1.3     100.    .00001  1       -1

        """
        filter = self._normalize_filter(filter)
        for _, card in self._enumerate_find(filter):
            yield card

    def find_one(self, filter=None):
        """Find the first card matching the query denoted by *filter*.

        :type filter: dict, str
        :param filter: Specifies which card to find.
        :return: The first matching card, or ``None`` if no match
                 is found.
        """
        filter = self._normalize_filter(filter)
        _, card = self._enumerate_find_one(filter)
        return card
    
    def replace(self, filter, card):
        """Replace cards matching the query denoted by
        *filter* with *card*.

        :type filter: dict, str
        :param filter: Specifies which cards to replace.
        :param card: The replacement card
        """
        filter = self._normalize_filter(filter)
        for i, _ in self._enumerate_find(filter):
            self._cards[i] = card

    def replace_one(self, filter, card):
        """Replace the first card matching the query denoted by
        *filter* with *card*.

        :type filter: dict, str
        :param filter: Specifies which card to replace.
        :param card: The replacement card
        :return: The replacement card, or ``None`` if no match
                 is found.
        """
        filter = self._normalize_filter(filter)
        i, _ = self._enumerate_find_one(filter)
        if i:
            self._cards[i] = card
            return card
        else:
            return None
            
    def _update_card(self, card, update):
        for index, value in self._iter_index_value(update):
            card[index] = value
    
    def update(self, filter, update):
        """Update cards matching the query denoted by *filter*
        with changes denoted by *update* dict, which has
        the same keyword options as the *fields* dict in *filter*.

        .. note:: 
        
            Avoid this function as there is no current tutorial,
            has not been well tested, and does not appear to add any
            functionality not achieved otherwise.

        :type filter: dict, str
        :param filter: Specifies which cards to replace.
        :param card: The replacement card
        """
        filter = self._normalize_filter(filter)
        for i, _ in self._enumerate_find(filter):
            self._update_card(self._cards[i], update)
    
    def delete(self, filter=None):
        """Delete cards matching the query denoted by
        *filter*.

        :type filter: dict, str
        :param filter: Specifies which cards to delete.
        :return: The number of cards deleted.
        """
        filter = self._normalize_filter(filter)
        delete_i = [i for i, _ in self._enumerate_find(filter)]
        for i in reversed(delete_i):
            del self._cards[i]
        return len(delete_i)
            
    def _get_card_by_index(self, index):
        return self._cards[index]
            
    def _get_cards_by_indexes(self, indexes):
        return [self._cards[i] for i in indexes]

    def _get_cards_by_name(self, name):
        return list(self.find({"name": name}))
    
    def _get_cards_by_slice(self, slice_):
        return list(self._cards[slice_])
            
    def __getitem__(self, key):
        """Get card(s) in the deck.

        :type key: int, slice, list, str
        :param key: The indexing key denoting where to get 
                    the card(s)
        :return: The card(s)

        If *key* is of type ``str``, this method
        returns all cards with name *key*.
        """
        if isinstance(key, int):
            return self._get_card_by_index(key)
        elif isinstance(key, slice):
            return self._get_cards_by_slice(key)
        elif isinstance(key, str):
            return self._get_cards_by_name(key)
        elif isinstance(key, Sequence):
            return self._get_cards_by_indexes(key)
        else:
            raise TypeError(key, type(key))
            
    def _set_card_by_index(self, index, card):
        self._cards[index] = card
            
    def _set_cards_by_indexes(self, indexes, cards):
        for i, card in zip(indexes, cards):
            self._cards[i] = card
    
    def _set_cards_by_slice(self, slice_, cards):
        steps = range(slice_.start, slice_.stop. slice_.step)
        for i, card in zip(steps, cards):
            self._cards[i] = card
            
    def __setitem__(self, key, value):
        """Set card(s) in the deck.

        :type key: int, slice, list
        :param key: The indexing key denoting where to set 
                    the card(s)
        :param value: The card(s) to set
        """
        if isinstance(key, int):
            return self._set_card_by_index(key, value)
        elif isinstance(key, slice):
            return self._set_cards_by_slice(key, value)
        elif islist(key):
            return self._set_cards_by_indexes(key, value)
        else:
            raise TypeError(key, type(key))

    @classmethod
    def loads(cls, deck_str):
        """Load :class:`~bulkdata.deck.Deck` object from a
        bulk data string.

        :param deck_str: The bulk data string
        :return: The loaded :class:`~bulkdata.deck.Deck` object
        """
        cards = []
        header, card_tuples = BDFParser(deck_str).parse()

        for name, fields in card_tuples:
            card = Card(name)
            fields = [Field(field_val) for field_val in fields]
            card.set_raw_fields(fields)
            cards.append(card)
        obj = cls(cards, header)

        if obj.find_one({"name": None}):
            raise Warning("Loaded cards with no name. This usually "
                          "implies there was an error parsing the bdf file.")
        
        return obj

    @classmethod
    def load(cls, fp):
        """Load :class:`~bulkdata.deck.Deck` object from a
        bulk data file object.

        :param fp: The bulk data file object
        :return: The loaded :class:`~bulkdata.deck.Deck` object
        """
        return cls.loads(fp.read())

    def dumps(self, format="fixed"):
        """Dump the deck to a bulk data string.

        :param format: The desired format, can be one of: 
                       ["free", "fixed"], defaults to "fixed"
        :return: The bulk data string
        """
        bulk = "".join([card.dumps(format) for card in self.cards])
        if self.header:
            return self.header + "\nBEGIN BULK\n" + bulk + "ENDDATA"
        else:
            return bulk

    def dump(self, fp, format="fixed"):
        """Dump the deck to a bulk data file.

        :param fp: The bulk data file object
        :param format: The desired format, can be one of: 
                       ["free", "fixed"], defaults to "fixed"
        """
        return fp.write(self.dumps(format=format))

    def sort(self, key=None, reverse=False):
        """Sort the cards in the deck.
        
        :param key: Specifies a function of one argument that
                    is used to extract a comparison key from each card.
                    If None, the cards will be sorted by name.
        :param reverse: Boolean value. If set to True, then the cards 
                        are sorted as if each comparison were reversed.
        """
        key = key or (lambda card: card.name)
        self._cards = sorted(self._cards, key=key, reverse=reverse)

    def __str__(self):
        """Dump the deck to as a bulk data string with default
        format
        
        :return: The bulk data string
        """
        return self.dumps()

    def __len__(self):
        """Return number of cards in the deck.
        """
        return self.cards.__len__()

    def __iter__(self):
        """Iterate through the cards in the deck.
        """
        return self.cards.__iter__()

    def __bool__(self):
        """Return ``True`` if the deck contains any cards,
        ``False`` otherwise.
        """ 
        return bool(self.cards)

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, 
                               repr_list(self.cards))

    @property
    def cards(self):
        """The deck cards.
        """
        return self._cards


__all__ = ["Deck"]