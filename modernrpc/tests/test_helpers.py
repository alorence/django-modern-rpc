import datetime

import pytest

from modernrpc.helpers import get_builtin_date
try:
    # Python 3
    import xmlrpc.client as xmlrpc_module
except ImportError:
    # Python 2
    import xmlrpclib as xmlrpc_module


def test_get_builtin_date():

    date1 = get_builtin_date("2016-10-20T21:54:00")
    assert isinstance(date1, datetime.datetime)
    assert date1.year == 2016
    assert date1.month == 10
    assert date1.day == 20
    assert date1.hour == 21
    assert date1.minute == 54
    assert date1.second == 0

    date2 = get_builtin_date(datetime.datetime(2012, 5, 9, 23, 12, 12))
    assert isinstance(date2, datetime.datetime)
    assert date2.year == 2012
    assert date2.month == 5
    assert date2.day == 9
    assert date2.hour == 23
    assert date2.minute == 12
    assert date2.second == 12

    xdate = xmlrpc_module.DateTime(datetime.datetime(1954, 12, 19, 4, 44, 44))
    date3 = get_builtin_date(xdate)
    assert isinstance(date3, datetime.datetime)
    assert date3.year == 1954
    assert date3.month == 12
    assert date3.day == 19
    assert date3.hour == 4
    assert date3.minute == 44
    assert date3.second == 44

    date4 = get_builtin_date("05 11 2014", "%d %m %Y")
    assert isinstance(date3, datetime.datetime)
    assert date4.year == 2014
    assert date4.month == 11
    assert date4.day == 5


def test_get_builtin_date_invalid():

    # Invalid month: 2016-16-04
    date1 = get_builtin_date("2016-16-04T21:54:00")
    assert date1 is None

    with pytest.raises(ValueError) as excinfo:
        get_builtin_date("2016-16-04T21:54:00", raise_exception=True)
