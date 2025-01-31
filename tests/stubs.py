"""
Note: this module is NOT listed in any settings.MODERNRPC_METHODS_MODULES
All methods declared here must be manually registered to be available to remote call
"""

from modernrpc.server import RpcServer

main_server = RpcServer()
server_v1 = RpcServer()
server_v2 = RpcServer()


@main_server.register_procedure
def dummy_remote_procedure_1():
    # Manually registered remote procedure.
    return 33


@main_server.register_procedure(name="another_name")
def dummy_remote_procedure_2():
    # Manually registered remote procedure, with custom name.
    return 33


@main_server.register_procedure(name="rpc.invalid.name")
def dummy_remote_procedure_3():
    # Manually registered remote procedure, with invalid custom name.
    return 42


@main_server.register_procedure(name="divide")
def dummy_remote_procedure_4():
    # Manually registered remote procedure, with invalid custom name (name already registered).
    return 42


def not_decorated_procedure():
    pass


@server_v1.register_procedure(name="foo")
def func_v1():
    # Function to register with the name "foo" under "v1" entry_point
    return "V1"


@server_v2.register_procedure(name="foo")
def func_v2():
    # Function to register with the name "foo" under "v2" entry_point
    return "V2"
