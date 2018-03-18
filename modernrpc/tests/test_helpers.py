# coding: utf-8
import datetime

import pytest

from modernrpc.helpers import get_builtin_date
from . import xmlrpclib


def test_get_builtin_date():

    date1 = get_builtin_date("2016-10-20T21:54:00")
    assert isinstance(date1, datetime.datetime)
    assert date1.year == 2016
    assert date1.month == 10
    assert date1.day == 20
    assert date1.hour == 21
    assert date1.minute == 54
    assert date1.second == 0


def test_get_builtin_date_2():

    date = get_builtin_date(datetime.datetime(2012, 5, 9, 23, 12, 12))
    assert isinstance(date, datetime.datetime)
    assert date.year == 2012
    assert date.month == 5
    assert date.day == 9
    assert date.hour == 23
    assert date.minute == 12
    assert date.second == 12


def test_get_builtin_date_3():

    date3 = get_builtin_date(xmlrpclib.DateTime(datetime.datetime(1954, 12, 19, 4, 44, 44)))
    assert isinstance(date3, datetime.datetime)
    assert date3.year == 1954
    assert date3.month == 12
    assert date3.day == 19
    assert date3.hour == 4
    assert date3.minute == 44
    assert date3.second == 44


def test_get_builtin_date_4():

    date = get_builtin_date("05 11 2014", "%d %m %Y")
    assert isinstance(date, datetime.datetime)
    assert date.year == 2014
    assert date.month == 11
    assert date.day == 5


def test_get_builtin_date_invalid():

    # Invalid month: 2016-16-04
    date1 = get_builtin_date("2016-16-04T21:54:00")
    assert date1 is None


def test_get_builtin_date_invalid_with_exception():
    with pytest.raises(ValueError):
        get_builtin_date("2016-16-04T21:54:00", raise_exception=True)
