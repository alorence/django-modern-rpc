from modernrpc.core import rpc_method, JSONRPC_PROTOCOL, XMLRPC_PROTOCOL


@rpc_method(protocol=JSONRPC_PROTOCOL)
def json_only():
    return 'JSON only'


@rpc_method(protocol=XMLRPC_PROTOCOL)
def xml_only():
    return 'XML only'
