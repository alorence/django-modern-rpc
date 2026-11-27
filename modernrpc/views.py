import logging
from http import HTTPStatus
from typing import TYPE_CHECKING

from django.http import HttpRequest
from django.http.response import HttpResponse

from modernrpc.core import RpcRequestContext
from modernrpc.exceptions import RPCParseError

if TYPE_CHECKING:
    from modernrpc.server import RpcServer

logger = logging.getLogger(__name__)


def handle_rpc_request(request: HttpRequest, server: "RpcServer") -> HttpResponse:
    """
    Synchronous view function to handle RPC requests.

    :param request: The HTTP request object
    :param server: The RPC server instance
    :return: An HTTP response object
    """
    if response := server.check_request(request):
        return response

    if not (handler := server.get_request_handler(request)):
        return HttpResponse(
            f"Unable to handle your request, unsupported Content-Type {request.content_type}.",
            status=HTTPStatus.BAD_REQUEST,
            content_type="text/plain",
        )

    context = RpcRequestContext(request, server, handler, handler.protocol)
    try:
        request_body = server.decode_request_body(request)

    except RPCParseError as exc:
        result_data = handler.serialize_exception_result(exc, context)

    else:
        result_data = handler.process_request(request_body, context)

    return handler.build_http_response(result_data)


async def handle_rpc_request_async(request: HttpRequest, server: "RpcServer") -> HttpResponse:
    """
    Asynchronous view function to handle RPC requests.

    :param request: The HTTP request object
    :param server: The RPC server instance
    :return: An HTTP response object
    """
    if response := server.check_request(request):
        return response

    if not (handler := server.get_request_handler(request)):
        return HttpResponse(
            f"Unable to handle your request, unsupported Content-Type {request.content_type}.",
            status=HTTPStatus.BAD_REQUEST,
            content_type="text/plain",
        )

    context = RpcRequestContext(request, server, handler, handler.protocol)
    try:
        request_body = server.decode_request_body(request)

    except RPCParseError as exc:
        result_data = handler.serialize_exception_result(exc, context)

    else:
        result_data = await handler.aprocess_request(request_body, context)

    return handler.build_http_response(result_data)
