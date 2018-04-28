# coding: utf-8
import datetime

from modernrpc.conf import settings
from modernrpc.tests.test_registry import not_decorated_procedure
from modernrpc.tests.test_rpc_method_object import dummy_function_with_doc
from .test_registry import dummy_remote_procedure_1, dummy_remote_procedure_2, dummy_remote_procedure_3, \
    dummy_remote_procedure_4
from .test_rpc_method_object import dummy_function, single_line_documented, multi_line_documented_1, \
    multi_line_documented_2
from .testsite.rpc_methods_stub.generic import existing_but_not_decorated, another_name
from .testsite.rpc_methods_stub.with_authentication import logged_user_required_alt, logged_superuser_required_alt, \
    power_2


def test_not_called_functions():
    # These functions are used only to test registering, but they are never called.
    # We call them now, so coverage doesn't report error
    existing_but_not_decorated()
    not_decorated_procedure()
    dummy_remote_procedure_1()
    dummy_remote_procedure_2()
    dummy_remote_procedure_3()
    dummy_remote_procedure_4()
    dummy_function()
    dummy_function_with_doc('john', datetime.datetime.now(), 'Male')
    single_line_documented()
    multi_line_documented_1()
    multi_line_documented_2()
    logged_user_required_alt(20)
    logged_superuser_required_alt(6)
    another_name()
    power_2(5)
    # We need to access a Django-only setting at least once
    assert bool(settings.SECRET_KEY)
