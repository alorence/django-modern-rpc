# coding: utf-8
import datetime

import pytest
from django.utils import six
from django.utils.six.moves import xmlrpc_client
from pytest import raises

from modernrpc.helpers import get_builtin_date, change_str_types


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

    date3 = get_builtin_date(xmlrpc_client.DateTime(datetime.datetime(1954, 12, 19, 4, 44, 44)))
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


@pytest.mark.skipif(six.PY2, reason='This test if for Python 3 only')
def test_string_upd_error_with_py3():
    raises(AssertionError, change_str_types('123'))


@pytest.mark.skipif(six.PY3, reason='This test if for Python 2 only')
def test_string_upd_1():
    assert change_str_types('abc', unicode) == u'abc'


@pytest.mark.skipif(six.PY3, reason='This test if for Python 2 only')
def test_string_upd_2():
    assert change_str_types(u'abc', str) == 'abc'


@pytest.mark.skipif(six.PY3, reason='This test if for Python 2 only')
def test_string_upd_3():
    in_list = [145, 964, 84, ['ghjfgh', 64], [[84, 9.254, b'trdf', 645], '456', u'784', 'sdfg']]
    expected_out = [145, 964, 84, [u'ghjfgh', 64], [[84, 9.254, b'trdf', 645], u'456', u'784', u'sdfg']]
    assert change_str_types(in_list, unicode) == expected_out


@pytest.mark.skipif(six.PY3, reason='This test if for Python 2 only')
def test_string_upd_4():
    in_list = [145, 964, 84, [u'ghjfgh', 64], [[84, 9.254, b'trdf', 645], u'456', u'784', 'sdfg']]
    expected_out = [145, 964, 84, ['ghjfgh', 64], [[84, 9.254, b'trdf', 645], '456', '784', 'sdfg']]
    assert change_str_types(in_list, str) == expected_out


@pytest.mark.skipif(six.PY3, reason='This test if for Python 2 only')
def test_string_upd_5():
    in_list = (145, 964, 84, ['ghjfgh', 64], [(84, 9.254, b'trdf', 645), '456', u'784', 'sdfg'])
    expected_out = (145, 964, 84, [u'ghjfgh', 64], [(84, 9.254, b'trdf', 645), u'456', u'784', u'sdfg'])
    assert change_str_types(in_list, unicode) == expected_out


@pytest.mark.skipif(six.PY3, reason='This test if for Python 2 only')
def test_string_upd_6():
    in_list = (145, 964, 84, (u'ghjfgh', 64), ([84, 9.254, b'trdf', 645], u'456', u'784', 'sdfg'))
    expected_out = (145, 964, 84, ('ghjfgh', 64), ([84, 9.254, b'trdf', 645], '456', '784', 'sdfg'))
    assert change_str_types(in_list, str) == expected_out


@pytest.mark.skipif(six.PY3, reason='This test if for Python 2 only')
def test_string_upd_7():
    in_dict = {
        'a': 456,
        'b': [84, 5.1, 'strdfg', u'trdt'],
        'pp': {
            'x': 32,
            'y': ['rtg', 'poi', 'aze']
        },
    }
    expected_out = {
        'a': 456,
        'b': [84, 5.1, u'strdfg', u'trdt'],
        'pp': {
            'x': 32,
            'y': [u'rtg', u'poi', u'aze']
        },
    }
    assert change_str_types(in_dict, unicode) == expected_out


@pytest.mark.skipif(six.PY3, reason='This test if for Python 2 only')
def test_string_upd_8():
    in_dict = {
        'a': 456,
        'b': [84, 5.1, u'strdfg', u'trdt'],
        'pp': {
            'x': 32,
            'y': [u'rtg', 'poi', u'aze']
        },
    }
    expected_out = {
        'a': 456,
        'b': [84, 5.1, 'strdfg', 'trdt'],
        'pp': {
            'x': 32,
            'y': ['rtg', 'poi', 'aze']
        },
    }
    assert change_str_types(in_dict, str) == expected_out
