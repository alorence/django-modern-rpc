# coding: utf-8
import future.utils
import pytest

from modernrpc.compat import standardize_strings


@pytest.mark.skipif(future.utils.PY2, reason='Python 3 specific test')
def test_standardize_str_error_with_py3():
    assert isinstance(standardize_strings('123'), str)


@pytest.mark.skipif(future.utils.PY3, reason='Python 2 specific test')
def test_standardize_str_to_unicode():
    assert standardize_strings('abc', unicode) == u'abc'


@pytest.mark.skipif(future.utils.PY3, reason='Python 2 specific test')
def test_standardize_unicode_to_str():
    assert standardize_strings(u'abc', str) == 'abc'


@pytest.mark.skipif(future.utils.PY3, reason='Python 2 specific test')
def test_standardize_list_to_unicode():
    input_val_ = [145, 964, 84, ['ghjfgh', 64], [[84, 9.254, b'trdf', 645], '456', u'784', 'sdfg']]
    output_val = [145, 964, 84, [u'ghjfgh', 64], [[84, 9.254, b'trdf', 645], u'456', u'784', u'sdfg']]
    assert standardize_strings(input_val_, unicode) == output_val


@pytest.mark.skipif(future.utils.PY3, reason='Python 2 specific test')
def test_standardize_list_to_str():
    input_val_ = [145, 964, 84, [u'ghjfgh', 64], [[84, 9.254, b'trdf', 645], u'456', u'784', 'sdfg']]
    output_val = [145, 964, 84, ['ghjfgh', 64], [[84, 9.254, b'trdf', 645], '456', '784', 'sdfg']]
    assert standardize_strings(input_val_, str) == output_val


@pytest.mark.skipif(future.utils.PY3, reason='Python 2 specific test')
def test_standardize_set_to_unicode():
    input_val_ = (145, 964, 84, ['ghjfgh', 64], [(84, 9.254, b'trdf', 645), '456', u'784', 'sdfg'])
    output_val = (145, 964, 84, [u'ghjfgh', 64], [(84, 9.254, b'trdf', 645), u'456', u'784', u'sdfg'])
    assert standardize_strings(input_val_, unicode) == output_val


@pytest.mark.skipif(future.utils.PY3, reason='Python 2 specific test')
def test_standardize_set_to_str():
    input_val_ = (145, 964, 84, (u'ghjfgh', 64), ([84, 9.254, b'trdf', 645], u'456', u'784', 'sdfg'))
    output_val = (145, 964, 84, ('ghjfgh', 64), ([84, 9.254, b'trdf', 645], '456', '784', 'sdfg'))
    assert standardize_strings(input_val_, str) == output_val


@pytest.mark.skipif(future.utils.PY3, reason='Python 2 specific test')
def test_standardize_dict_to_unicode():
    input_dict = {
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
    assert standardize_strings(input_dict, unicode) == expected_out


@pytest.mark.skipif(future.utils.PY3, reason='Python 2 specific test')
def test_standardize_dict_to_str():
    input_dict = {
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
    assert standardize_strings(input_dict, str) == expected_out


@pytest.mark.skipif(future.utils.PY3, reason='Python 2 specific test')
def test_standardize_nothing():
    assert standardize_strings(54, None) == 54


@pytest.mark.skipif(future.utils.PY3, reason='Python 2 specific test')
def test_standardize_invalid_type():
    with pytest.raises(TypeError):
        assert standardize_strings("64", int)


@pytest.mark.skipif(future.utils.PY3, reason='Python 2 specific test')
def test_method_level_str_std(xmlrpc_client, jsonrpc_client):
    """TODO: what was the idea here ?"""
    assert jsonrpc_client.force_unicode_input("abcde") == "<type 'unicode'>"
    assert xmlrpc_client.force_unicode_input("abcde") == "<type 'unicode'>"
