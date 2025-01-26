# PEP 585: use of list[Any] instead of List[Any] is available since Python 3.9, enable it for older versions
# PEP 604: use of typeA | typeB is available since Python 3.10, enable it for older versions
from __future__ import annotations

from typing import Any

from modernrpc.exceptions import RPCInvalidRequest
from modernrpc.handlers.base import GenericRpcErrorResult, JsonRpcRequest, JsonRpcResult


class Unmarshaller:
    def dict_to_request(self, structured_data: dict[str, Any] | list[dict]) -> JsonRpcRequest | list[JsonRpcRequest]:
        if isinstance(structured_data, list):
            return [self.dict_to_request(data) for data in structured_data]

        try:
            method_name = structured_data["method"]
        except KeyError as e:
            raise RPCInvalidRequest("Unable to find method name", data=structured_data) from e

        params = structured_data.get("params")
        args = params if isinstance(params, (list, tuple)) else []
        kwargs = params if isinstance(params, dict) else {}

        # Standard request (with "id" field)
        if "id" in structured_data:
            return JsonRpcRequest(
                request_id=structured_data["id"],
                method_name=method_name,
                args=args,
                kwargs=kwargs,
            )

        # Notification request
        return JsonRpcRequest(
            method_name=method_name,
            args=args,
            kwargs=kwargs,
        )


class Marshaller:
    def result_to_dict(
        self, result: JsonRpcResult | list[JsonRpcResult]
    ) -> list[dict[str, Any]] | dict[str, Any] | None:
        if isinstance(result, list):
            return [self.result_to_dict(r) for r in result]

        if result.request.is_notification:
            return None

        base_result = {
            "id": result.request.request_id,
            "jsonrpc": result.request.jsonrpc,
        }

        if isinstance(result, GenericRpcErrorResult):
            response_payload = {
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
