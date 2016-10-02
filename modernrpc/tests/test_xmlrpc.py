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


def test_basic_types(live_server):
    client = xmlrpc_module.ServerProxy(live_server.url + '/all-rpc/')
    response = client.basic_types()

    assert isinstance(response['bool'], bool)
    assert response['bool'] is True

    assert isinstance(response['int'], int)
    assert response['int'] == 42

    assert isinstance(response['float'], float)
    assert response['float'] == 51.2

    assert isinstance(response['string'], str)
    assert response['string'] == 'abcde'

    assert isinstance(response['list'], list)
    assert response['list'] == [1, 2, 3]

    assert isinstance(response['struct'], dict)
    assert response['struct'] == {'a': 6, 'b': 21}
