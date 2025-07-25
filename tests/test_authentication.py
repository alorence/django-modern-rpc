from unittest.mock import Mock

import pytest

from modernrpc import RpcRequestContext
from modernrpc.constants import NOT_SET
from modernrpc.core import ProcedureWrapper
from modernrpc.exceptions import AuthenticationError


def dummy():
    return 42


class TestProcedureAuth:
    @pytest.fixture
    def req(self, xmlrpc_rf):
        return xmlrpc_rf()

    @pytest.fixture
    def context(self, req, server):
        handler = server.get_request_handler(req)
        return RpcRequestContext(req, server, handler, handler.protocol)

    async def test_auth_not_set(self, req, context):
        wrapper = ProcedureWrapper(dummy)

        assert wrapper.auth is NOT_SET
        assert wrapper.check_permissions(req) is True

        assert wrapper.execute(context) == 42
        assert await wrapper.aexecute(context) == 42

    def test_auth_none(self, req, context):
        wrapper = ProcedureWrapper(dummy, auth=None)

        assert wrapper.auth is None
        assert wrapper.check_permissions(req) is True

        assert wrapper.execute(context) == 42

    @pytest.mark.parametrize(
        "auth_result",
        [
            object(),
            True,
            12345,
            "john.doe",
        ],
    )
    async def test_single_auth_returns_ok(self, req, context, auth_result):
        auth_callback = Mock(return_value=auth_result)

        wrapper = ProcedureWrapper(dummy, auth=auth_callback)

        assert wrapper.auth is auth_callback

        assert bool(wrapper.check_permissions(req)) is True
        assert wrapper.check_permissions(req) is auth_result

        assert wrapper.execute(context) == 42
        assert await wrapper.aexecute(context) == 42

    @pytest.mark.parametrize("auth_result", [False, None, 0, ""])
    async def test_single_auth_returns_ko(self, req, context, auth_result):
        auth_callback = Mock(return_value=auth_result)
        wrapper = ProcedureWrapper(dummy, auth=auth_callback)

        assert wrapper.auth is auth_callback

        with pytest.raises(AuthenticationError):
            wrapper.check_permissions(req)

        with pytest.raises(AuthenticationError):
            wrapper.execute(context)

        with pytest.raises(AuthenticationError):
            await wrapper.aexecute(context)

    @pytest.mark.parametrize("exception_klass", [KeyError, ValueError, TypeError, RuntimeError])
    async def test_single_auth_raises_exception(self, req, context, exception_klass):
        auth_callback = Mock(side_effect=exception_klass)
        wrapper = ProcedureWrapper(dummy, auth=auth_callback)

        assert wrapper.auth is auth_callback

        with pytest.raises(exception_klass):
            wrapper.check_permissions(req)

        with pytest.raises(AuthenticationError):
            wrapper.execute(context)

        with pytest.raises(AuthenticationError):
            await wrapper.aexecute(context)

    async def test_multiple_auth(self, req, context):
        auth_callbacks = [Mock(), Mock()]

        wrapper = ProcedureWrapper(dummy, auth=auth_callbacks)
        assert wrapper.auth is auth_callbacks

        assert wrapper.check_permissions(req) == auth_callbacks[0].return_value

        assert wrapper.execute(context) == 42
        assert await wrapper.aexecute(context) == 42

    async def test_multiple_auth_false_true(self, req, context):
        ok_result = object()
        auth_callbacks = [Mock(return_value=False), Mock(return_value=ok_result)]

        wrapper = ProcedureWrapper(dummy, auth=auth_callbacks)
        check_perms_result = wrapper.check_permissions(req)

        assert bool(check_perms_result) is True
        assert check_perms_result is ok_result

        auth_callbacks[0].assert_called_once()
        auth_callbacks[1].assert_called_once()

        assert wrapper.execute(context) == 42
        assert await wrapper.aexecute(context) == 42

    async def test_multiple_auth_true_false(self, req, context):
        ok_result = object()
        auth_callbacks = [Mock(return_value=ok_result), Mock(return_value=False)]

        wrapper = ProcedureWrapper(dummy, auth=auth_callbacks)
        check_perms_result = wrapper.check_permissions(req)

        assert bool(check_perms_result) is True
        assert check_perms_result is ok_result

        auth_callbacks[0].assert_called_once()
        auth_callbacks[1].assert_not_called()

        assert wrapper.execute(context) == 42
        assert await wrapper.aexecute(context) == 42
