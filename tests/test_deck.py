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


def test_deck_find_fields(cards):
    pass


def test_deck_find_contains(cards):
    pass


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
    assert not deck.find_one({"name": ""})
    assert not deck.find_one({"name": "+"})

    with open(EXPECT_DIR + "/testA-fixed.bdf") as f:
        assert deck.dumps("fixed") == f.read()

    with open(EXPECT_DIR + "/testA-free.bdf") as f:
        assert deck.dumps("free") == f.read()


def test_deck_sort_by_name(cards):

    deck = Deck(cards)
    deck.sort()

    for i in range(len(deck)-1):
        c1 = deck[i]
        c2 = deck[i+1]
        assert c1.name < c2.name


def test_deck_sort_by_name_reverse(cards):

    deck = Deck(cards)
    deck.sort(reverse=True)

    for i in range(len(deck)-1):
        c1 = deck[i]
        c2 = deck[i+1]
        assert c1.name > c2.name


def test_deck_sort_by_first_val(cards):

    deck = Deck(cards)
    deck.sort(key=lambda card: card[0])
    
    for i in range(len(deck)-1):
        c1 = deck[i]
        c2 = deck[i+1]
        assert c1[0] < c2[0]


def test_zaero_example():

    bdf_filename = BDF_DIR + "/zaero-example.bdf"

    # load Deck from BDF file
    with open(bdf_filename) as bdf_file:
        deck = Deck.load(bdf_file)

    # CORD2R variables
    cid = 1
    rid = None
    a = [-2.9, 1.0, 0.0]
    b = [3.6, 0.0, 1.0]
    c = [5.2, 1.0, -2.9]

    # create CORD2R card
    cord2r = Card("CORD2R")
    cord2r.append(cid)
    cord2r.append(rid)
    cord2r.extend(a)
    cord2r.extend(b)
    cord2r.extend(c)

    # # print the CORD2R card in fixed format (the default)
    # print("-- CORD2R fixed formatting --")
    # print(cord2r.dumps("fixed"))

    # # print the CORD2R card in free format
    # print("-- CORD2R free formatting --")
    # print(cord2r.dumps("free"))

    # add card to the deck
    deck.append(cord2r)

    # get AEROZ card
    aeroz = deck.find_one({"name": "AEROZ"})

    # print("-- AEROZ before update --")
    # print(aeroz.dumps())

    # update the ACSID field (first one)
    aeroz[0] = cid

    # update mass and length units fields while we're at it
    aeroz[[3, 4]] = ["N", "M"] 

    # print("-- AEROZ after update --")
    # print(aeroz.dumps())

    # dump Deck to update BDF file
    with open(EXPECT_DIR + "/zaero-example-update.bdf") as f:
        assert deck.dumps() == f.read()

    # with open(EXPECT_DIR + "/zaero-example-update.bdf", "w") as f:
    #     deck.dump(f)
    # assert False


    




    