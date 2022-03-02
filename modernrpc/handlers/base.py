# coding: utf-8
import logging
from abc import ABC, abstractmethod
from typing import Any, List

from django.http import HttpRequest

from modernrpc.core import (
    registry,
    Protocol,
    RPCRequestContext,
)
from modernrpc.exceptions import (
    RPCUnknownMethod,
    RPCInvalidRequest,
)

logger = logging.getLogger(__name__)


class BaseResult(ABC):
    @abstractmethod
    def format(self):
        """Dumps response content into the right format. Protocol specific implementations of this method must be
        written."""


class SuccessResult(BaseResult, ABC):
    def __init__(self, data: Any):
        self.data = data


class ErrorResult(BaseResult, ABC):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message


class RPCHandler(ABC):
    protocol = None  # type: Protocol

    def __init__(self, entry_point):
        self.entry_point = entry_point

    @staticmethod
    @abstractmethod
    def valid_content_types() -> List[str]:
        """Return the list of content-types supported by the concrete handler"""

    def can_handle(self, request: HttpRequest):
        """
        Return True if this instance can handle the given request.

        Default implementation will check Content-Type for supported value
        """
        return (
            getattr(request, "content_type", "").lower() in self.valid_content_types()
        )

    def _get_called_method(self, name):
        if not name:
            raise RPCInvalidRequest(
                "Missing methodName. Please provide the name of the procedure you want to call"
            )

        _method = registry.get_method(name, self.entry_point, self.protocol)
        if not _method:
            raise RPCUnknownMethod(name)

        return _method

    def process_request(self, request_body: str, context: RPCRequestContext) -> str:
        """
        Process a single request. Return the str content redy to be sent as HttpResponse

        Implementations of this method must ensure no exception is raised from here. All code must be securized
        to return a proper RPC error response on any exception.
        """

    @abstractmethod
    def parse_request(self, request_body: str) -> Any:
        ...

    @abstractmethod
    def process_single_request(
        self, request_data: Any, context: RPCRequestContext
    ) -> BaseResult:
        ...

    @abstractmethod
    def dumps_result(self, result: BaseResult) -> str:
        ...
