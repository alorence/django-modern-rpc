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
def divide(numerator, denominator, x=50, y=90, z=120, a=1, b=5, c=10):
    """
    Divide a numerator by a denominator

    :param numerator: The numerator
    :param denominator: The denominator
    :param x: useless, needed to check arguments ordering
    :param y: useless, needed to check arguments ordering
    :param z: useless, needed to check arguments ordering
    :param a: useless, needed to check arguments ordering
    :param b: useless, needed to check arguments ordering
    :param c: useless, needed to check arguments ordering
    :type numerator: int or double
    :type denominator: int or double
    :type x: int
    :type y: int
    :type z: int
    :type a: int
    :type b: int
    :type c: int
    :return:
    :rtype: int or double
    """
    return numerator / denominator


@rpc_method(name='customized_name')
def another_name():
    """This one will help to test method registration
    when name has been customized"""
    pass


class MyCustomException(RPCException):

    def __init__(self):
        super(MyCustomException, self).__init__(RPC_CUSTOM_ERROR_BASE + 5, 'This is a test error')


@rpc_method
def raise_custom_exception():
    raise MyCustomException()


class MyCustomExceptionWithData(RPCException):

    def __init__(self, data):
        super(MyCustomExceptionWithData, self).__init__(RPC_CUSTOM_ERROR_BASE + 5, 'This exception has additional data', data)


@rpc_method
def raise_custom_exception_with_data():
    raise MyCustomExceptionWithData(['a', 'b', 'c'])


@rpc_method()
def add_one_month(date):
    """Adds 31 days to the given date, and returns the result."""
    return get_builtin_date(date) + datetime.timedelta(days=31)


def existing_but_not_decorated():
    """This function help to validate only methods with decorator are effectively added to the registry"""
    return 42 * 42


@rpc_method
def get_invalid_result():
    """Return an object instance that cannot be serialized in json or xml"""
    from django.http.response import HttpResponse
    return HttpResponse(content='dummy')
