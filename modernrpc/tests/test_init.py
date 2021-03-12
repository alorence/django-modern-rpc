# coding: utf-8
import pytest
from django.apps.registry import apps

from modernrpc.apps import check_settings


def test_init_check_ok():
    # Default settings define a MODERNRPC_METHODS_MODULES with valid values
    result = check_settings(apps.get_app_config("modernrpc"))
    assert not result


@pytest.mark.parametrize('empty_value', [[], set(), tuple(), None])
def test_settings_check_with_empty_modules_list(settings, empty_value):
    # With empty or None value, first check must complain
    settings.MODERNRPC_METHODS_MODULES = empty_value

    result = check_settings(apps.get_app_config("modernrpc"))
    assert len(result) == 1
    assert result[0].id == 'modernrpc.W001'


@pytest.mark.parametrize('empty_value', [[], set(), tuple(), None])
def test_registry_empty_if_settings_not_defined(settings, rpc_registry, empty_value):
    # Update setting value to remove any value
    settings.MODERNRPC_METHODS_MODULES = empty_value

    app = apps.get_app_config("modernrpc")
    app.ready()

    # Registry is empty in such case
    assert not rpc_registry.get_all_method_names()


@pytest.mark.parametrize("module_name", [
    'invalid.module.reference',
    'testsite.rpc_methods_stub.module_with_invalid_import'
])
def test_settings_check_with_module_not_found(settings, module_name):
    settings.MODERNRPC_METHODS_MODULES = [module_name]

    result = check_settings(apps.get_app_config("modernrpc"))
    assert len(result) == 1
    assert result[0].id == 'modernrpc.E001'


@pytest.mark.parametrize("module_name", [
    'invalid.module.reference',
    'testsite.rpc_methods_stub.module_with_invalid_import'
])
def test_app_init_with_module_not_found(settings, rpc_registry, module_name):
    settings.MODERNRPC_METHODS_MODULES = [module_name]

    app = apps.get_app_config("modernrpc")
    with pytest.raises(ImportError):
        app.ready()

    # Registry is empty in such case
    assert not rpc_registry.get_all_method_names()


def test_settings_check_with_syntax_error_in_module(settings):
    settings.MODERNRPC_METHODS_MODULES = ['testsite.rpc_methods_stub.module_with_syntax_errors']

    result = check_settings(apps.get_app_config("modernrpc"))
    assert len(result) == 1
    assert result[0].id == 'modernrpc.E002'


def test_app_init_with_syntax_error_in_module(settings, rpc_registry):
    # modernrpc / tests / testsite / rpc_methods_stub / module_with_syntax_errors
    settings.MODERNRPC_METHODS_MODULES = ['testsite.rpc_methods_stub.module_with_syntax_errors']

    app = apps.get_app_config("modernrpc")
    with pytest.raises(SyntaxError):
        app.ready()

    # Registry is empty in such case
    assert not rpc_registry.get_all_method_names()
