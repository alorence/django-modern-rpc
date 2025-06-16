from __future__ import annotations

import datetime
import xmlrpc.client
from typing import TYPE_CHECKING, Any, Iterable, Sequence

from modernrpc.constants import NOT_SET

if TYPE_CHECKING:
    from enum import Flag
    from typing import Callable


def check_flags_compatibility(a: Flag, b: Flag) -> bool:
    """Check that both flags are compatible"""
    return bool(a & b)


def get_builtin_date(
    date: str | datetime.datetime | xmlrpc.client.DateTime,
    date_format: str = "%Y-%m-%dT%H:%M:%S",
    raise_exception: bool = False,
) -> datetime.datetime | None:
    """
    Try to convert a date to a builtin instance of ``datetime.datetime``.
    The input date can be a ``str``, a ``datetime.datetime``, a ``xmlrpc.client.Datetime`` or a ``xmlrpclib.Datetime``
    instance. The returned object is a ``datetime.datetime``.

    :param date: The date object to convert.
    :param date_format: If the given date is a str, it is passed to strptime for parsing
    :param raise_exception: If set to True, an exception will be raised if the input string cannot be parsed
    :return: A valid ``datetime.datetime`` instance
    """
    if isinstance(date, datetime.datetime):
        # Default XML-RPC handler is configured to decode a dateTime.iso8601 value
        # to builtin datetime.datetime instance
        return date
    if isinstance(date, xmlrpc.client.DateTime):
        # If a special xmlrpc.client.DateTime instance is given, convert it to a standard datetime instance
        return datetime.datetime.strptime(date.value, "%Y%m%dT%H:%M:%S")

    # If the date is given as str. This is the normal behavior for JSON-RPC
    try:
        return datetime.datetime.strptime(date, date_format)
    except ValueError:
        if raise_exception:
            raise
        return None


def ensure_sequence(element: Any) -> Sequence:
    """Ensure the given argument is a sequence object (tuple, list). If not, return a list containing its value."""
    return element if isinstance(element, (list, tuple)) else [element]


def first(seq: Iterable, default=NOT_SET) -> Any:
    """
    Return the first element of the given iterable, or default value if the iterable is empty.
    When the default value is not set, raise an IndexError if the iterable is empty.

    This helper should be used when RUF015 is encountered on linting.
    See https://docs.astral.sh/ruff/rules/unnecessary-iterable-allocation-for-first-element/
    """
    try:
        return next(iter(seq))
    except StopIteration:
        if default is not NOT_SET:
            return default
        raise IndexError("No element found in iterable") from None


def first_true(iterable: Iterable[Any], default: Any = None, pred: Callable[[Any], bool] | None = None) -> Any:
    """
    Same as more_itertools.first_true(), but avoid dependency to a new lib
    Doc: https://more-itertools.readthedocs.io/en/stable/api.html#more_itertools.first_true
    """
    return next(filter(pred, iterable), default)
