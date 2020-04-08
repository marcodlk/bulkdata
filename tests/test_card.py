#!/usr/bin/env python

"""Tests for `bulkdata.card` module."""

import pytest
from collections.abc import Sequence

from bulkdata.format import FixedFormat, FreeFormat
from bulkdata.card import Card, CardType
from bulkdata.card import RawCard


@pytest.fixture 
def fields():
    return {
        "id": 99,
        "string": "helloworld",
        "integers": [0, 1, 2],
        "reals": [3.3, 6.6, 9.9]
    }


@pytest.fixture
def card_str():
    return """\
HELLO   99      helloworld      0       3.3     1       6.6     2       +0      
+0      9.9
"""


def test_rawcard(fields, card_str):

    format_ = FixedFormat()
    numfields = 1 + 2 + len(fields["integers"]) + len(fields["reals"])

    card = RawCard(format_.write_field("HELLO"), size=numfields)

    assert len(card.fields) == numfields

    card[0] = format_.write_field(fields["id"])
    card[1:3] = format_.split(format_.write_field(fields["string"], fieldspan=2))
    card[3::2] = [format_.write_field(integer) for integer in fields["integers"]]
    card[4::2] = [format_.write_field(real) for real in fields["reals"]]

    assert len(card.fields) == numfields
    assert format_.normalize(card[0]) == format_.normalize(fields["id"])
    assert format_.normalize("".join(card[1:3])) == format_.normalize(fields["string"])
    assert format_.normalize(card[3::2]) == format_.normalize(fields["integers"])
    assert format_.normalize(card[4::2]) == format_.normalize(fields["reals"])

    assert format_.write_card(card) == card_str

    # card = bulkdata.RawCard("HELLO", size=numfields)

    # card[0] = bulkdata.to_field(fields["id"])
    # card[1:3]  = bulkdata.to_fields(fields["string"], span=2)
    # card[3::2] = bulkdata.to_fields(fields["integers"])
    # card[4::2] = bulkdata.to_fields(fields["reals"])

    # bulkdata.dumps(card) == card_str

    # bulkdata.to_field(99) in card


def test_card_blank():

    size = 16
    card = Card("BLANK", format=FixedFormat(), size=size)
    assert len(card.fields) == size
    # format object strips trailing blank fields during write
    expect = """\
BLANK                                                                   +0      
+0
"""
    assert card.dumps() == expect


def test_card_setmultifieldvalue():

    long_string = "the-answer-is-42"
    long_number = 1234567891012345

    card = Card(format=FixedFormat(), size=2)
    card[:] = long_string
    got_string = "".join(card[:])
    assert got_string == long_string
    
    card[:] = long_number
    got_number = "".join([str(num) for num in card[:]]) # pylint: disable=not-an-iterable
    assert int(got_number) == long_number


def test_card_size_set(fields, card_str):

    format_ = FixedFormat()

    numfields = 1 + 2 + len(fields["integers"]) + len(fields["reals"])
    card = Card("HELLO", format=format_, size=numfields)

    assert len(card.fields) == numfields

    card[0] = fields["id"]
    card[1:3] = fields["string"]
    card[3::2] = fields["integers"]
    card[4::2] = fields["reals"]

    assert len(card.fields) == numfields
    assert card[0] == fields["id"]
    assert "".join(card[1:3]) == fields["string"]
    assert card[3::2] == fields["integers"]
    assert card[4::2] == fields["reals"]

    assert card.dumps() == card_str


def test_card_resize_set(fields, card_str):

    format_ = FixedFormat()

    numfields = 1 + 2 + len(fields["integers"]) + len(fields["reals"])
    card = Card("HELLO", format=format_)
    card.resize(numfields)

    assert len(card.fields) == numfields

    card[0] = fields["id"]
    card[1:3] = fields["string"]
    card[3::2] = fields["integers"]
    card[4::2] = fields["reals"]

    assert len(card.fields) == numfields
    assert card[0] == fields["id"]
    assert "".join(card[1:3]) == fields["string"]
    assert card[3::2] == fields["integers"]
    assert card[4::2] == fields["reals"]

    assert card.dumps() == card_str


def test_card_oversize_set_strip(fields, card_str):

    numfields = 1 + 2 + len(fields["integers"]) + len(fields["reals"])
    size = 1000
    card = Card("HELLO", format=FixedFormat(), size=size)

    assert len(card.fields) == size

    card[0] = fields["id"]
    card[1:3] = fields["string"]
    card[3::2] = fields["integers"]
    card[4::2] = fields["reals"]

    card.strip()

    assert len(card.fields) == numfields
    assert card[0] == fields["id"]
    assert "".join(card[1:3]) == fields["string"]
    assert card[3::2] == fields["integers"]
    assert card[4::2] == fields["reals"]

    assert card.dumps() == card_str


