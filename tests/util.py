from bulkdata.field import Field

class MockCard():

    def __init__(self, name, fields):
        self._name = name
        self._fields = [Field(val) for val in fields]

    @property
    def name(self):
        return self._name

    @property
    def fields(self):
        return self._fields