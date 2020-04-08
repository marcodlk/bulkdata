from abc import ABC, abstractmethod
from .util import repr_list

class BulkDataCard(ABC):

    @property
    @abstractmethod
    def name(self):
       return ""

    @property
    @abstractmethod
    def fields(self):
        return []

    def __len__(self):
        return self.fields.__len__()

    def __iter__(self):
        return self.fields.__iter__()

    def __bool__(self):
        return bool(self.fields)

    def __repr__(self):
        return "{}({}, {})".format(self.__class__.__name__, 
                                   self.name, 
                                   repr_list(self.fields))


class BulkDataDeck(ABC):

    @property
    @abstractmethod
    def cards(self):
        return []

    def __len__(self):
        return self.cards.__len__()

    def __iter__(self):
        return self.cards.__iter__()

    def __bool__(self):
        return bool(self.cards)

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, 
                               repr_list(self.cards))


class BulkDataFormat(ABC):
    """Base class for bulk data formatting object that handles
    serialization and deserialization of bulk data objects, as
    well as any utility functions related to formatting
    """

    @abstractmethod
    def write_field(self, value, fieldspan):
        return NotImplemented

    @abstractmethod
    def write_card(self, name, fields):
        return NotImplemented

    @abstractmethod
    def write_deck(self, card_strs):
        return NotImplemented

    # @abstractmethod
    # def read_field(self, field_str):
    #     return NotImplemented

    @abstractmethod
    def read_card(self, card_str):
        return NotImplemented

    @abstractmethod
    def read_deck(self, deck_str):
        return NotImplemented
