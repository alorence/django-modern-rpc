# coding: utf-8
import datetime

import pytest

from modernrpc.helpers import get_builtin_date
from . import xmlrpclib


@pytest.mark.parametrize("date", [
    "2016-10-20T21:54:00",
    datetime.datetime(2016, 10, 20, 21, 54, 00),
    xmlrpclib.DateTime(datetime.datetime(2016, 10, 20, 21, 54, 00))
])
def test_get_builtin_date(date):
    d = get_builtin_date(date)
    assert isinstance(d, datetime.datetime)
    assert d.year == 2016
    assert d.month == 10
    assert d.day == 20
    assert d.hour == 21
    assert d.minute == 54
    assert d.second == 0


def test_get_builtin_date_4():
    d = get_builtin_date("20 10 2016 21h54m00", "%d %m %Y %Hh%Mm%S")
    assert isinstance(d, datetime.datetime)
    assert d.year == 2016
    assert d.month == 10
    assert d.day == 20
    assert d.hour == 21
    assert d.minute == 54
    assert d.second == 0


def test_get_builtin_date_invalid():
    # Invalid month: 2016-16-04
    assert get_builtin_date("2016-16-04T21:54:00") is None
    assert get_builtin_date("2016-12-32T21:54:00") is None
    assert get_builtin_date("2016-12-20T21:54") is None


def test_get_builtin_date_invalid_with_exception():
    with pytest.raises(ValueError):
        get_builtin_date("2016-16-04T21:54:00", raise_exception=True)
    with pytest.raises(ValueError):
        get_builtin_date("2016-12-32T21:54:00", raise_exception=True)
    with pytest.raises(ValueError):
        get_builtin_date("2016-12-20T21:54", raise_exception=True)
