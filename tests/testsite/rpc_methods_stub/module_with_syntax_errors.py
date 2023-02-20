# coding: utf-8
from modernrpc.core import rpc_method


@rpc_method()
minus(a, b):
    return a - b
