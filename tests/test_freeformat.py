#!/usr/bin/env python

"""Tests for `bulkdata.format` module."""

import pytest

# from click.testing import CliRunner

from bulkdata.abc import BulkDataCard
from bulkdata.format import FreeFormat


class MockCard(BulkDataCard):

    def __init__(self, name, fields):
        self._name = name
        self._fields = fields

    @property
    def name(self):
        return self._name

    @property
    def fields(self):
        return self._fields


@pytest.fixture
def freeformat():
    return FreeFormat()


def test_write_string_field(freeformat):

    field = freeformat.write_field("helloworld", fieldspan=1)
    assert field == "hellowor"
    field = freeformat.write_field("helloworld", fieldspan=2)
    assert field == "helloworld"
    fields = freeformat.split(field)
    assert fields[0] == "hellowor"
    assert fields[1] == "ld"


# def test_write_integer_field(freeformat):

#     test_tuples = [
#         ("1", 1),
#         ("12", 12),
#         ("123", 123),
#         ("1234", 1234),
#         ("12345", 12345),
#         ("123456", 123456),
#         ("1234567", 1234567),
#         ("12345678", 12345678),
#     ]
    
#     for expect, integer in test_tuples:
#         field = freeformat.write_field(integer)
#         assert field == expect

#     test_long = [
#         ("-12345678", -12345678),
#         ("123456789", 123456789)
#     ]
    
#     for expect, integer in test_long:
#         field = freeformat.write_field(integer, fieldspan=2)
#         assert field == expect


# def test_write_integer_field_fail(freeformat):

#     test_fails = [
#         -12345678,
#         123456789
#     ]
    
#     for integer in test_fails:
#         with pytest.raises(ValueError):
#             freeformat.write_field(integer)


# def test_write_real_field(freeformat):

#     test_tuples = [
#         ("1234567.", 1234567.), 
#         ("-123456.", -123456.), 
#         ("1.235+13", 12345678901234.), 
#         ("123.4567", 123.4567), 
#         ("123.4568", 123.45678), 
#         ("1.234568", 1.2345678), 
#         ("0.123457", 0.12345678), 
#         ("1.", 1.), 
#         ("12.", 12.), 
#         ("123.", 123.), 
#         ("1234.", 1234.), 
#         ("12345.", 12345.), 
#         ("123456.", 123456.), 
#         ("1.2346+7", 12345678.), 
#         ("-1.235+6", -1234567.),
#         ("9233443.", 9233443.323)
#     ]
    
#     for expect, real in test_tuples:
#         field = freeformat.write_field(real)
#         assert field == expect


def test_write_blank(freeformat):

    assert freeformat.write_blank() == " "


def test_split(freeformat):

    string = "the answer is 42"
    field = freeformat.write_field(string, fieldspan=2)
    assert field == string[:16]
    fields = freeformat.split(field)
    assert fields[0] == string[:8]
    assert fields[1] == string[8:16]

    string = "the answer to the universe is 42"
    field = freeformat.write_field(string, fieldspan=4)
    assert field[-32:] == string[:32]
    fields = freeformat.split(field)
    assert fields[0] == string[-32:-24]
    assert fields[1] == string[-24:-16]
    assert fields[2] == string[-16:-8]
    assert fields[3] == string[-8:]


def test_normalize_string(freeformat):

    string = "  helloworld      "
    assert freeformat.normalize(string) == string.strip()


def test_normalize_int(freeformat):

    integer = 1238947
    assert freeformat.normalize(integer) == "1238947"


# def test_normalize_real(freeformat):

#     real = 3.14
#     assert freeformat.normalize(real) == "3.14"
#     real = 1000000000.
#     assert freeformat.normalize(real) == "1.0000+9"


def test_write_card(freeformat):

    name = "TEST"
    fields_str = "yes these fields are not properly formatted this is a test"
    fields = fields_str.split()
    card = MockCard(name, fields)
    actual = freeformat.write_card(card)
    expect = """\
TEST,yes,these,fields,are,not,properly,formatte,this,+0
+0,is,a,test,
"""
    assert actual == expect


def test_write_empty_card(freeformat):

    card = MockCard(None, [])
    actual = freeformat.write_card(card)
    expect = "\n"
    assert actual == expect


def test_write_deck(freeformat):

    card_tuples = (
        ("card1", ["1", "2", "3"]), 
        ("card2", ["4", "5", "6"]), 
        ("card3", ["7", "8", "9"])
    )
    cards = [MockCard(name, fields) for name, fields in card_tuples]
    actual = freeformat.write_deck(cards)
    expect = "card1,1,2,3,\ncard2,4,5,6,\ncard3,7,8,9,\n"
    assert actual == expect


# def test_read_integer_field(freeformat):

#     test_tuples = [
#         ("1", 1),
#         ("12", 12),
#         ("123", 123),
#         ("1234", 1234),
#         ("12345", 12345),
#         ("123456", 123456),
#         ("1234567", 1234567),
#         ("12345678", 12345678),
#     ]
    
#     for integer_str, expect in test_tuples:
#         field = freeformat.read_field(integer_str)
#         assert field == expect

#     test_long = [
#         ("       -12345678", -12345678),
#         ("       123456789", 123456789)
#     ]
    
#     for integer_str, expect in test_long:
#         field = freeformat.read_field(integer_str)
#         assert field == expect


# def test_read_real_field(freeformat):

#     test_tuples = [
#         ("1234567.", 1234567.), 
#         ("-123456.", -123456.), 
#         ("1.235+13", 1.235e13), 
#         ("123.4567", 123.4567), 
#         ("123.4568", 123.4568), 
#         ("1.234568", 1.234568), 
#         ("0.123457", 0.123457), 
#         ("1.", 1.), 
#         ("12.", 12.), 
#         ("123.", 123.), 
#         ("1234.", 1234.), 
#         ("12345.", 12345.), 
#         ("123456.", 123456.), 
#         ("1.2346+7", 1.2346e7), 
#         ("-1.235+6", -1.235e6),
#         ("9233443.", 9233443.)
#     ]
    
#     for real_str, expect in test_tuples:
#         field = freeformat.read_field(real_str)
#         assert field == expect


def test_read_card(freeformat):

    card_str = """\
$
$
HELLO,99,hellowor,ld,0,3.3,1,6.6,2,+0      
+0,9.9
$
$
"""

    name, fields = freeformat.read_card(card_str)
    assert name.strip() == "HELLO"
    assert len(fields) == 9


def test_read_deck(freeformat):

    deck_str = """\
$
$
HELLO,99,hellowor,ld,0,3.3,1,6.6,2,+0      
+0,9.9,
$
$
HELLO,99,hellowor,ld,0,3.3,1,6.6,2,+0      
+0,9.9,
$
$
HELLO,99,hellowor,ld,0,3.3,1,6.6,2,+0      
+0,9.9,
$
$
HELLO,99,hellowor,ld,0,3.3,1,6.6,2,+0      
+0,9.9,
$
$
HELLO,99,hellowor,ld,0,3.3,1,6.6,2,+0      
+0,9.9,
$
$
"""

    header, card_tuples = freeformat.read_deck(deck_str)

    assert not header
    for name, fields in card_tuples:
        assert name.strip() == "HELLO"
        assert len(fields) == 9