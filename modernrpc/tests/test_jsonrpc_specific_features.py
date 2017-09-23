# coding: utf-8
from jsonrpcclient.http_client import HTTPClient


def test_call_with_named_args(live_server):

    c = HTTPClient(live_server.url + '/all-rpc/')

    result = c.divide(numerator=10, denominator=2, z=123)
    assert result == 5.0


def test_notify(live_server):

    c = HTTPClient(live_server.url + '/all-rpc/')

    assert c.notify('add', 5, 12) is None


def test_multicall_with_named_params(live_server):

    c = HTTPClient(live_server.url + '/all-rpc/')

    calls_args = [
        {'methodName': 'add', 'params': {'a': 5, 'b': 10}},
        {'methodName': 'divide', 'params': {'numerator': 30, 'denominator': 5}},
    ]
    result = c.request('system.multicall', [calls_args])

    assert isinstance(result, list)
    # Since json-rpc doesn't provide standard for system.multicall,
    # we used the same rules than the one used for xml-rpc
    # See https://mirrors.talideon.com/articles/multicall.html:
    assert result[0] == [15]  # 5 + 10
    assert result[1] == [6]   # 30 / 5
