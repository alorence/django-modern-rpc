# coding: utf-8
import pytest

from dummy_jsonrpc_client import ServerProxy, ProtocolError


def test_jsrpc_user_is_logged(live_server, django_user_model):

    django_user_model.objects.create_user('johndoe', email='jd@example.com', password='123456')

    client = ServerProxy(live_server.url + '/all-rpc/', login='johndoe', password='123456')
    assert client.logged_user_required(5) == 25

    with pytest.raises(ProtocolError):
        client = ServerProxy(live_server.url + '/all-rpc/')
        client.logged_user_required(4)
