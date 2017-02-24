# coding: utf-8
import datetime

from django.utils import six
from django.utils.six.moves import xmlrpc_client

from modernrpc.conf import settings


def get_builtin_date(date, format="%Y-%m-%dT%H:%M:%S", raise_exception=False):
    """
    Try to convert a date to a builtin instance of ``datetime.datetime``.
    The input date can be a ``str``, a ``datetime.datetime``, a ``xmlrpc.client.Datetime`` or a ``xmlrpclib.Datetime``
    instance. The returned object is a ``datetime.datetime``.

    :param date: The date object to convert.
    :param format: If the given date is a str, format is passed to strptime to parse it
    :param raise_exception: If set to true, an exception will be raised when the input str can't be parsed properly.
    :return: A valid ``datetime.datetime`` instance
    """
    if isinstance(date, datetime.datetime):
        # Default XML-RPC handler is configured to decode dateTime.iso8601 type
        # to builtin datetime.datetim instance
        return date
    elif isinstance(date, xmlrpc_client.DateTime):
        # If constant settings.MODERNRPC_XMLRPC_USE_BUILTIN_TYPES has been set to True
        # the date is decoded as DateTime object
        return datetime.datetime.strptime(date.value, "%Y%m%dT%H:%M:%S")
    else:
        # If date is given as str (or unicode for python 2)
        # This is the normal behavior for JSON-RPC
        try:
            return datetime.datetime.strptime(date, format)
        except ValueError:
            if raise_exception:
                raise
            else:
                return None


def change_str_types(arg, strtype=settings.MODERNRPC_PY2_STR_TYPE):
    assert six.PY2, "This function should be used with Python 2 only"

    if not strtype:
        return arg

    if strtype == str:
        # We want to convert from unicode to str
        return unicode_to_str(arg)
    elif strtype == unicode:
        # We want to convert from str to unicode
        return str_to_unicode(arg)

    raise TypeError


def str_to_unicode(arg):
    if isinstance(arg, str):
        return unicode(arg, settings.MODERNRPC_PY2_STR_ENCODING)
    elif isinstance(arg, (list, tuple, set)):
        return type(arg)([str_to_unicode(element) for element in arg])
    elif isinstance(arg, dict):
        return {k: str_to_unicode(v) for k, v in arg.iteritems()}
    return arg


def unicode_to_str(arg):
    if isinstance(arg, unicode):
        return arg.encode(settings.MODERNRPC_PY2_STR_ENCODING)
    elif isinstance(arg, (list, tuple, set)):
        return type(arg)([unicode_to_str(element) for element in arg])
    elif isinstance(arg, dict):
        return {k: unicode_to_str(v) for k, v in arg.iteritems()}
    return arg
