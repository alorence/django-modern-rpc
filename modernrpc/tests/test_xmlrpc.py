# coding: utf-8

try:
    # Python 3
    import xmlrpc.client as xmlrpc_module
except ImportError:
    # Python 2
    import xmlrpclib as xmlrpc_module


def test_basic_add(live_server):
    client = xmlrpc_module.ServerProxy(live_server.url + '/all-rpc/')
    assert client.add(2, 3) == 5


def test_xrpc_list_methods(live_server):

    client = xmlrpc_module.ServerProxy(live_server.url + '/all-rpc/')
    result = client.system.listMethods()

    assert type(result) == list
    assert 'system.listMethods' in result
    assert len(result) > 1


def test_get_signature(live_server):

    client = xmlrpc_module.ServerProxy(live_server.url + '/all-rpc/')

    signature = client.system.getSignature('add')
    # This one doesn not have any docstring defined
    assert type(signature) == list
    assert len(signature) == 0

    signature = client.system.getSignature('divide')
    # Return type + 2 parameters = 3 elements in the signature
    assert type(signature) == list
    assert len(signature) == 3
    assert signature[0] == 'int or double'
    assert signature[1] == 'int or double'
    assert signature[2] == 'int or double'
