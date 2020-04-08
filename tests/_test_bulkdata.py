#!/usr/bin/env python

"""Tests for `bulkdata` package."""

import pytest

# from click.testing import CliRunner

import bulkdata as bd
from bulkdata.format import FixedFormat
from bulkdata.bulkdata import BulkData


@pytest.fixture
def bulkdata():
    """BulkData object initialized with fixed-format
    """
    return BulkData(format=FixedFormat())


def test_bulkdata_card(bulkdata):

    # initialize card object, with name "HELLO"
    card = bulkdata.Card("HELLO")

    # these are the values we want to put in the card
    id = 99
    string = "helloworld"
    integers = [0, 1, 2]
    reals = [3.3, 6.6, 9.9]

    # append the first field
    card.append(id)

    # append the string entry that spans 2 fields
    card.append(string, fieldspan=2)

    # integers and reals list entries alternate
    for integer, real in zip(integers, reals):
        card.append(integer)
        card.append(real)


def test_bulkdata_deck(bulkdata):

    bdf_filename = "sampledeck.bdf"

    with open(bdf_filename) as bdf_file:
        deck = bulkdata.load(bdf_file)

    with open(bdf_filename, "w") as bdf_file:
        bulkdata.dump(deck, bdf_file)


def test_package_card(bd):

    # initialize card object, with name "HELLO"
    card = bd.Card("HELLO")

    # these are the values we want to put in the card
    id = 99
    string = "helloworld"
    integers = [0, 1, 2]
    reals = [3.3, 6.6, 9.9]

    # append the first field
    card.append(id)

    # append the string entry that spans 2 fields
    card.append(string, fieldspan=2)

    # integers and reals list entries alternate
    for integer, real in zip(integers, reals):
        card.append(integer)
        card.append(real)

    card_str = bd.dumps(card)
    expect = """\
   HELLO      99      helloworld       0     3.3       1     6.6       2      +0
+0           9.9"""
    assert card_str == expect


def test_package_deck():

    bdf_filename = "sampledeck.bdf"

    with open(bdf_filename) as bdf_file:
        deck = bd.load(bdf_file)

    with open(bdf_filename, "w") as bdf_file:
        bd.dump(deck, bdf_file)