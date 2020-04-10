#!/usr/bin/env python

"""Tests for `bulkdata.parse` module."""

import pytest

from bulkdata.parse import BDFParser

from . import BDF_DIR, EXPECT_DIR


def test_parse_card_simple():

    card_str = """\
$
$
HELLO   99      helloworld      0       3.3     1       6.6     2       +0      
+0      9.9
$
$
"""

    name, fields = BDFParser(card_str).parse_card()
    assert name.strip() == "HELLO"
    assert len(fields) == 9


def test_parse_card_mixedcont():
    
    card_str = """\
BARL    6666    10              BAR
+       5.5     3.0
"""

    name, fields = BDFParser(card_str).parse_card()
    assert name.strip() == "BARL"
    assert len(fields) == 10


def test_parse_card_sparse():

    card_str = """\
SPARSE  test1
        test2
        test3
"""
    name, fields = BDFParser(card_str).parse_card()
    assert name.strip() == "SPARSE"
    assert len(fields) == 17


def test_parse_deck_cards_only():

    deck_str = """\
$
$
HELLO   99      helloworld      0       3.3     1       6.6     2       +0      
+0      9.9
$
$
HELLO,99,hellowor,ld,0,3.3,1,6.6,2,+0      
+0,9.9
$
$
HELLO,99,hellowor,ld,0,3.3,1,6.6,2,
,9.9
$
$
HELLO   99      helloworld      0       3.3     1       6.6     2       +0      
+0      9.9
$
$
HELLO   99      helloworld      0       3.3     1       6.6     2       +0      
+0      9.9
$
$
"""

    header, card_tuples = BDFParser(deck_str).parse()

    assert not header
    assert len(card_tuples) == 5
    for name, fields in card_tuples:
        assert name.strip() == "HELLO"
        assert len(fields) == 9


def test_parse_deck():

    header_str = """\
THIS
IS
A
TEST
ANSWER IS 42\
"""
    deck_str = """{}
BEGIN BULK
$
$
HELLO   99      helloworld      0       3.3     1       6.6     2       +0      
+0      9.9
$
$
HELLO   99      helloworld      0       3.3     1       6.6     2       +0      
+0      9.9
$
$
HELLO   99      helloworld      0       3.3     1       6.6     2       +0      
+0      9.9
$
$
HELLO   99      helloworld      0       3.3     1       6.6     2       +
+       9.9
$
$
HELLO   99      helloworld      0       3.3     1       6.6     2
        9.9
$
$
ENDDATA
IGNORE THIS
""".format(header_str)

    header, card_tuples = BDFParser(deck_str).parse()

    assert header == header_str
    assert len(card_tuples) == 5
    for name, fields in card_tuples:
        assert name.strip() == "HELLO"
        assert len(fields) == 9


def test_parse_bdf_pyNastran():

    bdf_filename = BDF_DIR + "/testA.bdf"
    expect_header_filename = EXPECT_DIR + "/testA-header.bdf"

    with open(bdf_filename) as bdf_file:
        bdf_str = bdf_file.read()

    with open(expect_header_filename) as header_file:
        expect_header = header_file.read()

    header, card_tuples = BDFParser(bdf_str).parse()

    assert header == expect_header
    assert len(card_tuples) == 143
