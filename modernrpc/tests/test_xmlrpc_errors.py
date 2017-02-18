# coding: utf-8
import json
import xml.etree.cElementTree as ET

import pytest
import requests
from django.utils.six.moves import xmlrpc_client

from modernrpc.exceptions import RPC_INVALID_REQUEST, RPC_METHOD_NOT_FOUND, RPC_INVALID_PARAMS, \
    RPC_CUSTOM_ERROR_BASE, RPC_CUSTOM_ERROR_MAX, RPC_INTERNAL_ERROR, RPC_PARSE_ERROR


def test_xrpc_call_unknown_method(live_server):

    client = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')

    with pytest.raises(xmlrpc_client.Fault) as excinfo:
        client.non_existing_method()

    assert 'Method not found: non_existing_method' in excinfo.value.faultString
    assert excinfo.value.faultCode == RPC_METHOD_NOT_FOUND


def test_xrpc_invalid_params(live_server):

    client = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')

    with pytest.raises(xmlrpc_client.Fault) as excinfo:
        client.add(42)

    assert 'Invalid parameters' in excinfo.value.faultString
    # Python2: takes exactly 2 arguments (1 given)
    # Python3: 1 required positional argument
    assert 'argument' in excinfo.value.faultString
    assert excinfo.value.faultCode == RPC_INVALID_PARAMS


def test_xrpc_invalid_params_2(live_server):

    client = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')

    with pytest.raises(xmlrpc_client.Fault) as excinfo:
        client.add(42, -51, 98)

    # Python2: takes exactly 2 arguments (3 given)
    # Python3: takes 2 positional arguments but 3 were given
    assert 'arguments' in excinfo.value.faultString
    assert excinfo.value.faultCode == RPC_INVALID_PARAMS


def test_xrpc_internal_error(live_server):

    client = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')

    with pytest.raises(xmlrpc_client.Fault) as excinfo:
        client.raise_custom_exception()

    assert 'This is a test error' in excinfo.value.faultString
    assert RPC_CUSTOM_ERROR_BASE <= excinfo.value.faultCode <= RPC_CUSTOM_ERROR_MAX


def test_xrpc_divide_by_zero(live_server):

    client = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')

    with pytest.raises(xmlrpc_client.Fault) as excinfo:
        client.divide(42, 0)

    # Python2: integer division or modulo by zero
    # Python3: division by zero
    assert 'by zero' in excinfo.value.faultString
    assert excinfo.value.faultCode == RPC_INTERNAL_ERROR


def test_xrpc_invalid_request_missing_method_name(live_server):
    invalid_payload = '''<?xml version="1.0"?>
<methodCall>
  <params>
     <param>
        <value><double>2.41</double></value>
     </param>
  </params>
</methodCall>'''
    headers = {'content-type': 'text/xml'}
    response = requests.post(live_server.url + '/all-rpc/', data=invalid_payload, headers=headers)

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


def test_xrpc_invalid_request_but_valid_xml(live_server):
    invalid_payload = '''<?xml version="1.0"?>
<methodCall>
</methodCall>'''
    headers = {'content-type': 'text/xml'}
    response = requests.post(live_server.url + '/all-rpc/', data=invalid_payload, headers=headers)

    tree = ET.fromstring(response.content)
    members = tree.find('fault').find('value').find('struct')

    code, message = '', ''
    for member in members:
        if member.find('name').text == 'faultCode':
            code = int(member.find('value').find('int').text)
        elif member.find('name').text == 'faultString':
            message = member.find('value').find('string').text

    assert 'ResponseError' in message
    assert code == RPC_INVALID_REQUEST


def test_xrpc_invalid_xml(live_server):
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
    response = requests.post(live_server.url + '/all-rpc/', data=invalid_payload, headers=headers)

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


def test_xrpc_invalid_request_json_request(live_server):
    invalid_payload = json.dumps({
        "method": 'add',
        "params": [5, 6],
        "jsonrpc": "2.0",
        "id": 42,
    })
    headers = {'content-type': 'text/xml'}
    response = requests.post(live_server.url + '/all-rpc/', data=invalid_payload, headers=headers)

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


def test_xrpc_invalid_request_bad_type_value(live_server):
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
    response = requests.post(live_server.url + '/all-rpc/', data=invalid_payload, headers=headers)

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
