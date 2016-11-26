# coding: utf-8
import pytest
from django.utils.six.moves import xmlrpc_client


def test_xrpc_user_is_logged(live_server, django_user_model):

    django_user_model.objects.create_user('johndoe', email='jd@example.com', password='123456')

    orig_url = live_server.url + '/all-rpc/'
    auth_url = orig_url.replace('http://', 'http://johndoe:123456@')

    client = xmlrpc_client.ServerProxy(auth_url)
    assert client.logged_user_required(5) == 25

    with pytest.raises(xmlrpc_client.ProtocolError):
        client = xmlrpc_client.ServerProxy(orig_url)
        client.logged_user_required(4)


def test_jsrpc_user_is_admin(live_server, django_user_model):

    django_user_model.objects.create_user('johndoe', email='jd@example.com', password='123456')
    django_user_model.objects.create_superuser('admin', email='admin@example.com', password='123456')

    orig_url = live_server.url + '/all-rpc/'
    johndoe_auth_url = orig_url.replace('http://', 'http://johndoe:123456@')
    admin_auth_url = orig_url.replace('http://', 'http://admin:123456@')

    client = xmlrpc_client.ServerProxy(admin_auth_url)
    # Admin is OK
    assert client.superuser_required(5) == 15

    with pytest.raises(xmlrpc_client.ProtocolError):
        # JohnDoe don't have sufficient permissions
        client = xmlrpc_client.ServerProxy(johndoe_auth_url)
        client.superuser_required(5)

    with pytest.raises(xmlrpc_client.ProtocolError):
        # Anonymous user don't have sufficient permissions
        client = xmlrpc_client.ServerProxy(orig_url)
        client.superuser_required(4)
