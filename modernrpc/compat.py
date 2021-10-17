# coding: utf-8
import future.utils

from modernrpc.conf import settings


def _generic_convert_string(value, target_type, encoding):
    """
    Generic method to convert any argument type (string type, list, set, tuple, dict) to an equivalent,
    with string values converted to given 'to_type' (str or unicode).
    This method must be used with Python 2 interpreter only.

    :param value: The value to convert
    :param target_type: The target string type to convert to
    :param encoding: When
    :return:
    """
    if future.utils.PY3 or isinstance(value, target_type):
        return value

    if isinstance(value, future.utils.string_types):
        if target_type == str:
            return value.encode(encoding)
        elif target_type == unicode:
            return unicode(value, encoding)
        else:
            raise TypeError

    elif isinstance(value, (list, tuple, set)):
        return type(value)([_generic_convert_string(element, target_type, encoding) for element in value])

    elif isinstance(value, dict):
        return {k: _generic_convert_string(v, target_type, encoding) for k, v in value.items()}

    return value


def standardize_strings(arg, target_type=settings.MODERNRPC_PY2_STR_TYPE, encoding=settings.MODERNRPC_PY2_STR_ENCODING):
    """
    Python 2 only. Lookup given *arg* and convert its str or unicode value according to MODERNRPC_PY2_STR_TYPE and
    MODERNRPC_PY2_STR_ENCODING settings.
    """
    if not target_type or future.utils.PY3:
        return arg

    if target_type in (str, "str"):
        # We want to convert from unicode to str
        return _generic_convert_string(arg, str, encoding)

    elif target_type in (unicode, "unicode"):
        # We want to convert from str to unicode
        return _generic_convert_string(arg, unicode, encoding)

    raise TypeError('standardize_strings() called with an invalid strtype: "{}". Allowed values: str or unicode'
                    .format(repr(target_type)))
