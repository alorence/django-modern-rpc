# coding: utf-8
import json
import random
import re
import xml.etree.cElementTree as ET
from json import JSONDecodeError

import pytest
import requests
from django.core.serializers.json import DjangoJSONEncoder

from modernrpc.exceptions import (
    RPC_METHOD_NOT_FOUND,
    RPC_INVALID_PARAMS,
    RPC_INTERNAL_ERROR,
    RPC_INVALID_REQUEST,
    RPC_PARSE_ERROR,
    RPC_CUSTOM_ERROR_BASE,
)


class TestCommonErrors:
    @pytest.mark.parametrize(
        "method, params, exc_match, exc_code",
        [
            (
                "non_existing_method",
                [],
                r'Method not found: "non_existing_method"',
                RPC_METHOD_NOT_FOUND,
            ),
            (
                "add",
                [42],
                r"Invalid parameters: add\(\) missing 1 required positional argument",
                RPC_INVALID_PARAMS,
            ),
            (
                "add",
                [5, 9, 6],
                r"Invalid parameters: add\(\) takes 2 positional arguments but 3 were given",
                RPC_INVALID_PARAMS,
            ),
            (
                "divide",
                [50, 0],
                r"Internal error: division by zero",
                RPC_INTERNAL_ERROR,
            ),
            (
                "get_invalid_result",
                [],
                r"Unable to serialize result",
                RPC_INTERNAL_ERROR,
            ),
            (
                "raise_custom_exception",
                [],
                r"This is a test error",
                RPC_CUSTOM_ERROR_BASE + 5,
            ),
            # Data validity will be checked in JSON-RPC specific class:
            (
                "raise_custom_exception_with_data",
                [],
                r"This exception has additional data",
                RPC_CUSTOM_ERROR_BASE + 5,
            ),
        ],
    )
    def test_generic_errors(
        self, any_rpc_client, caplog, method, params, exc_match, exc_code
    ):
        with pytest.raises(
            any_rpc_client.error_response_exception, match=exc_match
        ) as exc_info:
            any_rpc_client.call(method, *params)
        any_rpc_client.assert_exception_code(exc_info.value, exc_code)

        assert re.search(exc_match, caplog.records[-1].message)


class TestJsonRpcSpecificBehaviors:
    @staticmethod
    def low_level_jsonrpc_call(url, payload, headers, raw_payload=None):
        data = raw_payload or json.dumps(payload, cls=DjangoJSONEncoder)
        return requests.post(url, data=data, headers=headers).json()

    def test_missing_method_name(
        self, live_server, endpoint_path, jsonrpc_content_type
    ):
        # Missing 'method' in payload

        headers = {"content-type": jsonrpc_content_type}
        payload = {
            # "method": 'add',
            "params": [5, 6],
            "jsonrpc": "2.0",
            "id": random.randint(1, 1000),
        }
        response = self.low_level_jsonrpc_call(
            live_server.url + endpoint_path, payload, headers=headers
        )

        assert 'Missing parameter "method"' in response["error"]["message"]
        assert RPC_INVALID_REQUEST == response["error"]["code"]

    def test_missing_version(self, live_server, endpoint_path, jsonrpc_content_type):
        # Missing 'jsonrpc' in payload

        headers = {"content-type": jsonrpc_content_type}
        payload = {
            "method": "add",
            "params": [5, 6],
            # "jsonrpc": "2.0",
            "id": random.randint(1, 1000),
        }
        response = self.low_level_jsonrpc_call(
            live_server.url + endpoint_path, payload, headers=headers
        )

        assert 'Missing parameter "jsonrpc"' in response["error"]["message"]
        assert RPC_INVALID_REQUEST == response["error"]["code"]

    def test_invalid_version(self, live_server, endpoint_path, jsonrpc_content_type):
        # Bad value for payload member 'jsonrpc'

        headers = {"content-type": jsonrpc_content_type}
        payload = {
            "method": "add",
            "params": [5, 6],
            "jsonrpc": "1.0",
            "id": random.randint(1, 1000),
        }
        response = self.low_level_jsonrpc_call(
            live_server.url + endpoint_path, payload, headers=headers
        )

        expected_error = 'Invalid request: Parameter "jsonrpc" has an unsupported value "1.0". It must be set to "2.0"'
        assert expected_error == response["error"]["message"]
        assert RPC_INVALID_REQUEST == response["error"]["code"]

    def test_invalid_payload(self, live_server, endpoint_path, jsonrpc_content_type):
        # Closing '}' is missing from this payload => invalid json data
        headers = {"content-type": jsonrpc_content_type}
        invalid_json_payload = """
            {
                "method": "add",
                "params": [},
                "jsonrpc": "2.0",
                "id": 74
            }
        """
        response = self.low_level_jsonrpc_call(
            live_server.url + endpoint_path,
            payload=None,
            headers=headers,
            raw_payload=invalid_json_payload,
        )

        assert "error" in response
        assert "result" not in response
        # On ParseError, JSON has not been properly deserialized, so the request ID can't be returned in error response
        assert response["id"] is None
        error = response["error"]

        assert "Parse error" in error["message"]
        assert "unable to read the request" in error["message"]
        assert error["code"] == RPC_PARSE_ERROR

    def test_invalid_payload_type(
        self, live_server, endpoint_path, jsonrpc_content_type
    ):
        # Json payload is not a struct or a list
        headers = {"content-type": jsonrpc_content_type}
        response = self.low_level_jsonrpc_call(
            live_server.url + endpoint_path, "10", headers=headers
        )

        assert "error" in response
        assert "result" not in response
        assert response["id"] is None
        error = response["error"]

        assert "Invalid JSON-RPC payload" in error["message"]
        assert error["code"] == RPC_INVALID_REQUEST

    def test_no_content_type(self, live_server, endpoint_path):
        payload = {
            "method": "add",
            "params": [5, 6],
            "jsonrpc": "2.0",
            "id": 51,
        }
        headers = {"content-type": ""}

        with pytest.raises(JSONDecodeError) as exc_info:
            self.low_level_jsonrpc_call(
                live_server.url + endpoint_path, payload, headers=headers
            )

        # requests 2.27 introduced a new JSONDecodeError subclass, moving the response content in a different attr
        response_str = getattr(exc_info.value, "doc", None) or getattr(
            exc_info.value, "strerror"
        )
        assert (
            "Unable to handle your request, the Content-Type header is mandatory"
            in response_str
        )

    def test_empty_id(self, live_server, endpoint_path, jsonrpc_content_type):
        headers = {"content-type": jsonrpc_content_type}
        payload = {
            "method": "add",
            "params": [5, 6],
            "jsonrpc": "2.0",
            "id": None,
        }

        response = self.low_level_jsonrpc_call(
            live_server.url + endpoint_path, payload, headers=headers
        )
        assert "error" in response
        assert "result" not in response
        assert response["id"] is None

        expected_error = (
            'Invalid request: Parameter "id" has an unsupported "null" value. It must be set to a positive '
            'integer value, or must be completely removed from request payload for special "notification" requests'
        )
        assert response["error"]["code"] == RPC_INVALID_REQUEST
        assert response["error"]["message"] == expected_error


