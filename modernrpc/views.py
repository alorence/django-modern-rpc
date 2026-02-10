from __future__ import annotations

import logging
from http import HTTPStatus
from typing import TYPE_CHECKING

from django.http.response import HttpResponse

from modernrpc.core import RpcRequestContext

if TYPE_CHECKING:
    from django.http import HttpRequest

    from modernrpc.server import RpcServer


logger = logging.getLogger(__name__)


def handle_rpc_request(request: HttpRequest, server: RpcServer) -> HttpResponse:
    """
    Synchronous view function to handle RPC requests.

    :param request: The HTTP request object
    :param server: The RPC server instance
    :return: An HTTP response object
    """
    response = server.check_request(request)
    if response:
        return response

    handler = server.get_request_handler(request)
    if not handler:
        return HttpResponse(
            f"Unable to handle your request, unsupported Content-Type {request.content_type}.",
            status=HTTPStatus.BAD_REQUEST,
            content_type="text/plain",
        )

    result_data = handler.process_request(
        request.body.decode(request.encoding or server.default_encoding),
        RpcRequestContext(request, server, handler, handler.protocol),
    )

    return server.build_response(handler, result_data)


async def handle_rpc_request_async(request: HttpRequest, server: RpcServer) -> HttpResponse:
    """
    Asynchronous view function to handle RPC requests.

    :param request: The HTTP request object
    :param server: The RPC server instance
    :return: An HTTP response object
    """
    response = server.check_request(request)
    if response:
        return response

    handler = server.get_request_handler(request)
    if not handler:
        return HttpResponse(
            f"Unable to handle your request, unsupported Content-Type {request.content_type}.",
            status=HTTPStatus.BAD_REQUEST,
            content_type="text/plain",
        )

    result_data = await handler.aprocess_request(
        request.body.decode(request.encoding or server.default_encoding),
        RpcRequestContext(request, server, handler, handler.protocol),
    )

    return server.build_response(handler, result_data)
