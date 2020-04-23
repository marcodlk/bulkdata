from .field import Field


class BaseFormatter:

    newline = "\n"
    delimiter = ""
    valuesperline = 8 # fields with value, per line
    fieldwidth = 8

    def format_field(self, field):
        if isinstance(field, Field):
            field = field.raw
        else:
            field = field
        return field[:self.fieldwidth]
        
    def continuation(self, index=""):
        label = "+" + str(index)
        beg = self.format_field(label)
        end = self.format_field(label)
        return beg + self.newline + end

    def endofline(self, index):
        valuesperline = self.valuesperline
        if index and valuesperline:
            if index < valuesperline:
                return False
            else:
                return True
        else:
            return False

    def remove_trailing_blanks(self, fields):
        fields = list(fields)
        for i in reversed(range(len(fields))):
            if not fields[i]:
                del fields[i]
            else:
                break
        return fields

    def format_card(self, card):
        
        card_str = ""
        line_pos = 0   # position in the line
        line_count = 0 # line counter
        
        def concat_field(field, last_field=False):
            nonlocal card_str, line_pos, line_count

            card_str += self.format_field(field or " ")
            card_str += self.delimiter
            line_pos += 1
            
            # if end-of-line is reached, concat continuation
            if self.endofline(line_pos) and not last_field:
                card_str += self.continuation(line_count)
                card_str += self.delimiter
                line_pos = 0
                line_count += 1

        fields = self.remove_trailing_blanks(card.fields)
        print(fields)
        card_str += self.format_field(card.name or " ")

        if len(fields) > 0:
            card_str += self.delimiter

            for field in fields[:-1]:
                concat_field(field)
            
            concat_field(fields[-1], last_field=True)
        
        return card_str.rstrip(" " + self.delimiter) + self.newline


class FixedFormatter(BaseFormatter):

    def format_field(self, field):
        field = super().format_field(field)
        return "{:<{}}".format(field, self.fieldwidth)


class FreeFormatter(BaseFormatter):

    delimiter = ","


_formatters = {
    "fixed": FixedFormatter(),
    "free": FreeFormatter()
}

_defaultformat = "fixed"


def format_card(card, format=None):

    format = format or _defaultformat

    return _formatters[format].format_card(card)
