from __future__ import annotations

from modernrpc import Protocol, RpcNamespace, RpcRequestContext
from modernrpc.exceptions import RPCInvalidParams
from modernrpc.handlers.base import GenericRpcErrorResult, XmlRpcRequest

system = RpcNamespace()


@system.register_procedure(name="listMethods", context_target="_ctx")
def __system_list_methods(_ctx: RpcRequestContext):
    """Returns a list of all methods available in the current entry point"""
    server = _ctx.server
    return list(server.procedures.keys())


@system.register_procedure(name="methodSignature", context_target="_ctx")
def __system_method_signature(method_name: str, _ctx: RpcRequestContext):
    """
    Returns an array describing the signature of the given method name.

    The result is an array with:
     - Return type as first elements
     - Types of method arguments from element 1 to N
    :param method_name: Name of a method available for current entry point (and protocol)
    :param _ctx: Request context for this call
    :return: An array of arrays describing types of return values and method arguments
    """
    server = _ctx.server
    wrapper = server.get_procedure(method_name, _ctx.protocol)
    # See http://xmlrpc-c.sourceforge.net/introspection.html
    undefined = "undef"
    return_type = wrapper.return_doc.get("type") or undefined
    args_types = [arg_doc.get("type") or undefined for arg_doc in wrapper.args_doc.values()]

    return [[return_type, *args_types]]


@system.register_procedure(name="methodHelp", context_target="_ctx")
def __system_method_help(method_name: str, _ctx: RpcRequestContext):
    """
    Returns the documentation of the given method name.

    :param method_name: Name of a method available for current entry point (and protocol)
    :param _ctx: Request context for this call
    :return: Documentation text for the RPC method
    """
    server = _ctx.server
    method = server.get_procedure(method_name, _ctx.protocol)
    return method.raw_docstring


@system.register_procedure(name="multicall", protocol=Protocol.XML_RPC, context_target="_ctx")
def __system_multi_call(calls: list, _ctx: RpcRequestContext):
    """
    Call multiple RPC methods at once.

    :param calls: An array of struct like {"methodName": string, "params": array }
    :param _ctx: Request context for this call
    :return:
    """
    if not isinstance(calls, list):
        raise RPCInvalidParams(f"system.multicall first argument should be a list, {type(calls).__name__} given.")

    def result_to_serializable_data(result):
        if isinstance(result, GenericRpcErrorResult):
            return {
                "faultCode": result.code,
                "faultString": result.message,
            }
        return (result.data,)

    requests = [XmlRpcRequest(call.get("methodName"), call.get("params")) for call in calls]

    results = [_ctx.handler.process_single_request(request, _ctx) for request in requests]

    return [result_to_serializable_data(result) for result in results]
