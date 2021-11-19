# coding: utf-8
import base64
import json
import pyexpat
import xmlrpc.client
from abc import ABC, abstractmethod

import jsonrpcclient.exceptions
import jsonrpcclient.http_client
import pytest
import requests


class JsonrpcErrorResponse(Exception):
    def __init__(self, code, message, data=None):
        self.code = code
        self.message = message
        self.data = data


class AbstractRpcTestClient(ABC):
    error_response_exception = None
    invalid_response_exception = None
    auth_error_exception = None

    def __init__(self, url, **kwargs):
        self._url = url
        self._auth = kwargs.get("auth")

    @staticmethod
    def assert_exception_code(exception, error_code):
        """

        :param exception: The exception instance
        :param error_code: Error code, as int
        :return:
        """
        exc_code = getattr(exception, "code", None) or getattr(exception, "faultCode", None)
        assert exc_code == error_code

    def _get_headers(self):
        if not self._auth:
            return {}

        kind, *_ = self._auth
        if kind in ("basic", "basic_auth"):
            _, username, password = self._auth
            credz = "{}:{}".format(username, password)
            b64_credz = base64.standard_b64encode(credz.encode("utf-8")).decode("utf-8")
            return {
                "Authorization": "Basic {}".format(b64_credz)
            }
        raise ValueError("Unknown Authentication kind: {}".format(kind))

    @abstractmethod
    def call(self, method, args=None):
        pass


class AbstractXmlRpcTestClient(AbstractRpcTestClient):
    @abstractmethod
    def multicall(self, calls_data):
        pass


class AbstractJsonRpcTestClient(AbstractRpcTestClient):
    def __init__(self, url, **kwargs):
        super(AbstractJsonRpcTestClient, self).__init__(url, **kwargs)
        self._request_id = 0
        self._content_type = kwargs.get("jsonrpc_content_type", "application/json")

    @property
    def request_id(self):
        pre_increment = self._request_id
        self._request_id += 1
        return pre_increment

    def _get_headers(self):
        headers = {"Content-Type": self._content_type}
        headers.update(super(AbstractJsonRpcTestClient, self)._get_headers())
        return headers

    @abstractmethod
    def batch_request(self, calls_data):
        pass


class RequestBasedJsonRpcClient(AbstractJsonRpcTestClient):
    """requests based client"""
    error_response_exception = JsonrpcErrorResponse
    invalid_response_exception = json.decoder.JSONDecodeError
    auth_error_exception = JsonrpcErrorResponse

    batch_result_klass = list

    def call(self, method, *args, **kwargs):
        headers = self._get_headers()

        try:
            is_notify = kwargs.pop("notify")
        except KeyError:
            is_notify = False

        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": kwargs or args,
            "id": self.request_id
        }

        response_content = requests.post(self._url, data=json.dumps(payload), headers=headers).json()

        if is_notify:
            return
        try:
            return response_content["result"]
        except KeyError:
            raise JsonrpcErrorResponse(
                response_content['error']['code'],
                response_content['error']['message'],
                response_content["error"].get("data"),
            )

    def batch_request(self, calls_data):
        headers = self._get_headers()

        batch = []
        for method, args, *extra_params in calls_data:
            req = {'jsonrpc': '2.0', 'method': method, 'params': args}
            if "notify_only" not in extra_params:
                req["id"] = self.request_id
            batch.append(req)

        response = requests.post(self._url, data=json.dumps(batch), headers=headers)
        if response.content:
            return response.json()
        return None


