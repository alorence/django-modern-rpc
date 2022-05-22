# coding: utf-8
import base64
import itertools
import json.decoder
import pyexpat
import xmlrpc.client
from abc import ABC, abstractmethod
from typing import Optional, Type

import jsonrpcclient.clients.http_client
import pytest
from jsonrpcclient.exceptions import ReceivedErrorResponseError
from jsonrpcclient.requests import Request, Notification


class JsonrpcErrorResponse(Exception):
    """A simple wrapper around Rpc error response"""

    def __init__(self, code, message, data=None):
        self.code = code
        self.message = message
        self.data = data


class AbstractRpcTestClient(ABC):
    """Base class RPC clients used to run tests"""

    error_response_exception = None  # type: Optional[Type[Exception]]
    invalid_response_exception = None  # type: Optional[Type[Exception]]
    auth_error_exception = None  # type: Optional[Type[Exception]]

    def __init__(self, url, **kwargs):
        self._url = url
        self._auth = kwargs.get("auth")

    @staticmethod
    def assert_exception_code(exception, error_code):
        """
        Check error response exception code to verify it the expected one

        :param exception: The exception instance
        :param error_code: Error code, as int
        """
        exc_code = getattr(exception, "code", None) or getattr(
            exception, "faultCode", None
        )
        assert exc_code == error_code

    def _get_headers(self):
        """Build headers specific to cliet configuration.

        Base implementation will only set Authorization header"""
        if not self._auth:
            return {}

        kind, *_ = self._auth
        if kind in ("basic", "basic_auth"):
            _, username, password = self._auth
            credz = "{}:{}".format(username, password)
            b64_credz = base64.standard_b64encode(credz.encode("utf-8")).decode("utf-8")
            return {"Authorization": "Basic {}".format(b64_credz)}
        raise ValueError("Unknown Authentication kind: {}".format(kind))

    @abstractmethod
    def call(self, method, args=None):
        """Perform a standard RPC call"""

    @abstractmethod
    def check_response_headers(self, headers):
        """Raise exception when invalid headers are detected in response"""


class AbstractJsonRpcTestClient(AbstractRpcTestClient):
    def __init__(self, url, **kwargs):
        super().__init__(url, **kwargs)
        self._content_type = kwargs.get("jsonrpc_content_type", "application/json")

    def _get_headers(self):
        headers = {"Content-Type": self._content_type}
        headers.update(super()._get_headers())
        return headers

    @abstractmethod
    def batch_request(self, calls_data):
        """Perform a JSON-RPC batch request"""
        pass

    def check_response_headers(self, headers):
        """Raise exception when invalid headers are detected in response"""
        response_ct = headers["Content-Type"]
        expected_ct = "application/json"
        if not response_ct.startswith(expected_ct):
            error_msg = (
                'Invalid Content-Type returned by server: "{}". Expected: "{}"'.format(
                    response_ct, expected_ct
                )
            )
            raise ValueError(error_msg)


class AbstractXmlRpcTestClient(AbstractRpcTestClient):
    @abstractmethod
    def multicall(self, calls_data):
        """Perform an XML-RPC multicall"""
        pass

    def check_response_headers(self, headers):
        """Raise exception when invalid headers are detected in response"""
        response_ct = headers["Content-Type"]
        expected_ct = "text/xml"
        if not response_ct.startswith(expected_ct):
            error_msg = (
                'Invalid Content-Type returned by server: "{}". Expected: "{}"'.format(
                    response_ct, expected_ct
                )
            )
            raise ValueError(error_msg)


class JsonrpcclientlibClient(AbstractJsonRpcTestClient):
    error_response_exception = JsonrpcErrorResponse
    invalid_response_exception = json.decoder.JSONDecodeError
    auth_error_exception = JsonrpcErrorResponse

    batch_result_klass = list

    def __init__(self, url, **kwargs):
        super().__init__(url, **kwargs)
        self._id_generator = itertools.count(0)
        self._client = jsonrpcclient.clients.http_client.HTTPClient(
            self._url, id_generator=self._id_generator
        )
        # self._client = jsonrpcclient.clients.http_client.HTTPClient(self._url)

    def call(self, method, *args, **kwargs):
        if "notify" in kwargs and kwargs.pop("notify"):
            req = Notification(method, *args, **kwargs)
        else:
            req = Request(method, *args, **kwargs)

        try:
            response = self._client.send(req, headers=self._get_headers())
        except ReceivedErrorResponseError as exc:
            raise JsonrpcErrorResponse(
                exc.response.code, exc.response.message, exc.response.data
            )

        self.check_response_headers(response.raw.headers)

        return response.data.result

    def batch_request(self, calls_data):
        batch = []
        for method, params, *extra_params in calls_data:
            if isinstance(params, list):
                args, kwargs = params, {}
            elif isinstance(params, dict):
                args, kwargs = [], params

            if "notify_only" in extra_params:
                batch.append(Notification(method, *args, **kwargs))
            else:
                batch.append(
                    Request(method, *args, **kwargs, id_generator=self._id_generator)
                )

        response = self._client.send(batch, headers=self._get_headers())

        self.check_response_headers(response.raw.headers)

        return None if not response.raw.content else response.raw.json()


