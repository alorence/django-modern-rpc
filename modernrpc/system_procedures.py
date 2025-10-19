from __future__ import annotations

import asyncio

from modernrpc import Protocol, RpcNamespace, RpcRequestContext
from modernrpc.config import settings
from modernrpc.exceptions import RPCInvalidParams
from modernrpc.types import RpcErrorResult
from modernrpc.xmlrpc.handler import XmlRpcRequest

system = RpcNamespace()


@system.register_procedure(name="listMethods", context_target="_ctx")
def __system_list_methods(_ctx: RpcRequestContext):
    """Returns a list of all procedures exposed by the server"""
    server = _ctx.server
    return list(server.procedures.keys())


@system.register_procedure(name="methodSignature", context_target="_ctx")
def __system_method_signature(method_name: str, _ctx: RpcRequestContext):
    """
    Returns an array describing the signature of the given procedure.

    The result is a list with:

     - Return type as first element
     - Types of arguments from element 1 to N

    :param method_name: Name of the procedure
    :param _ctx: Request context for this call
    :return: An array of arrays describing types of return values and method arguments
    """
    server = _ctx.server
    wrapper = server.get_procedure_wrapper(method_name, _ctx.protocol)
    # See http://xmlrpc-c.sourceforge.net/introspection.html
    undefined = "undef"
    return_type = ", ".join(wrapper.returns.documented_type) if wrapper.returns.documented_type else undefined
    args_types = [arg.documented_type or undefined for arg in wrapper.arguments.values()]

    return [[return_type, *args_types]]


@system.register_procedure(name="methodHelp", context_target="_ctx")
def __system_method_help(method_name: str, _ctx: RpcRequestContext):
    """
    Returns the documentation of the given procedure.

    :param method_name: Name of the procedure
    :param _ctx: Request context for this call
    :return: Documentation text for the procedure
    """
    server = _ctx.server
    method = server.get_procedure_wrapper(method_name, _ctx.protocol)
    return method.text_doc


if settings.MODERNRPC_XMLRPC_ASYNC_MULTICALL:

    @system.register_procedure(name="multicall", protocol=Protocol.XML_RPC, context_target="_ctx")
    async def __system_multicall(calls: list, _ctx: RpcRequestContext):
        """
        Call multiple procedure at once, using asyncio.gather().

        :param calls: An array of struct like {"methodName": string, "params": [..., ...]}
        :param _ctx: Request context for this call
        :return: An array containing the result of each procedure call
        """
        if not isinstance(calls, list):
            raise RPCInvalidParams(f"system.multicall first argument should be a list, {type(calls).__name__} given.")

        requests = (XmlRpcRequest(call.get("methodName"), call.get("params")) for call in calls)
        results = await asyncio.gather(*(_ctx.handler.aprocess_single_request(request, _ctx) for request in requests))

        return [
            {"faultCode": result.code, "faultString": result.message}
            if isinstance(result, RpcErrorResult)
            else (result.data,)
            for result in results
        ]
else:

    @system.register_procedure(name="multicall", protocol=Protocol.XML_RPC, context_target="_ctx")
    def __system_multicall(calls: list, _ctx: RpcRequestContext):
        """
        Call multiple procedure at once.

        :param calls: An array of struct like {"methodName": string, "params": [..., ...]}
        :param _ctx: Request context for this call
        :return: An array containing the result of each procedure call
        """
        if not isinstance(calls, list):
            raise RPCInvalidParams(f"system.multicall first argument should be a list, {type(calls).__name__} given.")

        requests = (XmlRpcRequest(call.get("methodName"), call.get("params")) for call in calls)
        results = (_ctx.handler.process_single_request(request, _ctx) for request in requests)

        return [
            {"faultCode": result.code, "faultString": result.message}
            if isinstance(result, RpcErrorResult)
            else (result.data,)
            for result in results
        ]
