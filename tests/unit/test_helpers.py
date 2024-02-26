import datetime
import xmlrpc.client

import pytest

from modernrpc.helpers import ensure_sequence, get_builtin_date


@pytest.mark.parametrize(
    ("arg", "expected_result"),
    [
        ((1, 2, 3), (1, 2, 3)),
        (("a", "b", "c"), ("a", "b", "c")),
        ("azerty", ["azerty"]),
        ({"x": 42}, [{"x": 42}]),
    ],
)
def test_ensure_sequence_1(arg, expected_result):
    assert ensure_sequence(arg) == expected_result


@pytest.mark.parametrize(
    "date",
    [
        "2016-10-20T21:54:00",
        datetime.datetime(2016, 10, 20, 21, 54, 00),
        xmlrpc.client.DateTime(datetime.datetime(2016, 10, 20, 21, 54, 00)),
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
    with pytest.raises(ValueError, match="time data .+ does not match format '%Y-%m-%dT%H:%M:%S'"):
        get_builtin_date(date_str, raise_exception=True)
