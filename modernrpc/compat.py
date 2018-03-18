# coding: utf-8
from django.utils import six

from modernrpc.conf import settings


def _generic_convert_string(v, from_type, to_type, encoding):
    """
    Generic method to convert any argument type (string type, list, set, tuple, dict) to an equivalent,
    with string values converted to given 'to_type' (str or unicode).
    This method must be used with Python 2 interpreter only.

    :param v: The value to convert
    :param from_type: The original string type to convert
    :param to_type: The target string type to convert to
    :param encoding: When
    :return:
    """

    assert six.PY2, "This function should be used with Python 2 only"
    assert from_type != to_type

    if from_type == six.binary_type and isinstance(v, six.binary_type):
        return six.text_type(v, encoding)

    elif from_type == six.text_type and isinstance(v, six.text_type):
        return v.encode(encoding)

    elif isinstance(v, (list, tuple, set)):
        return type(v)([_generic_convert_string(element, from_type, to_type, encoding) for element in v])

    elif isinstance(v, dict):
        return {k: _generic_convert_string(v, from_type, to_type, encoding) for k, v in v.iteritems()}

    return v


def standardize_strings(arg, strtype=settings.MODERNRPC_PY2_STR_TYPE, encoding=settings.MODERNRPC_PY2_STR_ENCODING):
    """
    Python 2 only. Lookup given *arg* and convert its str or unicode value according to MODERNRPC_PY2_STR_TYPE and
    MODERNRPC_PY2_STR_ENCODING settings.
    """
    assert six.PY2, "This function should be used with Python 2 only"

    if not strtype:
        return arg

    if strtype == six.binary_type or strtype == 'str':
        # We want to convert from unicode to str
        return _generic_convert_string(arg, six.text_type, six.binary_type, encoding)

    elif strtype == six.text_type or strtype == 'unicode':
        # We want to convert from str to unicode
        return _generic_convert_string(arg, six.binary_type, six.text_type, encoding)

    raise TypeError('standardize_strings() called with an invalid strtype: "{}". Allowed values: str or unicode'
                    .format(repr(strtype)))
