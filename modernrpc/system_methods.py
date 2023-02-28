from typing import TYPE_CHECKING

from modernrpc.core import (
    ENTRY_POINT_KEY,
    HANDLER_KEY,
    PROTOCOL_KEY,
    Protocol,
    REQUEST_KEY,
    RPCRequestContext,
    registry,
    rpc_method,
)
from modernrpc.exceptions import RPCInvalidParams

if TYPE_CHECKING:
    from modernrpc.handlers import XMLRPCHandler


@rpc_method(name="system.listMethods")
def __system_list_methods(**kwargs):
    """Returns a list of all methods available in the current entry point"""
    entry_point: str = kwargs.get(ENTRY_POINT_KEY)
    protocol: Protocol = kwargs.get(PROTOCOL_KEY)
    return registry.get_all_method_names(entry_point, protocol, sort_methods=True)


@rpc_method(name="system.methodSignature")
def __system_method_signature(method_name, **kwargs):
    """
    Returns an array describing the signature of the given method name.

    The result is an array with:
     - Return type as first elements
     - Types of method arguments from element 1 to N
    :param method_name: Name of a method available for current entry point (and protocol)
    :param kwargs:
    :return: An array of arrays describing types of return values and method arguments
    """
    entry_point: str = kwargs.get(ENTRY_POINT_KEY)
    protocol: Protocol = kwargs.get(PROTOCOL_KEY)

    method = registry.get_method(method_name, entry_point, protocol)
    if method is None:
        raise RPCInvalidParams(
            f"Unknown method {method_name}. Unable to retrieve signature."
        )

    # See http://xmlrpc-c.sourceforge.net/introspection.html
    undefined = "undef"
    return_type = method.return_doc.get("type") or undefined
    args_types = [
        arg_doc.get("type") or undefined for arg_doc in method.args_doc.values()
    ]

    return [[return_type, *args_types]]


@rpc_method(name="system.methodHelp")
def __system_method_help(method_name, **kwargs):
    """
    Returns the documentation of the given method name.

    :param method_name: Name of a method available for current entry point (and protocol)
    :param kwargs:
    :return: Documentation text for the RPC method
    """
    entry_point: str = kwargs.get(ENTRY_POINT_KEY)
    protocol: Protocol = kwargs.get(PROTOCOL_KEY)

    method = registry.get_method(method_name, entry_point, protocol)
    if method is None:
        raise RPCInvalidParams(
            f"Unknown method {method_name}. Unable to retrieve its documentation."
        )
    return method.html_doc


@rpc_method(name="system.multicall", protocol=Protocol.XML_RPC)
def __system_multi_call(calls, **kwargs):
    """
    Call multiple RPC methods at once.

    :param calls: An array of struct like {"methodName": string, "params": array }
    :param kwargs: Internal data
    :return:
    """
    if not isinstance(calls, list):
        raise RPCInvalidParams(
            f"system.multicall first argument should be a list, {type(calls).__name__} given."
        )

    context = RPCRequestContext(
        request=kwargs[REQUEST_KEY],
        handler=kwargs[HANDLER_KEY],
        protocol=kwargs[PROTOCOL_KEY],
        entry_point=kwargs[ENTRY_POINT_KEY],
    )
    handler: XMLRPCHandler = context.handler

    results = []
    for call in calls:
        method_name = call.get("methodName")
        params = call.get("params")

        result = handler.process_single_request((method_name, params), context)
        results.append(result.serializable_data())

    return results
