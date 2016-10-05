# coding: utf-8
import pytest
import requests

from modernrpc.exceptions import RPC_INVALID_RESQUEST, RPC_METHOD_NOT_FOUND, RPC_PARSE_ERROR, RPC_INVALID_PARAMS, \
    RPC_CUSTOM_ERROR_BASE, RPC_CUSTOM_ERROR_MAX, RPC_INTERNAL_ERROR

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
try:
    # Python 3
    import xmlrpc.client as xmlrpc_module
except ImportError:
    # Python 2
    import xmlrpclib as xmlrpc_module


def test_xrpc_call_unknown_method(live_server):

    client = xmlrpc_module.ServerProxy(live_server.url + '/all-rpc/')

    with pytest.raises(xmlrpc_module.Fault) as e:
        client.non_existing_medthod()

        assert 'Method not found: non_existing_medthod' in e.faultString
        assert e.faultCode == RPC_METHOD_NOT_FOUND


def test_xrpc_invalid_params(live_server):

    client = xmlrpc_module.ServerProxy(live_server.url + '/all-rpc/')

    with pytest.raises(xmlrpc_module.Fault) as e:
        client.add(42)

        assert 'Invalid parameters' in e.faultString
        assert '1 required positional argument' in e.faultString
        assert e.faultCode == RPC_INVALID_PARAMS


def test_xrpc_invalid_params2(live_server):

    client = xmlrpc_module.ServerProxy(live_server.url + '/all-rpc/')

    with pytest.raises(xmlrpc_module.Fault) as e:
        client.add(42, -51, 98)

        assert 'Invalid parameters' in e.faultString
        assert 'takes 2 positional arguments but 3 were given' in e.faultString
        assert e.faultCode == RPC_INVALID_PARAMS


def test_xrpc_internal_error(live_server):

    client = xmlrpc_module.ServerProxy(live_server.url + '/all-rpc/')

    with pytest.raises(xmlrpc_module.Fault) as e:
        client.raise_custom_exception()

        assert 'This is a test error' in e.faultString
        assert RPC_CUSTOM_ERROR_BASE <= e.faultCode <= RPC_CUSTOM_ERROR_MAX


def test_xrpc_divide_by_zero(live_server):

    client = xmlrpc_module.ServerProxy(live_server.url + '/all-rpc/')

    with pytest.raises(xmlrpc_module.Fault) as e:
        client.divide(42, 0)

        assert 'Internal error' in e.faultString
        assert 'division by zero' in e.faultString
        assert e.faultCode == RPC_INTERNAL_ERROR


def test_xrpc_invalid_request(live_server):
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

    assert 'Invalid request' in message
    assert 'Missing methodName' in message
    assert code == RPC_INVALID_RESQUEST


def test_xrpc_invalid_request2(live_server):
    invalid_payload = '''<?xml version="1.0"?>
<methodCall>
    <methodName>add</methodName>
    <params>
        <param>
            <value><float>2.41</float></value>
        </param>
        <param>
            <value><int>84</int></value>
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

    assert 'Invalid request' in message
    assert 'unknown tag' in message
    assert code == RPC_INVALID_RESQUEST


def test_xrpc_parse_error(live_server):
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

    assert 'Parse error' in message
    assert 'unable to read the request' in message
    assert code == RPC_PARSE_ERROR
