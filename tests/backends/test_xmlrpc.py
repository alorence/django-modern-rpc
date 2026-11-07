import base64
import inspect
import xmlrpc.client
from collections import OrderedDict
from datetime import datetime
from typing import Any

import pytest
from helpers import assert_xml_data_are_equal
from pytest_django import Settings

from modernrpc.exceptions import RPCInvalidRequest, RPCMarshallingError, RPCParseError
from modernrpc.xmlrpc.backends import XmlRpcDeserializer, XmlRpcSerializer
from modernrpc.xmlrpc.handler import XmlRpcErrorResult, XmlRpcHandler, XmlRpcRequest, XmlRpcSuccessResult


@pytest.fixture
def dummy_xmlrpc_request() -> XmlRpcRequest:
    return XmlRpcRequest(method_name="foo.bar")


class TestXmlRpcDeserializer:
    """
    This class will test the XmlRpcDeserializer classes.
    It will ensure that a given request payload is parsed correctly and the extracted data
    have the correct type and value
    """

    def test_method_name_no_params(self, xml_deserializer: XmlRpcDeserializer) -> None:
        payload = """
            <?xml version="1.0"?>
            <methodCall>
              <methodName>
                foo.bar
              </methodName>
            </methodCall>
        """
        request = xml_deserializer.loads(inspect.cleandoc(payload))
        assert request.method_name == "foo.bar"
        assert request.args == []

    def test_method_name_empty_params(self, xml_deserializer: XmlRpcDeserializer) -> None:
        payload = """
            <?xml version="1.0"?>
            <methodCall>
              <methodName>
                foo.bar
              </methodName>
              <params>
              </params>
            </methodCall>
        """
        request = xml_deserializer.loads(inspect.cleandoc(payload))
        assert request.method_name == "foo.bar"
        assert request.args == []

    @pytest.mark.parametrize(
        "inner_template",
        [
            "<{type}>{value}</{type}>",
            "<{type}>        {value}    </{type}>",
        ],
    )
    @pytest.mark.parametrize(
        "outer_template",
        [
            "{inner}",
            "<value>{inner}</value>",
            "\n    {inner}\n    ",
            "<value>        {inner}    </value>",
        ],
    )
    @pytest.mark.parametrize(
        ("typ", "value", "expected_value"),
        [
            ("nil", "", None),
            ("boolean", "1", True),
            ("boolean", "0", False),
            ("int", "16", 16),
            ("i4", "16", 16),
            ("int", "-123", -123),
            ("i4", "-123", -123),
            ("double", "20", 20.0),
            ("double", "3.14159", 3.14159),
            ("double", "-3.14159", -3.14159),
            ("string", "xyz", "xyz"),
            ("string", "lorem\nipsum", "lorem\nipsum"),
            ("string", "😵‍💫💗", "😵‍💫💗"),
            ("dateTime.iso8601", "20250101T00:00:00", datetime(2025, 1, 1, 0, 0, 0)),
        ],
    )
    def test_param_scalar(
        self,
        xml_deserializer: XmlRpcDeserializer,
        inner_template: str,
        outer_template: str,
        typ: str,
        value: Any,
        expected_value: Any,
        request: pytest.FixtureRequest,
    ) -> None:
        """
        This is a huge test, configured with multiple possible values.
        Here is a description of the parametrization applied to it:

        inner_template: is used to ensure the request is correctly parsed with or without spaces around real value.
          Some backends are known to fail in such case. See 'request'

        outer_template: is used to ensure the request is correctly parsed with or without spaces around <value> and
          <type> tags, or when no <value> tags are used

        typ, value: the strings used to represent a specific value in an XML-RPC request

        expected_value: the Python value expected once request have been parsed

        request: used to dynamically mark the test as XFail when some conditions are met
        """
        is_builtin_backend = "PythonXmlRpc" in xml_deserializer.__class__.__name__
        have_space_around = "\n" in inner_template or " " in inner_template
        type_have_parsing_issues = typ in ("boolean", "string", "dateTime.iso8601")
        if is_builtin_backend and have_space_around and type_have_parsing_issues:
            # When spaces are parsed around the text value of a node, builtin PythonXmlRpcBackend fail to
            # extract the correct value. Mark this test as XFail in this case
            marker = pytest.mark.xfail(
                reason="PythonXmlRpcDeserializer incorrectly parse tags surrounded with spaces", strict=True
            )
            request.applymarker(marker)

        inner = inner_template.format(type=typ, value=value)
        outer = outer_template.format(inner=inner)
        payload = f"""
            <?xml version="1.0"?>
            <methodCall>
            <methodName>foo</methodName>
            <params>
                <param>{outer}</param>
            </params>
            </methodCall>
        """.lstrip()
        rpc_request = xml_deserializer.loads(inspect.cleandoc(payload))
        assert rpc_request.args == [expected_value]

    def test_param_binary(self, xml_deserializer: XmlRpcDeserializer) -> None:
        initial_data = b"\x3247\x9684\x41\x77\\x12\x34"
        b64_data = base64.b64encode(initial_data).decode()
        payload = f"""
            <?xml version="1.0"?>
            <methodCall>
              <methodName>foo.bar.baz</methodName>
              <params>
                <param>
                  <value>
                    <base64>{b64_data}</base64>
                  </value>
                </param>
              </params>
            </methodCall>
        """
        request = xml_deserializer.loads(inspect.cleandoc(payload))
        assert request.method_name == "foo.bar.baz"
        assert request.args == [initial_data]

    def test_param_array_single_value(self, xml_deserializer: XmlRpcDeserializer) -> None:
        payload = """
            <?xml version="1.0"?>
            <methodCall>
              <methodName>foo.bar.baz</methodName>
              <params>
                <param>
                  <value>
                    <array>
                      <data>
                        <value><i4>8</i4></value>
                      </data>
                    </array>
                  </value>
                </param>
              </params>
            </methodCall>
        """
        request = xml_deserializer.loads(inspect.cleandoc(payload))
        assert request.method_name == "foo.bar.baz"
        assert request.args == [[8]]

    def test_array_params_multiple_values(self, xml_deserializer: XmlRpcDeserializer) -> None:
        payload = """
            <?xml version="1.0"?>
            <methodCall>
              <methodName>foo.bar.baz</methodName>
              <params>
                <param>
                  <value>
                    <array>
                      <data>
                        <value><i4>5</i4></value>
                        <value><int>9</int></value>
                        <value><string>abc</string></value>
                      </data>
                    </array>
                  </value>
                </param>
                <param>
                  <value>
                    <array>
                      <data>
                        <value><double>0</double></value>
                      </data>
                    </array>
                  </value>
                </param>
              </params>
            </methodCall>
        """
        request = xml_deserializer.loads(inspect.cleandoc(payload))
        assert request.method_name == "foo.bar.baz"
        assert request.args == [[5, 9, "abc"], [0.0]]

    def test_param_struct_single_value(self, xml_deserializer: XmlRpcDeserializer) -> None:
        payload = """
            <?xml version="1.0"?>
            <methodCall>
              <methodName>foo.bar.baz</methodName>
              <params>
                <param>
                  <value>
                    <struct>
                      <member>
                        <name>pi</name>
                        <value><double>3.14</double></value>
                      </member>
                    </struct>
                  </value>
                </param>
              </params>
            </methodCall>
        """
        request = xml_deserializer.loads(inspect.cleandoc(payload))
        assert request.method_name == "foo.bar.baz"
        assert request.args == [{"pi": 3.14}]

    def test_param_struct_multiple_values(self, xml_deserializer: XmlRpcDeserializer) -> None:
        payload = """
            <?xml version="1.0"?>
            <methodCall>
              <methodName>foo.bar.baz</methodName>
              <params>
                <param>
                  <value>
                    <struct>
                      <member>
                        <name>foo</name>
                        <value><int>9</int></value>
                      </member>
                    </struct>
                  </value>
                </param>
                <param>
                  <value>
                    <struct>
                      <member>
                        <name>bar</name>
                        <value><double>9</double></value>
                      </member>
                      <member>
                        <name>baz</name>
                        <value><string>9</string></value>
                      </member>
                    </struct>
                  </value>
                </param>
              </params>
            </methodCall>
        """
        request = xml_deserializer.loads(inspect.cleandoc(payload))
        assert request.method_name == "foo.bar.baz"
        assert request.args == [{"foo": 9}, {"bar": 9.0, "baz": "9"}]

    def test_invalid_xml_payload(self, xml_deserializer: XmlRpcDeserializer) -> None:
        payload = inspect.cleandoc("""
            <?xml version="1.0"?>
            <methodCall>
              <methodName>foo.baz</methodName
              <params>
                <param><value><i4>11</i4></value></param>
              </params>
            </methodCall>
        """)
        with pytest.raises(RPCParseError):
            xml_deserializer.loads(payload)

    def test_missing_root_tag(self, request: pytest.FixtureRequest, xml_deserializer: XmlRpcDeserializer) -> None:
        if "PythonXmlRpc" in xml_deserializer.__class__.__name__:
            marker = pytest.mark.xfail(
                reason='PythonXmlRpcDeserializer allows requests without any "methodCall" root tag', strict=True
            )
            request.applymarker(marker)

        payload = inspect.cleandoc("""
            <?xml version="1.0"?>
            <foo>
              <methodName>foo.baz</methodName>
              <params>
                <param><value><int>5</int></value></param>
              </params>
            </foo>
        """)
        with pytest.raises(RPCInvalidRequest):
            xml_deserializer.loads(payload)

    def test_missing_method_name(self, xml_deserializer: XmlRpcDeserializer) -> None:
        payload = inspect.cleandoc("""
            <?xml version="1.0"?>
            <methodCall>
              <params>
                <param><value><int>5</int></value></param>
              </params>
            </methodCall>
        """)
        with pytest.raises(RPCInvalidRequest):
            xml_deserializer.loads(payload)

    def test_invalid_type(self, xml_deserializer: XmlRpcDeserializer) -> None:
        payload = inspect.cleandoc("""
            <?xml version="1.0"?>
            <methodCall>
              <methodName>foo.bar</methodName>
              <params>
                <param><value><foo>5</foo></value></param>
              </params>
            </methodCall>
        """)
        with pytest.raises(RPCInvalidRequest):
            xml_deserializer.loads(payload)

    @pytest.mark.parametrize("val", [5, True, False, -3, -1, "null", "true", "false"])
    def test_invalid_bool_value(self, xml_deserializer: XmlRpcDeserializer, val: Any) -> None:
        payload = inspect.cleandoc(f"""
            <?xml version="1.0"?>
            <methodCall>
              <methodName>foo.bar</methodName>
              <params>
                <param><value><boolean>{val}</boolean></value></param>
              </params>
            </methodCall>
        """)
        with pytest.raises(RPCInvalidRequest):
            xml_deserializer.loads(payload)