def test_card_append():

    card = Card("TEST")
    for value in [1, 2, 3, 4, 5, 6, 7, 8]:
        card.append(value)
    for value in [1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8]:
        card.append(value)
    for value in ["a", "b", "c", "d", "e", "f", "g","h"]:
        card.append(value)

    expect = """\
TEST    1       2       3       4       5       6       7       8       +0      
+0      1.1     2.2     3.3     4.4     5.5     6.6     7.7     8.8     +1      
+1      a       b       c       d       e       f       g       h
"""
    assert card.dumps() == expect


def test_card_extend():

    card = Card("TEST")
    card.extend([1, 2, 3, 4, 5, 6, 7, 8])
    card.extend([1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8])
    card.extend(["a", "b", "c", "d", "e", "f", "g","h"])

    expect = """\
TEST    1       2       3       4       5       6       7       8       +0      
+0      1.1     2.2     3.3     4.4     5.5     6.6     7.7     8.8     +1      
+1      a       b       c       d       e       f       g       h
"""
    assert card.dumps() == expect


def test_card_incremental_set_append(fields, card_str):

    card = Card("HELLO", format=FixedFormat())
    card.append(fields["id"])
    card.append(fields["string"], 2)
    for integer, real in zip(fields["integers"], fields["reals"]):
        card.append(integer)
        card.append(real)

    assert card.dumps() == card_str


def test_card_incremental_set_extend(fields, card_str):

    card = Card("HELLO", format=FixedFormat())
    card.extend([fields["id"], "helloworl", "ld"])
    for integer, real in zip(fields["integers"], fields["reals"]):
        card.extend([integer, real])

    assert card.dumps() == card_str


def test_load_card_modify(fields, card_str):

    card = Card.loads(card_str, format=FixedFormat())
    assert card.dumps() == card_str
    
    for value in fields.values():
        if isinstance(value, str):# and len(value) > 8:
            assert value[:8] in card
        elif isinstance(value, Sequence):
            for each in value:
                assert each in card
        else:
            assert value in card

    card.name = "GOODBYE"
    card[0] = 100
    card[1] = "she"
    card[2] = "planet"
    card[3::2] = [3, 4, 5]
    card[4::2] = [1.1, 2.2, 3.3]

    modified_card_str = """\
GOODBYE 100     she     planet  3       1.1     4       2.2     5       +0      
+0      3.3
"""

    assert card.dumps() == modified_card_str


def test_card_get_long_string():

    long_string = "the-answer-to-life-the-universe-and-everything"

    card = Card("LONGSTR", format=FixedFormat())
    card.append(long_string, fieldspan=8)

    got_string = card.get_long(slice(0, 8, 1))
    assert got_string == long_string

    got_string = card.get_long(slice(0, None, 1))
    assert got_string == long_string

    index = list(range(8))
    got_string = card.get_long(index)
    assert got_string == long_string

    got_string = card.get_long(0)
    assert got_string == "the-answ"


def test_card_get_long_number():

    long_number =  1000000000000000

    card = Card("LONGNUM", format=FixedFormat())
    card.append(long_number, fieldspan=2)

    got_number = card.get_long(slice(0, 2, 1))
    assert got_number == long_number

    got_number = card.get_long(slice(0, None, 1))
    assert got_number == long_number

    index = list(range(2))
    got_number = card.get_long(index)
    assert got_number == long_number

    got_number = card.get_long(0)
    assert got_number == 10000000


# def test_card_get_long_number():

#     long_number =  1000000000000000000000000000000000000000000000

#     card = Card("LONGNUM", format=FixedFormat())
#     card.append(long_number, fieldspan=8)

#     got_number = card.get_long(slice(0, 8, 1))
#     assert got_number == long_number

#     got_number = card.get_long(slice(0, None, 1))
#     assert got_number == long_number

#     index = list(range(8))
#     got_number = card.get_long(index)
#     assert got_number == long_number

#     got_number = card.get_long(0)
#     assert got_number == 10000000


def test_card_freeformat(fields):

    numfields = 1 + 2 + len(fields["integers"]) + len(fields["reals"])
    card = Card("HELLO", format=FreeFormat(), size=numfields)

    card[0] = fields["id"]
    card[1:3] = fields["string"]
    card[3::2] = fields["integers"]
    card[4::2] = fields["reals"]

    card_str = """\
HELLO,99,hellowor,ld,0,3.3,1,6.6,2,+0
+0,9.9,
"""
    assert card.dumps() == card_str
