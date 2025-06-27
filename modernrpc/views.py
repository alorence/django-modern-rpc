from __future__ import annotations

import logging
from http import HTTPStatus
from typing import TYPE_CHECKING

from django.http.response import HttpResponse

from modernrpc.config import settings
from modernrpc.core import RpcRequestContext

if TYPE_CHECKING:
    from django.http import HttpRequest

    from modernrpc.server import RpcServer


logger = logging.getLogger(__name__)


def handle_rpc_request(
    request: HttpRequest, server: RpcServer, default_encoding: str = settings.MODERNRPC_DEFAULT_ENCODING
) -> HttpResponse:
    """
    Synchronous view function to handle RPC requests.

    :param request: The HTTP request object
    :param server: The RPC server instance
    :param default_encoding: The default encoding to use for request body
    :return: An HTTP response object
    """
    if not request.content_type:
        return HttpResponse(
            "Unable to handle your request, the Content-Type header is mandatory to allow server "
            "to determine which handler can interpret your request.",
            status=HTTPStatus.BAD_REQUEST,
            content_type="text/plain",
        )

    handler = server.get_request_handler(request)
    if not handler:
        return HttpResponse(
            f"Unable to handle your request, unsupported Content-Type {request.content_type}.",
            status=HTTPStatus.BAD_REQUEST,
            content_type=request.content_type,
        )

    context = RpcRequestContext(request, server, handler, handler.protocol)
    request_body = request.body.decode(request.encoding or default_encoding)
    result_data = handler.process_request(request_body, context)

    if isinstance(result_data, tuple) and len(result_data) == 2:
        status, result_data = result_data
    else:
        status = HTTPStatus.OK

    return HttpResponse(result_data, status=status, content_type=handler.response_content_type)


async def handle_rpc_request_async(
    request: HttpRequest, server: RpcServer, default_encoding: str = settings.MODERNRPC_DEFAULT_ENCODING
) -> HttpResponse:
    """
    Asynchronous view function to handle RPC requests.

    :param request: The HTTP request object
    :param server: The RPC server instance
    :param default_encoding: The default encoding to use for request body
    :return: An HTTP response object
    """
    if not request.content_type:
        return HttpResponse(
            "Unable to handle your request, the Content-Type header is mandatory to allow server "
            "to determine which handler can interpret your request.",
            status=HTTPStatus.BAD_REQUEST,
            content_type="text/plain",
        )

    handler = server.get_request_handler(request)

    if not handler:
        return HttpResponse(
            f"Unable to handle your request, unsupported Content-Type {request.content_type}.",
            status=HTTPStatus.BAD_REQUEST,
            content_type=request.content_type,
        )

    context = RpcRequestContext(request, server, handler, handler.protocol)
    request_body = request.body.decode(request.encoding or default_encoding)
    result_data = await handler.aprocess_request(request_body, context)

    if isinstance(result_data, tuple) and len(result_data) == 2:
        status, result_data = result_data
    else:
        status = HTTPStatus.OK

    return HttpResponse(result_data, status=status, content_type=handler.response_content_type)
