from collections.abc import Sequence

from .card import Card
from .field import Field, write_field
from .util import islist, repr_list
from .parse import BDFParser


class Deck():
    
    def __init__(self, cards=None, header=None):
        self._cards = cards or []
        self.header = header or ""
        
    def append(self, card):
        self._cards.append(card)
        
    def extend(self, card):
        self._cards.extend(card)

    def _normalize_filter_value(self, value):
        return write_field(value).strip()
    
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
                value = self._normalize_filter_value(value)
                match *= (card.fields[index].strip() == value)
            return match
        else:
            return True
        
    def _matches_contains(self, filter, card):
        filter_contains = filter.get("contains")
        if filter_contains:
            filter_contains = [
                self._normalize_filter_value(value)
                for value in self._iter(filter_contains)
            ]
            # loop through fields, popping off matches
            for field in card.fields:
                try:
                    filter_contains.remove(field.strip())
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

    def _normalize_filter(self, filter):
        if filter is None:
            return {}
        elif isinstance(filter, str):
            return {"name": filter}
        else:
            return filter

    def find(self, filter=None):
        filter = self._normalize_filter(filter)
        for _, card in self._enumerate_find(filter):
            yield card

    def find_one(self, filter=None):
        try:
            return next(self.find(filter))
        except StopIteration:
            return None
    
    def replace(self, filter, card):
        filter = self._normalize_filter(filter)
        for i, _ in self._enumerate_find(filter):
            self._cards[i] = card
            
    def _update_card(self, card, update):
        for index, value in self._iter_index_value(update):
            card[index] = value
    
    def update(self, filter, update):
        filter = self._normalize_filter(filter)
        for i, _ in self._enumerate_find(filter):
            self._update_card(self._cards[i], update)
    
    def delete(self, filter=None):
        filter = self._normalize_filter(filter)
        delete_i = [i for i, _ in self._enumerate_find(filter)]
        for i in reversed(delete_i):
            del self._cards[i]
            
    def _get_card_by_index(self, index):
        return self._cards[index]
            
    def _get_cards_by_indexes(self, indexes):
        return [self._cards[i] for i in indexes]

    def _get_cards_by_name(self, name):
        return list(self.find({"name": name}))
    
    def _get_cards_by_slice(self, slice_):
        return list(self._cards[slice_])
            
    def __getitem__(self, key):
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
        return cls.loads(fp.read())

    def dumps(self, format=None):
        bulk = "".join([card.dumps(format) for card in self.cards])
        if self.header:
            return self.header + "\nBEGIN BULK\n" + bulk + "ENDDATA"
        else:
            return bulk

    def dump(self, fp, format=None):
        return fp.write(self.dumps(format=format))

    def __str__(self):
        return self.dumps()

    def __len__(self):
        return self.cards.__len__()

    def __iter__(self):
        return self.cards.__iter__()

    def __bool__(self):
        return bool(self.cards)

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, 
                               repr_list(self.cards))

    @property
    def cards(self):
        return self._cards


__all__ = ["Deck"]