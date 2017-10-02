from modernrpc.core import rpc_method, JSONRPC, XMLRPC


@rpc_method(protocol=JSONRPC)
def method_x():
    return 'JSON only'


@rpc_method(protocol=XMLRPC)
def method_y():
    return 'XML only'
