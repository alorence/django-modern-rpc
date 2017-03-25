from django.utils import six

from modernrpc.conf import settings


def generic_convert_string(v, from_type, to_type):
    """Generic method to convert from a unicode to str or from str to unicode. Works only with Python 2"""

    if from_type == str and isinstance(v, str):
        return unicode(v, settings.MODERNRPC_PY2_STR_ENCODING)

    elif from_type == unicode and isinstance(v, unicode):
        return v.encode(settings.MODERNRPC_PY2_STR_ENCODING)

    elif isinstance(v, (list, tuple, set)):
        return type(v)([generic_convert_string(element, from_type, to_type) for element in v])

    elif isinstance(v, dict):
        return {k: generic_convert_string(v, from_type, to_type) for k, v in v.iteritems()}

    return v


def standardize_strings(arg, strtype=settings.MODERNRPC_PY2_STR_TYPE):
    assert six.PY2, "This function should be used with Python 2 only"

    if not strtype:
        return arg

    if strtype == str:
        # We want to convert from unicode to str
        return generic_convert_string(arg, unicode, str)

    elif strtype == unicode:
        # We want to convert from str to unicode
        return generic_convert_string(arg, str, unicode)

    raise TypeError('standardize_strings() called with an invalid strtype: "{}"'.format(strtype))
