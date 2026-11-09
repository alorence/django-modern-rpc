import asyncio
from http import HTTPStatus
from typing import TYPE_CHECKING, cast

import pytest

from modernrpc import RpcServer
from modernrpc.exceptions import RPC_INTERNAL_ERROR, RPC_INVALID_PARAMS, RPC_METHOD_NOT_FOUND, RPC_PARSE_ERROR
from tests.helpers import XmlRpcRF, extract_xmlrpc_fault_data, extract_xmlrpc_success_result

if TYPE_CHECKING:
    from unittest.mock import Mock


@pytest.mark.usefixtures("all_xml_deserializers", "all_xml_serializers")
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
class TestXmlRpcAsyncView:
    async def test_standard_call(self, xmlrpc_rf: XmlRpcRF, server: RpcServer, asynchronous: bool):
        method_name = "async_simple_procedure" if asynchronous else "simple_procedure"
        request = xmlrpc_rf(method_name=method_name, params=["bar", 42])

        response = await server.async_view(request)

        assert response.status_code == HTTPStatus.OK
        assert extract_xmlrpc_success_result(response) == "foo='bar' bar=42"
        cast("Mock", server.on_error).assert_not_called()

    async def test_procedure_exception(self, xmlrpc_rf: XmlRpcRF, server: RpcServer, asynchronous: bool):
        method_name = "async_simple_procedure" if asynchronous else "simple_procedure"
        request = xmlrpc_rf(method_name=method_name, params=["bar", -2])

        response = await server.async_view(request)

        assert response.status_code == HTTPStatus.OK
        code, message = extract_xmlrpc_fault_data(response)
        assert code == RPC_INTERNAL_ERROR
        assert message == "Internal error"
        cast("Mock", server.on_error).assert_called_once()

    async def test_invalid_xml_payload_request(self, xmlrpc_rf: XmlRpcRF, server: RpcServer, asynchronous: bool):
        method_name = "async_simple_procedure" if asynchronous else "simple_procedure"
        request = xmlrpc_rf(method_name=method_name, params=["bar", 11])
        request._body = request.body.replace(b"<value>", b"!value>")  # noqa: SLF001

        response = await server.async_view(request)

        assert response.status_code == HTTPStatus.OK
        code, message = extract_xmlrpc_fault_data(response)
        assert code == RPC_PARSE_ERROR
        assert "Parse error, unable to read the request:" in message
        cast("Mock", server.on_error).assert_called_once()

    async def test_invalid_params(self, xmlrpc_rf: XmlRpcRF, server: RpcServer, asynchronous: bool):
        method_name = "async_simple_procedure" if asynchronous else "simple_procedure"
        request = xmlrpc_rf(method_name=method_name, params=["bar", "baz", -111])

        response = await server.async_view(request)

        assert response.status_code == HTTPStatus.OK
        code, message = extract_xmlrpc_fault_data(response)
        assert code == RPC_INVALID_PARAMS
        assert message == "Invalid parameters: too many positional arguments"
        cast("Mock", server.on_error).assert_called_once()

    async def test_invalid_result(self, xmlrpc_rf: XmlRpcRF, server: RpcServer, asynchronous: bool):
        method_name = "async_unserializable_result_procedure" if asynchronous else "unserializable_result_procedure"
        request = xmlrpc_rf(method_name=method_name, params=[])

        response = await server.async_view(request)

        assert response.status_code == HTTPStatus.OK
        code, message = extract_xmlrpc_fault_data(response)
        assert code == RPC_INTERNAL_ERROR
        assert message == "Internal error"
        cast("Mock", server.on_error).assert_called_once()

    async def test_system_list_methods(self, xmlrpc_rf: XmlRpcRF, server: RpcServer, asynchronous: bool):
        request = xmlrpc_rf(method_name="system.listMethods")

        response = await server.async_view(request)

        assert response.status_code == HTTPStatus.OK
        assert extract_xmlrpc_success_result(response) == [
            "system.listMethods",
            "system.methodSignature",
            "system.methodHelp",
            "system.multicall",
            "simple_procedure",
            "unserializable_result_procedure",
            "async_simple_procedure",
            "async_unserializable_result_procedure",
            "async_cancelled_procedure",
        ]
        cast("Mock", server.on_error).assert_not_called()

    async def test_system_method_signature(self, xmlrpc_rf: XmlRpcRF, server: RpcServer, asynchronous: bool):
        method_name = "async_simple_procedure" if asynchronous else "simple_procedure"
        request = xmlrpc_rf(method_name="system.methodSignature", params=[method_name])
        response = await server.async_view(request)
        assert response.status_code == HTTPStatus.OK
        assert extract_xmlrpc_success_result(response) == [["undef", "str", "int"]]
        cast("Mock", server.on_error).assert_not_called()

    async def test_system_method_help(self, xmlrpc_rf: XmlRpcRF, server: RpcServer, asynchronous: bool):
        method_name = "async_simple_procedure" if asynchronous else "simple_procedure"
        request = xmlrpc_rf(method_name="system.methodHelp", params=[method_name])
        response = await server.async_view(request)
        assert response.status_code == HTTPStatus.OK
        assert (
            extract_xmlrpc_success_result(response)
            == "Return a simple string when the given 'bar' is positive, raise ValueError when it is negative"
        )
        cast("Mock", server.on_error).assert_not_called()

    async def test_system_method_signature_invalid_arg(
        self, xmlrpc_rf: XmlRpcRF, server: RpcServer, asynchronous: bool
    ):
        request = xmlrpc_rf(method_name="system.methodSignature", params=["non_existant_method"])
        response = await server.async_view(request)
        assert response.status_code == HTTPStatus.OK
        code, message = extract_xmlrpc_fault_data(response)
        assert code == RPC_METHOD_NOT_FOUND
        assert message == 'Method not found: "non_existant_method"'
        cast("Mock", server.on_error).assert_called_once()

    async def test_system_method_help_invalid_arg(self, xmlrpc_rf: XmlRpcRF, server: RpcServer, asynchronous: bool):
        request = xmlrpc_rf(method_name="system.methodHelp", params=["non_existant_method"])
        response = await server.async_view(request)
        assert response.status_code == HTTPStatus.OK
        code, message = extract_xmlrpc_fault_data(response)
        assert code == RPC_METHOD_NOT_FOUND
        assert message == 'Method not found: "non_existant_method"'
        cast("Mock", server.on_error).assert_called_once()


