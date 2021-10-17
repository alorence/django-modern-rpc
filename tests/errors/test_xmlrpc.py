# coding: utf-8
import json
import xml.etree.cElementTree as ET

import pytest
import requests

from modernrpc.exceptions import RPC_INVALID_REQUEST, RPC_METHOD_NOT_FOUND, RPC_INVALID_PARAMS, \
    RPC_CUSTOM_ERROR_BASE, RPC_CUSTOM_ERROR_MAX, RPC_INTERNAL_ERROR, RPC_PARSE_ERROR
from tests import xmlrpclib


def test_xmlrpc_call_unknown_method(xmlrpc_client):
    with pytest.raises(xmlrpclib.Fault) as excinfo:
        xmlrpc_client.non_existing_method()

    assert 'Method not found: "non_existing_method"' in excinfo.value.faultString
    assert excinfo.value.faultCode == RPC_METHOD_NOT_FOUND


def test_xmlrpc_invalid_params(xmlrpc_client):
    with pytest.raises(xmlrpclib.Fault) as excinfo:
        xmlrpc_client.add(42)

    assert excinfo.value.faultString == "Invalid parameters: add() missing 1 required positional argument: 'b'"
    assert excinfo.value.faultCode == RPC_INVALID_PARAMS


def test_xmlrpc_invalid_params_2(xmlrpc_client):
    with pytest.raises(xmlrpclib.Fault) as excinfo:
        xmlrpc_client.add(42, -51, 98)

    assert excinfo.value.faultString == "Invalid parameters: add() takes 2 positional arguments but 3 were given"
    assert excinfo.value.faultCode == RPC_INVALID_PARAMS


def test_xmlrpc_internal_error(xmlrpc_client):
    with pytest.raises(xmlrpclib.Fault) as excinfo:
        xmlrpc_client.raise_custom_exception()

    assert 'This is a test error' in excinfo.value.faultString
    assert RPC_CUSTOM_ERROR_BASE <= excinfo.value.faultCode <= RPC_CUSTOM_ERROR_MAX


def test_xmlrpc_exception_with_data(xmlrpc_client):
    with pytest.raises(xmlrpclib.Fault) as excinfo:
        xmlrpc_client.raise_custom_exception_with_data()

    # XML-RPC does not support additional data. The returned exception only contains code and message
    assert 'This exception has additional data' in excinfo.value.faultString
    assert RPC_CUSTOM_ERROR_BASE <= excinfo.value.faultCode <= RPC_CUSTOM_ERROR_MAX


def test_xmlrpc_divide_by_zero(xmlrpc_client):
    with pytest.raises(xmlrpclib.Fault) as excinfo:
        xmlrpc_client.divide(42, 0)

    assert excinfo.value.faultString == "Internal error: division by zero"
    assert excinfo.value.faultCode == RPC_INTERNAL_ERROR


def test_xmlrpc_invalid_request_missing_method_name(all_rpc_url):
    invalid_payload = '''<?xml version="1.0"?>
<methodCall>
  <params>
     <param>
        <value><double>2.41</double></value>
     </param>
  </params>
</methodCall>'''
    headers = {'content-type': 'text/xml'}
    response = requests.post(all_rpc_url, data=invalid_payload, headers=headers)

    tree = ET.fromstring(response.content)
    members = tree.find('fault').find('value').find('struct')

    code, message = '', ''
    for member in members:
        if member.find('name').text == 'faultCode':
            code = int(member.find('value').find('int').text)
        elif member.find('name').text == 'faultString':
            message = member.find('value').find('string').text

    assert 'Missing methodName' in message
    assert code == RPC_INVALID_REQUEST


def test_xmlrpc_invalid_request_but_valid_xml(all_rpc_url):
    invalid_payload = '''<?xml version="1.0"?>
<methodCall>
</methodCall>'''
    headers = {'content-type': 'text/xml'}
    response = requests.post(all_rpc_url, data=invalid_payload, headers=headers)

    tree = ET.fromstring(response.content)
    members = tree.find('fault').find('value').find('struct')

    code, message = '', ''
    for member in members:
        if member.find('name').text == 'faultCode':
            code = int(member.find('value').find('int').text)
        elif member.find('name').text == 'faultString':
            message = member.find('value').find('string').text

    assert 'The request appear to be invalid' in message
    assert code == RPC_INVALID_REQUEST


def test_xmlrpc_invalid_xml(all_rpc_url):
    # "</methodName" misses the closing '>'
    invalid_payload = '''<?xml version="1.0"?>
<methodCall>
  <methodName>examples.getStateName</methodName
  <params>
     <param>
        <value><double>2.41</double></value>
     </param>
  </params>
</methodCall>'''
    headers = {'content-type': 'text/xml'}
    response = requests.post(all_rpc_url, data=invalid_payload, headers=headers)

    tree = ET.fromstring(response.content)
    members = tree.find('fault').find('value').find('struct')

    code, message = '', ''
    for member in members:
        if member.find('name').text == 'faultCode':
            code = int(member.find('value').find('int').text)
        elif member.find('name').text == 'faultString':
            message = member.find('value').find('string').text

    assert 'not well-formed' in message
    assert code == RPC_PARSE_ERROR


def test_xmlrpc_invalid_request_json_request(all_rpc_url):
    invalid_payload = json.dumps({
        "method": 'add',
        "params": [5, 6],
        "jsonrpc": "2.0",
        "id": 42,
    })
    headers = {'content-type': 'text/xml'}
    response = requests.post(all_rpc_url, data=invalid_payload, headers=headers)

    tree = ET.fromstring(response.content)
    members = tree.find('fault').find('value').find('struct')

    code, message = '', ''
    for member in members:
        if member.find('name').text == 'faultCode':
            code = int(member.find('value').find('int').text)
        elif member.find('name').text == 'faultString':
            message = member.find('value').find('string').text

    assert 'not well-formed' in message
    assert code == RPC_PARSE_ERROR


def test_xmlrpc_invalid_request_bad_type_value(all_rpc_url):
    invalid_payload = '''<?xml version="1.0"?>
<methodCall>
  <methodName>examples.getStateName</methodName
  <params>
     <param>
        <value><double>2.41</double></value>
     </param>
  </params>
</methodCall>'''
    headers = {'content-type': 'text/xml'}
    response = requests.post(all_rpc_url, data=invalid_payload, headers=headers)

    tree = ET.fromstring(response.content)
    members = tree.find('fault').find('value').find('struct')

    code, message = '', ''
    for member in members:
        if member.find('name').text == 'faultCode':
            code = int(member.find('value').find('int').text)
        elif member.find('name').text == 'faultString':
            message = member.find('value').find('string').text

    assert 'not well-formed' in message
    assert code == RPC_PARSE_ERROR


def test_xmlrpc_invalid_multicall(xmlrpc_client):
    with pytest.raises(xmlrpclib.Fault) as excinfo:
        xmlrpc_client.system.multicall('method1')

    assert 'argument should be a list' in excinfo.value.faultString
    assert excinfo.value.faultCode == RPC_INVALID_PARAMS


def test_xmlrpc_invalid_result(xmlrpc_client):
    with pytest.raises(xmlrpclib.Fault) as excinfo:
        xmlrpc_client.get_invalid_result()

    # We cannot test for returned error message because it is too different accross various python versions
    # assert 'cannot marshal' in excinfo.value.faultString
    assert excinfo.value.faultCode == RPC_INTERNAL_ERROR
