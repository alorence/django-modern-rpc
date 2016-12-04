# coding: utf-8
import datetime

import pytest

from modernrpc.config import settings
from modernrpc.exceptions import RPCException
from modernrpc.handlers.base import RPCHandler
from test_methods_register import another_dummy_method
from test_rpc_method_object import dummy_function, single_line_documented, multi_line_documented_1, \
    multi_line_documented_2
from testsite.rpc_methods_stub.generic import existing_but_not_decorated
from testsite.rpc_methods_stub.not_decorated import full_documented_method, func_a, func_b, func_c, \
    another_not_decorated
from testsite.rpc_methods_stub.with_authentication import logged_user_required_alt, logged_superuser_required_alt


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
    dummy_function()
    single_line_documented()
    multi_line_documented_1()
    multi_line_documented_2()
    logged_user_required_alt(20)
    logged_superuser_required_alt(6)
    assert True


class MyBadHandler(RPCHandler):
    pass


def test_bad_handler_definition(rf):

    request = rf.get('/rpc')

    h = MyBadHandler(request, settings.MODERNRPC_DEFAULT_ENTRYPOINT_NAME)
    with pytest.raises(NotImplementedError):
        h.loads("")
    with pytest.raises(NotImplementedError):
        h.dumps({"x": "y"})
    with pytest.raises(NotImplementedError):
        MyBadHandler.valid_content_types()
    with pytest.raises(NotImplementedError):
        h.parse_request()
    with pytest.raises(NotImplementedError):
        h.result_success(42)
    with pytest.raises(NotImplementedError):
        h.result_error(RPCException(1, ''))
