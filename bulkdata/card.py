from collections import OrderedDict
from collections.abc import Sequence

from .abc import BulkDataCard
from .format import DefaultFormat
from .util import islist


class RawCard(BulkDataCard):

    def __init__(self, name=None, size=0):
        self._name = name
        self._fields = [None for _ in range(size)]

    def append(self, field):
        self._fields.append(field)

    def extend(self, fields):
        self._fields.extend(fields)

    def pop(self):
        return self._fields.pop()
        
    def resize(self, size):
        numfields = len(self._fields)
        diff = size - numfields
        if diff > 0:
            for _ in range(diff):
                self._fields.append(None)
        if diff < 0:
            for _ in range(abs(diff)):
                self._fields.pop()
    
    def strip(self):
        for i in reversed(range(len(self._fields))):
            if not self._fields[i]:
                del self._fields[i]

    def __setitem__(self, key, value):
        if islist(key):
            for i in key:
                self._fields.__setitem__(i)
        else:
            self._fields.__setitem__(key, value)

    def __getitem__(self, key):
        if islist(key):
            return [self._fields.__getitem__(i)
                    for i in key]
        else:
            return self._fields.__getitem__(key)

    def __contains__(self, value):
        # normalize value and field values to be comparable
        normal_value = value.strip()
        normal_fields = [field.strip() for field in self._fields]
        return normal_fields.__contains__(normal_value)

    # def __repr__(self):
    #     return "{}({})".format(self.__class__.__name__, self._name)

    # def __len__(self):
    #     return self._fields.__len__()

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, new_name):
        self._name = new_name

    @property
    def fields(self):
        return self._fields

    @fields.setter
    def fields(self, new_fields):
        self._fields = new_fields


class Card(BulkDataCard):
    
    def __init__(self, name=None, size=0, format=None):
        self._format = format or DefaultFormat()
        self._raw = RawCard(size=size)
        self.name = name

    def _convert_to_fields(self, value, fieldspan=1):
        if fieldspan == 1:
            return [self._format.write_field(value).strip()]
        elif fieldspan > 1:
            longfield = self._format.write_field(value, fieldspan=fieldspan)
            return [field.strip() for field in self._format.split(longfield)]
        else:
            raise ValueError("fieldspan < 1")

    def set_raw_fields(self, fields):
        self._raw.fields = fields

    def reformat(self, new_format):
        field_values = [self._format.read_field(field)
                        for field in self.fields]
        self.resize(0)
        self._format = new_format
        for value in field_values:
            self.append(value)

    def append(self, value, fieldspan=1):
        self._raw.extend(self._convert_to_fields(value, fieldspan))

    def extend(self, values, fieldspan=1):
        if fieldspan == 1:
            fields = [self._format.write_field(value).strip()
                      for value in values]
            self._raw.extend(fields)
        else:
            for value in values:
                self._raw.extend(self._convert_to_fields(value, fieldspan))

    def pop(self):
        return self._raw.pop()
        
    def resize(self, size):
        self._raw.resize(size)
    
    def strip(self):
        self._raw.strip()
        
    def _setsinglefield(self, index, value):
        self._raw[index] = self._format.write_field(value).strip()
        
    def _setmultifieldlist(self, indexs, values):
        numindexs = len(indexs)
        if len(values) > numindexs:
            raise IndexError("Number of values, {}, greater than number "
                             "of indexes, {}.\n"
                             "Values: {}\n"
                             "Indexs: {}"
                             .format(len(values), numindexs, values, indexs))
        for i, index in enumerate(indexs):
            try:
                self._setsinglefield(index, values[i])
            except IndexError:
                # no more values to set
                break
            
    def _setmultifieldvalue(self, indexs, value):
        fieldspan = len(indexs)
        if fieldspan < 1:
            raise ValueError("fieldspan < 1")
        fields = self._convert_to_fields(value, fieldspan=fieldspan)
        for i, index in enumerate(indexs):
            self._raw[index] = fields[i]
    
    def _setmultifield(self, indexs, value):
        if islist(value):
            self._setmultifieldlist(indexs, value)
        else:
            self._setmultifieldvalue(indexs, value)

    def _convert_slice_to_steps(self, slice_):
        start = slice_.start or 0
        stop  = slice_.stop or len(self._raw)
        step  = slice_.step or 1
        return list(range(start, stop, step))
        
    def __setitem__(self, key, value):
        if isinstance(key, int):
            self._setsinglefield(key, value)
        elif isinstance(key, slice):
            steps = self._convert_slice_to_steps(key)
            self._setmultifield(steps, value)
        elif islist(value):
            self._setmultifield(key, value)
        else:
            raise TypeError(key, type(key))

    def _getsinglefield(self, key):
        field = self._raw.__getitem__(key)
        return self._format.read_field(field)

    def _getmultifield(self, key):
        fields = self._raw.__getitem__(key)
        return [
            self._format.read_field(field)
            for field in fields
        ]

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._getsinglefield(key)
        elif islist(key) or isinstance(key, slice):
            return self._getmultifield(key)
        else:
            raise TypeError(key, type(key))

    def get_long(self, key):
        """Get field value spanning multiple fields
        """
        if isinstance(key, int):
            return self._getsinglefield(key)
        elif islist(key) or isinstance(key, slice):
            fields = self._raw.__getitem__(key)
            longfield = "".join(fields)
            return self._format.read_field(longfield)
        else:
            raise TypeError(key, type(key))
            
    def dumps(self, format=None):
        format = format or self._format
        return format.write_card(self)
    
    @classmethod
    def loads(cls, card_str, format=None):
        
        format = format or DefaultFormat()

        card_name, card_fields = format.read_card(card_str) 
        obj = cls(card_name, format=format)
        obj._raw.extend(card_fields)
        
        return obj
    
    def __contains__(self, value):
        # normalize value and field values to be comparable
        normal_value = self._format.normalize(value)
        normal_fields = self._format.normalize(self._raw.fields)
        return normal_fields.__contains__(normal_value)
    
    def __str__(self):
        return self.dumps()

    # def __repr__(self):
    #     return "{}({})".format(self.__class__.__name__, self.name, self.fields)

    @property
    def name(self):
        return self._raw.name
    
    @name.setter
    def name(self, new_name):
        self._raw.name = new_name
    
    @property
    def fields(self):
        return self._raw.fields

    @property
    def format(self):
        return self._format

    @format.setter
    def format(self, new_format):
        self.reformat(new_format)


