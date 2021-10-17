# coding: utf-8
import xml

import future.utils
import jsonrpcclient.exceptions
import pytest

from modernrpc.exceptions import RPC_METHOD_NOT_FOUND
from tests import xmlrpclib, jsonrpclib

try:
    # Python 3
    from json.decoder import JSONDecodeError
except ImportError:
    # Python 2: json.loads will raise a ValueError when loading json
    JSONDecodeError = ValueError


def test_xmlrpc_basic_add(xmlrpc_client):
    assert xmlrpc_client.add(2, 3) == 5


def test_jsonrpc_basic_add(jsonrpc_client):
    assert jsonrpc_client.add(2, 3) == 5


def test_xmlrpc_list_methods(xmlrpc_client):
    result = xmlrpc_client.system.listMethods()

    assert type(result) == list
    assert len(result) > 1
    assert 'system.listMethods' in result
    assert 'divide' in result
    assert 'customized_name' in result


def test_jsonrpc_list_methods(jsonrpc_client):
    # Can't call jsonrpc_client.system.listMethods() directly. jsonrpcclient doesn't support
    # remote procedure with a dotted ('.') name
    result = jsonrpc_client.request('system.listMethods')

    assert type(result) == list
    assert len(result) > 1
    assert 'system.listMethods' in result
    assert 'divide' in result
    assert 'customized_name' in result


def test_xmlrpc_get_signature(xmlrpc_client):
    signature = xmlrpc_client.system.methodSignature('add')
    # This one does not have any docstring defined
    assert type(signature) == list
    assert len(signature) == 0


def test_xmlrpc_get_signature_2(xmlrpc_client):
    signature = xmlrpc_client.system.methodSignature('divide')
    # Return type + 2 parameters = 3 elements in the signature
    assert type(signature) == list
    assert len(signature) == 9
    assert signature[0] == 'int or double'
    assert signature[1] == 'int or double'
    assert signature[2] == 'int or double'
    assert signature[3] == 'int'
    assert signature[4] == 'int'
    assert signature[5] == 'int'
    assert signature[6] == 'int'
    assert signature[7] == 'int'
    assert signature[8] == 'int'


def test_xmlrpc_get_signature_invalid_method(xmlrpc_client):
    with pytest.raises(xmlrpclib.Fault):
        xmlrpc_client.system.methodSignature('inexistant_method')


def test_jsonrpc_get_signature(jsonrpc_client):
    signature = jsonrpc_client.request('system.methodSignature', "add")
    # This one doesn not have any docstring defined
    assert type(signature) == list
    assert len(signature) == 0


def test_jsonrpc_get_signature_2(jsonrpc_client):
    signature = jsonrpc_client.request('system.methodSignature', "divide")
    # Return type + 2 parameters = 3 elements in the signature
    assert type(signature) == list
    assert len(signature) == 9
    assert signature[0] == 'int or double'
    assert signature[1] == 'int or double'
    assert signature[2] == 'int or double'
    assert signature[3] == 'int'
    assert signature[4] == 'int'
    assert signature[5] == 'int'
    assert signature[6] == 'int'
    assert signature[7] == 'int'
    assert signature[8] == 'int'


def test_jsonrpc_get_signature_invalid_method(jsonrpc_client):
    with pytest.raises(jsonrpcclient.exceptions.ReceivedErrorResponse):
        jsonrpc_client.request('system.methodSignature', 'inexistant_method')


def test_xmlrpc_method_help(xmlrpc_client):
    help_msg = xmlrpc_client.system.methodHelp('add')
    assert type(help_msg) == str
    assert help_msg == ''


def test_xmlrpc_method_help_2(xmlrpc_client):
    help_msg = xmlrpc_client.system.methodHelp('divide')
    assert 'Divide a numerator by a denominator' in help_msg


def test_xmlrpc_method_help_invalid_method(xmlrpc_client):
    with pytest.raises(xmlrpclib.Fault):
        xmlrpc_client.system.methodHelp('inexistant_method')


def test_jsonrpc_method_help(jsonrpc_client):
    help_text = jsonrpc_client.request('system.methodHelp', "add")

    # Type = unicode in Python 2, str in Python 3
    assert type(help_text) == future.utils.text_type
    assert help_text == ''


def test_jsonrpc_method_help_2(jsonrpc_client):
    help_text = jsonrpc_client.request('system.methodHelp', "divide")
    assert 'Divide a numerator by a denominator' in help_text


def test_jsonrpc_method_help_invalid_method(jsonrpc_client):
    with pytest.raises(jsonrpcclient.exceptions.ReceivedErrorResponse):
        jsonrpc_client.request('system.methodSignature', 'inexistant_method')


def test_xmlrpc_protocol_specific_methods(xmlrpc_client):
    methods_list = xmlrpc_client.system.listMethods()
    assert 'method_x' not in methods_list
    assert 'method_y' in methods_list


def test_xmlrpc_protocol_specific_methods_2(xmlrpc_client):
    # method_y is available only via XML-RPC
    assert xmlrpc_client.method_y() == 'XML only'


def test_xmlrpc_protocol_specific_methods_invalid_method(xmlrpc_client):
    with pytest.raises(xmlrpclib.Fault) as excinfo:
        # method_x is available only via JSON-RPC
        xmlrpc_client.method_x()

    assert 'Method not found: "method_x"' in excinfo.value.faultString
    assert excinfo.value.faultCode == RPC_METHOD_NOT_FOUND


def test_jsonrpc_protocol_specific_methods(jsonrpc_client):
    methods_list = jsonrpc_client.request('system.listMethods')
    assert 'method_x' in methods_list
    assert 'method_y' not in methods_list


def test_jsonrpc_protocol_specific_methods_2(jsonrpc_client):
    # method_x is available only via JSON-RPC
    assert jsonrpc_client.method_x() == 'JSON only'


def test_jsonrpc_protocol_specific_methods_invalid_method(jsonrpc_client):
    # method_y is available only via XML-RPC
    with pytest.raises(jsonrpcclient.exceptions.ReceivedErrorResponse) as excinfo:
        jsonrpc_client.method_y()

    assert 'Method not found: "method_y"' in excinfo.value.message
    assert excinfo.value.code == RPC_METHOD_NOT_FOUND


def test_xmlrpc_protocol_specific_error(json_only_url):
    # Specific xmlrpc client communicating with json only endpoint
    xmlrpc_client = xmlrpclib.ServerProxy(json_only_url)

    with pytest.raises(xml.parsers.expat.ExpatError) as excinfo:
        # There is no method available via this entry point for XML-RPC clients.
        # The returned error message cannot be encapsulated in a proper XML-RPC response (since the entry
        # point is not configured to handle and respond via the protocol). The returned error message is RAW,
        # so XML-RPC cannot parse it and generate an ExpatError
        xmlrpc_client.system.listMethods()
    assert 'syntax error' in str(excinfo.value)


def test_jsonrpc_protocol_specific_error(xml_only_url):
    # Specific jsonrpc client communicating with xml only endpoint
    jsonrpc_client = jsonrpclib.HTTPClient(xml_only_url)

    with pytest.raises(jsonrpcclient.exceptions.ParseResponseError) as excinfo:
        # There is no method available via this entry point for JSON-RPC clients.
        # The returned error message cannot be encapsulated in a proper JSON-RPC response (since the entry
        # point is not configured to handle and respond via this protocol). The returned error message is RAW,
        # so JSON-RPC cannot parse it and generate a JSONDecodeError, or a ValueError in python 2
        jsonrpc_client.request('system.listMethods')

    assert 'The response was not valid JSON' in str(excinfo.value)
