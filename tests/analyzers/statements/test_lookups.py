import re
from typing import Type

import pytest

from beagle.analyzers.queries.lookups import (
    And,
    Contains,
    EndsWith,
    Exact,
    FieldLookup,
    IContains,
    IExact,
    Not,
    Or,
    Regex,
    StartsWith,
)


@pytest.mark.parametrize(
    "cls,value,prop,result",
    [
        (Contains, "test", "test", True),
        (Contains, "test", "worst", False),
        (Contains, "test", "he is the test", True),
        (Contains, "test", "the test was bad", True),
        (Contains, "test", "the TEST was bad", False),
        (IContains, "test", "TEST", True),
        (IContains, "test", "tEsT", True),
        (IContains, "test", "worst", False),
        # Test we reject null value.
        (IContains, "test", None, False),
        (IContains, "test", "he is the test", True),
        (IContains, "test", "the test was bad", True),
        (Exact, "test", "test", True),
        (Exact, "test", " test ", False),
        (Exact, "test", "some test a", False),
        (IExact, "test", "test", True),
        (IExact, "test", "TEST", True),
        (IExact, "test", "tEst", True),
        (StartsWith, "test", "test", True),
        (StartsWith, "test", "not a test", False),
        (StartsWith, "test", "test is the best", True),
        (EndsWith, "test", "test", True),
        (EndsWith, "test", "not test but a nest", False),
        (EndsWith, "test", "the best test", True),
        (Regex, r"\d", "test 1 test", True),
        (Regex, re.compile(r"\d"), "test 1 test", True),
        (Regex, r"\d", "test test", False),
        (Regex, re.compile(r"\d"), "test test", False),
    ],
)
def test_lookups(cls: Type[FieldLookup], value: str, prop: str, result: str):
    # prop -> value being tested again, value -> the thing we're looking up
    assert cls(value).test(prop) == result


def test_and():
    assert And(StartsWith("foo"), EndsWith("bar")).test("foo bar") is True
    assert And(StartsWith("foo"), EndsWith("bar")).test("foo nar bar") is True
    assert And(StartsWith("foo"), EndsWith("bar")).test("bar foo") is False


def test_or():
    assert Or(StartsWith("foo"), EndsWith("bar")).test("foo bar") is True
    assert Or(StartsWith("foo"), EndsWith("bar")).test("foo") is True
    assert Or(StartsWith("foo"), EndsWith("bar")).test("bar") is True
    assert Or(StartsWith("foo"), EndsWith("bar")).test("foo nar bar") is True
    assert Or(StartsWith("foo"), EndsWith("bar")).test("bar foo") is False


def test_not():
    assert Not(Contains("test")).test("hello") is True
    assert Not(Not(Contains("test"))).test("hello") is False


def test_operator_overloading():
    assert (~Contains("test")).test("hello") is True
    assert (Contains("test") & EndsWith("hello")).test("test my hello") is True
    assert (Contains("test") | EndsWith("hello")).test("hello") is True
