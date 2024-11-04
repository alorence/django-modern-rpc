from modernrpc.core import Protocol, rpc_method


@rpc_method(protocol=Protocol.JSON_RPC)
def json_only():
    return "JSON only"


@rpc_method(protocol=Protocol.XML_RPC)
def xml_only():
    return "XML only"
