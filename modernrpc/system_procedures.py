import asyncio
from collections.abc import Iterable
from typing import Any, TypeAlias

from modernrpc import Protocol, RpcNamespace, RpcRequestContext
from modernrpc.config import settings
from modernrpc.exceptions import RPC_INVALID_REQUEST, RPCInvalidParams
from modernrpc.types import RpcErrorResult, RpcRequest, RpcSuccessResult
from modernrpc.xmlrpc.handler import XmlRpcRequest

system = RpcNamespace()

MULTICALL_NAME = "system.multicall"
RECURSIVE_MULTICALL_ERROR = "Invalid request: recursive system.multicall forbidden"

MulticallResult: TypeAlias = RpcSuccessResult[RpcRequest] | RpcErrorResult[RpcRequest]


@system.register_procedure(name="listMethods", context_target="_ctx")
def __system_list_methods(_ctx: RpcRequestContext):
    """Returns a list of all procedures exposed by the server"""
    server = _ctx.server
    return list(server.procedures.keys())


@system.register_procedure(name="methodSignature", context_target="_ctx")
def __system_method_signature(method_name: str, _ctx: RpcRequestContext):
    """
    Returns an array describing the possible signatures for the given procedure.

    Currently, this procedure only returns one possible signature, so the result is a list of 1 list.

    The inner list contains:

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
    return_type = wrapper.returns.documented_type or undefined
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


def _check_multicall_args(calls: Any, ctx: RpcRequestContext) -> list[XmlRpcRequest]:
    """Validate system.multicall argument and build the list of requests to process."""
    if not isinstance(calls, list):
        raise RPCInvalidParams(f"system.multicall first argument should be a list, {type(calls).__name__} given.")
    ctx.server.check_batch_size(len(calls))
    return [XmlRpcRequest(call.get("methodName"), call.get("params") or []) for call in calls]


def _recursive_multicall_error(request: RpcRequest) -> MulticallResult:
    return RpcErrorResult(request=request, code=RPC_INVALID_REQUEST, message=RECURSIVE_MULTICALL_ERROR)


def _format_multicall_results(results: Iterable[MulticallResult]) -> list[Any]:
    return [
        {"faultCode": result.code, "faultString": result.message}
        if isinstance(result, RpcErrorResult)
        else (result.data,)
        for result in results
    ]


if settings.MODERNRPC_XMLRPC_ASYNC_MULTICALL:

    @system.register_procedure(name="multicall", protocol=Protocol.XML_RPC, context_target="_ctx")
    async def __system_multicall(calls: list[Any], _ctx: RpcRequestContext):
        """
        Call multiple procedure at once, using asyncio.gather().

        :param calls: An array of struct like {"methodName": string, "params": [..., ...]}
        :param _ctx: Request context for this call
        :return: An array containing the result of each procedure call
        """
        requests = _check_multicall_args(calls, _ctx)

        async def process(request: XmlRpcRequest) -> MulticallResult:
            if request.method_name == MULTICALL_NAME:
                return _recursive_multicall_error(request)
            return await _ctx.handler.aprocess_single_request(request, _ctx)

        results = await asyncio.gather(*(process(request) for request in requests))
        return _format_multicall_results(results)
else:

    @system.register_procedure(name="multicall", protocol=Protocol.XML_RPC, context_target="_ctx")
    def __system_multicall(calls: list[Any], _ctx: RpcRequestContext):
        """
        Call multiple procedure at once.

        :param calls: An array of struct like {"methodName": string, "params": [..., ...]}
        :param _ctx: Request context for this call
        :return: An array containing the result of each procedure call
        """
        requests = _check_multicall_args(calls, _ctx)
        results = (
            _recursive_multicall_error(request)
            if request.method_name == MULTICALL_NAME
            else _ctx.handler.process_single_request(request, _ctx)
            for request in requests
        )
        return _format_multicall_results(results)
