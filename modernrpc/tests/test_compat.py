import pytest
from django.utils import six
from pytest import raises

from modernrpc.compat import standardize_strings


@pytest.mark.skipif(six.PY2, reason='This test if for Python 3 only')
def test_standardize_str_error_with_py3():
    with raises(AssertionError):
        standardize_strings('123')


@pytest.mark.skipif(six.PY3, reason='This test if for Python 2 only')
def test_standardize_str_1():
    assert standardize_strings('abc', unicode) == u'abc'


@pytest.mark.skipif(six.PY3, reason='This test if for Python 2 only')
def test_standardize_str_2():
    assert standardize_strings(u'abc', str) == 'abc'


@pytest.mark.skipif(six.PY3, reason='This test if for Python 2 only')
def test_standardize_str_3():
    in_list = [145, 964, 84, ['ghjfgh', 64], [[84, 9.254, b'trdf', 645], '456', u'784', 'sdfg']]
    expected_out = [145, 964, 84, [u'ghjfgh', 64], [[84, 9.254, b'trdf', 645], u'456', u'784', u'sdfg']]
    assert standardize_strings(in_list, unicode) == expected_out


@pytest.mark.skipif(six.PY3, reason='This test if for Python 2 only')
def test_standardize_str_4():
    in_list = [145, 964, 84, [u'ghjfgh', 64], [[84, 9.254, b'trdf', 645], u'456', u'784', 'sdfg']]
    expected_out = [145, 964, 84, ['ghjfgh', 64], [[84, 9.254, b'trdf', 645], '456', '784', 'sdfg']]
    assert standardize_strings(in_list, str) == expected_out


@pytest.mark.skipif(six.PY3, reason='This test if for Python 2 only')
def test_standardize_str_5():
    in_list = (145, 964, 84, ['ghjfgh', 64], [(84, 9.254, b'trdf', 645), '456', u'784', 'sdfg'])
    expected_out = (145, 964, 84, [u'ghjfgh', 64], [(84, 9.254, b'trdf', 645), u'456', u'784', u'sdfg'])
    assert standardize_strings(in_list, unicode) == expected_out


@pytest.mark.skipif(six.PY3, reason='This test if for Python 2 only')
def test_standardize_str_6():
    in_list = (145, 964, 84, (u'ghjfgh', 64), ([84, 9.254, b'trdf', 645], u'456', u'784', 'sdfg'))
    expected_out = (145, 964, 84, ('ghjfgh', 64), ([84, 9.254, b'trdf', 645], '456', '784', 'sdfg'))
    assert standardize_strings(in_list, str) == expected_out


@pytest.mark.skipif(six.PY3, reason='This test if for Python 2 only')
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
    assert standardize_strings(in_dict, unicode) == expected_out


@pytest.mark.skipif(six.PY3, reason='This test if for Python 2 only')
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
    assert standardize_strings(in_dict, str) == expected_out


@pytest.mark.skipif(six.PY3, reason='This test if for Python 2 only')
def test_standardize_str_9():
    assert standardize_strings(54, None) == 54


@pytest.mark.skipif(six.PY3, reason='This test if for Python 2 only')
def test_standardize_str_10():
    with raises(TypeError):
        assert standardize_strings("64", int)
