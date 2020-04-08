from collections.abc import Sequence


def islist(value):
    return isinstance(value, Sequence) and not isinstance(value, str)


def repr_list(list_):
    if len(list_) > 10:
        return "[{} ... {}]".format(repr(list_[0]), repr(list_[-1]))
    else:
        return repr(list_)