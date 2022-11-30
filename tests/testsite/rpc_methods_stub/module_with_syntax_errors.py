# coding: utf-8
# flake8: noqa
# pylama: skip=1
from modernrpc.core import rpc_method


@rpc_method()
minus(a, b):
    return a - b
