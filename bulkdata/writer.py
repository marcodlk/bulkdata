try:
    from pyNastran.bdf.field_writer_8 import print_float_8
    from pyNastran.bdf.field_writer_16 import print_float_16

except ImportError:
    from .pyNastran.bdf.field_writer_8 import print_float_8
    from .pyNastran.bdf.field_writer_16 import print_float_16
