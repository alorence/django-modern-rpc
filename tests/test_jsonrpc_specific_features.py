# coding: utf-8
import pytest
from jsonrpcclient.exceptions import ReceivedErrorResponse

from modernrpc.exceptions import RPC_INVALID_PARAMS


def test_call_with_named_args(jsonrpc_client):

    result = jsonrpc_client.divide(numerator=10, denominator=2, z=123)
    assert result == 5.0


def test_call_with_named_args_errors(jsonrpc_client):

    with pytest.raises(ReceivedErrorResponse) as excinfo:
        jsonrpc_client.divide(wrong_param_1=10, wrong_param_2=20, z=25)

    assert 'Invalid parameters' in excinfo.value.message
    assert 'unexpected keyword argument' in excinfo.value.message
    assert excinfo.value.code == RPC_INVALID_PARAMS


def test_notify(jsonrpc_client):

    assert jsonrpc_client.notify('add', 5, 12) is None