class TestXmlRpcDeserializerKwargs:
    def test_builtin_xmlrpc_use_datetime(self, settings: Settings) -> None:
        # use_datetime is set to True by default, allowing ...
        settings.MODERNRPC_XML_DESERIALIZER = {
            "class": "modernrpc.xmlrpc.backends.xmlrpc.PythonXmlRpcDeserializer",
            "kwargs": {"load_kwargs": {"use_datetime": False, "use_builtin_types": False}},
        }
        handler_deserializer = XmlRpcHandler().deserializer
        payload = """
            <?xml version="1.0"?>
            <methodCall>
              <methodName>foo.bar</methodName>
              <params>
                <param><value>
                  <dateTime.iso8601>20260101T00:00:00</dateTime.iso8601>
                </value></param>
              </params>
            </methodCall>
        """

        request = handler_deserializer.loads(inspect.cleandoc(payload))

        assert isinstance(request.args[0], xmlrpc.client.DateTime)
        assert request.args[0] == datetime(2026, 1, 1, 0, 0, 0)

    @pytest.mark.parametrize(
        "deserializer",
        [
            "modernrpc.xmlrpc.backends.xmltodict.XmlToDictDeserializer",
            "modernrpc.xmlrpc.backends.etree.EtreeDeserializer",
            "modernrpc.xmlrpc.backends.lxml.LxmlDeserializer",
        ],
    )
    def test_nil_disallowed(self, settings: Settings, deserializer: str) -> None:
        settings.MODERNRPC_XML_DESERIALIZER = {
            "class": deserializer,
            "kwargs": {"unmarshaller_kwargs": {"allow_none": False}},
        }

        handler_deserializer = XmlRpcHandler().deserializer
        payload = inspect.cleandoc("""
            <?xml version="1.0"?>
            <methodCall>
              <methodName>foo.bar</methodName>
              <params>
                <param><value>
                  <nil/>
                </value></param>
              </params>
            </methodCall>
        """)

        with pytest.raises(RPCInvalidRequest, match="cannot unmarshal <nil/> unless allow_none is enabled"):
            handler_deserializer.loads(payload)


