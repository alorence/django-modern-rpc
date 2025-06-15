import base64
from collections import OrderedDict
from datetime import datetime
from textwrap import dedent

import pytest
from helpers import assert_xml_data_are_equal

from modernrpc.exceptions import RPCInvalidRequest, RPCMarshallingError, RPCParseError
from modernrpc.xmlrpc.handler import XmlRpcErrorResult, XmlRpcRequest, XmlRpcSuccessResult


class TestXmlRpcDeserializer:
    """
    This class will test the XmlRpcDeserializer classes.
    It will ensure that a given request payload is parsed correctly and the extracted data
    have correct type and value
    """

    def test_method_name_no_params(self, xml_deserializer):
        payload = """
            <?xml version="1.0"?>
            <methodCall>
              <methodName>
                foo.bar
              </methodName>
            </methodCall>
        """
        request = xml_deserializer.loads(dedent(payload).strip())
        assert request.method_name == "foo.bar"
        assert request.args == []

    def test_method_name_empty_params(self, xml_deserializer):
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
        request = xml_deserializer.loads(dedent(payload).strip())
        assert request.method_name == "foo.bar"
        assert request.args == []

    @pytest.mark.parametrize(
        "inner_template",
        [
            "<{type}>{value}</{type}>",
            "<{type}>\n    {value}\n    </{type}>",
        ],
    )
    @pytest.mark.parametrize(
        "outer_template",
        [
            "{inner}",
            "<value>{inner}</value>",
            "\n  {inner}  \n",
            "<value>\n        {inner}\n        </value>",
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
    def test_param_scalar(self, xml_deserializer, inner_template, outer_template, typ, value, expected_value, request):
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
        is_builtin_backend = "PythonXmlRpcBackend" in xml_deserializer.__class__.__name__
        have_space_around = "\n" in inner_template or " " in inner_template
        type_have_parsing_issues = typ in ("boolean", "string", "dateTime.iso8601")
        if is_builtin_backend and have_space_around and type_have_parsing_issues:
            # When spaces are parsed around the text value of a node, builtin XmlRpc
            # backend fail to extract the correct value. Mark this test as XFail in such case
            marker = pytest.mark.xfail(
                reason="PythonXmlRpcBackend incorrectly parse tags surrounded with spaces", strict=True
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
        """
        request = xml_deserializer.loads(dedent(payload).strip())
        assert request.args == [expected_value]

    def test_param_binary(self, xml_deserializer):
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
        request = xml_deserializer.loads(dedent(payload).strip())
        assert request.method_name == "foo.bar.baz"
        assert request.args == [initial_data]

    def test_param_array_single_value(self, xml_deserializer):
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
        request = xml_deserializer.loads(dedent(payload).strip())
        assert request.method_name == "foo.bar.baz"
        assert request.args == [[8]]

    def test_array_params_multiple_values(self, xml_deserializer):
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
        request = xml_deserializer.loads(dedent(payload).strip())
        assert request.method_name == "foo.bar.baz"
        assert request.args == [[5, 9, "abc"], [0.0]]

    def test_param_struc_single_value(self, xml_deserializer):
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
        request = xml_deserializer.loads(dedent(payload).strip())
        assert request.method_name == "foo.bar.baz"
        assert request.args == [{"pi": 3.14}]

    def test_param_struc_multiple_values(self, xml_deserializer):
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
        request = xml_deserializer.loads(dedent(payload).strip())
        assert request.method_name == "foo.bar.baz"
        assert request.args == [{"foo": 9}, {"bar": 9.0, "baz": "9"}]

    def test_invalid_xml_payload(self, xml_deserializer):
        payload = """
            <?xml version="1.0"?>
            <methodCall>
              <methodName>foo.baz</methodName
              <params>
                <param><value><i4>11</i4></value></param>
              </params>
            </methodCall>
        """
        with pytest.raises(RPCParseError):
            xml_deserializer.loads(dedent(payload).strip())

    def test_missing_root_tag(self, request, xml_deserializer):
        if "PythonXmlRpcBackend" in xml_deserializer.__class__.__name__:
            marker = pytest.mark.xfail(
                reason='PythonXmlRpcBackend allows requests without any "methodCall" root tag', strict=True
            )
            request.applymarker(marker)

        payload = """
            <?xml version="1.0"?>
            <foo>
              <methodName>foo.baz</methodName>
              <params>
                <param><value><int>5</int></value></param>
              </params>
            </foo>
        """
        with pytest.raises(RPCInvalidRequest):
            xml_deserializer.loads(dedent(payload).strip())

    def test_missing_method_name(self, xml_deserializer):
        payload = """
            <?xml version="1.0"?>
            <methodCall>
              <params>
                <param><value><int>5</int></value></param>
              </params>
            </methodCall>
        """
        with pytest.raises(RPCInvalidRequest):
            xml_deserializer.loads(dedent(payload).strip())

    def test_invalid_type(self, xml_deserializer):
        payload = """
            <?xml version="1.0"?>
            <methodCall>
              <methodName>foo.bar</methodName>
              <params>
                <param><value><foo>5</foo></value></param>
              </params>
            </methodCall>
        """
        with pytest.raises(RPCInvalidRequest):
            xml_deserializer.loads(dedent(payload).strip())

    @pytest.mark.parametrize("val", [5, True, False, -3, -1, "null", "true", "false"])
    def test_invalid_bool_value(self, xml_deserializer, val):
        payload = f"""
            <?xml version="1.0"?>
            <methodCall>
              <methodName>foo.bar</methodName>
              <params>
                <param><value><boolean>{val}</boolean></value></param>
              </params>
            </methodCall>
        """
        with pytest.raises(RPCInvalidRequest):
            xml_deserializer.loads(dedent(payload).strip())


class TestXmlRpcSerializer:
    req = XmlRpcRequest(method_name="foo")

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
    def test_result_scalar(self, xml_serializer, data, expected_type, expected_result):
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
            xml_serializer.dumps(XmlRpcSuccessResult(request=self.req, data=data)),
            expected_payload,
        )

    def test_result_null(self, xml_serializer):
        result = xml_serializer.dumps(XmlRpcSuccessResult(request=self.req, data=None))
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

    def test_result_binary(self, xml_serializer):
        res_data = b"\x04\x99\x54ufg\x10\xfe"
        b64_res_data = base64.b64encode(res_data).decode()
        result = xml_serializer.dumps(XmlRpcSuccessResult(request=self.req, data=res_data))
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

    def test_result_array_single_value(self, xml_serializer):
        result = xml_serializer.dumps(XmlRpcSuccessResult(request=self.req, data=["foo"]))
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
    def test_result_array_multiple_values(self, xml_serializer, array_value):
        result = xml_serializer.dumps(XmlRpcSuccessResult(request=self.req, data=array_value))
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

    def test_result_dict_single_value(self, xml_serializer):
        result = xml_serializer.dumps(XmlRpcSuccessResult(request=self.req, data={"pi": 3.14}))
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
    def test_result_dict_multiple_values(self, request, xml_serializer, struct_value):
        if "PythonXmlRpcBackend" in xml_serializer.__class__.__name__ and isinstance(struct_value, OrderedDict):
            marker = pytest.mark.xfail(reason="PythonXmlRpcBackend does not support OrderedDict", strict=True)
            request.applymarker(marker)

        result = xml_serializer.dumps(XmlRpcSuccessResult(request=self.req, data=struct_value))
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

    def test_result_error(self, xml_serializer):
        result = xml_serializer.dumps(XmlRpcErrorResult(request=self.req, code=-65000, message="foo", data="abcdef"))
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
    def test_int_overflow_result(self, xml_serializer, val):
        """XML-RPC enforce int value limits. Check that is correctly handled in backends"""
        result = XmlRpcSuccessResult(request=self.req, data=val)

        with pytest.raises(RPCMarshallingError):
            xml_serializer.dumps(result)
