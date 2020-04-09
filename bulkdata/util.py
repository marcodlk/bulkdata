from collections.abc import Sequence


def islist(value):
    return isinstance(value, Sequence) and not isinstance(value, str)


def repr_list(list_):
    if len(list_) > 10:
        return "[{} ... {}]".format(repr(list_[0]), repr(list_[-1]))
    else:
        return repr(list_)


def split_fields(fields_str, fieldwidth=8):
    """Split `fields_str` into fields of length `fieldwidth`
    """
    fields = []
    for start in range(0, len(fields_str), fieldwidth):
        stop = start + fieldwidth
        fields.append(fields_str[start:stop])
    return fields