class TestXmlRpcSerializer:
    @pytest.mark.parametrize(
        ("data", "expected_type", "expected_result"),
        [
            (False, "boolean", "0"),
            (True, "boolean", "1"),
            (55, "int", "55"),
            (-999, "int", "-999"),
            (0, "int", "0"),
            ("55", "string", "55"),
            ("foo.bar", "string", "foo.bar"),
            ("foo\nbar", "string", "foo\nbar"),
            (9.6, "double", "9.6"),
            (-3.14, "double", "-3.14"),
            (datetime(2025, 1, 1, 5, 6, 8), "dateTime.iso8601", "20250101T05:06:08"),
        ],
    )
    def test_result_scalar(
        self,
        xml_serializer: XmlRpcSerializer,
        dummy_xmlrpc_request: XmlRpcRequest,
        data: Any,
        expected_type: str,
        expected_result: Any,
    ) -> None:
        expected_payload = f"""<?xml version='1.0'?>
            <methodResponse>
                <params>
                    <param>
                        <value><{expected_type}>{expected_result}</{expected_type}></value>
                    </param>
                </params>
            </methodResponse>
        """
        assert_xml_data_are_equal(
            xml_serializer.dumps(XmlRpcSuccessResult(request=dummy_xmlrpc_request, data=data)),
            expected_payload,
        )

    def test_result_null(self, xml_serializer: XmlRpcSerializer, dummy_xmlrpc_request: XmlRpcRequest) -> None:
        result = xml_serializer.dumps(XmlRpcSuccessResult(request=dummy_xmlrpc_request, data=None))
        expected = """<?xml version='1.0'?>
            <methodResponse>
                <params>
                    <param>
                        <value><nil/></value>
                    </param>
                </params>
            </methodResponse>
        """
        assert_xml_data_are_equal(result, expected)

    def test_result_binary(self, xml_serializer: XmlRpcSerializer, dummy_xmlrpc_request: XmlRpcRequest) -> None:
        res_data = b"\x04\x99\x54ufg\x10\xfe"
        b64_res_data = base64.b64encode(res_data).decode()
        result = xml_serializer.dumps(XmlRpcSuccessResult(request=dummy_xmlrpc_request, data=res_data))
        expected = f"""<?xml version='1.0'?>
            <methodResponse>
              <params>
                <param>
                  <value>
                    <base64>{b64_res_data}</base64>
                  </value>
                </param>
              </params>
            </methodResponse>
        """
        assert_xml_data_are_equal(result, expected)

    def test_result_array_single_value(
        self, xml_serializer: XmlRpcSerializer, dummy_xmlrpc_request: XmlRpcRequest
    ) -> None:
        result = xml_serializer.dumps(XmlRpcSuccessResult(request=dummy_xmlrpc_request, data=["foo"]))
        expected = """<?xml version='1.0'?>
            <methodResponse>
              <params>
                <param>
                  <value>
                    <array>
                      <data>
                        <value><string>foo</string></value>
                      </data>
                    </array>
                  </value>
                </param>
              </params>
            </methodResponse>
        """
        assert_xml_data_are_equal(result, expected)

    @pytest.mark.parametrize(
        "array_value",
        [
            [1, 3, 5, "foo", "bar", 3.14],
            (1, 3, 5, "foo", "bar", 3.14),
        ],
    )
    def test_result_array_multiple_values(
        self, xml_serializer: XmlRpcSerializer, dummy_xmlrpc_request: XmlRpcRequest, array_value: Any
    ) -> None:
        result = xml_serializer.dumps(XmlRpcSuccessResult(request=dummy_xmlrpc_request, data=array_value))
        expected = """<?xml version='1.0'?>
            <methodResponse>
              <params>
                <param>
                  <value>
                    <array>
                      <data>
                        <value><int>1</int></value>
                        <value><int>3</int></value>
                        <value><int>5</int></value>
                        <value><string>foo</string></value>
                        <value><string>bar</string></value>
                        <value><double>3.14</double></value>
                      </data>
                    </array>
                  </value>
                </param>
              </params>
            </methodResponse>
        """
        assert_xml_data_are_equal(result, expected)

    def test_result_dict_single_value(
        self, xml_serializer: XmlRpcSerializer, dummy_xmlrpc_request: XmlRpcRequest
    ) -> None:
        result = xml_serializer.dumps(XmlRpcSuccessResult(request=dummy_xmlrpc_request, data={"pi": 3.14}))
        expected = """<?xml version='1.0'?>
            <methodResponse>
              <params>
                <param>
                  <value>
                    <struct>
                      <member>
                        <name>pi</name>
                        <value>
                          <double>3.14</double>
                        </value>
                      </member>
                    </struct>
                  </value>
                </param>
              </params>
            </methodResponse>
        """
        assert_xml_data_are_equal(result, expected)

    @pytest.mark.parametrize(
        "struct_value",
        [
            {"a": 12, "b": ["1", "2", "3"], "final": None},
            OrderedDict(a=12, b=["1", "2", "3"], final=None),
        ],
    )
    def test_result_dict_multiple_values(
        self,
        request: pytest.FixtureRequest,
        xml_serializer: XmlRpcSerializer,
        dummy_xmlrpc_request: XmlRpcRequest,
        struct_value: Any,
    ) -> None:
        if "PythonXmlRpc" in xml_serializer.__class__.__name__ and isinstance(struct_value, OrderedDict):
            marker = pytest.mark.xfail(reason="PythonXmlRpcSerializer does not support OrderedDict", strict=True)
            request.applymarker(marker)

        result = xml_serializer.dumps(XmlRpcSuccessResult(request=dummy_xmlrpc_request, data=struct_value))
        expected = """<?xml version='1.0'?>
            <methodResponse>
              <params>
                <param>
                  <value>
                    <struct>
                      <member>
                        <name>a</name>
                        <value>
                          <int>12</int>
                        </value>
                      </member>
                      <member>
                        <name>b</name>
                        <value>
                          <array>
                            <data>
                              <value><string>1</string></value>
                              <value><string>2</string></value>
                              <value><string>3</string></value>
                            </data>
                          </array>
                        </value>
                      </member>
                      <member>
                        <name>final</name>
                        <value><nil/></value>
                      </member>
                    </struct>
                  </value>
                </param>
              </params>
            </methodResponse>
        """
        assert_xml_data_are_equal(result, expected)

    def test_result_error(self, xml_serializer: XmlRpcSerializer, dummy_xmlrpc_request: XmlRpcRequest) -> None:
        result = xml_serializer.dumps(
            XmlRpcErrorResult(request=dummy_xmlrpc_request, code=-65000, message="foo", data="abcdef")
        )
        expected = """<?xml version='1.0'?>
          <methodResponse>
            <fault>
              <value>
                <struct>
                  <member>
                    <name>faultCode</name>
                    <value>
                      <int>-65000</int>
                    </value>
                  </member>
                  <member>
                    <name>faultString</name>
                    <value>
                      <string>foo</string>
                    </value>
                  </member>
                </struct>
              </value>
            </fault>
          </methodResponse>
        """
        assert_xml_data_are_equal(result, expected)

    @pytest.mark.parametrize("val", [2**32, 2**31 + 5, -(2**31) - 1])
    def test_int_overflow_result(
        self, xml_serializer: XmlRpcSerializer, dummy_xmlrpc_request: XmlRpcRequest, val: Any
    ) -> None:
        """XML-RPC enforce int value limits. Check that is correctly handled in backends"""
        result = XmlRpcSuccessResult(request=dummy_xmlrpc_request, data=val)

        with pytest.raises(RPCMarshallingError):
            xml_serializer.dumps(result)


