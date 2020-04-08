from collections.abc import Sequence
import re

from numpy import isnan

from .abc import BulkDataFormat
from .parse import BDFParser
from .writer import print_float_8, print_float_16


MAXLINELENGTH = 80

rx_REAL_pat = r"""
    [-+]? # optional sign
    (?:
        (?: \d* \. \d+ ) # .1 .12 .123 etc 9.1 etc 98.1 etc
        |
        (?: \d+ \.? ) # 1. 12. 123. etc 1 12 123 etc
    )
    # followed by optional exponent part if desired
    (?: 
        (?: [Ee]? | [+-]?) \d+ 
    ) 
    ?
"""
rx_REAL = re.compile(rx_REAL_pat, re.VERBOSE)

rx_INT = re.compile(r"^[-+]?([1-9]\d*|0)$")


class BaseFormat(BulkDataFormat):

    def __init__(self, delimiter, newline, 
                headwidth, fieldwidth, tailwidth, 
                fieldsperline, align):
        self.delimiter = delimiter
        self.newline = newline
        self.fieldwidth = fieldwidth
        self.tailwidth = tailwidth
        self.headwidth = headwidth
        self.fieldsperline = fieldsperline
        self.fieldsperbody = fieldsperline - 2
        self.align = align

    def split(self, fields_str):
        """Split `fields_str` into fields of length :attr:`fieldwidth`
        """
        fields = []
        for start in range(0, len(fields_str), self.fieldwidth):
            stop = start + self.fieldwidth
            fields.append(fields_str[start:stop])
        return fields

    def normalize(self, value):
        if isinstance(value, str):
            return value.strip()
        elif isinstance(value, Sequence):
            return [self.normalize(each) for each in value]
        else:
            return self.write_field(value).strip()

    def _format_str(self, value, align, width):
        """Convert string value to formatted field string.
        """
        field = "{:{}{}}".format(value, align, width)[:width]
        return field

    def _format_int(self, value, align, width):
        """Convert integer number to formatted field string.
        """
        field = "{:{}{}}".format(value, align, width)
        if len(field) > width:
            raise ValueError("Integer field value has too many digits: {}".format(value))
        return field

    def _format_real(self, value, align, width):
        if width == 8:
            field = "{:{}{}}".format(print_float_8(value).strip(), align, width) # TODO: clean this up
            return field
        elif width == 16:
            field = "{:{}{}}".format(print_float_16(value).strip(), align, width)
            return field
        else:
            raise Exception("Bad width: {}".format(width))

    def _calc_totalfieldwidth(self, fieldwidth, fieldspan):
        return (fieldwidth + len(self.delimiter)) * fieldspan - len(self.delimiter)
    
    def write_field(self, value, fieldspan=1, align=None, fieldwidth=None):
        fieldwidth = fieldwidth or self.fieldwidth
        if not fieldwidth:
            return str(value)
        align = align or self.align
        # width = (fieldwidth + len(self.delimiter)) * fieldspan - len(self.delimiter)
        width = self._calc_totalfieldwidth(fieldwidth, fieldspan)
        if isinstance(value, str):
            field = self._format_str(value, align, width)
        elif isinstance(value, int):
            field = self._format_int(value, align, width)
        else:
            field = self._format_real(value, align, width)
        return field

    def write_blank(self, fieldspan=1):
        return self.write_field(" ", fieldspan)
        
    def continuation(self, index=""):
        label = "+" + str(index)
        beg = self.write_field(label, align="<")
        end = self.write_field(label, align="<")
        return beg + self.newline + end + self.delimiter
    
    def endofline(self, index):
        maxfields = self.fieldsperbody
        if index and maxfields:
            if index < maxfields:
                return False
            else:
                return True
        else:
            return False

    def write_card(self, card):
        
        card_str = ""
        line_pos = 0   # position in the line
        line_count = 0 # line counter
        
        def concat_field(field, last_field=False):
            nonlocal card_str, line_pos, line_count

            # card_str += field or self.write_blank()
            card_str += self.write_field(field or " ")
            card_str += self.delimiter
            line_pos += 1
            
            # if end-of-line is reached, concat continuation
            if self.endofline(line_pos) and not last_field:
                card_str += self.continuation(line_count)
                line_pos = 0
                line_count += 1

        fields = card.fields
        card_str += self.write_field(card.name or " ")

        if len(fields) > 0:
            card_str += self.delimiter

            for field in fields[:-1]:
                concat_field(field)
            
            concat_field(fields[-1], last_field=True)
        
        return card_str.rstrip(" ") + self.newline

    def write_deck(self, deck):
        deck_str = "".join([self.write_card(card) for card in deck])
        if hasattr(deck, "header"):
            deck_str = deck.header + deck_str
        return deck_str

    def _force_E(self, real_field):
        # if no "E" or "e", insert it
        return re.sub("(?<!^)(?<![E|e])[+-]", r"E\g<0>", real_field)

    def _is_match(self, rx, field):
        field = field.strip()
        try:
            return rx.match(field).group(0) == field
        except (TypeError, IndexError, AttributeError):
            return False

    def is_integer_field(self, field):
        return self._is_match(rx_INT, field)

    def is_real_field(self, field):
        return self._is_match(rx_REAL, field)

    def read_integer_field(self, field):
        return int(field)

    def read_real_field(self, field):
        return float(self._force_E(field))

    def read_field(self, field):
        if self.is_integer_field(field):
            return self.read_integer_field(field)
        if self.is_real_field(field):
            return self.read_real_field(field)
        else:
            return field.strip()

    def is_comment(self, line):
        line = line.lstrip()
        return line and line[0] == "$"

    def read_line(self, line):
        fieldwidth = self.fieldwidth
        length = len(line)
        assert length <= MAXLINELENGTH
        fields = [line[i:i+fieldwidth] 
                for i in range(0, length, fieldwidth)]
        numfields = len(fields)
        head = None
        values = None
        tail = None
        if numfields == 0:
            raise ValueError("empty line")
        if numfields > 0:
            head = fields[0]
        if numfields > 1:
            values = fields[1:]
        if numfields == self.fieldsperline:
            tail = values.pop(-1)
        return head, values, tail

    def next_continuation_fields(self, lines_iter):

        while lines_iter:

            line = next(lines_iter)

            if self.is_comment(line):
                continue

            try:
                _, fields, tail = self.read_line(line)
            except ValueError:
                break

            yield fields

            if tail is None:
                break

    def next_card_fields(self, lines_iter):

        line = next(lines_iter)

        while self.is_comment(line):
            line = next(lines_iter)

        if not line.strip():
            raise ValueError("empty line")

        head, fields, tail = self.read_line(line)

        if tail:
            # get all continuation lines of card
            for cont_fields in self.next_continuation_fields(lines_iter):
                fields.extend(cont_fields)

        return head, fields

    def read_card(self, card_str):

        return BDFParser(card_str).parse_card()

    def split_header(self, deck_str):

        beginbulk = "BEGIN BULK"
        try:
            beginbulk_i = deck_str.index(beginbulk)
        except ValueError:
            return "", deck_str
        else:
            header_str = deck_str[:beginbulk_i]
            deck_str = deck_str[beginbulk_i + len(beginbulk):]
            return header_str, deck_str

    def ignore_enddata(self, deck_str):
        
        enddata = "ENDDATA"
        try:
            enddata_i = deck_str.index(enddata)
        except ValueError:
            return deck_str
        else:
            return deck_str[:enddata_i]

    def read_deck(self, deck_str):

        header, cards = BDFParser(deck_str).parse()

        return header, cards