class CardType:
    
    def __init__(self, name, format=None):
        self._name = name
        self._entries = OrderedDict()
        self._format = format

    def register(self, name, index, default=None, valid=None, fieldspan=1):
        entry_meta = {
            "index": index,
            "default": default,
            "valid": valid,
            "fieldspan": fieldspan
        }
        self._entries[name] = entry_meta

    def _validate(self, valid, value):
        if valid and not valid(value):
            raise Exception("failed validation") #TODO

    def __call__(self, *args, **kwargs):
        
        entry_names = list(self._entries.keys())
        entry_values = {}
        
        for arg in args:
            name = entry_names.pop(0)
            entry_values[name] = arg
            
        for name, arg in kwargs.items():
            entry_names.pop(entry_names.index(name))
            entry_values[name] = arg
            
        # entries not handled by args or kwargs, try to use defaults
        for name in entry_names:
            default = self._entries[name].get("default")
            if default is not None:
                entry_values[name] = default
            else:
                raise ValueError("No value specified for required field: {}".format(name))

        # validate and count total number of fields required
        numfields = 0
        for name, entry_meta in self._entries.items():
            
            value = entry_values[name]
            fieldspan = entry_meta["fieldspan"]
            valid = entry_meta["valid"]
            
            if islist(value):
                
                for each in value:
                    self._validate(valid, each)
                numfields += len(value) * fieldspan
                
            else:
                
                self._validate(valid, value)
                numfields += 1 * fieldspan
        
        card = Card(self._name, size=numfields, format=self._format)
        
        for name, entry_meta in self._entries.items():
            
            value = entry_values[name]

            card[entry_meta["index"]] = value
            
        return card

    @property
    def format(self):
        return self._format


__all__ = ["RawCard", "Card"]