import re

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
    if is_integer_field(field):
        return read_integer_field(field)
    if is_real_field(field):
        return read_real_field(field)
    else:
        return field.strip()