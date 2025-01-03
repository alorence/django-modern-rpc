import datetime

from modernrpc.core import PROTOCOL_KEY, rpc_method
from modernrpc.exceptions import RPC_CUSTOM_ERROR_BASE, RPCException
from modernrpc.helpers import get_builtin_date

# In this file, some methods are decorated with @rpc_method without parenthesis, some
# are decorated with @rpc_method(). Both notations are supported and must works the same way


@rpc_method()
def add(a, b):
    return a + b


@rpc_method
def divide(numerator, denominator, x="xx", y=b"zz", z=None, a=3.14, b=5, c=10):
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
    :type x: str
    :type y: bytes
    :type z: list
    :type a: float
    :type b: int
    :type c: int
    :return:
    :rtype: int or double
    """
    return numerator / denominator


@rpc_method(name="customized_name")
def another_name():
    """This one will help to test method registration
    when name has been customized"""


class MyCustomException(RPCException):
    def __init__(self):
        super().__init__(RPC_CUSTOM_ERROR_BASE + 5, "This is a test error")


@rpc_method
def raise_custom_exception():
    raise MyCustomException


class MyCustomExceptionWithData(RPCException):
    def __init__(self, data):
        super().__init__(RPC_CUSTOM_ERROR_BASE + 5, "This exception has additional data", data)


@rpc_method
def raise_custom_exception_with_data():
    raise MyCustomExceptionWithData(["a", "b", "c"])


@rpc_method()
def add_one_month(date):
    """Adds 30 days to the given date, and returns the result."""
    return get_builtin_date(date) + datetime.timedelta(days=30)


def existing_but_not_decorated():
    """This function help to validate only methods with decorator are effectively added to the registry"""
    return 42 * 42


@rpc_method
def get_invalid_result():
    """Return an object instance that cannot be serialized in json or xml"""
    from django.http.response import HttpResponse

    return HttpResponse(content="dummy")


@rpc_method()
def method_with_kwargs(**kwargs):
    return str(kwargs.get(PROTOCOL_KEY))


@rpc_method()
def method_with_kwargs_2(x, **kwargs):
    return x, str(kwargs.get(PROTOCOL_KEY))
