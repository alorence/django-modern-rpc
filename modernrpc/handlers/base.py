# coding: utf-8
import logging

from modernrpc.exceptions import RPCInvalidRequest

logger = logging.getLogger(__name__)


class RPCHandler(object):

    protocol = None

    def __init__(self, request, entry_point):
        self.request = request
        self.entry_point = entry_point

    def loads(self, data):
        raise NotImplementedError("You must override loads()")

    def dumps(self, obj):
        raise NotImplementedError("You must override dumps()")

    @staticmethod
    def valid_content_types():
        raise NotImplementedError("You must override valid_content_types()")

    def can_handle(self):
        # Get the content-type header from incoming request. Method differs depending on current Django version
        try:
            # Django 1.10
            content_type = self.request.content_type
        except AttributeError:
            # Django up to 1.9
            content_type = self.request.META['CONTENT_TYPE']

        if not content_type:
            # We don't accept a request with missing Content-Type request
            raise RPCInvalidRequest('Missing header: Content-Type')

        result = content_type.lower() in self.valid_content_types()
        logger.debug('Check if handler for {} can parse_request the request: {}'.format(self.protocol, result))
        return result

    def parse_request(self):
        raise NotImplementedError("You must override parse_request()")

    def result_success(self, data):
        raise NotImplementedError("You must override result_success()")

    def result_error(self, exception):
        raise NotImplementedError("You must override result_error()")
