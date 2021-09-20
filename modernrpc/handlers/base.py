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

    def parse_request(self, data):
        """Parse given request data and build a RPC payload"""
        raise NotImplementedError()

    def build_full_result(self, response_content, **kwargs):
        raise NotImplementedError()

    def build_result_success(self, data, **kwargs):
        raise NotImplementedError()

    def build_result_error(self, code, message, **kwargs):
        raise NotImplementedError()
