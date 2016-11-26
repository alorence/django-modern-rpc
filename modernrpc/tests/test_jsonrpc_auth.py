# coding: utf-8
import datetime
import sys

import django.utils.six as six
import pytest
from django.utils.six import text_type
from dummy_jsonrpc_client import ServerProxy, ProtocolError
from modernrpc.exceptions import RPC_INTERNAL_ERROR


def test_user_logged(live_server, django_user_model):

    django_user_model.objects.create_user('johndoe', email='jd@example.com', password='123456')

    client = ServerProxy(live_server.url + '/all-rpc/', login='johndoe', password='123456')
    assert client.method_need_login(5) == 25

    with pytest.raises(ProtocolError):
        client = ServerProxy(live_server.url + '/all-rpc/')
        client.method_need_login(4)
