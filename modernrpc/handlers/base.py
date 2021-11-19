# coding: utf-8
import logging
from abc import ABC, abstractmethod

from modernrpc.core import RpcResult, registry, REQUEST_KEY, ENTRY_POINT_KEY, PROTOCOL_KEY, HANDLER_KEY
from modernrpc.exceptions import (
    RPCException,
    RPC_METHOD_NOT_FOUND,
    RPC_INTERNAL_ERROR,
    RPC_INVALID_PARAMS
)

logger = logging.getLogger(__name__)


class RPCHandler(ABC):
    protocol = None

    def __init__(self, entry_point):
        self.entry_point = entry_point

    @staticmethod
    @abstractmethod
    def valid_content_types():
        """Return the list of content-types supported by the concrete handler"""

    def can_handle(self, request):
        return request.content_type.lower() in self.valid_content_types()

    @abstractmethod
    def parse_request(self, request_body):
        """Parse given request body and build a RPC request wrapper"""

    @abstractmethod
    def validate_request(self, rpc_request):
        """Check current request to ensure it is valid regarding protocol specifications

        Default implementation does nothing
        :rpc_request: The request to validate
        :type rpc_request: RPCRequest
        """

    def process_request(self, request, rpc_request):
        """
        :param request:
        :type rpc_request: HttpRequest
        :param rpc_request:
        :type rpc_request: RpcRequest
        :return:
        :rtype: RpcResult
        """
        rpc_result = RpcResult(rpc_request.request_id)
        try:
            self.validate_request(rpc_request)
        except RPCException as exc:
            rpc_result.set_error(exc.code, exc.message)
            return rpc_result

        _method = registry.get_method(rpc_request.method_name, self.entry_point, self.protocol)
        if not _method:
            rpc_result.set_error(RPC_METHOD_NOT_FOUND, 'Method not found: "{}"'.format(rpc_request.method_name))
            return rpc_result

        if not _method.check_permissions(request):
            rpc_result.set_error(
                RPC_INTERNAL_ERROR, 'Authentication failed when calling "{}"'.format(rpc_request.method_name)
            )
            return rpc_result

        args, kwargs = rpc_request.args, rpc_request.kwargs
        # If the RPC method needs to access some configuration, update kwargs dict
        if _method.accept_kwargs:
            kwargs.update({
                REQUEST_KEY: request,
                ENTRY_POINT_KEY: self.entry_point,
                PROTOCOL_KEY: self.protocol,
                HANDLER_KEY: self,
            })

        logger.debug('Params: args = %s - kwargs = %s', args, kwargs)

        try:
            # Call the rpc method, as standard python function
            rpc_result.set_success(_method.function(*args, **kwargs))

        except TypeError as exc:
            # If given params cannot be transmitted properly to python function
            rpc_result.set_error(RPC_INVALID_PARAMS, "Invalid parameters: {}".format(exc))

        except RPCException as exc:
            rpc_result.set_error(exc.code, exc.message, data=exc.data)

        except Exception as exc:
            rpc_result.set_error(RPC_INTERNAL_ERROR, "Internal error: {}".format(exc))

        return rpc_result

    @abstractmethod
    def build_response_data(self, result):
        """
        :param result:
        :type result: modernrpc.core.RpcResult
        :return:
        """
