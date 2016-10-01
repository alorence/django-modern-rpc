# coding: utf-8
import logging

from modernrpc.core import get_method
from modernrpc.exceptions import RPCUnknownMethod, RPCInvalidRequest

logger = logging.getLogger(__name__)


class RPCHandler(object):

    def __init__(self, entry_point, rpc_type):
        self.rpc_type = rpc_type
        self.entry_point = entry_point

    def loads(self, data):
        raise NotImplementedError("You must override loads()")

    def dumps(self, obj):
        raise NotImplementedError("You must override dumps()")

    def get_method(self, method_name):
        return get_method(method_name, self.entry_point, self.rpc_type)

    def call_method(self, method_name, params):
        method = self.get_method(method_name)
        if not method:
            raise RPCUnknownMethod(method_name)

        return method(*params)

    @staticmethod
    def valid_content_types():
        raise NotImplementedError("You must override valid_content_types()")

    def can_handle(self, request):
        try:
            # Django 1.10
            content_type = request.content_type
        except AttributeError:
            # Django up to 1.9
            content_type = request.META['CONTENT_TYPE']

        if not content_type:
            raise RPCInvalidRequest('Missing header: Content-Type')

        result = content_type.lower() in self.valid_content_types()
        logger.debug('Check if handler for {} can handle the request: {}'.format(self.rpc_type, result))
        return result

    def handle(self, request):
        raise NotImplementedError("You must override handle()")
