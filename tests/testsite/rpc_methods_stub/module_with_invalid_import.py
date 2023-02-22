from modernrpc.core import rpc_method
from invalid_package import unknown_module


@rpc_method()
def minus(a, b):
    return a - b
