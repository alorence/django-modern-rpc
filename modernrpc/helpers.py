# coding: utf-8
import datetime

import xmlrpc.client as xmlrpc_client
from typing import Union, Optional, Any, Iterable


def get_builtin_date(
    date: Union[str, datetime.datetime, xmlrpc_client.DateTime],
    date_format: str = "%Y-%m-%dT%H:%M:%S",
    raise_exception: bool = False,
) -> Optional[datetime.datetime]:
    """
    Try to convert a date to a builtin instance of ``datetime.datetime``.
    The input date can be a ``str``, a ``datetime.datetime``, a ``xmlrpc.client.Datetime`` or a ``xmlrpclib.Datetime``
    instance. The returned object is a ``datetime.datetime``.

    :param date: The date object to convert.
    :param date_format: If the given date is a str, format is passed to strptime to parse it
    :param raise_exception: If set to True, an exception will be raised if the input string cannot be parsed
    :return: A valid ``datetime.datetime`` instance
    """
    if isinstance(date, datetime.datetime):
        # Default XML-RPC handler is configured to decode dateTime.iso8601 type
        # to builtin datetime.datetim instance
        return date
    if isinstance(date, xmlrpc_client.DateTime):
        # If constant settings.MODERNRPC_XMLRPC_USE_BUILTIN_TYPES has been set to True
        # the date is decoded as DateTime object
        return datetime.datetime.strptime(date.value, "%Y%m%dT%H:%M:%S")

    # If date is given as str. This is the normal behavior for JSON-RPC
    try:
        return datetime.datetime.strptime(date, date_format)
    except ValueError:
        if raise_exception:
            raise
        return None


def ensure_sequence(element: Any) -> Iterable:
    """Ensure the given argument is a sequence object (tuple, list). If not, return a list containing its value."""
    return element if isinstance(element, (list, tuple)) else [element]
