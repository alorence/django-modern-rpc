# coding: utf-8
import pytest
import requests
from django.core.exceptions import ImproperlyConfigured

from modernrpc.views import RPCEntryPoint


def test_forbidden_get(all_rpc_url):

    r = requests.get(all_rpc_url)
    assert r.status_code == 405

    r2 = requests.post(all_rpc_url)
    assert r2.status_code == 200


def test_allowed_get(all_rpc_doc_url):

    r = requests.get(all_rpc_doc_url)
    assert r.status_code == 200

    r2 = requests.post(all_rpc_doc_url)
    assert r2.status_code == 405


def test_invalid_entry_point(settings, rf):
    settings.MODERNRPC_HANDLERS = []

    entry_point = RPCEntryPoint.as_view()
    with pytest.raises(ImproperlyConfigured) as exc_info:
        entry_point(rf.post('xxx'))

    assert 'handler' in str(exc_info.value)
