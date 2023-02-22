"""This module will test behavior when library is started"""
import pytest
from django.apps.registry import apps
from django.core.exceptions import ImproperlyConfigured

import modernrpc
from modernrpc.apps import check_settings
from modernrpc.core import ALL
from tests.unit.stubs import (
    dummy_remote_procedure_1,
    dummy_remote_procedure_2,
    dummy_remote_procedure_3,
    dummy_remote_procedure_4,
    not_decorated_procedure,
)


class TestInitChecks:
    def test_init_check_ok(self):
        # Default settings define a MODERNRPC_METHODS_MODULES with valid values
        result = check_settings(apps.get_app_config("modernrpc"))
        assert not result

    @pytest.mark.parametrize("empty_value", [[], set(), tuple(), None])
    def test_settings_check_with_empty_modules_list(self, settings, empty_value):
        # With empty or None value, first check must complain
        settings.MODERNRPC_METHODS_MODULES = empty_value

        result = check_settings(apps.get_app_config("modernrpc"))
        assert len(result) == 1
        assert result[0].id == "modernrpc.W001"

    @pytest.mark.parametrize(
        "module_name",
        [
            "invalid.module.reference",
            "testsite.rpc_methods_stub.module_with_invalid_import",
        ],
    )
    def test_settings_check_with_module_not_found(self, settings, module_name):
        settings.MODERNRPC_METHODS_MODULES = [module_name]

        result = check_settings(apps.get_app_config("modernrpc"))
        assert len(result) == 1
        assert result[0].id == "modernrpc.E001"

    def test_settings_check_with_syntax_error_in_module(self, settings):
        settings.MODERNRPC_METHODS_MODULES = [
            "testsite.rpc_methods_stub.module_with_syntax_errors"
        ]

        result = check_settings(apps.get_app_config("modernrpc"))
        assert len(result) == 1
        assert result[0].id == "modernrpc.E002"


@pytest.fixture(scope="function")
def rpc_registry():
    """An instance of internal rpc method registry, reset to its initial state after each use"""
    # Performing a shallow copy is ok here, since we will only add or remove methods in the registry inside tests
    # If for any reason, an existing method have to be modified inside a test, a deep copy must be preferred here to
    # ensure strict isolation between tests
    _registry_dump = {**modernrpc.core.registry._registry}
    yield modernrpc.core.registry
    modernrpc.core.registry._registry = _registry_dump


class TestAppInit:
    """Test behaviors of AppConfig.ready() method, automatically called by Django at project startup"""

    @pytest.mark.parametrize("empty_value", [[], set(), tuple(), None])
    def test_registry_empty_if_settings_not_defined(
        self, settings, rpc_registry, empty_value
    ):
        # Update setting value to remove any value
        settings.MODERNRPC_METHODS_MODULES = empty_value

        app = apps.get_app_config("modernrpc")
        app.ready()

        # Registry is empty in such case
        assert not rpc_registry.get_all_method_names()

    @pytest.mark.parametrize(
        "module_name",
        [
            "invalid.module.reference",
            "testsite.rpc_methods_stub.module_with_invalid_import",
        ],
    )
    def test_app_init_with_module_not_found(self, settings, rpc_registry, module_name):
        settings.MODERNRPC_METHODS_MODULES = [module_name]

        app = apps.get_app_config("modernrpc")
        with pytest.raises(ImportError):
            app.ready()

        # Registry is empty in such case
        assert not rpc_registry.get_all_method_names()

    def test_app_init_with_syntax_error_in_module(self, settings, rpc_registry):
        # modernrpc / tests / testsite / rpc_methods_stub / module_with_syntax_errors
        settings.MODERNRPC_METHODS_MODULES = [
            "testsite.rpc_methods_stub.module_with_syntax_errors"
        ]

        app = apps.get_app_config("modernrpc")
        with pytest.raises(SyntaxError):
            app.ready()

        # Registry is empty in such case
        assert not rpc_registry.get_all_method_names()


