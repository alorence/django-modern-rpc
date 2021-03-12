# coding: utf-8
# flake8: noqa
from modernrpc.core import rpc_method


@rpc_method()
minus(a, b):
    return a - b
