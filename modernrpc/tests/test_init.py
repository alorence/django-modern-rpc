import pytest
from django.apps.registry import apps

from modernrpc.apps import check_required_settings_defined
from modernrpc.core import get_all_method_names


def test_init_import_warning(settings):

    settings.MODERNRPC_METHODS_MODULES = [
        'invalid_module'
    ]
    app = apps.get_app_config("modernrpc")

    with pytest.warns(Warning):
        app.ready()


def test_settings_check(settings):

    assert len(check_required_settings_defined(apps.get_app_config("modernrpc"))) == 0

    settings.MODERNRPC_METHODS_MODULES = []

    result = check_required_settings_defined(apps.get_app_config("modernrpc"))
    assert len(result) == 1
    assert result[0].id == 'modernrpc.E001'


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

    # Re-init library, with None modules list
    settings.MODERNRPC_METHODS_MODULES = None
    app.ready()
    custom_rpc_methods = [m for m in get_all_method_names() if not m.startswith('system.')]
    assert len(custom_rpc_methods) == 0

    # Restore original state for registry
    settings.MODERNRPC_METHODS_MODULES = orig_modules_list
    app.ready()
