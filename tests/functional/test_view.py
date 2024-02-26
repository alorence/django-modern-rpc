import pytest
import requests

from modernrpc.exceptions import RPC_METHOD_NOT_FOUND


def test_requests_to_endpoint(live_server, endpoint_path):
    r = requests.get(live_server.url + endpoint_path)
    assert r.status_code == 405

    r2 = requests.post(live_server.url + endpoint_path)
    assert r2.status_code == 200


def test_requests_to_docs(live_server, all_rpc_docs_path):
    r = requests.get(live_server.url + all_rpc_docs_path)
    assert r.status_code == 200

    r2 = requests.post(live_server.url + all_rpc_docs_path)
    assert r2.status_code == 405


# In testsite.rpc_methods_stub.generic, a function has not been decorated
# Ensure it is not available in registry
def test_not_registered_method(any_rpc_client):
    assert "existing_but_not_decorated" not in any_rpc_client.call("system.listMethods")


def test_not_registered_method_call(any_rpc_client):
    assert "existing_but_not_decorated" not in any_rpc_client.call("system.listMethods")

    with pytest.raises(any_rpc_client.error_response_exception) as exc_info:
        any_rpc_client.call("existing_but_not_decorated")
    any_rpc_client.assert_exception_code(exc_info.value, RPC_METHOD_NOT_FOUND)


class TestJsonOnlyEntryPoint:
    @pytest.fixture(scope="session")
    def endpoint_path(self):
        return "/json-only/"

    def test_request_to_unsupported_endpoint(self, xmlrpc_client):
        exc_match = r"syntax error: line 1, column 0"
        with pytest.raises(xmlrpc_client.invalid_response_exception, match=exc_match) as exc_info:
            # There is no method available via this entry point for XML-RPC clients.
            # The returned error message cannot be encapsulated in a proper XML-RPC response (since the entry
            # point is not configured to handle and respond via the protocol). The returned error message is RAW,
            # so XML-RPC cannot parse it and generate an ExpatError
            xmlrpc_client.call("any_method")
        # ExpatError is raised with code == 2. This may be dropped later (as it is not relevant)
        xmlrpc_client.assert_exception_code(exc_info.value, 2)


class TestXmlOnlyEntryPoint:
    @pytest.fixture(scope="session")
    def endpoint_path(self):
        return "/xml-only/"

    def test_request_to_unsupported_endpoint(self, jsonrpc_client):
        exc_match = r'Invalid Content-Type returned by server: "text/plain". Expected: "application/json"'
        # TODO: find a way to read the error text returned, and check it is the expected one
        with pytest.raises(ValueError, match=exc_match) as exc_info:
            # There is no method available via this entry point for JSON-RPC clients.
            # The returned error message cannot be encapsulated in a proper JSON-RPC response (since the entry
            # point is not configured to handle and respond via this protocol). The returned error message is RAW,
            # so JSON-RPC cannot parse it and generate a ParseResponseError
            jsonrpc_client.call("any_method")
        jsonrpc_client.assert_exception_code(exc_info.value, None)
