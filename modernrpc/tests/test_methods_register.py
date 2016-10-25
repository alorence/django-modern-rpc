# coding: utf-8
import pytest
from django.core.exceptions import ImproperlyConfigured

from modernrpc.core import register_method
from testsite.rpc_methods_stub.not_decorated import func_a, func_b, func_c, full_documented_method


def test_redundant_names():

    # func_a is registered once, it's OK
    register_method(func_a)

    # We try to register another function, with an existing name => error
    with pytest.raises(ImproperlyConfigured) as excinfo:
        register_method(func_b, 'func_a')
    assert 'func_a has already been registered' in str(excinfo.value)


def test_reserved_names():

    with pytest.raises(ImproperlyConfigured) as excinfo:
        register_method(func_c(), 'rpc.func_c')
    assert 'method names starting with "rpc." are reserved' in str(excinfo.value)


def test_register_twice():
    # Registering twice or more the same method is OK, no exception should be raised
    register_method(full_documented_method)
    register_method(full_documented_method)
