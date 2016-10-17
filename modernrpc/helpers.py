# coding: utf-8
import datetime

try:
    # Python 3
    import xmlrpc.client as xmlrpc_module
except ImportError:
    # Python 2
    import xmlrpclib as xmlrpc_module


def get_builtin_date(date, format="%Y-%m-%dT%H:%M:%S", raise_exception=False):
    """
    Try to convert a date to a builtin instance of datetime.datetime.
    The input date can be a str, a datetime.datetime or a xmlrpc.client.Datetime instance. The returned object
    is a datetime.datetime.

    :param date: The date object to convert.
    :param format: If the given date is a str, format is passed to strptime to parse it
    :param raise_exception: If set to true, an exception will be raised when the input str can't be parsed properly.
    :return: A valid datetime.datetime instance
    """
    if isinstance(date, datetime.datetime):
        # Default XML-RPC handler is configured to decode dateTime.iso8601 type
        # to builtin datetime.datetim instance
        return date
    elif isinstance(date, xmlrpc_module.DateTime):
        # If constant MODERNRPC_XML_USE_BUILTIN_TYPES has been set to True
        # in django settings, the date is decoded as DateTime object
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
