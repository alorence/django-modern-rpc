from invalid_package import unknown_module

from modernrpc.core import rpc_method


@rpc_method()
def minus(a, b):
    return a - b