@pytest.mark.usefixtures("all_xml_deserializers", "all_xml_serializers")
class TestXmlRpcAsyncMulticall:
    async def test_multicall_standard(self, xmlrpc_rf: XmlRpcRF, server_using_sync_or_async_multicall: RpcServer):
        mc_params = [
            [
                {"methodName": "simple_procedure", "params": ("xxx", 20)},
                {"methodName": "simple_procedure", "params": ("yyy", -20)},
                {"methodName": "async_simple_procedure", "params": ("xxx", 20)},
                {"methodName": "async_simple_procedure", "params": ("yyy", -20)},
            ]
        ]
        request = xmlrpc_rf(method_name="system.multicall", params=mc_params)

        response = await server_using_sync_or_async_multicall.async_view(request)

        assert response.status_code == HTTPStatus.OK
        assert extract_xmlrpc_success_result(response) == [
            ["foo='xxx' bar=20"],
            {"faultCode": -32603, "faultString": "Internal error"},
            ["foo='xxx' bar=20"],
            {"faultCode": -32603, "faultString": "Internal error"},
        ]
        assert cast("Mock", server_using_sync_or_async_multicall.on_error).call_count == 2

    async def test_multicall_missing_params(self, xmlrpc_rf: XmlRpcRF, server_using_sync_or_async_multicall: RpcServer):
        """Ensure multicall works when a call entry has no 'params' key."""
        mc_params = [
            [
                {"methodName": "simple_procedure", "params": ("xxx", 20)},
                {"methodName": "system.listMethods"},
            ]
        ]
        request = xmlrpc_rf(method_name="system.multicall", params=mc_params)

        response = await server_using_sync_or_async_multicall.async_view(request)

        assert response.status_code == HTTPStatus.OK
        result = extract_xmlrpc_success_result(response)
        assert result[0] == ["foo='xxx' bar=20"]
        assert isinstance(result[1], list)  # listMethods returns a list
        cast("Mock", server_using_sync_or_async_multicall.on_error).assert_not_called()

    async def test_multicall_cancelled_procedure(
        self, xmlrpc_rf: XmlRpcRF, server_using_sync_or_async_multicall: RpcServer
    ):
        """Ensure a task cancellation raised by one call of a multicall is propagated, not converted to an RPC fault"""
        mc_params = [
            [
                {"methodName": "simple_procedure", "params": ("xxx", 20)},
                {"methodName": "async_cancelled_procedure"},
                {"methodName": "async_simple_procedure", "params": ("yyy", 20)},
            ]
        ]
        request = xmlrpc_rf(method_name="system.multicall", params=mc_params)

        with pytest.raises(asyncio.CancelledError):
            await server_using_sync_or_async_multicall.async_view(request)

        cast("Mock", server_using_sync_or_async_multicall.on_error).assert_not_called()

    async def test_multicall_invalid_params_1(
        self, xmlrpc_rf: XmlRpcRF, server_using_sync_or_async_multicall: RpcServer
    ):
        mc_params = ["foo.bar"]
        request = xmlrpc_rf(method_name="system.multicall", params=mc_params)

        response = await server_using_sync_or_async_multicall.async_view(request)

        assert response.status_code == HTTPStatus.OK
        code, message = extract_xmlrpc_fault_data(response)
        assert code == RPC_INVALID_PARAMS
        assert message == "Invalid parameters: system.multicall first argument should be a list, str given."
        cast("Mock", server_using_sync_or_async_multicall.on_error).assert_called_once()

    async def test_multicall_invalid_params_2(
        self, xmlrpc_rf: XmlRpcRF, server_using_sync_or_async_multicall: RpcServer
    ):
        mc_params = [
            {
                "calls": [
                    {"methodName": "simple_procedure", "params": ("xxx", 20)},
                    {"methodName": "simple_procedure", "params": ("yyy", -20)},
                    {"methodName": "async_simple_procedure", "params": ("xxx", 20)},
                    {"methodName": "async_simple_procedure", "params": ("yyy", -20)},
                ]
            }
        ]
        request = xmlrpc_rf(method_name="system.multicall", params=mc_params)

        response = await server_using_sync_or_async_multicall.async_view(request)

        assert response.status_code == HTTPStatus.OK
        code, message = extract_xmlrpc_fault_data(response)
        assert code == RPC_INVALID_PARAMS
        assert message == "Invalid parameters: system.multicall first argument should be a list, dict given."
        cast("Mock", server_using_sync_or_async_multicall.on_error).assert_called_once()
