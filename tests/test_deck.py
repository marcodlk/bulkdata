#!/usr/bin/env python

"""Tests for `bulkdata.deck` module."""

import pytest

# from bulkdata.format import FixedFormat, FreeFormat
from bulkdata.card import Card
from bulkdata.deck import Deck

from . import BDF_DIR, EXPECT_DIR

@pytest.fixture 
def cards():
    
    def make_card(name, id, keys, integers, reals):
        card = Card(name)
        card.append(id)
        for key, integer, real in zip(keys, integers, reals):
            card.extend([key, integer, real])
        return card

    cards_name = ("ONE", "TWO", "THREE", "FOUR")
    cards_id = (
        100 + i
        for i in range(len(cards_name))
    )
    cards_keys = (
        ("this-%d" % i, "that-%d" % i, "other-%d" % i) 
        for i in range(len(cards_name))
    )
    cards_integers = (
        (1 * i, 2 * i, 3 * i) 
        for i in range(len(cards_name))
    )
    cards_reals = (
        (2.1 * i, 4.2 * i, 8.4 * i) 
        for i in range(len(cards_name))
    )
    cards = [
        make_card(name, id, keys, integers, reals)
        for name, id, keys, integers, reals in zip(cards_name,
                                                   cards_id,
                                                   cards_keys,
                                                   cards_integers,
                                                   cards_reals)
    ]
    return cards


def test_deck_init_iter(cards):

    deck = Deck(cards)
    assert len(deck) == len(cards)

    for i, card in enumerate(deck):
        assert card == cards[i]


def test_deck_append(cards):

    deck = Deck()
    assert len(deck) == 0

    for card in cards:
        deck.append(card)
    assert len(deck) == len(cards)

    for i, card in enumerate(deck):
        assert card == cards[i]


def test_deck_extend(cards):

    deck = Deck()
    assert len(deck) == 0

    deck.extend(cards)
    assert len(deck) == len(cards)

    for i, card in enumerate(deck):
        assert card == cards[i]


def test_deck_find(cards):

    deck = Deck(cards)

    found = list(deck.find())
    assert len(found) == len(cards)

    for name in ("ONE", "TWO", "THREE", "FOUR"):
        found = list(deck.find({"name": name}))
        found2 = list(deck.find(name))
        assert len(found) == 1
        assert len(found2) == 1


def test_deck_find_one():

    deck = Deck()

    for _ in range(10):
        deck.append(Card("CLONE"))

    card = deck.find_one("CLONE")
    assert card.name == "CLONE"
    assert card == list(deck.find("CLONE"))[0]


def test_deck_find_notexist():
   
    deck = Deck()

    for _ in range(10):
        deck.append(Card("CLONE"))

    card = deck.find_one("UNIQUE")
    assert card is None

    cards = list(deck.find("UNIQUE"))
    assert not cards


def test_deck_replace(cards):

    deck = Deck(cards)

    replacement = Card("UNO")
    deck.replace({"name": "ONE"}, replacement)

    assert not list(deck.find({"name": "ONE"}))
    assert list(deck.find({"name": "UNO"}))
    assert len(deck) == len(cards)


def test_deck_update(cards):

    deck = Deck(cards)

    index = 0
    index_value = "int"
    update = {"index": index, "value": index_value}
    deck.update({"name": "ONE"}, update)

    card = next(deck.find({"name": "ONE"}))
    assert card[index] == index_value

    slice_ = slice(0, 2)
    slice_value = "sliceslice"
    update = {"index": slice_, "value": slice_value}
    deck.update({"name": "TWO"}, update)

    card = next(deck.find({"name": "TWO"}))
    assert card[:2] == ["slicesli", "ce"]
    assert card.get_large(slice_) == slice_value

    indexs =[-4, -3, -2, -1]
    indexs_values = [1001, 1002, 1003, 1004]
    update = {"index": indexs, "value": indexs_values}
    deck.update({"name": "THREE"}, update)

    card = next(deck.find({"name": "THREE"}))
    assert card[indexs] == indexs_values

    for notlisttype in (slice, int, str):
        with pytest.raises(TypeError):
            deck.update({}, {"index": notlisttype(), "value": list()})

    deck_str = deck.dumps()

    # redo the update, but without using update func
    deck2 = Deck(cards)

    card = deck.find_one({"name": "ONE"})
    card[index] = index_value 

    card = deck.find_one({"name": "TWO"})
    card[slice_] = slice_value

    card = deck.find_one({"name": "THREE"})
    card[indexs] = indexs_values

    deck2_str = deck2.dumps()

    assert deck_str == deck2_str


def test_deck_load_bdf_pyNastran():

    bdf_filename = BDF_DIR + "/testA.bdf"

    with open(bdf_filename) as bdf_file:
        deck = Deck.load(bdf_file)

    aero = deck.find_one("AERO")
    assert not (aero[0] or aero[1])
    assert aero[2] == aero[3] == 1.0
    
    assert not deck.find_one({"name": None})

    # with open(EXPECT_DIR + "/testA-fixed.bdf", "w") as f:
    #     deck.dump(f)
    with open(EXPECT_DIR + "/testA-fixed.bdf") as f:
        deck.dumps("fixed") == f.read()


    




    