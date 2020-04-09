try:
    from pyNastran.bdf.field_writer_8 import print_float_8
    from pyNastran.bdf.field_writer_16 import print_float_16
    from pyNastran.bdf.field_writer_8 import print_field_8
    from pyNastran.bdf.field_writer_16 import print_field_16

except ImportError:
    from .pyNastran.bdf.field_writer_8 import print_float_8
    from .pyNastran.bdf.field_writer_16 import print_float_16
    from .pyNastran.bdf.field_writer_8 import print_field_8
    from .pyNastran.bdf.field_writer_16 import print_field_16


def write_field(value, fieldspan=1):
    """Convert `value` to field string
    """
    width = fieldspan * 8
    if isinstance(value, str):
        field = value[:width]
    elif width == 8:
        field = print_field_8(value).strip()
    elif width == 16:
        field = print_field_16(value).strip()
    else:
        raise ValueError("non-character field entries "
                         "cannot span more than 2 fields, "
                         "but received fieldspan: {}".format(fieldspan))
    return "{:<{}}".format(field, width)