from modernrpc.core import rpc_method, JSONRPC_PROTOCOL, XMLRPC_PROTOCOL


@rpc_method(protocol=JSONRPC_PROTOCOL)
def method_x():
    return 'JSON only'


@rpc_method(protocol=XMLRPC_PROTOCOL)
def method_y():
    return 'XML only'
