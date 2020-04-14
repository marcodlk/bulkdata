"""The :mod:`~bulkdata.card` module provides classes related
to the creation and manipulation of bulk data card objects.
It contains the :class:`~bulkdata.card.Card` class that 
facilitates the conversion of collections of field values to
and from bulk data card formatted strings.
"""

from collections import OrderedDict

from .field import Field, LargeField
from .format import format_card
from .parse import BDFParser
from .util import islist, split_fields, repr_list


class Card:
    """:class:`~bulkdata.card.Card` class allows the user 
    to create and modify bulk data cards.

    :param name: The name of the card
    :param size: The number of initial blank fields, defaults to 0
    """
    
    def __init__(self, name=None, size=0):
        self.name = name
        self._fields = [self._blank_field() for _ in range(size)]

    def _convert_to_fields(self, value, fieldspan=1):
        if fieldspan == 1:
            return [Field(value)]
        elif fieldspan > 1:
            return LargeField(value, fieldspan).split()
        else:
            raise ValueError("fieldspan < 1")

    def _blank_field(self):
        return Field(None)

    def set_raw_fields(self, fields):
        """Set the fields directly, without internal conversion of `fields`
        values to `Field` objects.
        
        .. note:: 
            
            The user should avoid using this function unless he/she
            knows what they are doing.
        """
        self._fields = fields

    def append(self, value, fieldspan=1):
        """Append a field value to card fields.

        :param value: The field value
        :param fieldspan: The number of field cells the value spans,
                          defaults to 1
        """
        self._fields.extend(self._convert_to_fields(value, fieldspan))

    def extend(self, values, fieldspan=1):
        """Extend card fields with sequence of field values.

        :param values: The sequence of field values
        :param fieldspan: The number of field cells that each value spans,
                          defaults to 1
        """
        if fieldspan == 1:
            fields = [Field(value) for value in values]
            self._fields.extend(fields)
        else:
            for value in values:
                self._fields.extend(self._convert_to_fields(value, fieldspan))

    def pop(self):
        """Remove the last field.
        """
        return self._fields.pop()
        
    def resize(self, size):
        """Resize the card fields to contain *size* fields. If current
        number of fields is greater than *size*, the extra fields will
        be removed from the end. If number of fields is less than *size*,
        extra blank fields are appended.

        :param size: The desired number of fields
        """
        numfields = len(self._fields)
        diff = size - numfields
        if diff > 0:
            for _ in range(diff):
                self._fields.append(Field(None))
        if diff < 0:
            for _ in range(abs(diff)):
                self._fields.pop()
    
    def strip(self): #TODO: rename to rstrip ?
        """Remove any trailing blank fields.
        """
        for i in reversed(range(len(self._fields))):
            if not self._fields[i]:
                del self._fields[i]
            else:
                break
        
    def _setsinglefield(self, index, value):
        """Set a single field value at the index.
        """
        self._fields[index] = Field(value)
        
    def _setmultifieldlist(self, indexs, values):
        """Set list of field values at the given indexes.
        """
        numindexs = len(indexs)
        if len(values) > numindexs:
            raise IndexError("Number of values, {}, greater than number "
                             "of indexes, {}.\n"
                             "Values: {}\n"
                             "Indexs: {}"
                             .format(len(values), numindexs, values, indexs))
        for i, index in enumerate(indexs):
            try:
                value = values[i]
            except IndexError:
                # no more values, set blank
                value = None
            self._setsinglefield(index, value)
            
    def _setmultifieldvalue(self, indexs, value):
        """Set a field value spanning multiple field cells given 
        by indexes.
        """
        fieldspan = len(indexs)
        if fieldspan < 1:
            raise ValueError("fieldspan < 1")
        fields = self._convert_to_fields(value, fieldspan=fieldspan)
        for i, index in enumerate(indexs):
            try:
                new_field = fields[i]
            except IndexError:
                new_field = self._blank_field()
            self._fields[index] = new_field
    
    def _setmultifield(self, indexs, value):
        """Set field value(s) spanning multiple field cells.
        """
        if islist(value):
            self._setmultifieldlist(indexs, value)
        else:
            self._setmultifieldvalue(indexs, value)

    def _convert_slice_to_steps(self, slice_):
        """Convert a slice to a list of the corresponding steps.
        """
        start = slice_.start or 0
        stop  = slice_.stop or len(self._fields)
        step  = slice_.step or 1
        return list(range(start, stop, step))
        
    def __setitem__(self, key, value):
        """Set field item into the card.

        :type key: int, slice, list
        :param key: The indexing key denoting where to set 
                    the field(s)
        :param value: The field value(s) to set
        """
        if isinstance(key, int):
            self._setsinglefield(key, value)
        elif isinstance(key, slice):
            steps = self._convert_slice_to_steps(key)
            self._setmultifield(steps, value)
        elif islist(key):
            self._setmultifield(key, value)
        else:
            raise TypeError(key, type(key))

    def _getsinglefield(self, index):
        """Get a single field value at the index.
        """
        return self._fields[index].value

    def _getmultifield(self, indexs):
        """Get list of field values at the given indexes.
        """
        return [self._fields[i].value for i in indexs]

    def __getitem__(self, key):
        """Get field item from the card.

        :type key: int, slice, list
        :param key: The indexing key denoting which field(s) to get
        :return: The field value(s)
        """
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
        """Get field value spanning multiple fields. This gets the
        same fields as :meth:`~bulkdata.card.Card.__getitem__`
        but it joins them before converting to a single large value.
        
        :param key: The indexing object denoting which field(s) to get
        :return: The large field value
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

    def __delitem__(self, key):
        """Delete the field item from card.
        
        :type key: int, slice
        :param key: The indexing key denoting which field(s)
                    to delete
        """
        self._fields.__delitem__(key)
            
    def dumps(self, format="fixed"):
        """Dump the card to bulk data formatted string.

        :param format: the desired format, can be one of: 
                       ["free", "fixed"], defaults to "fixed"
        :return: The bulk data card string representation
        """
        return format_card(self, format)
    
    @classmethod
    def loads(cls, card_str):
        """Load :class:`~bulkdata.card.Card` object from a
        bulk data card string.

        :param card_str: the bulk data card string
        :return: The loaded :class:`~bulkdata.card.Card` object
        """
        card_name, card_fields = BDFParser(card_str).parse_card()
        obj = cls(card_name)
        obj.set_raw_fields([Field(value) for value in card_fields])
        
        return obj

    def values(self):
        """Get a list of the values of the card fields.
        """
        return [field.value for field in self._fields]
    
    def __contains__(self, value):
        """Return ``True`` if the card contains a field
        with the specified value, ``False`` otherwise.

        :param value: The specified value
        """
        return self._fields.__contains__(value)
    
    def __str__(self):
        """Dump the card to as a bulk data card string
        with default format.
        
        :return: The bulk data card string
        """
        return self.dumps()

    def __len__(self):
        """Return number of fields in the card.
        """
        return self.fields.__len__()

    def __iter__(self):
        """Iterate through the fields in the card.
        """
        return self.fields.__iter__()

    def __bool__(self):
        """Return ``True`` if the card contains any fields,
        ``False`` otherwise.
        """ 
        return bool(self.fields)

    def __repr__(self):
        return "{}(\"{}\", {})".format(self.__class__.__name__, 
                                   self.name, 
                                   repr_list(self.values()))

    @property
    def name(self):
        """The card name.
        """
        return self._name
    
    @name.setter
    def name(self, new_name):
        if new_name:
            new_name = new_name.strip()
        self._name = new_name
    
    @property
    def fields(self):
        """The card fields.
        """
        return self._fields


# class CardType:
    
#     def __init__(self, name):
#         self._name = name
#         self._entries = OrderedDict()

#     def register(self, name, index, default=None, valid=None, fieldspan=1):
#         entry_meta = {
#             "index": index,
#             "default": default,
#             "valid": valid,
#             "fieldspan": fieldspan
#         }
#         self._entries[name] = entry_meta

#     def _validate(self, valid, value):
#         if valid and not valid(value):
#             raise Exception("failed validation") #TODO

#     def __call__(self, *args, **kwargs):
        
#         entry_names = list(self._entries.keys())
#         entry_values = {}
        
#         for arg in args:
#             name = entry_names.pop(0)
#             entry_values[name] = arg
            
#         for name, arg in kwargs.items():
#             entry_names.pop(entry_names.index(name))
#             entry_values[name] = arg
            
#         # entries not handled by args or kwargs, try to use defaults
#         for name in entry_names:
#             default = self._entries[name].get("default")
#             if default is not None:
#                 entry_values[name] = default
#             else:
#                 raise ValueError("No value specified for required field: {}".format(name))

#         # validate and count total number of fields required
#         numfields = 0
#         for name, entry_meta in self._entries.items():
            
#             value = entry_values[name]
#             fieldspan = entry_meta["fieldspan"]
#             valid = entry_meta["valid"]
            
#             if islist(value):
                
#                 for each in value:
#                     self._validate(valid, each)
#                 numfields += len(value) * fieldspan
                
#             else:
                
#                 self._validate(valid, value)
#                 numfields += 1 * fieldspan
        
#         card = Card(self._name, size=numfields)
        
#         for name, entry_meta in self._entries.items():
            
#             value = entry_values[name]

#             card[entry_meta["index"]] = value
            
#         return card


__all__ = ["Card"]