class TestXmlRpcSpecificBehaviors:
    @staticmethod
    def low_level_xmlrpc_call(url, payload):
        response = requests.post(
            url, data=payload, headers={"content-type": "text/xml"}
        )
        tree = ET.fromstring(response.content)
        members = tree.find("fault").find("value").find("struct")

        code, message = "", ""
        for member in members:
            if member.find("name").text == "faultCode":
                code = int(member.find("value").find("int").text)
            elif member.find("name").text == "faultString":
                message = member.find("value").find("string").text

        return code, message

    def test_missing_method_name(self, live_server, endpoint_path):
        invalid_payload = """<?xml version="1.0"?>
    <methodCall>
      <params>
         <param>
            <value><double>2.41</double></value>
         </param>
      </params>
    </methodCall>"""
        code, message = self.low_level_xmlrpc_call(
            live_server.url + endpoint_path, payload=invalid_payload
        )

        assert (
            "Invalid request: Missing methodName. Please provide "
            "the name of the procedure you want to call" == message
        )
        assert code == RPC_INVALID_REQUEST

    def test_incomplete_payload(self, live_server, endpoint_path):
        invalid_payload = """<?xml version="1.0"?>
<methodCall>
</methodCall>"""
        code, message = self.low_level_xmlrpc_call(
            live_server.url + endpoint_path, payload=invalid_payload
        )

        assert "Invalid request: The request appear to be invalid." == message
        assert code == RPC_INVALID_REQUEST

    def test_invalid_payload(self, live_server, endpoint_path):
        # "</methodName" misses the closing '>'
        invalid_payload = """<?xml version="1.0"?>
    <methodCall>
      <methodName>examples.getStateName</methodName
      <params>
         <param>
            <value><double>2.41</double></value>
         </param>
      </params>
    </methodCall>"""
        code, message = self.low_level_xmlrpc_call(
            live_server.url + endpoint_path, payload=invalid_payload
        )

        assert "not well-formed" in message
        assert code == RPC_PARSE_ERROR

    def test_invalid_json_payload(self, live_server, endpoint_path):
        invalid_payload = json.dumps(
            {
                "method": "add",
                "params": [5, 6],
                "jsonrpc": "2.0",
                "id": 42,
            }
        )
        code, message = self.low_level_xmlrpc_call(
            live_server.url + endpoint_path, payload=invalid_payload
        )

        assert "not well-formed" in message
        assert code == RPC_PARSE_ERROR

    def test_bad_type_value(self, live_server, endpoint_path):
        invalid_payload = """<?xml version="1.0"?>
<methodCall>
  <methodName>examples.getStateName</methodName
  <params>
     <param>
        <value><double>2.41</double></value>
     </param>
  </params>
</methodCall>"""
        code, message = self.low_level_xmlrpc_call(
            live_server.url + endpoint_path, payload=invalid_payload
        )

        assert "not well-formed" in message
        assert code == RPC_PARSE_ERROR
