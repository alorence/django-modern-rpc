# coding: utf-8

from jsonrpcclient.http_client import HTTPClient


def test_call_with_named_args(live_server):

    c = HTTPClient(live_server.url + '/all-rpc/')

    result = c.divide(numerator=10, denominator=2, z=123)
    assert result == 5.0


def test_notify(live_server):

    c = HTTPClient(live_server.url + '/all-rpc/')

    assert c.notify('add', 5, 12) == None
