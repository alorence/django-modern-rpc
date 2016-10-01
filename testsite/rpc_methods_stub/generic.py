from modernrpc.core import rpc_method


@rpc_method()
def add(a, b):
    return a + b
