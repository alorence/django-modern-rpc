# coding: utf-8
import pytest
from django.utils import six
from pytest import raises

from modernrpc.compat import standardize_strings


@pytest.mark.skipif(six.PY2, reason='Python 3 specific test')
def test_standardize_str_error_with_py3():
    with raises(AssertionError) as excpinfo:
        standardize_strings('123')
    assert 'python 2 only' in str(excpinfo.value).lower()


@pytest.mark.skipif(six.PY3, reason='Python 2 specific test')
def test_standardize_str_1():
    # six.text_type is 'unicode' in Python 2
    assert standardize_strings('abc', six.text_type) == u'abc'


@pytest.mark.skipif(six.PY3, reason='Python 2 specific test')
def test_standardize_str_2():
    # six.binary_type is 'str' in Python 2
    assert standardize_strings(u'abc', six.binary_type) == 'abc'


@pytest.mark.skipif(six.PY3, reason='Python 2 specific test')
def test_standardize_str_3():
    in_list = [145, 964, 84, ['ghjfgh', 64], [[84, 9.254, b'trdf', 645], '456', u'784', 'sdfg']]
    expected_out = [145, 964, 84, [u'ghjfgh', 64], [[84, 9.254, b'trdf', 645], u'456', u'784', u'sdfg']]
    # six.text_type is 'unicode' in Python 2
    assert standardize_strings(in_list, six.text_type) == expected_out


@pytest.mark.skipif(six.PY3, reason='Python 2 specific test')
def test_standardize_str_4():
    in_list = [145, 964, 84, [u'ghjfgh', 64], [[84, 9.254, b'trdf', 645], u'456', u'784', 'sdfg']]
    expected_out = [145, 964, 84, ['ghjfgh', 64], [[84, 9.254, b'trdf', 645], '456', '784', 'sdfg']]
    # six.binary_type is 'str' in Python 2
    assert standardize_strings(in_list, six.binary_type) == expected_out


@pytest.mark.skipif(six.PY3, reason='Python 2 specific test')
def test_standardize_str_5():
    in_list = (145, 964, 84, ['ghjfgh', 64], [(84, 9.254, b'trdf', 645), '456', u'784', 'sdfg'])
    expected_out = (145, 964, 84, [u'ghjfgh', 64], [(84, 9.254, b'trdf', 645), u'456', u'784', u'sdfg'])
    # six.text_type is 'unicode' in Python 2
    assert standardize_strings(in_list, six.text_type) == expected_out


@pytest.mark.skipif(six.PY3, reason='Python 2 specific test')
def test_standardize_str_6():
    in_list = (145, 964, 84, (u'ghjfgh', 64), ([84, 9.254, b'trdf', 645], u'456', u'784', 'sdfg'))
    expected_out = (145, 964, 84, ('ghjfgh', 64), ([84, 9.254, b'trdf', 645], '456', '784', 'sdfg'))
    # six.binary_type is 'str' in Python 2
    assert standardize_strings(in_list, six.binary_type) == expected_out


@pytest.mark.skipif(six.PY3, reason='Python 2 specific test')
def test_standardize_str_7():
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
    # six.text_type is 'unicode' in Python 2
    assert standardize_strings(in_dict, six.text_type) == expected_out


@pytest.mark.skipif(six.PY3, reason='Python 2 specific test')
def test_standardize_str_8():
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
    # six.binary_type is 'str' in Python 2
    assert standardize_strings(in_dict, six.binary_type) == expected_out


@pytest.mark.skipif(six.PY3, reason='Python 2 specific test')
def test_standardize_str_9():
    assert standardize_strings(54, None) == 54


@pytest.mark.skipif(six.PY3, reason='Python 2 specific test')
def test_standardize_str_10():
    with raises(TypeError):
        assert standardize_strings("64", int)


@pytest.mark.skipif(six.PY3, reason='Python 2 specific test')
def test_method_level_str_std(xmlrpc_client, jsonrpc_client):
    """TODO: what was the idea here ?"""
    assert jsonrpc_client.force_unicode_input("abcde") == "<type 'unicode'>"
    assert xmlrpc_client.force_unicode_input("abcde") == "<type 'unicode'>"
