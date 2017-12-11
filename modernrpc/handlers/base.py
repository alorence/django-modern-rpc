# coding: utf-8
from django.utils import six

import modernrpc.compat
from modernrpc.core import registry, REQUEST_KEY, ENTRY_POINT_KEY, PROTOCOL_KEY, HANDLER_KEY
from modernrpc.exceptions import RPCInvalidRequest, RPCUnknownMethod, AuthenticationFailed, RPCInvalidParams
from modernrpc.utils import get_modernrpc_logger

logger = get_modernrpc_logger(__name__)


class RPCHandler(object):

    protocol = None

    def __init__(self, request, entry_point):
        self.request = request
        self.entry_point = entry_point

    def loads(self, str_data):
        """Convert serialized string data to valid Python data, depending on current handler protocol"""
        raise NotImplementedError("You must override loads()")

    def dumps(self, obj):
        """Convert Python data to serialized form, according to current handler protocol."""
        raise NotImplementedError("You must override dumps()")

    @staticmethod
    def valid_content_types():
        raise NotImplementedError("You must override valid_content_types()")

    def can_handle(self):
        # Get the content-type header from incoming request. Method differs depending on current Django version
        try:
            # Django >= 1.10
            content_type = self.request.content_type
        except AttributeError:
            # Django up to 1.9
            content_type = self.request.META['CONTENT_TYPE']

        if not content_type:
            # We don't accept a request with missing Content-Type request
            raise RPCInvalidRequest('Missing header: Content-Type')

        return content_type.lower() in self.valid_content_types()

    def process_request(self):
        """
        Parse self.request to extract payload. Parse it to retrieve RPC call information, and
        execute the corresponding RPC Method. At any time, raise an exception when detecting error.
        :return: The result of RPC Method execution
        """
        raise NotImplementedError("You must override process_request()")

    def result_success(self, data):
        """Return a HttpResponse instance containing the result payload for the given data"""
        raise NotImplementedError("You must override result_success()")

    def result_error(self, exception, http_response_cls=None):
        """Return a HttpResponse instance containing the result payload for the given exception"""
        raise NotImplementedError("You must override result_error()")

    def execute_procedure(self, name, args=None, kwargs=None):
        """
        Call the concrete python function corresponding to given RPC Method `name` and return the result.

        Raise RPCUnknownMethod, AuthenticationFailed, RPCInvalidParams or any Exception sub-class.
        """

        _method = registry.get_method(name, self.entry_point, self.protocol)

        if not _method:
            raise RPCUnknownMethod(name)

        logger.debug('Check authentication / permissions for method {} and user {}'
                     .format(name, self.request.user))

        if not _method.check_permissions(self.request):
            raise AuthenticationFailed(name)

        logger.debug('RPC method {} will be executed'.format(name))

        # Replace default None value with empty instance of corresponding type
        args = args or []
        kwargs = kwargs or {}

        # If the RPC method needs to access some internals, update kwargs dict
        if _method.accept_kwargs:
            kwargs.update({
                REQUEST_KEY: self.request,
                ENTRY_POINT_KEY: self.entry_point,
                PROTOCOL_KEY: self.protocol,
                HANDLER_KEY: self,
            })

        if six.PY2:
            method_std, encoding = _method.str_standardization, _method.str_std_encoding
            args = modernrpc.compat.standardize_strings(args, strtype=method_std, encoding=encoding)
            kwargs = modernrpc.compat.standardize_strings(kwargs, strtype=method_std, encoding=encoding)

        logger.debug('Params: args = {} - kwargs = {}'.format(args, kwargs))

        try:
            # Call the rpc method, as standard python function
            return _method.function(*args, **kwargs)

        except TypeError as e:
            # If given arguments cannot be transmitted properly to python function,
            # raise an Invalid Params exceptions
            raise RPCInvalidParams(str(e))
