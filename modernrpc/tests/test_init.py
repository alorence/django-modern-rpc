# coding: utf-8
import pytest
from django.apps.registry import apps

from modernrpc.apps import check_required_settings_defined


def test_init_import_warning(settings, rpc_registry):

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


def test_registry_not_empty(rpc_registry):
    # Retrieve all methods defined in custom modules (minus system.* methods)
    custom_rpc_methods = [m for m in rpc_registry.get_all_method_names() if not m.startswith('system.')]
    # Ensure a normal init registered some rpc methods
    assert len(custom_rpc_methods) > 0


def test_registry_empty_after_reset(rpc_registry):

    rpc_registry.reset()
    # Retrieve all methods defined in custom modules (minus system.* methods)
    custom_rpc_methods = [m for m in rpc_registry.get_all_method_names() if not m.startswith('system.')]
    # Ensure a normal init registered some rpc methods
    assert len(custom_rpc_methods) == 0


def test_warning_on_invalid_module_reference(settings, rpc_registry):
    rpc_registry.reset()
    # Re-init library, with only invalid module as "methods module"
    settings.MODERNRPC_METHODS_MODULES = ['invalid.module.reference']
    # This will ensure a warning is thrown, due to invalid module specified
    app = apps.get_app_config("modernrpc")
    with pytest.warns(Warning):
        app.ready()
    # Now, we should have removed all custom methods from the registry
    custom_rpc_methods = [m for m in rpc_registry.get_all_method_names() if not m.startswith('system.')]
    assert len(custom_rpc_methods) == 0


def test_registry_empty_if_settings_not_defined(settings, rpc_registry):
    rpc_registry.reset()
    # Re-init library, with None modules list
    settings.MODERNRPC_METHODS_MODULES = None
    app = apps.get_app_config("modernrpc")
    app.ready()
    custom_rpc_methods = [m for m in rpc_registry.get_all_method_names() if not m.startswith('system.')]
    assert len(custom_rpc_methods) == 0
