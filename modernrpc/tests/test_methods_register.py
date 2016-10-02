# coding: utf-8
import pytest
from django.core.exceptions import ImproperlyConfigured

from modernrpc.core import register_method
from rpc_methods_stub.not_decorated import func_a, func_b


def test_redundant_names():

    # func_a is registered once, it's OK
    register_method(func_a)

    # We try to register another function, with an existing name => error
    with pytest.raises(ImproperlyConfigured) as e:
        register_method(func_b, 'func_a')
        assert 'func_a has already been registered' in e.value
