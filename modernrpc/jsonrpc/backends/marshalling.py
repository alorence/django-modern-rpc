# PEP 585: use of list[Any] instead of List[Any] is available since Python 3.9, enable it for older versions
# PEP 604: use of typeA | typeB is available since Python 3.10, enable it for older versions
from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, overload

from modernrpc.constants import NOT_SET
from modernrpc.exceptions import RPCInvalidRequest
from modernrpc.jsonrpc.handler import JsonRpcRequest
from modernrpc.types import DictStrAny, RpcErrorResult

try:
    # types.NoneType is available only with Python 3.10+
    from types import NoneType
except ImportError:
    NoneType = type(None)  # type: ignore[misc]

if TYPE_CHECKING:
    from modernrpc.jsonrpc.handler import JsonRpcResult


class Unmarshaller:
    def __init__(self, validate_version: bool = True):
        self.validate_version = validate_version

    def validate_dict_request(self, request_data: DictStrAny) -> None:
        if "method" not in request_data:
            raise RPCInvalidRequest("Unable to find method name", data=request_data)

        if "jsonrpc" not in request_data:
            raise RPCInvalidRequest("jsonrpc required")

        if self.validate_version and request_data["jsonrpc"] != "2.0":
            raise RPCInvalidRequest(
                f'Parameter "jsonrpc" has an unsupported value "{request_data["jsonrpc"]}". It must be set to "2.0"'
            )

        # Notification request won't have "id" field
        # None is also an allowed value. Both cases are valid
        request_id = request_data.get("id")
        if type(request_id) not in (NoneType, int, float, str):
            raise RPCInvalidRequest(
                'Parameter "id" has an unsupported value. According to JSON-RPC 2.0 standard, it must '
                f"be a String, a Number or a Null value. Found: {type(request_id)}"
            )

    @overload
    def dict_to_request(self, structured_data: DictStrAny) -> JsonRpcRequest: ...

    @overload
    def dict_to_request(self, structured_data: list[DictStrAny]) -> list[JsonRpcRequest]: ...

    def dict_to_request(self, structured_data: DictStrAny | list[DictStrAny]) -> JsonRpcRequest | list[JsonRpcRequest]:
        if isinstance(structured_data, list):
            return [self.dict_to_request(data) for data in structured_data]

        self.validate_dict_request(structured_data)

        method_name = structured_data["method"]
        params = structured_data.get("params")
        args = params if isinstance(params, (list, tuple)) else []
        kwargs = params if isinstance(params, dict) else {}

        # Build request object. If "id" not in data, it's a notification request: request_id == NOT_SET
        return JsonRpcRequest(
            request_id=structured_data.get("id", NOT_SET),
            method_name=method_name,
            args=args,
            kwargs=kwargs,
        )


class Marshaller:
    @overload
    def result_to_dict(self, result: JsonRpcResult) -> DictStrAny | None: ...

    @overload
    def result_to_dict(self, result: Iterable[JsonRpcResult]) -> list[DictStrAny | None]: ...

    def result_to_dict(
        self, result: JsonRpcResult | Iterable[JsonRpcResult]
    ) -> DictStrAny | None | list[DictStrAny | None]:
        if isinstance(result, Iterable):
            return [self.result_to_dict(r) for r in result]

        if result.request.is_notification:
            return None

        base_result = {
            "id": result.request.request_id,
            "jsonrpc": result.request.jsonrpc,
        }

        if isinstance(result, RpcErrorResult):
            response_payload: DictStrAny = {
                **base_result,
                "error": {
                    "code": result.code,
                    "message": result.message,
                },
            }
            if result.data:
                response_payload["error"]["data"] = result.data
            return response_payload

        return {
            **base_result,
            "result": result.data,
        }
