# coding: utf-8
import logging

from modernrpc.exceptions import (RPCInvalidRequest)

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

    def format_success_data(self, data, **kwargs):
        raise NotImplementedError()

    def format_error_data(self, code, message, **kwargs):
        raise NotImplementedError()

    def build_full_result(self, response_content, **kwargs):
        raise NotImplementedError()

