import base64
import itertools
import pyexpat
import xmlrpc.client
from abc import ABC, abstractmethod
from typing import Union, Type, Any, List, Dict, Optional

import jsonrpcclient
import pytest
import requests
from jsonrpcclient.sentinels import NOID

UNDEFINED_AUTH = object()


class JsonrpcErrorResponse(Exception):
    """A simple wrapper around Rpc error response"""

    def __init__(self, code, message, data=None):
        self.code = code
        self.message = message
        self.data = data


class AbstractRpcTestClient(ABC):
    """Base class RPC clients used to run tests"""

    error_response_exception: Type[Exception]
    invalid_response_exception: Type[Exception]
    auth_error_exception: Type[Exception]

    def __init__(self, url, **kwargs):
        self._url = url
        self._auth = kwargs.get("auth")
        self._content_type = kwargs.get("content_type", self.default_content_type)

    @property
    @abstractmethod
    def default_content_type(self):
        ...

    @staticmethod
    def assert_exception_code(exception: Exception, expected_code: int):
        """
        Extract 'code' or 'faultCode' from given exception instance, and assert its equality
        with given 'expected_code'. Intended to be used in a pytest assertion.
        """
        exc_code = getattr(exception, "code", getattr(exception, "faultCode", None))
        assert exc_code == expected_code

    def _build_request_headers(self):
        """Build headers specific to client configuration"""
        _headers = {
            "Content-Type": self._content_type,
        }

        if not self._auth or self._auth == UNDEFINED_AUTH:
            return _headers

        kind, *_ = self._auth

        if kind not in ("basic", "basic_auth"):
            raise ValueError(f"Unknown Authentication kind: {kind}")

        _, username, password = self._auth
        credz = f"{username}:{password}"
        b64_credz = base64.standard_b64encode(credz.encode("utf-8")).decode("utf-8")

        _headers["Authorization"] = f"Basic {b64_credz}"
        return _headers

    @abstractmethod
    def call(
        self, method: str, args: Optional[Union[List[Any], Dict[str, Any]]] = None
    ):
        """Perform a standard RPC call. Return the reote procedure execution result."""

    @abstractmethod
    def check_response_headers(self, headers):
        """Raise exception when invalid headers are detected in response"""


class AbstractJsonRpcTestClient(AbstractRpcTestClient):
    @property
    def default_content_type(self):
        return "application/json"

    @abstractmethod
    def batch_request(self, calls_data):
        """Perform a JSON-RPC batch request"""

    def check_response_headers(self, headers):
        """Raise exception when invalid headers are detected in response"""
        response_ct = headers["Content-Type"]
        expected_ct = "application/json"
        if not response_ct.startswith(expected_ct):
            error_msg = f'Invalid Content-Type returned by server: "{response_ct}". Expected: "{expected_ct}"'
            raise ValueError(error_msg)


class AbstractXmlRpcTestClient(AbstractRpcTestClient):
    @property
    def default_content_type(self):
        return "text/xml"

    @abstractmethod
    def multicall(self, calls_data):
        """Perform an XML-RPC multicall"""

    def check_response_headers(self, headers):
        """Raise exception when invalid headers are detected in response"""
        response_ct = headers["Content-Type"]
        expected_ct = "text/xml"
        if not response_ct.startswith(expected_ct):
            error_msg = f'Invalid Content-Type returned by server: "{response_ct}". Expected: "{expected_ct}"'
            raise ValueError(error_msg)


class JsonrpcclientlibClient(AbstractJsonRpcTestClient):
    error_response_exception = JsonrpcErrorResponse
    auth_error_exception = JsonrpcErrorResponse
    batch_result_klass = list

    def __init__(self, url, **kwargs):
        super().__init__(url, **kwargs)
        self.url = url

    def call(self, method, *args, **kwargs):
        if "notify" in kwargs and kwargs.pop("notify"):
            json_req = jsonrpcclient.notification(method, params=args or kwargs)
        else:
            json_req = jsonrpcclient.request(method, params=args or kwargs)

        response = requests.post(
            self.url, json=json_req, headers=self._build_request_headers()
        )
        self.check_response_headers(response.headers)

        if response.content == b"":
            return None

        result = jsonrpcclient.parse(response.json())
        if isinstance(result, jsonrpcclient.Ok):
            return result.result

        raise JsonrpcErrorResponse(result.code, result.message, result.data)

    def batch_request(self, calls_data):
        batch_id_generator = itertools.count(0)

        batch = []
        for method, params, *extra_params in calls_data:
            if "notify_only" in extra_params:
                batch.append(jsonrpcclient.notification(method, params=params))
            else:
                batch.append(
                    jsonrpcclient.requests.request_pure(
                        method=method,
                        params=params,
                        id_generator=batch_id_generator,
                        id=NOID,
                    )
                )

        response = requests.post(
            self.url, json=batch, headers=self._build_request_headers()
        )
        self.check_response_headers(response.headers)

        return None if not response.content else response.json()


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
        # TODO: starting with python 3.8, 'headers' argument can be used to customize headers on ServerProxy
        self._client = xmlrpc.client.ServerProxy(self._url, transport=self._transport)

    def _get_headers_list(self):
        """Copy current headers' dict to a List[Tuple[str, str]] instance"""
        return list(self._build_request_headers().items())

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
        return multicall()


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
    """Authentication data. Default is None, can be overridden at module or class level"""
    return UNDEFINED_AUTH


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


@pytest.fixture(
    scope="session",
    params=["application/xml", "text/xml"],
)
def xmlrpc_content_type(request):
    """
    A Content-Type value supported by XML-RPC handler.

    Fixture parametrization will cause each XML-RPC test to be run N times
    """
    return request.param


@pytest.fixture(params=[PythonXmlRpcClient])
def xmlrpc_client(
    live_server, endpoint_path, client_auth, xmlrpc_content_type, request
):
    """A xml-rpc only client"""
    klass = request.param
    return klass(
        live_server.url + endpoint_path,
        auth=client_auth,
        content_type=xmlrpc_content_type,
    )


@pytest.fixture(params=[PythonXmlRpcClient])
def xmlrpc_client_with_builtin_types(
    live_server, endpoint_path, client_auth, xmlrpc_content_type, request
):
    """A xml-rpc only client with builtin types enabled"""
    klass = request.param
    return klass(
        live_server.url + endpoint_path,
        auth=client_auth,
        content_type=xmlrpc_content_type,
        use_builtin_types=True,
    )


@pytest.fixture(params=[JsonrpcclientlibClient])
def jsonrpc_client(
    live_server, endpoint_path, client_auth, jsonrpc_content_type, request
):
    """A json-rpc only client"""
    klass = request.param
    return klass(
        live_server.url + endpoint_path,
        auth=client_auth,
        content_type=jsonrpc_content_type,
    )


@pytest.fixture(params=[JsonrpcclientlibClient, PythonXmlRpcClient])
def any_rpc_client(live_server, endpoint_path, client_auth, request):
    """A RPC client (xml-rpc or json-rpc)"""
    klass = request.param
    return klass(live_server.url + endpoint_path, auth=client_auth)
