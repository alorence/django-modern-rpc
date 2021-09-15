# coding: utf-8
import pytest

from . import xmlrpclib, jsonrpclib


@pytest.fixture(scope='session')
def all_rpc_url(live_server):
    """Return the default RPC test endpoint URL. See 'testsite.urls' for additional info."""
    return live_server + '/all-rpc/'


@pytest.fixture(scope='session')
def all_rpc_doc_url(live_server):
    """Return the URL to view configured to serve RPC documentation. See 'testsite.urls' for additional info."""
    return live_server + '/all-rpc-doc/'


@pytest.fixture(scope='session')
def json_only_url(live_server):
    """Return the JSON-RPC specific endpoint URL. See 'testsite.urls' for additional info."""
    return live_server + '/json-only/'


@pytest.fixture(scope='session')
def xml_only_url(live_server):
    """Return the XML-RPC specific endpoint URL. See 'testsite.urls' for additional info."""
    return live_server + '/xml-only/'


@pytest.fixture(scope='session')
def xmlrpc_client(all_rpc_url):
    """Return the default XML-RPC client"""
    return xmlrpclib.ServerProxy(all_rpc_url)


@pytest.fixture(scope='session', params=[None, "application/json-rpc", "application/jsonrequest"])
def jsonrpc_client(request, all_rpc_url):
    """Return the default JSON-RPC client"""
    client = jsonrpclib.HTTPClient(all_rpc_url)
    if request.param is not None:
        # Allow parametrization of jsonrpc client
        client.session.headers.update({"Content-Type": request.param})
    return client


def get_url_with_auth(orig_url, username, password):
    return orig_url.replace('://', '://{uname}:{pwd}@').format(uname=username, pwd=password)
