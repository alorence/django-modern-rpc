import datetime
import xmlrpc.client

import pytest

from modernrpc import Protocol
from modernrpc.compat import is_union_type, union_str_repr
from modernrpc.helpers import check_flags_compatibility, ensure_sequence, first, get_builtin_date


@pytest.mark.parametrize(
    ("arg", "expected_result"),
    [
        ((1, 2, 3), (1, 2, 3)),
        (("a", "b", "c"), ("a", "b", "c")),
        ("azerty", ["azerty"]),
        ({"x": 42}, [{"x": 42}]),
    ],
)
def test_ensure_sequence(arg, expected_result):
    assert ensure_sequence(arg) == expected_result


@pytest.mark.parametrize(
    ("arg", "expected_result"),
    [
        ([1, 2, 3], 1),
        ((1, 2, 3), 1),
        (("a", "b", "c"), "a"),
        ("azerty", "a"),
        ({"x": 42}, "x"),
    ],
)
def test_first_helper(arg, expected_result):
    assert first(arg) == expected_result


@pytest.mark.parametrize(
    ("arg", "expected_exception"),
    [
        ((), IndexError),
        ([], IndexError),
        ({}, IndexError),
    ],
)
def test_first_helper_with_empty_arg(arg, expected_exception):
    with pytest.raises(expected_exception):
        first(arg)

    assert first(arg, default="default") == "default"


@pytest.mark.parametrize(
    "date",
    [
        "2016-10-20T21:54:00",
        datetime.datetime(2016, 10, 20, 21, 54, 0),
        xmlrpc.client.DateTime(datetime.datetime(2016, 10, 20, 21, 54, 0)),
    ],
)
def test_get_builtin_date(date):
    assert get_builtin_date(date) == datetime.datetime(2016, 10, 20, 21, 54, 0)


def test_get_builtin_date_with_format():
    res = get_builtin_date("20 10 2016 21h54m00", date_format="%d %m %Y %Hh%Mm%S")
    assert res == datetime.datetime(2016, 10, 20, 21, 54, 0)


@pytest.mark.parametrize(
    "date_str",
    [
        # Invalid month: 2016-16-04
        "2016-16-04T21:54:00",
        # Invalid day 2016-12-32
        "2016-12-32T21:54:00",
        # Invalid hour format, missing seconds
        "2016-12-20T21:54",
    ],
)
def test_get_builtin_date_invalid(date_str):
    assert get_builtin_date(date_str) is None
    with pytest.raises(ValueError, match=r"time data .+ does not match format '%Y-%m-%dT%H:%M:%S'"):
        get_builtin_date(date_str, raise_exception=True)


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        (Protocol.ALL, Protocol.ALL, True),
        (Protocol.ALL, Protocol.XML_RPC, True),
        (Protocol.ALL, Protocol.JSON_RPC, True),
        (Protocol.XML_RPC, Protocol.XML_RPC, True),
        (Protocol.XML_RPC, Protocol.ALL, True),
        (Protocol.XML_RPC, Protocol.JSON_RPC, False),
        (Protocol.JSON_RPC, Protocol.JSON_RPC, True),
        (Protocol.JSON_RPC, Protocol.ALL, True),
        (Protocol.JSON_RPC, Protocol.XML_RPC, False),
    ],
)
def test_flags_compatibility(a, b, expected):
    assert check_flags_compatibility(a, b) == expected


def test_union_type():
    assert is_union_type(int | str) is True
    assert is_union_type(int) is False
    assert is_union_type(type(None)) is False


def test_union_str_repr():
    assert union_str_repr(int | str) == "int | str"
