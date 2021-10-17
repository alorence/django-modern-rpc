import future.utils

from modernrpc.core import rpc_method


# Standardization to 'unicode' type
@rpc_method(str_standardization=future.utils.text_type)
def force_unicode_input(data):
    """Returns a string representation of input argument type"""
    return str(type(data))
