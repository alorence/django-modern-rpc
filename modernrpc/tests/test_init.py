import pytest
from django.apps.registry import apps

from modernrpc.core import get_all_method_names


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

    app = apps.get_app_config("modernrpc")
    orig_modules_list = settings.MODERNRPC_METHODS_MODULES

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
