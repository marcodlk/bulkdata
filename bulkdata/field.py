import re

try:
    from pyNastran.bdf.field_writer_8 import print_field_8
    from pyNastran.bdf.field_writer_16 import print_field_16

except ImportError:
    from .pyNastran.bdf.field_writer_8 import print_field_8
    from .pyNastran.bdf.field_writer_16 import print_field_16


rx_REAL_pat = r"""
    [-+]? # optional sign
    (?:
        (?: \d* \. \d+ ) # .1 .12 .123 etc 9.1 etc 98.1 etc
        |
        (?: \d+ \.? ) # 1. 12. 123. etc 1 12 123 etc
    )
    # followed by optional exponent part if desired
    (?: 
        (?: [Ee]? [+-]?) \d+ 
    ) 
    ?
"""
rx_REAL = re.compile(rx_REAL_pat, re.VERBOSE)

rx_INT = re.compile(r"^[-+]?([1-9]\d*|0)$")


def _force_E(real_field):
    # if no "E" or "e", insert it
    return re.sub("(?<!^)(?<![E|e])[+-]", r"E\g<0>", real_field)


def _is_match(rx, field):
    field = field.strip()
    try:
        return rx.match(field).group(0) == field
    except (TypeError, IndexError, AttributeError):
        return False


def is_integer_field(field):
    return _is_match(rx_INT, field)


def is_real_field(field):
    return _is_match(rx_REAL, field)


def read_integer_field(field):
    return int(field)


def read_real_field(field):
    return float(_force_E(field))


def read_field(field):
    """Convert `field` string to value
    """
    if is_integer_field(field):
        return read_integer_field(field)
    if is_real_field(field):
        return read_real_field(field)
    else:
        return field.strip()
    

def write_field(value, fieldspan=1):
    """Convert `value` to field string
    """
    width = fieldspan * 8
    if isinstance(value, str):
        return value[:width].strip()
    elif width == 8:
        return print_field_8(value).strip()
    elif width == 16:
        return print_field_16(value).strip()
    else:
        raise ValueError("non-character field entries "
                         "cannot span more than 2 fields, "
                         "but fieldspan is {}".format(fieldspan))


class Field:
    
    def __init__(self, value, fieldspan=1):
        self.span = fieldspan
        self.value = value

    @property
    def width(self):
        return self.span * 8
    
    def __eq__(self, other):
        if isinstance(other, Field):
            return self.raw == other.raw
        elif isinstance(other, str):
            return self.raw == other
        else:
            return self.value == other

    def __str__(self):
        return self.raw
    
    def __repr__(self):
        return "{}('{}')".format(self.__class__.__name__, self.raw)

    def __bool__(self):
        return bool(self.raw)
    
    @property
    def value(self):
        if self._value_change:
            self._value = read_field(self.raw)
        return self._value
    
    @value.setter
    def value(self, new_value):
        self.raw = write_field(new_value, fieldspan=self.span)
        self._value_change = True
        
    
class LargeField(Field):
    
    def __init__(self, value, fieldspan=2):
        super().__init__(value, fieldspan)
        
    def split(self, fieldspan=1):
        """Split into Fields with given `fieldspan`
        """
        fieldwidth = fieldspan * 8
        fields = []
        for start in range(0, len(self.raw), fieldwidth):
            stop = start + fieldwidth
            fields.append(Field(self.raw[start:stop], fieldspan))
        return fields

    @classmethod
    def join(cls, fields):
        large_str = "".join([field.raw for field in fields])
        return cls(large_str, fieldspan=len(fields))