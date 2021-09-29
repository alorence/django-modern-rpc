# coding: utf-8
import logging

import six

import modernrpc.compat
from modernrpc.core import RpcResult, registry, REQUEST_KEY, ENTRY_POINT_KEY, PROTOCOL_KEY, HANDLER_KEY
from modernrpc.exceptions import (
    RPCInvalidRequest,
    RPCException,
    RPC_METHOD_NOT_FOUND,
    RPC_INTERNAL_ERROR,
    RPC_INVALID_PARAMS
)

logger = logging.getLogger(__name__)


class RPCHandler(object):
    protocol = None

    def __init__(self, entry_point):
        self.entry_point = entry_point

    @staticmethod
    def valid_content_types():
        raise NotImplementedError("You must override valid_content_types()")

    def can_handle(self, request):
        if not request.content_type:
            # We don't accept a request with missing Content-Type request
            raise RPCInvalidRequest('Missing header: Content-Type')

        return request.content_type.lower() in self.valid_content_types()

    def parse_request(self, request_body):
        """Parse given request body and build a RPC request wrapper"""
        raise NotImplementedError()

    def validate_request(self, rpc_request):
        """Check current request to ensure it is valid regarding protocol specifications

        Default implementation does nothing
        :rpc_request: The request to validate
        :type rpc_request: RPCRequest
        """
        pass

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

        if six.PY2:
            method_std, encoding = _method.str_standardization, _method.str_std_encoding
            args = modernrpc.compat.standardize_strings(args, strtype=method_std, encoding=encoding)
            kwargs = modernrpc.compat.standardize_strings(kwargs, strtype=method_std, encoding=encoding)

        logger.debug('Params: args = %s - kwargs = %s', args, kwargs)

        try:
            # Call the rpc method, as standard python function
            rpc_result.set_success(_method.function(*args, **kwargs))

        except TypeError as te:
            # If given arguments cannot be transmitted properly to python function,
            # raise an Invalid Params exceptions
            # raise RPCInvalidParams(str(te))
            rpc_result.set_error(RPC_INVALID_PARAMS, "Invalid parameters: {}".format(te))

        except RPCException as re:
            rpc_result.set_error(re.code, re.message, data=re.data)

        except Exception as exc:
            # If given arguments cannot be transmitted properly to python function,
            # raise an Invalid Params exceptions
            # raise RPCInternalError(str(exc))
            rpc_result.set_error(RPC_INTERNAL_ERROR, "Internal error: {}".format(exc))

        return rpc_result

    def build_response_data(self, result):
        """
        :param result:
        :type result: modernrpc.core.RpcResult
        :return:
        """
        raise NotImplementedError()
