# coding: utf-8
import sys
import xml

import pytest
from django.utils.six.moves import xmlrpc_client
from jsonrpcclient.exceptions import ReceivedErrorResponse, ParseResponseError
from jsonrpcclient.http_client import HTTPClient

from modernrpc.exceptions import RPC_METHOD_NOT_FOUND

try:
    # Python 3
    from json.decoder import JSONDecodeError
except ImportError:
    # Python 2: json.loads will raise a ValueError when loading json
    JSONDecodeError = ValueError


def test_basic_add(live_server):
    x_client = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')
    assert x_client.add(2, 3) == 5

    j_client = HTTPClient(live_server.url + '/all-rpc/')
    assert j_client.request('add', 2, 3) == 5


def test_list_methods(live_server):

    x_client = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')
    result = x_client.system.listMethods()

    assert type(result) == list
    assert len(result) > 1
    assert 'system.listMethods' in result

    j_client = HTTPClient(live_server.url + '/all-rpc/')
    result = j_client.request('system.listMethods')

    assert type(result) == list
    assert len(result) > 1
    assert 'system.listMethods' in result


def test_get_signature(live_server):

    x_client = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')

    signature = x_client.system.methodSignature('add')
    # This one does not have any docstring defined
    assert type(signature) == list
    assert len(signature) == 0

    signature = x_client.system.methodSignature('divide')
    # Return type + 2 parameters = 3 elements in the signature
    assert type(signature) == list
    assert len(signature) == 3
    assert signature[0] == 'int or double'
    assert signature[1] == 'int or double'
    assert signature[2] == 'int or double'

    with pytest.raises(xmlrpc_client.Fault):
        x_client.system.methodSignature('inexistant_method')

    j_client = HTTPClient(live_server.url + '/all-rpc/')

    signature = j_client.request('system.methodSignature', "add")
    # This one doesn not have any docstring defined
    assert type(signature) == list
    assert len(signature) == 0

    signature = j_client.request('system.methodSignature', "divide")
    # Return type + 2 parameters = 3 elements in the signature
    assert type(signature) == list
    assert len(signature) == 3
    assert signature[0] == 'int or double'
    assert signature[1] == 'int or double'
    assert signature[2] == 'int or double'

    with pytest.raises(ReceivedErrorResponse):
        j_client.request('system.methodSignature', 'inexistant_method')


def test_method_help(live_server):

    x_client = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')

    help_msg = x_client.system.methodHelp('add')
    assert type(help_msg) == str
    assert help_msg == ''

    help_msg = x_client.system.methodHelp('divide')
    assert 'Divide a numerator by a denominator' in help_msg

    with pytest.raises(xmlrpc_client.Fault):
        x_client.system.methodHelp('inexistant_method')

    j_client = HTTPClient(live_server.url + '/all-rpc/')

    help_text = j_client.request('system.methodHelp', "add")
    if sys.version_info < (3, 0):
        assert type(help_text) == unicode  # noqa: F821

    else:
        assert type(help_text) == str
    assert help_text == ''

    help_text = j_client.request('system.methodHelp', "divide")
    assert 'Divide a numerator by a denominator' in help_text

    with pytest.raises(ReceivedErrorResponse):
        j_client.request('system.methodSignature', 'inexistant_method')


def test_protocol_specific_methods(live_server):

    x_client = xmlrpc_client.ServerProxy(live_server.url + '/xml-only/')

    methods_list = x_client.system.listMethods()
    assert 'method_x' not in methods_list
    assert 'method_y' in methods_list

    # method_y is available only via XML-RPC
    assert x_client.method_y() == 'XML only'

    with pytest.raises(xmlrpc_client.Fault) as excinfo:
        # method_x is available only via JSON-RPC
        x_client.method_x()

    assert 'Method not found: method_x' in excinfo.value.faultString
    assert excinfo.value.faultCode == RPC_METHOD_NOT_FOUND

    j_client = HTTPClient(live_server.url + '/json-only/')

    methods_list = j_client.request('system.listMethods')
    assert 'method_x' in methods_list
    assert 'method_y' not in methods_list

    # method_x is available only via JSON-RPC
    assert j_client.request('method_x') == 'JSON only'

    # method_y is available only via XML-RPC
    with pytest.raises(ReceivedErrorResponse) as excinfo:
        j_client.request('method_y')

    assert 'Method not found: method_y' in excinfo.value.message
    assert excinfo.value.code == RPC_METHOD_NOT_FOUND


def test_protocol_specific_error(live_server):

    x_client = xmlrpc_client.ServerProxy(live_server.url + '/json-only/')

    with pytest.raises(xml.parsers.expat.ExpatError) as excinfo:
        # There is no method available via this entry point for XML-RPC clients.
        # The returned error message cannot be encapsulated in a proper XML-RPC response (since the entry
        # point is not configured to handle and respond via the protocol). The returned error message is RAW,
        # so XML-RPC cannot parse it and generate an ExpatError
        x_client.system.listMethods()
    assert 'syntax error' in str(excinfo.value)

    j_client = HTTPClient(live_server.url + '/xml-only/')
    with pytest.raises(ParseResponseError):
        # There is no method available via this entry point for JSON-RPC clients.
        # The returned error message cannot be encapsulated in a proper JSON-RPC response (since the entry
        # point is not configured to handle and respond via this protocol). The returned error message is RAW,
        # so JSON-RPC cannot parse it and generate a JSONDecodeError, or a ValueError in python 2
        j_client.request('system.listMethods')
