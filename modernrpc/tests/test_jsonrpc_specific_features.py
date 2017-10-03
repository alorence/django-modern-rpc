# coding: utf-8
import pytest
from jsonrpcclient.exceptions import ReceivedErrorResponse
from jsonrpcclient.http_client import HTTPClient

from modernrpc.exceptions import RPC_INVALID_PARAMS


def test_call_with_named_args(live_server):

    c = HTTPClient(live_server.url + '/all-rpc/')

    result = c.divide(numerator=10, denominator=2, z=123)
    assert result == 5.0


def test_call_with_named_args_errors(live_server):

    c = HTTPClient(live_server.url + '/all-rpc/')

    with pytest.raises(ReceivedErrorResponse) as excinfo:
        c.divide(wrong_param_1=10, wrong_param_2=20, z=25)

    assert 'Invalid parameters' in excinfo.value.message
    assert 'unexpected keyword argument' in excinfo.value.message
    assert excinfo.value.code == RPC_INVALID_PARAMS


def test_notify(live_server):

    c = HTTPClient(live_server.url + '/all-rpc/')

    assert c.notify('add', 5, 12) is None
