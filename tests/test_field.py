#!/usr/bin/env python

"""Tests for `bulkdata.field` module."""

import pytest

from bulkdata.field import Field, LargeField
from bulkdata.field import _force_E
from bulkdata.field import is_integer_field, is_real_field
from bulkdata.field import read_integer_field, read_real_field, read_field
from bulkdata.field import write_field


@pytest.fixture
def integer_fields():
    return ("0", "1", "10000000", "-9999999")


@pytest.fixture
def integer_values():
    return (0, 1, 10000000, -9999999)


@pytest.fixture
def real_fields():
    return ("3.14+10", "3.14-10", "0.e+19", "0.e-19", "3.14", "-3.14")


@pytest.fixture
def real_values():
    return (3.14e10, 3.14e-10, 0.e19, 0.e-19, 3.14, -3.14)


def test_force_E():

    assert _force_E("3.14") == "3.14"
    assert _force_E("3.14+10") == "3.14E+10"
    assert _force_E("3.14-10") == "3.14E-10"


def test_is_integer_field(integer_fields, real_fields):

    for field in integer_fields:
        assert is_integer_field(field)

    for field in real_fields:
        assert not is_integer_field(field)


def test_is_real_field(real_fields):

    for field in real_fields:
        assert is_real_field(field)
    

def test_read_integer_field(integer_fields, integer_values):

    for field, value in zip(integer_fields, integer_values):
        assert read_integer_field(field) == value
        assert read_field(field) == value
    

def test_read_real_field(real_fields, real_values):

    for field, value in zip(real_fields, real_values):
        assert read_real_field(field) == value
        assert read_field(field) == value

def test_read_field_integer():

    test_tuples = [
        ("       1", 1),
        ("      12", 12),
        ("     123", 123),
        ("    1234", 1234),
        ("   12345", 12345),
        ("  123456", 123456),
        (" 1234567", 1234567),
        ("12345678", 12345678),
    ]
    
    for integer_str, expect in test_tuples:
        field = read_field(integer_str)
        assert field == expect

    test_long = [
        ("       -12345678", -12345678),
        ("       123456789", 123456789)
    ]
    
    for integer_str, expect in test_long:
        field = read_field(integer_str)
        assert field == expect


def test_read_field_real():

    test_tuples = [
        ("1234567.", 1234567.), 
        ("-123456.", -123456.), 
        ("1.235+13", 1.235e13), 
        ("123.4567", 123.4567), 
        ("123.4568", 123.4568), 
        ("1.234568", 1.234568), 
        ("0.123457", 0.123457), 
        ("      1.", 1.), 
        ("     12.", 12.), 
        ("    123.", 123.), 
        ("   1234.", 1234.), 
        ("  12345.", 12345.), 
        (" 123456.", 123456.), 
        ("1.2346+7", 1.2346e7), 
        ("-1.235+6", -1.235e6),
        ("9233443.", 9233443.)
    ]
    
    for real_str, expect in test_tuples:
        field = read_field(real_str)
        assert field == expect


def test_write_integer_field():

    test_tuples = [
        ("1", 1),
        ("12", 12),
        ("123", 123),
        ("1234", 1234),
        ("12345", 12345),
        ("123456", 123456),
        ("1234567", 1234567),
        ("12345678", 12345678),
    ]
    
    for expect, integer in test_tuples:
        field = write_field(integer)
        assert field == expect

    test_long = [
        ("-12345678", -12345678),
        ("123456789", 123456789)
    ]
    
    for expect, integer in test_long:
        field = write_field(integer, fieldspan=2)
        assert field == expect


def test_write_integer_field_fail():

    test_fails = [
        -12345678,
        123456789
    ]
    
    for integer in test_fails:
        with pytest.raises(RuntimeError):
            write_field(integer)

    with pytest.raises(ValueError):
        write_field(500, fieldspan=3)


def test_write_real_field():

    test_tuples = [
        ("1234567.", 1234567.), 
        ("-123456.", -123456.), 
        ("1.235+13", 12345678901234.), 
        ("123.4567", 123.4567), 
        ("123.4568", 123.45678), 
        ("1.234568", 1.2345678), 
        (".1234568", 0.12345678), 
        ("1.", 1.), 
        ("12.", 12.), 
        ("123.", 123.), 
        ("1234.", 1234.), 
        ("12345.", 12345.), 
        ("123456.", 123456.), 
        ("1.2346+7", 12345678.), 
        ("-1.235+6", -1234567.),
        ("9233443.", 9233443.323)
    ]
    
    for expect, real in test_tuples:
        field = write_field(real)
        assert field == expect


def test_write_real_field_fail():

    with pytest.raises(ValueError):
        write_field(500., fieldspan=3)


def test_write_string_field():

    test_tuples = [
        ("this", "this    "),
        ("is", "      is"),
        ("a-test", "a-test"),
        ("hellowor", "helloworld")
    ]

    for expect, value in test_tuples:
        field = write_field(value)
        assert field == expect


def test_write_string_largefield():

    test_tuples = [
        ("helloworld", 2),
        ("the-answer-to-life-the-universe-and-everything", 6)
    ]

    for value, fieldspan in test_tuples:
        assert write_field(value, fieldspan) == value