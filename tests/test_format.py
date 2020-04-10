#!/usr/bin/env python

"""Tests for `bulkdata.format` module."""

import pytest

from bulkdata.format import FixedFormatter, FreeFormatter

from .util import MockCard


@pytest.fixture
def fixedform():
    return FixedFormatter()


@pytest.fixture
def freeform():
    return FreeFormatter()


def test_write_string_field_fixed(fixedform):

    field = fixedform.format_field("hello")
    assert field == "hello   "

    field = fixedform.format_field("helloworld")
    assert field == "hellowor"


def test_write_string_field_free(freeform):

    field = freeform.format_field("hello")
    assert field == "hello"

    field = freeform.format_field("helloworld")
    assert field == "hellowor"


def test_format_card_fixed(fixedform):

    name = "TEST"
    fields_str = "yes these fields are not properly formatted this is a test"
    fields = fields_str.split()
    card = MockCard(name, fields)
    actual = fixedform.format_card(card)
    expect = """\
TEST    yes     these   fields  are     not     properlyformattethis    +0      
+0      is      a       test
"""
    assert actual == expect


def test_format_card_free(freeform):

    name = "TEST"
    fields_str = "yes these fields are not properly formatted this is a test"
    fields = fields_str.split()
    card = MockCard(name, fields)
    actual = freeform.format_card(card)
    expect = """\
TEST,yes,these,fields,are,not,properly,formatte,this,+0
+0,is,a,test
"""
    assert actual == expect


def test_write_empty_card(fixedform, freeform):

    card = MockCard(None, [])

    for formatter in (fixedform, freeform):
        actual = formatter.format_card(card)
        expect = "\n"
        assert actual == expect