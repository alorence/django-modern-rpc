from __future__ import annotations

import logging
from http import HTTPStatus
from typing import TYPE_CHECKING

from django.http.response import HttpResponse

from modernrpc.conf import settings
from modernrpc.core import RpcRequestContext

if TYPE_CHECKING:
    from django.http import HttpRequest

    from modernrpc.server import RpcServer


logger = logging.getLogger(__name__)


def handle_rpc_request(
    request: HttpRequest, server: RpcServer, default_encoding: str = settings.MODERNRPC_DEFAULT_ENCODING
) -> HttpResponse:
    if not request.content_type:
        return HttpResponse(
            "Unable to handle your request, the Content-Type header is mandatory to allow server "
            "to determine which handler can interpret your request.",
            status=HTTPStatus.BAD_REQUEST,
            content_type="text/plain",
        )

    handler = server.get_handler(request)
    if not handler:
        return HttpResponse(
            f"Unable to handle your request, unsupported Content-Type {request.content_type}.",
            status=HTTPStatus.BAD_REQUEST,
            content_type=request.content_type,
        )

    request_body = request.body.decode(request.encoding or default_encoding)
    context = RpcRequestContext(request, server, handler, handler.protocol)

    result_data = handler.process_request(request_body, context)

    if isinstance(result_data, tuple) and len(result_data) == 2:
        status, result_data = result_data
    else:
        status = HTTPStatus.OK

    return HttpResponse(result_data, status=status, content_type=handler.response_content_type)