class FixedFormat(BaseFormat):
    """ZAERO Fixed Format
    """
    def __init__(self, align="left"):
        if align in ["<", "left"]:
            align = "<"
        elif align in [">", "right"]:
            align = ">"
        else:
            raise ValueError(align)
        super().__init__(delimiter="", newline="\n", headwidth=8, 
                         fieldwidth=8, tailwidth=8, fieldsperline=10, 
                         align=align)


class FreeFormat(BaseFormat):

    def __init__(self):
        super().__init__(delimiter=",", newline="\n", headwidth=8, 
                         fieldwidth=8, tailwidth=8, fieldsperline=10, 
                         align="")
    
    def _calc_totalfieldwidth(self, fieldwidth, fieldspan):
        return fieldwidth * fieldspan

    def write_field(self, value, fieldspan=1, align=None, fieldwidth=None):
        field = super().write_field(value, fieldspan, align, fieldwidth)
        return field.strip()

    def write_blank(self):
        return " "

    def read_line(self, line):
        length = len(line)
        assert length <= MAXLINELENGTH
        fields = line.rstrip(",").split(",")
        numfields = len(fields)
        head = None
        values = None
        tail = None
        if numfields == 0:
            raise ValueError("empty line")
        if numfields > 0:
            head = fields[0]
        if numfields > 1:
            values = fields[1:]
        if numfields == self.fieldsperline:
            tail = values.pop(-1)
        return head, values, tail


class SmallFormat(BaseFormat):
    """NASTRAN Small Format
    """
    def __init__(self, align="left"):
        if align in ["<", "left"]:
            align = "<"
        elif align in [">", "right"]:
            align = ">"
        else:
            raise ValueError(align)
        super().__init__(delimiter="", newline="\n", headwidth=8, 
                         fieldwidth=8, tailwidth=8, fieldsperline=10, 
                         align=align)


# class LargeFormat(BaseFormat):
#     """NASTRAN Large Format (TODO)
#     """
#     def __init__(self):a
#         if align in ["<", "left"]:
#             align = "<"
#         elif align in [">", "right"]:
#             align = "<"
#         else:
#             raise ValueError(align)
#         super().__init__(delimiter="", newline="\n", headwidth=8, 
#                          fieldwidth=16, tailwidth=8, fieldsperline=6, 
#                          align=align)


DefaultFormat = FixedFormat


__all__ = ["FixedFormat", "FreeFormat"]