class TestRegistry:
    """Test internal rpc registry methods"""

    def test_registry_empty_after_reset(self, rpc_registry):
        # Ensure a normal init registered some rpc methods
        assert len(rpc_registry.get_all_method_names()) > 0
        # Reset
        rpc_registry.reset()
        # After reset, no mre remote procedure in registry
        assert len(rpc_registry.get_all_method_names()) == 0

    def test_manual_registration(self, rpc_registry):
        assert "dummy_remote_procedure_1" not in rpc_registry.get_all_method_names()
        rpc_registry.register_method(dummy_remote_procedure_1)
        assert "dummy_remote_procedure_1" in rpc_registry.get_all_method_names()

    def test_double_registration(self, rpc_registry):
        # Registering twice is not a problem
        assert (
            rpc_registry.register_method(dummy_remote_procedure_1)
            == "dummy_remote_procedure_1"
        )
        assert (
            rpc_registry.register_method(dummy_remote_procedure_1)
            == "dummy_remote_procedure_1"
        )

    def test_manual_registration_with_different_name(self, rpc_registry):
        assert "another_name" not in rpc_registry.get_all_method_names()
        rpc_registry.register_method(dummy_remote_procedure_2)
        assert "another_name" in rpc_registry.get_all_method_names()
        assert "dummy_remote_procedure_2" not in rpc_registry.get_all_method_names()

    def test_invalid_custom_name(self, rpc_registry):
        exc_match = r'method names starting with "rpc." are reserved'
        with pytest.raises(ImproperlyConfigured, match=exc_match):
            rpc_registry.register_method(dummy_remote_procedure_3)

        assert "rpc.invalid.name" not in rpc_registry.get_all_method_names()
        assert "dummy_remote_procedure_3" not in rpc_registry.get_all_method_names()

    def test_duplicated_name(self, rpc_registry):
        exc_match = r"has already been registered"
        with pytest.raises(ImproperlyConfigured, match=exc_match):
            rpc_registry.register_method(dummy_remote_procedure_4)

    def test_wrong_manual_registration(self, rpc_registry):
        # Trying to register a method not decorated now raises an ImproperlyConfigured exception
        with pytest.raises(ImproperlyConfigured):
            rpc_registry.register_method(not_decorated_procedure)

    def test_method_names_list(self, rpc_registry):
        raw_list = rpc_registry.get_all_method_names()
        sorted_list = rpc_registry.get_all_method_names(sort_methods=True)

        assert len(raw_list) == len(sorted_list)
        assert raw_list != sorted_list

        for n in raw_list:
            assert n in sorted_list
        for n in sorted_list:
            assert n in raw_list

    def test_methods_list(self, rpc_registry):
        raw_list = rpc_registry.get_all_methods()
        sorted_list = rpc_registry.get_all_methods(sort_methods=True)

        assert len(raw_list) == len(sorted_list)
        assert raw_list != sorted_list

        for m in raw_list:
            assert m in sorted_list

        for m in sorted_list:
            assert m in raw_list

    # Tests for backward compatibility
    def test_backward_compat_register_method(self, rpc_registry):
        assert "dummy_remote_procedure_1" not in modernrpc.core.get_all_method_names()
        modernrpc.core.register_rpc_method(dummy_remote_procedure_1)
        assert "dummy_remote_procedure_1" in modernrpc.core.get_all_method_names()

    def test_backward_compat_registry(self, rpc_registry):
        assert rpc_registry.get_method("divide", ALL, ALL) == modernrpc.core.get_method(
            "divide", ALL, ALL
        )
        assert (
            rpc_registry.get_all_method_names() == modernrpc.core.get_all_method_names()
        )

        # registry.get_all_methods() return a dict_values instance
        # It needs to be casted to list to allow comparison
        assert list(rpc_registry.get_all_methods()) == list(
            modernrpc.core.get_all_methods()
        )

    def test_backward_compat_registry_reset(self, rpc_registry):
        # Ensure a normal init registered some rpc methods
        assert len(modernrpc.core.get_all_method_names()) > 0
        # Reset
        modernrpc.core.reset_registry()
        # After reset, no mre remote procedure in registry
        assert len(modernrpc.core.get_all_method_names()) == 0

    def test_get_methods(self, rpc_registry):
        methods = rpc_registry.get_all_methods(sort_methods=False)
        sorted_methods = rpc_registry.get_all_methods(sort_methods=True)

        assert methods != sorted_methods
        assert len(methods) == len(sorted_methods)
        # Ensure all methods from on is referenced in other
        assert all([method in sorted_methods for method in methods])
        assert all([method in methods for method in sorted_methods])
