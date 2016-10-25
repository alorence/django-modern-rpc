# coding: utf-8
import requests


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
