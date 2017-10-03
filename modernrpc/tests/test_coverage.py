# coding: utf-8
import datetime

from modernrpc.conf import settings
from test_methods_register import another_dummy_method, another_dummy_method_2, another_dummy_method_3, \
    another_dummy_method_4
from test_rpc_method_object import dummy_function, single_line_documented, multi_line_documented_1, \
    multi_line_documented_2
from testsite.rpc_methods_stub.generic import existing_but_not_decorated, another_name
from testsite.rpc_methods_stub.not_decorated import full_documented_method, func_a, func_b, func_c, \
    another_not_decorated
from testsite.rpc_methods_stub.with_authentication import logged_user_required_alt, logged_superuser_required_alt, \
    power_2


def test_not_called_functions():
    # These functions are used only to test registering, but they are never called.
    # We call them now, so coverage doesn't report error
    func_a()
    func_b()
    func_c()
    full_documented_method('john', datetime.datetime.now(), 'Male')
    existing_but_not_decorated()
    another_not_decorated()
    another_dummy_method()
    another_dummy_method_2()
    another_dummy_method_3()
    another_dummy_method_4()
    dummy_function()
    single_line_documented()
    multi_line_documented_1()
    multi_line_documented_2()
    logged_user_required_alt(20)
    logged_superuser_required_alt(6)
    another_name()
    power_2(5)
    # We need to access a Django-only setting at least once
    assert bool(settings.SECRET_KEY)
