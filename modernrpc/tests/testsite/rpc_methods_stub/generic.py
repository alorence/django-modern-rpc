# coding: utf-8
import datetime

from modernrpc.core import rpc_method
from modernrpc.exceptions import RPCException, RPC_CUSTOM_ERROR_BASE
from modernrpc.helpers import get_builtin_date

# In this file, some methods are decorated with @rpc_method without parenthesis, some
# are decorated with @rpc_method(). Both notations are supported and must works the same way


@rpc_method()
def add(a, b):
    return a + b


@rpc_method
def divide(numerator, denominator):
    """
    Divide a numerator by a denominator

    :param numerator:
    :param denominator:
    :type numerator: int or double
    :type denominator: int or double
    :return:
    :rtype: int or double
    """
    return numerator / denominator


class MyCustomException(RPCException):
    pass


@rpc_method
def raise_custom_exception():
    raise MyCustomException(RPC_CUSTOM_ERROR_BASE + 5, 'This is a test error')


@rpc_method()
def add_one_month(date):
    """Adds 31 days to the given date, and returns the result."""
    return get_builtin_date(date) + datetime.timedelta(days=31)


def existing_but_not_decorated():
    """This function help to validate only methods with decorator are effectively added to the registry"""
    return 42 * 42
