from modernrpc.core import rpc_method
from modernrpc.exceptions import RPCException, RPC_CUSTOM_ERROR_BASE


@rpc_method()
def add(a, b):
    return a + b


@rpc_method()
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


@rpc_method()
def raise_custom_exception():
    raise MyCustomException(RPC_CUSTOM_ERROR_BASE + 5, 'This is a test error')
