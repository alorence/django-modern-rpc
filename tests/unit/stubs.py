"""
Note: this module is NOT listed in any settings.MODERNRPC_METHODS_MODULES
All methods declared here must be manually registered to be available to remote call
"""

from modernrpc.core import rpc_method


@rpc_method
def dummy_remote_procedure_1():
    # Manually registered remote procedure.
    return 33


@rpc_method(name="another_name")
def dummy_remote_procedure_2():
    # Manually registered remote procedure, with custom name.
    return 33


@rpc_method(name="rpc.invalid.name")
def dummy_remote_procedure_3():
    # Manually registered remote procedure, with invalid custom name.
    return 42


@rpc_method(name="divide")
def dummy_remote_procedure_4():
    # Manually registered remote procedure, with invalid custom name (name already registered).
    return 42


def not_decorated_procedure():
    pass


@rpc_method(name="foo", entry_point="v1")
def func_v1():
    # Function to register with the name "foo" under "v1" entry_point
    return "V1"


@rpc_method(name="foo", entry_point="v2")
def func_v2():
    # Function to register with the name "foo" under "v2" entry_point
    return "V2"
