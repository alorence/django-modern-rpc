# coding: utf-8
# flake8: noqa
from modernrpc.core import rpc_method
from invalid_package import unknown_module  # noqa


@rpc_method()
def minus(a, b):
    return a - b
