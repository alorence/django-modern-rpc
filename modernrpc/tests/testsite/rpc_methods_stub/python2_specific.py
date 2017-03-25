from modernrpc.core import rpc_method


@rpc_method(str_standardization=unicode)
def force_unicode_input(data):
    """Return a string representation type of input argument"""
    return str(type(data))
