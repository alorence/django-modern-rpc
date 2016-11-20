# coding: utf-8
import xml

import pytest
from django.utils.six.moves import xmlrpc_client
from modernrpc.exceptions import RPC_METHOD_NOT_FOUND


def test_xrpc_basic_add(live_server):
    client = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')
    assert client.add(2, 3) == 5


def test_xrpc_list_methods(live_server):

    client = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')
    result = client.system.listMethods()

    assert type(result) == list
    assert 'system.listMethods' in result
    assert len(result) > 1


def test_xrpc_get_signature(live_server):

    client = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')

    signature = client.system.methodSignature('add')
    # This one does not have any docstring defined
    assert type(signature) == list
    assert len(signature) == 0

    signature = client.system.methodSignature('divide')
    # Return type + 2 parameters = 3 elements in the signature
    assert type(signature) == list
    assert len(signature) == 3
    assert signature[0] == 'int or double'
    assert signature[1] == 'int or double'
    assert signature[2] == 'int or double'

    with pytest.raises(xmlrpc_client.Fault):
        client.system.methodSignature('inexistant_method')


def test_xrpc_method_help(live_server):

    client = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')

    help_msg = client.system.methodHelp('add')
    assert type(help_msg) == str
    assert help_msg == ''

    help_msg = client.system.methodHelp('divide')
    assert 'Divide a numerator by a denominator' in help_msg

    with pytest.raises(xmlrpc_client.Fault):
        client.system.methodHelp('inexistant_method')


def test_xrpc_only_method(live_server):

    client = xmlrpc_client.ServerProxy(live_server.url + '/xml-only/')

    methods_list = client.system.listMethods()
    assert 'method_x' not in methods_list
    assert 'method_y' in methods_list

    # method_y is available only via XML-RPC
    result = client.method_y()
    assert result == 'XML only'

    with pytest.raises(xmlrpc_client.Fault) as excinfo:
        # method_x is available only via JSON-RPC
        client.method_x()

    assert 'Method not found: method_x' in excinfo.value.faultString
    assert excinfo.value.faultCode == RPC_METHOD_NOT_FOUND


def test_jsrpc_only_internal_error(live_server):

    client = xmlrpc_client.ServerProxy(live_server.url + '/json-only/')

    with pytest.raises(xml.parsers.expat.ExpatError) as excinfo:
        # There is no method available via this entry point. The entry point cannot handle the request.
        # The returned error message cannot be encapsulated in a proper XML-RPC response (since the entry
        # point is not configured to handle and respond via the protocol). The returned error message is RAW,
        # so XML-RPC cannot parse it and generate an ExpatError
        client.system.listMethods()
    assert 'syntax error' in str(excinfo.value)