class JsonrpcclientlibClient(AbstractJsonRpcTestClient):
    error_response_exception = jsonrpcclient.exceptions.ReceivedErrorResponse
    invalid_response_exception = jsonrpcclient.exceptions.ParseResponseError
    auth_error_exception = jsonrpcclient.exceptions.ReceivedErrorResponse

    batch_result_klass = list

    def __init__(self, url, **kwargs):
        super().__init__(url, **kwargs)
        self._client = jsonrpcclient.HTTPClient(url)

    def call(self, method, *args, **kwargs):
        headers_dump = {**self._client.session.headers}
        self._client.session.headers.update(self._get_headers())

        if "notify" in kwargs and kwargs.pop("notify"):
            self._client.notify(method, *args, **kwargs)
            self._client.session.headers = headers_dump
            return

        result = self._client.request(method, *args, **kwargs)
        self._client.session.headers = headers_dump

        return result

    def batch_request(self, calls_data):
        headers_dump = {**self._client.session.headers}
        self._client.session.headers.update(self._get_headers())

        batch = []
        for method, args, *extra_params in calls_data:
            req = {'jsonrpc': '2.0', 'method': method, 'params': args}
            if "notify_only" not in extra_params:
                req["id"] = self.request_id
            batch.append(req)

        result = self._client.send(batch)
        self._client.session.headers = headers_dump

        return result


class PythonXmlRpcClient(AbstractXmlRpcTestClient):
    error_response_exception = xmlrpc.client.Fault
    invalid_response_exception = pyexpat.ExpatError
    auth_error_exception = xmlrpc.client.Fault

    multicall_result_klass = xmlrpc.client.MultiCallIterator

    def _get_headers(self):
        return [
            (key, value) for key, value in super(PythonXmlRpcClient, self)._get_headers().items()
        ]

    def __init__(self, url, **kwargs):
        super(PythonXmlRpcClient, self).__init__(url, **kwargs or {})
        self._use_builtin_types = kwargs.get("use_builtin_types", False)

        self._transport = xmlrpc.client.Transport(use_builtin_types=self._use_builtin_types)
        self._transport.get_host_info = lambda host: (host, self._get_headers(), {})
        self._client = xmlrpc.client.ServerProxy(self._url, transport=self._transport)

    def call(self, method, *args):
        return getattr(self._client, method)(*args)

    def multicall(self, calls_data):
        multicall = xmlrpc.client.MultiCall(self._client)
        for method, args, in calls_data:
            getattr(multicall, method)(*args)
        result = multicall()
        return result


@pytest.fixture(scope="session")
def endpoint_path():
    return "/all-rpc/"


@pytest.fixture(scope="session")
def all_rpc_docs_path():
    return '/all-rpc-doc/'


@pytest.fixture(scope="session")
def client_auth():
    return None


@pytest.fixture(scope="session", params=["application/json", "application/json-rpc", "application/jsonrequest"])
def jsonrpc_content_type(request):
    return request.param


@pytest.fixture(scope="function", params=[PythonXmlRpcClient])
def xmlrpc_client(live_server, endpoint_path, client_auth, request):
    """A xml-rpc only client"""
    klass = request.param
    return klass(live_server.url + endpoint_path, auth=client_auth)


@pytest.fixture(scope="function", params=[PythonXmlRpcClient])
def xmlrpc_client_with_builtin_types(live_server, endpoint_path, client_auth, request):
    """A xml-rpc only client"""
    klass = request.param
    return klass(live_server.url + endpoint_path, auth=client_auth, use_builtin_types=True)


@pytest.fixture(scope="function", params=[RequestBasedJsonRpcClient, JsonrpcclientlibClient])
def jsonrpc_client(live_server, endpoint_path, client_auth, jsonrpc_content_type, request):
    """A json-rpc only client"""
    klass = request.param
    return klass(live_server.url + endpoint_path, auth=client_auth, jsonrpc_content_type=jsonrpc_content_type)


@pytest.fixture(scope="function", params=[
    RequestBasedJsonRpcClient, JsonrpcclientlibClient, PythonXmlRpcClient
])
def any_rpc_client(live_server, endpoint_path, client_auth, jsonrpc_content_type, request):
    """A RPC client (xml-rpc or json-rpc)"""
    klass = request.param
    return klass(live_server.url + endpoint_path, auth=client_auth, jsonrpc_content_type=jsonrpc_content_type)