class PythonXmlRpcClient(AbstractXmlRpcTestClient):
    error_response_exception = xmlrpc.client.Fault
    invalid_response_exception = pyexpat.ExpatError
    auth_error_exception = xmlrpc.client.Fault

    multicall_result_klass = xmlrpc.client.MultiCallIterator

    def __init__(self, url, **kwargs):
        super().__init__(url, **kwargs or {})
        self._use_builtin_types = kwargs.get("use_builtin_types", False)

        self._transport = xmlrpc.client.Transport(
            use_builtin_types=self._use_builtin_types
        )
        # Monkey-patch Transport.get_host_info() to ensure customized headers can be injected into XML-RPC requests
        self._transport.get_host_info = lambda host: (
            host,
            self._get_headers_list(),
            {},
        )
        self._client = xmlrpc.client.ServerProxy(self._url, transport=self._transport)

    def _get_headers_list(self):
        """Copy current headers' dict to a List[Tuple[str, str]] instance"""
        return [(key, value) for key, value in self._get_headers().items()]

    def call(self, method, *args):
        _rpc_method = getattr(self._client, method)
        return _rpc_method(*args)

    def multicall(self, calls_data):
        multicall = xmlrpc.client.MultiCall(self._client)
        for (
            method,
            args,
        ) in calls_data:
            getattr(multicall, method)(*args)
        result = multicall()
        return result


@pytest.fixture(scope="session")
def endpoint_path():
    """The path for default RPC endpoint. Can be overriden at module or class level"""
    return "/all-rpc/"


@pytest.fixture(scope="session")
def all_rpc_docs_path():
    """Path to documentation specific endpoint"""
    return "/all-rpc-doc/"


@pytest.fixture(scope="session")
def client_auth():
    """Authentication data. Default is None, can be overriden at module or class level"""
    return None


@pytest.fixture(
    scope="session",
    params=["application/json", "application/json-rpc", "application/jsonrequest"],
)
def jsonrpc_content_type(request):
    """
    A Content-Type value supported by JSON-RPC handler.

    Fixture parametrization will cause each JSON-RPC test to be run N times
    """
    return request.param


@pytest.fixture(scope="function", params=[PythonXmlRpcClient])
def xmlrpc_client(live_server, endpoint_path, client_auth, request):
    """A xml-rpc only client"""
    klass = request.param
    return klass(live_server.url + endpoint_path, auth=client_auth)


@pytest.fixture(scope="function", params=[PythonXmlRpcClient])
def xmlrpc_client_with_builtin_types(live_server, endpoint_path, client_auth, request):
    """A xml-rpc only client with builtin types enabled"""
    klass = request.param
    return klass(
        live_server.url + endpoint_path, auth=client_auth, use_builtin_types=True
    )


@pytest.fixture(scope="function", params=[JsonrpcclientlibClient])
def jsonrpc_client(
    live_server, endpoint_path, client_auth, jsonrpc_content_type, request
):
    """A json-rpc only client"""
    klass = request.param
    return klass(
        live_server.url + endpoint_path,
        auth=client_auth,
        jsonrpc_content_type=jsonrpc_content_type,
    )


@pytest.fixture(scope="function", params=[JsonrpcclientlibClient, PythonXmlRpcClient])
def any_rpc_client(
    live_server, endpoint_path, client_auth, jsonrpc_content_type, request
):
    """A RPC client (xml-rpc or json-rpc)"""
    klass = request.param
    return klass(
        live_server.url + endpoint_path,
        auth=client_auth,
        jsonrpc_content_type=jsonrpc_content_type,
    )
