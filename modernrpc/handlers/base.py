# coding: utf-8
import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, List

from django.http import HttpRequest

from modernrpc.core import (
    registry,
    Protocol,
    RPCRequestContext,
)
from modernrpc.exceptions import (
    RPCMethodNotFound,
)

if TYPE_CHECKING:
    from modernrpc.core import RPCMethod

RequestData = Any

logger = logging.getLogger(__name__)


# Note: dataclasses may be used here as soon as Python 3.5 support will be dropped
class BaseResult(ABC):
    """
    Base class for results returned from procedure execution

    Subclass must be created for Error / Success result semantic, as well as for protocol-specific features
    """

    @abstractmethod
    def format(self):
        """Dumps response content into the right format. Protocol specific
        implementations of this method must be written."""


class SuccessResult(BaseResult, ABC):
    """Base success result wrapper"""

    def __init__(self, data: Any):
        self.data = data


class ErrorResult(BaseResult, ABC):
    """Base error result wrapper"""

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message


class RPCHandler(ABC):
    """Base class for concrete RPC Handlers. Provide an interface as well as some common methods implementations."""

    protocol = None  # type: Protocol

    def __init__(self, entry_point):
        self.entry_point = entry_point

    def get_method_wrapper(self, name: str) -> "RPCMethod":
        """
        Return RPCMethod instance corresponding to given name, from the registry

        An exception is raised on any error

        :raise: RPCUnknownMethod
        """
        _method = registry.get_method(name, self.entry_point, self.protocol)
        if not _method:
            raise RPCMethodNotFound(name)

        return _method

    @staticmethod
    @abstractmethod
    def valid_content_types() -> List[str]:
        """Return the list of content-types supported by the concrete handler"""

    @staticmethod
    @abstractmethod
    def response_content_type() -> str:
        """Return the Content-Type value to set in responses"""

    def can_handle(self, request: HttpRequest) -> bool:
        """
        Return True if this instance can handle the given request.

        Default implementation will check Content-Type for supported value
        """
        return (
            getattr(request, "content_type", "").lower() in self.valid_content_types()
        )

    @abstractmethod
    def process_request(self, request_body: str, context: RPCRequestContext) -> str:
        """
        Fully process a request. Return the str content ready to be sent as HttpResponse.

        This is the only method the view is supposed to call after choosing the right handler.
        Concrete implementation must perform all work here, according to its protocol specifications.

        Important: This method should delegate concrete procedure execution to process_single_request(). This will
        help to implement multi-request (JSON-RPC batch / XML-RPC system.multicall) features.

        Implementations of this method must ensure no exception is raised from here. All code must be secured
        to return a proper RPC error response on any exception.
        """

    @abstractmethod
    def parse_request(self, request_body: str) -> RequestData:
        """
        Parse the body of incoming request and extract data needed for execution.

        The return-type of this method depends on concrete implementation.

        Must raises RPCException or subclasses on errors
        """

    @abstractmethod
    def process_single_request(
        self, request_data: RequestData, context: RPCRequestContext
    ) -> BaseResult:
        """
        Perform all mandatory task before executing a single procedure.

        Check request format, retrieve RPCMethod wrapper, call the corresponding function and return the resulting data.
        All errors must be caught internally, concrete implementations must not raise exception from this method.

        :param request_data: Request information, as returned by parse_request() method
        :param context: Information needed to execution procedure
        :return: A result instance (Error or Success)
        """

    @abstractmethod
    def dumps_result(self, result: BaseResult) -> str:
        """
        Serialize the result instance (Error or Success) into a string ready to be returned to HTTP response.

        All errors must be caught internally and converted to proper error response. Concrete implementations must
        not raise exception from this method.
        """