class TestXmlRpcSerializerKwargs:
    @pytest.mark.parametrize("data_with_none", [None, {"foo": None}, [15, None, 16]])
    def test_builtin_xmlrpc_none_disallowed(
        self, dummy_xmlrpc_request: XmlRpcRequest, settings: Settings, data_with_none: Any
    ) -> None:
        # allow_none is set to True by default, allowing None values to be serialized
        # ensure that the correct exception is raised when the option is set to False
        settings.MODERNRPC_XML_SERIALIZER = {
            "class": "modernrpc.xmlrpc.backends.xmlrpc.PythonXmlRpcSerializer",
            "kwargs": {"dump_kwargs": {"allow_none": False}},
        }
        handler_serializer = XmlRpcHandler().serializer

        result = XmlRpcSuccessResult(request=dummy_xmlrpc_request, data=data_with_none)
        with pytest.raises(RPCMarshallingError, match="cannot marshal None unless allow_none is enabled"):
            handler_serializer.dumps(result)

    @pytest.mark.parametrize(
        "serializer",
        [
            "modernrpc.xmlrpc.backends.xmltodict.XmlToDictSerializer",
            "modernrpc.xmlrpc.backends.etree.EtreeSerializer",
            "modernrpc.xmlrpc.backends.lxml.LxmlSerializer",
        ],
    )
    @pytest.mark.parametrize("data_with_none", [None, {"foo": None}, [15, None, 16]])
    def test_xmlrpc_marshaller_none_disallowed(
        self, dummy_xmlrpc_request: XmlRpcRequest, settings: Settings, serializer: str, data_with_none: Any
    ) -> None:
        # allow_none is set to True by default, allowing None values to be serialized
        # ensure that the correct exception is raised when the option is set to False
        settings.MODERNRPC_XML_SERIALIZER = {
            "class": serializer,
            "kwargs": {"marshaller_kwargs": {"allow_none": False}},
        }
        handler_serializer = XmlRpcHandler().serializer

        result = XmlRpcSuccessResult(request=dummy_xmlrpc_request, data=data_with_none)
        with pytest.raises(RPCMarshallingError, match="cannot marshal None unless allow_none is enabled"):
            handler_serializer.dumps(result)
