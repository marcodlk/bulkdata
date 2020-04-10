from collections import OrderedDict

from .field import Field, LargeField
from .format import format_card
from .parse import BDFParser
from .util import islist, split_fields, repr_list


class Card:
    
    def __init__(self, name=None, size=0):
        self.name = name
        self._fields = [Field(None) for _ in range(size)]

    def _convert_to_fields(self, value, fieldspan=1):
        if fieldspan == 1:
            return [Field(value)]
        elif fieldspan > 1:
            return LargeField(value, fieldspan).split()
        else:
            raise ValueError("fieldspan < 1")

    def set_raw_fields(self, fields):
        self._fields = fields

    def append(self, value, fieldspan=1):
        self._fields.extend(self._convert_to_fields(value, fieldspan))

    def extend(self, values, fieldspan=1):
        if fieldspan == 1:
            fields = [Field(value) for value in values]
            self._fields.extend(fields)
        else:
            for value in values:
                self._fields.extend(self._convert_to_fields(value, fieldspan))

    def pop(self):
        return self._fields.pop()
        
    def resize(self, size):
        numfields = len(self._fields)
        diff = size - numfields
        if diff > 0:
            for _ in range(diff):
                self._fields.append(Field(None))
        if diff < 0:
            for _ in range(abs(diff)):
                self._fields.pop()
    
    def strip(self):
        for i in reversed(range(len(self._fields))):
            if not self._fields[i]:
                del self._fields[i]
        
    def _setsinglefield(self, index, value):
        self._fields[index] = Field(value)
        
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
            self._fields[index] = fields[i]
    
    def _setmultifield(self, indexs, value):
        if islist(value):
            self._setmultifieldlist(indexs, value)
        else:
            self._setmultifieldvalue(indexs, value)

    def _convert_slice_to_steps(self, slice_):
        start = slice_.start or 0
        stop  = slice_.stop or len(self._fields)
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

    def _getsinglefield(self, index):
        return self._fields[index].value

    def _getmultifield(self, indexs):
        return [self._fields[i].value for i in indexs]

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._getsinglefield(key)
        elif isinstance(key, slice):
            key = self._convert_slice_to_steps(key)
            return self._getmultifield(key)
        elif islist(key):
            return self._getmultifield(key)
        else:
            raise TypeError(key, type(key))

    def get_large(self, key):
        """Get field value spanning multiple fields
        """
        if isinstance(key, int):
            return self._getsinglefield(key)
        elif isinstance(key, slice):
            fields = self._fields[key]
        elif islist(key): 
            fields = [self._fields[i] for i in key]
        else:
            raise TypeError(key, type(key))
        return LargeField.join(fields).value
            
    def dumps(self, format=None):
        return format_card(self, format)
    
    @classmethod
    def loads(cls, card_str):

        card_name, card_fields = BDFParser(card_str).parse_card()
        obj = cls(card_name)
        obj.set_raw_fields([Field(value) for value in card_fields])
        
        return obj

    def values(self):
        return [field.value for field in self._fields]
    
    def __contains__(self, value):
        return self._fields.__contains__(value)
    
    def __str__(self):
        return self.dumps()

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

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, new_name):
        if new_name:
            new_name = new_name.strip()
        self._name = new_name
    
    @property
    def fields(self):
        return self._fields


class CardType:
    
    def __init__(self, name):
        self._name = name
        self._entries = OrderedDict()

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
        
        card = Card(self._name, size=numfields)
        
        for name, entry_meta in self._entries.items():
            
            value = entry_values[name]

            card[entry_meta["index"]] = value
            
        return card


__all__ = ["Card", "CardType"]