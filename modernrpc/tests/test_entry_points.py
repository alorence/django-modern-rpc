# coding: utf-8
import requests
from django.core.exceptions import ImproperlyConfigured
from pytest import raises

from modernrpc.views import RPCEntryPoint


def test_forbidden_get(live_server):

    r = requests.get(live_server.url + '/all-rpc/')
    assert r.status_code == 405

    r2 = requests.post(live_server.url + '/all-rpc/')
    assert r2.status_code == 200


def test_allowed_get(live_server):

    r = requests.get(live_server.url + '/all-rpc-doc/')
    assert r.status_code == 200

    r2 = requests.post(live_server.url + '/all-rpc-doc/')
    assert r2.status_code == 405


def test_invalid_entry_point(settings, rf):
    settings.MODERNRPC_HANDLERS = []

    entry_point = RPCEntryPoint.as_view()
    with raises(ImproperlyConfigured) as exc_info:
        entry_point(rf.post('xxx'))

    assert 'handler' in str(exc_info.value)
