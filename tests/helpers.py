from __future__ import annotations

import json
import xmlrpc.client
from doctest import Example
from json import JSONDecodeError
from typing import TYPE_CHECKING, Any, Callable
from xml.etree import ElementTree as ET

import jsonrpcclient.sentinels
import pytest
from _pytest.main import Failed
from lxml.doctestcompare import PARSE_XML, LXMLOutputChecker  # ty: ignore[unresolved-import]

from modernrpc import Protocol
from modernrpc.jsonrpc.backends.json import PythonJsonDeserializer, PythonJsonSerializer
from modernrpc.jsonrpc.backends.orjson import OrjsonDeserializer, OrjsonSerializer
from modernrpc.jsonrpc.backends.rapidjson import RapidjsonDeserializer, RapidjsonSerializer
from modernrpc.jsonrpc.backends.simplejson import SimplejsonDeserializer, SimplejsonSerializer
from modernrpc.xmlrpc.backends.etree import EtreeDeserializer, EtreeSerializer
from modernrpc.xmlrpc.backends.lxml import LxmlDeserializer, LxmlSerializer
from modernrpc.xmlrpc.backends.xmlrpc import PythonXmlRpcDeserializer, PythonXmlRpcSerializer
from modernrpc.xmlrpc.backends.xmltodict import XmlToDictDeserializer, XmlToDictSerializer

if TYPE_CHECKING:
    from django.http import HttpResponse

    from modernrpc.jsonrpc.handler import RequestIdType
    from modernrpc.types import DictStrAny

ALL_PROTOCOLS = [Protocol.XML_RPC, Protocol.JSON_RPC]
# List all backends supported in tests for deserialization (data to request object) and
# serialization (result to response data). These constants will be used to define some parametrized fixtures
# to ensure every test is run with all backend combinations
XML_DESERIALIZERS_CLASSES = [PythonXmlRpcDeserializer, XmlToDictDeserializer, EtreeDeserializer, LxmlDeserializer]
XML_SERIALIZERS_CLASSES = [PythonXmlRpcSerializer, XmlToDictSerializer, EtreeSerializer, LxmlSerializer]
JSON_DESERIALIZERS_CLASSES = [PythonJsonDeserializer, SimplejsonDeserializer, OrjsonDeserializer, RapidjsonDeserializer]
JSON_SERIALIZERS_CLASSES = [PythonJsonSerializer, SimplejsonSerializer, OrjsonSerializer, RapidjsonSerializer]


def build_xml_rpc_request_data(method="dummy", params=()) -> str:
    return xmlrpc.client.dumps(methodname=method, params=tuple(params))


def build_json_rpc_request_data(
    method="dummy", params: tuple = (), is_notification=False, req_id: RequestIdType = None
) -> DictStrAny:
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
    except ET.ParseError as e:
        raise Failed(f"Unable to parse XML payload:\n{response.content}") from e

    fault_code = root.find("./fault/value/struct/member/name[.='faultCode']/../value/int")
    fault_string = root.find("./fault/value/struct/member/name[.='faultString']/../value/string")

    if fault_code is None:
        raise Failed("No faultCode found!")
    if fault_string is None:
        raise Failed("No faultString found!")

    try:
        fault_code_value = int(fault_code.text)  # type: ignore[arg-type]
    except ValueError as e:
        raise Failed(f'Unable to parse faultCode "{fault_code}" as int') from e

    if fault_string.text is None:
        raise Failed("faultString text is None")

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
