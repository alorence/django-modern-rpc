from __future__ import annotations

import json
import xmlrpc.client
from doctest import Example
from json import JSONDecodeError
from typing import TYPE_CHECKING, Any, Callable
from xml.etree import ElementTree as ET

import jsonrpcclient.sentinels
import pytest
from lxml.doctestcompare import PARSE_XML, LXMLOutputChecker

from modernrpc import Protocol
from modernrpc.helpers import ensure_sequence
from modernrpc.jsonrpc.backends._json import PythonJsonBackend
from modernrpc.jsonrpc.backends._orjson import OrjsonBackend
from modernrpc.jsonrpc.backends._rapidjson import RapidJsonBackend
from modernrpc.jsonrpc.backends._simplejson import SimpleJsonBackend
from modernrpc.xmlrpc.backends._etree import EtreeBackend
from modernrpc.xmlrpc.backends._lxml import LxmlBackend
from modernrpc.xmlrpc.backends._xmlrpc import PythonXmlRpcBackend
from modernrpc.xmlrpc.backends._xmltodict import XmlToDictBackend

if TYPE_CHECKING:
    from django.http import HttpResponse

ALL_PROTOCOLS = [Protocol.XML_RPC, Protocol.JSON_RPC]
# List all backends supported in tests for deserialization (data to request object) and
# serialization (result to response data). These constants will be used to define some parametrized fixtures
# to ensure every test is run with all backend combinations
XML_DESERIALIZERS_CLASSES = [PythonXmlRpcBackend, XmlToDictBackend, EtreeBackend, LxmlBackend]
XML_SERIALIZERS_CLASSES = [PythonXmlRpcBackend, XmlToDictBackend, EtreeBackend, LxmlBackend]
JSON_DESERIALIZERS_CLASSES = [PythonJsonBackend, SimpleJsonBackend, OrjsonBackend, RapidJsonBackend]
JSON_SERIALIZERS_CLASSES = [PythonJsonBackend, SimpleJsonBackend, OrjsonBackend, RapidJsonBackend]


def build_xml_rpc_request_data(method="dummy", params=()) -> str:
    return xmlrpc.client.dumps(methodname=method, params=tuple(params))


def build_json_rpc_request_data(method="dummy", params=(), is_notification=False, req_id=None) -> dict[str, Any]:
    if params:
        params = ensure_sequence(params)
    if is_notification:
        return jsonrpcclient.notification(method=method, params=params)
    return jsonrpcclient.request(method=method, params=params, id=req_id or jsonrpcclient.sentinels.NOID)


def assert_json_data_are_equal(got: str, want: str) -> None:
    # NOTE: At some point, jsondiff may be used for better JSON data comparison. For now,
    #  comparing json.loads() results seems to work well for our use cases
    assert json.loads(got) == json.loads(want)


def assert_xml_data_are_equal(got: str, want: str) -> None:
    checker = LXMLOutputChecker()
    bgot, bwant = got.encode(), want.encode()
    if not checker.check_output(bgot, bwant, PARSE_XML):
        pytest.fail(checker.output_difference(Example("", want), bgot, PARSE_XML))


def extract_xmlrpc_success_result(response: HttpResponse) -> Any:
    data, _ = xmlrpc.client.loads(response.content.decode(), use_datetime=True, use_builtin_types=True)
    return data[0]


def extract_xmlrpc_fault_data(response: HttpResponse) -> tuple[int, str]:
    # TODO : use xmlrpc.client.loads()?
    try:
        root = ET.fromstring(response.content)
    except ET.ParseError:
        pytest.fail(f"Unable to parse XML payload:\n{response.content}")
        raise

    fault_code = root.find("./fault/value/struct/member/name[.='faultCode']/../value/int")
    fault_string = root.find("./fault/value/struct/member/name[.='faultString']/../value/string")

    if fault_code is None:
        pytest.fail("No faultCode found!")
    if fault_string is None:
        pytest.fail("No faultString found!")

    try:
        fault_code_value = int(fault_code.text)
    except ValueError:
        pytest.fail(f'Unable to parse faultCode "{fault_code.text}" as int')
        raise

    return fault_code_value, fault_string.text


def extract_jsonrpc_success_result(response: HttpResponse) -> Any:
    try:
        response_data = json.loads(response.content)
    except JSONDecodeError:
        pytest.fail(f"Unable to parse JSON payload:\n{response.content.decode()}")
        raise

    try:
        result = response_data["result"]
    except KeyError:
        pytest.fail(f'Unable to extract result from payload "{response_data}"')
        raise

    return result


def extract_jsonrpc_fault_data(response: HttpResponse) -> tuple[int, str]:
    try:
        response_data = json.loads(response.content)
    except JSONDecodeError:
        pytest.fail(f"Unable to parse JSON payload:\n{response.content.decode()}")
        raise

    try:
        error_data = response_data["error"]
    except KeyError:
        pytest.fail(f'Unable to extract error datat from payload "{response_data}"')
        raise

    try:
        err_code = int(error_data["code"])
    except KeyError:
        pytest.fail(f'Unable to extract error code from payload "{response_data}"')
        raise
    except ValueError:
        pytest.fail(f'Unable to convert error code "{error_data["code"]}" to int')
        raise

    try:
        message = error_data["message"]
    except KeyError:
        pytest.fail(f'Unable to extract error message from payload "{response_data}"')
        raise

    return err_code, message


def params_with_xfail(possible_values: list, condition: Callable, reason: str):
    """
    Build a list of replacement value for a fixture containing one or more xfail instances (depending on condition)
    """
    return [
        pytest.param(element, marks=pytest.mark.xfail(reason=reason)) if condition(element) else element
        for element in possible_values
    ]
