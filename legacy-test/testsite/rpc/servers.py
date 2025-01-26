from modernrpc.core import Protocol
from modernrpc.server import RPCServer

from .generic import bp as generic
from .specific_types import bp as spec_types

server = RPCServer()

server.register_namespace(generic)
server.register_namespace(spec_types)

jsonrpc_server = RPCServer(supported_protocol=Protocol.JSON_RPC)
xmlrpc_server = RPCServer(supported_protocol=Protocol.XML_RPC)


@jsonrpc_server.register_procedure
@server.register_procedure
def json_only():
    return "JSON only"


@xmlrpc_server.register_procedure
@server.register_procedure
def xml_only():
    return "XML only"
