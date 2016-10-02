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
