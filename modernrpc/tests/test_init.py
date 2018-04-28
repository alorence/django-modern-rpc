# coding: utf-8
import pytest
from django.apps.registry import apps

from modernrpc.apps import check_required_settings_defined


def test_settings_check(settings):

    # With default testsite.settings, check method shouldn't complain
    assert len(check_required_settings_defined(apps.get_app_config("modernrpc"))) == 0

    # After deleting values in settings.MODERNRPC_METHODS_MODULES, the check should warn
    settings.MODERNRPC_METHODS_MODULES = []

    result = check_required_settings_defined(apps.get_app_config("modernrpc"))
    assert len(result) == 1
    assert result[0].id == 'modernrpc.E001'


def test_warning_on_invalid_module_reference(settings, rpc_registry):

    # Update setting value, to only contain reference to an invalid module
    settings.MODERNRPC_METHODS_MODULES = ['invalid.module.reference']

    # This will ensure a warning is thrown, due to invalid module specified
    app = apps.get_app_config("modernrpc")
    with pytest.warns(Warning):
        app.ready()

    # Now, we should have removed all custom methods from the registry
    custom_rpc_methods = [m for m in rpc_registry.get_all_method_names() if not m.startswith('system.')]
    assert len(custom_rpc_methods) == 0


def test_registry_empty_if_settings_not_defined(settings, rpc_registry):

    # Update setting value to remove any value
    settings.MODERNRPC_METHODS_MODULES = None

    app = apps.get_app_config("modernrpc")
    app.ready()

    # Now, we should have removed all custom methods from the registry
    custom_rpc_methods = [m for m in rpc_registry.get_all_method_names() if not m.startswith('system.')]
    assert len(custom_rpc_methods) == 0
