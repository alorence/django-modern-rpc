# coding: utf-8
import sys
try:
    # Python 3
    from json.decoder import JSONDecodeError
except ImportError:
    # Python 2: json.loads will raise a ValueError when loading json
    JSONDecodeError = ValueError

import pytest

from dummy_jsonrpc_client import ServerProxy, JsonRpcFault
from modernrpc.exceptions import RPC_METHOD_NOT_FOUND


def test_jsrpc_basic_add(live_server):

    client = ServerProxy(live_server.url + '/all-rpc/')

    result = client.add(2, 3)
    assert result == 5


def test_jsrpc_list_methods(live_server):

    client = ServerProxy(live_server.url + '/all-rpc/')

    result = client.system.listMethods()

    assert type(result) == list
    assert len(result) > 1
    assert 'system.listMethods' in result


def test_jsrpc_system_get_signature(live_server):

    client = ServerProxy(live_server.url + '/all-rpc/')

    signature = client.system.methodSignature("add")
    # This one doesn not have any docstring defined
    assert type(signature) == list
    assert len(signature) == 0

    signature = client.system.methodSignature("divide")
    # Return type + 2 parameters = 3 elements in the signature
    assert type(signature) == list
    assert len(signature) == 3
    assert signature[0] == 'int or double'
    assert signature[1] == 'int or double'
    assert signature[2] == 'int or double'

    with pytest.raises(JsonRpcFault):
        client.system.methodSignature('inexistant_method')


def test_jsrpc_method_help(live_server):

    client = ServerProxy(live_server.url + '/all-rpc/')

    help_text = client.system.methodHelp("add")
    if sys.version_info < (3, 0):
        assert type(help_text) == unicode  # noqa: F821

    else:
        assert type(help_text) == str
    assert help_text == ''

    help_text = client.system.methodHelp("divide")
    assert 'Divide a numerator by a denominator' in help_text

    with pytest.raises(JsonRpcFault):
        client.system.methodSignature('inexistant_method')


def test_jsrpc_only_method(live_server):

    client = ServerProxy(live_server.url + '/json-only/')

    methods_list = client.system.listMethods()
    assert 'method_x' in methods_list
    assert 'method_y' not in methods_list

    result = client.method_x()
    assert result == 'JSON only'

    # method_y is available only via XML-RPC
    with pytest.raises(JsonRpcFault) as excinfo:
        client.method_y()

    assert 'Method not found: method_y' in excinfo.value.faultString
    assert excinfo.value.faultCode == RPC_METHOD_NOT_FOUND


def test_xrpc_only_internal_error(live_server):

    client = ServerProxy(live_server.url + '/xml-only/')
    with pytest.raises(JSONDecodeError):
        # There is no method available via this entry point. The entry point cannot handle the request.
        # The returned error message cannot be encapsulated in a proper JSON-RPC response (since the entry
        # point is not configured to handle and respond via this protocol). The returned error message is RAW,
        # so JSON-RPC cannot parse it and generate a JSONDecodeError, or a ValueError in python 2
        client.system.listMethods()
