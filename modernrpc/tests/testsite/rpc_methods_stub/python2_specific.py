from modernrpc.core import rpc_method


@rpc_method(str_standardization=unicode)
def force_unicode_input(data):
    """Returns a string representation of input argument type"""
    return str(type(data))
