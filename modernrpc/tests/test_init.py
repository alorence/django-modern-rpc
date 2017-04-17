import pytest
from django.apps.registry import apps
from django.core.exceptions import ImproperlyConfigured
from pytest import raises

from modernrpc.core import get_all_method_names
from testsite.rpc_methods_stub.generic import add, divide


def test_init_missing_method_modules_setting(settings):

    settings.MODERNRPC_METHODS_MODULES = []
    app = apps.get_app_config("modernrpc")

    with pytest.warns(Warning):
        app.ready()


def test_init_import_warning(settings):

    settings.MODERNRPC_METHODS_MODULES = [
        'invalid_module'
    ]
    app = apps.get_app_config("modernrpc")

    with pytest.warns(Warning):
        app.ready()


def test_init_registry_cleaning(settings):

    orig_modules_list = settings.MODERNRPC_METHODS_MODULES

    app = apps.get_app_config("modernrpc")
    app.ready()

    # Retrieve all methods defined in custom modules (not system.* methods)
    custom_rpc_methods = [m for m in get_all_method_names() if not m.startswith('system.')]
    # Ensure a normal init registered some custom methods
    assert len(custom_rpc_methods) > 0

    # Re-init library, with only invalid module as "methods module"
    settings.MODERNRPC_METHODS_MODULES = ['nope']
    app.ready()

    # Now, we should have removed all custom methods from the registry
    custom_rpc_methods = [m for m in get_all_method_names() if not m.startswith('system.')]
    assert len(custom_rpc_methods) == 0

    # Restore original state for registry
    settings.MODERNRPC_METHODS_MODULES = orig_modules_list
    app.ready()


def test_invalid_method_name():

    # Customize the name of a method from RPC modules. Setting its name to rpc.something
    # makes it invalid regarding XML-RPC standard
    add.modernrpc_name = 'rpc.unauthorized.name'

    # Initialize the app
    app = apps.get_app_config("modernrpc")
    with raises(ImproperlyConfigured):
        # A RPC method with name starting with 'rpc.*' must raises a ImproperlyConfigured
        app.ready()

    # Restore state
    del add.modernrpc_name
    app.ready()


def test_rpc_method_name_duplicated():

    # Customize the name of a method from RPC modules. Setting its name to the same as
    # another RPC method
    divide.modernrpc_name = 'add'

    # Initialize the app
    app = apps.get_app_config("modernrpc")
    with raises(ImproperlyConfigured):
        # A RPC method with name starting with 'rpc.*' must raises a ImproperlyConfigured
        app.ready()

    # Restore state
    del divide.modernrpc_name
    app.ready()
