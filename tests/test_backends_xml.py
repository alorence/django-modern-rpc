import base64
from datetime import datetime
from textwrap import dedent

import pytest
from conftest import XML_DESERIALIZERS_CLASSES
from helpers import assert_xml_data_are_equal

from modernrpc.exceptions import RPCInternalError, RPCInvalidRequest, RPCParseError
from modernrpc.handlers.base import XmlRpcErrorResult, XmlRpcRequest, XmlRpcSuccessResult


class TestXmlDeserializer:
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

    def test_nil_params(self, xml_deserializer):
        payload = """
            <?xml version="1.0"?>
            <methodCall>
              <methodName>
                bar
              </methodName>
              <params>
                <param><value><nil/></value></param>
                <param><nil/></param>
              </params>
            </methodCall>
        """
        request = xml_deserializer.loads(dedent(payload).strip())
        assert request.method_name == "bar"
        assert request.args == [None, None]

    def test_nil_params_with_indentation(self, xml_deserializer):
        payload = """
            <?xml version="1.0"?>
            <methodCall>
              <methodName>
                bar
              </methodName>
              <params>
                <param>
                  <value>
                    <nil/>
                  </value>
                </param>
                <param>
                  <nil/>
                </param>
              </params>
            </methodCall>
        """
        request = xml_deserializer.loads(dedent(payload).strip())
        assert request.method_name == "bar"
        assert request.args == [None, None]

    def test_bool_params(self, xml_deserializer):
        payload = """
            <?xml version="1.0"?>
            <methodCall>
              <methodName>zzz</methodName>
              <params>
                <param>
                  <value>
                    <boolean>1</boolean>
                  </value>
                </param>
                <param>
                  <boolean>0</boolean>
                </param>
              </params>
            </methodCall>
        """
        request = xml_deserializer.loads(dedent(payload).strip())
        assert request.method_name == "zzz"
        assert request.args == [True, False]

    def test_int_params(self, xml_deserializer):
        payload = """
            <?xml version="1.0"?>
            <methodCall>
              <methodName>foo.baz</methodName>
              <params>
                <param><value><int>99</int></value></param>
                <param><value><i4>11</i4></value></param>
              </params>
            </methodCall>
        """
        request = xml_deserializer.loads(dedent(payload).strip())
        assert request.method_name == "foo.baz"
        assert request.args == [99, 11]

    def test_int_params_with_indentation(self, xml_deserializer):
        payload = """
            <?xml version="1.0"?>
            <methodCall>
              <methodName>
                foo
              </methodName>
              <params>
                <param>
                  <value>
                    <int>
                      57
                    </int>
                  </value>
                </param>
                <param>
                  <value>
                    <i4>
                      33
                    </i4>
                  </value>
                </param>
              </params>
            </methodCall>
        """
        request = xml_deserializer.loads(dedent(payload).strip())
        assert request.method_name == "foo"
        assert request.args == [57, 33]

    def test_double_params(self, xml_deserializer):
        payload = """
            <?xml version="1.0"?>
            <methodCall>
              <methodName>xxx</methodName>
              <params>
                <param><value><double>127.1</double></value></param>
                <param><double>123.4</double></param>
                <param>
                  <value>
                    <double>
                      57
                    </double>
                  </value>
                </param>
                <param>
                  <double>
                    59
                  </double>
                </param>
              </params>
            </methodCall>
        """
        request = xml_deserializer.loads(dedent(payload).strip())
        assert request.method_name == "xxx"
        assert request.args == [127.1, 123.4, 57.0, 59.0]

    def test_str_params(self, xml_deserializer):
        payload = """
            <?xml version="1.0"?>
            <methodCall>
              <methodName>💗</methodName>
              <params>
                <param>
                  <value>
                    <string>abcd efg hij $☺</string>
                  </value>
                </param>
                <param>
                  <string>😵‍💫 pop</string>
                </param>
              </params>
            </methodCall>
        """
        request = xml_deserializer.loads(dedent(payload).strip())
        assert request.method_name == "💗"
        assert request.args == ["abcd efg hij $☺", "😵‍💫 pop"]

    def test_datetime_params(self, xml_deserializer):
        payload = """
            <?xml version="1.0"?>
            <methodCall>
              <methodName>foo.bar.baz</methodName>
              <params>
                <param>
                  <value>
                    <dateTime.iso8601>20250101T00:00:00</dateTime.iso8601>
                  </value>
                </param>
              </params>
            </methodCall>
        """
        request = xml_deserializer.loads(dedent(payload).strip())
        assert request.method_name == "foo.bar.baz"
        assert request.args == [
            datetime(2025, 1, 1, 0, 0, 0),
        ]

    def test_binary_params(self, xml_deserializer):
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

    def test_array_params(self, xml_deserializer):
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

    def test_struct_params(self, xml_deserializer):
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


class TestXmlDeserializerErrors:
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

    @pytest.mark.parametrize(
        "xml_deserializer",
        [
            pytest.param(
                klass,
                marks=pytest.mark.xfail(
                    reason="BuiltinXmlRpc is not strict enough, it allows requests without methodCall root tag"
                ),
            )
            if "BuiltinXmlRpc" in klass.__name__
            else klass
            for klass in XML_DESERIALIZERS_CLASSES
        ],
        indirect=True,
    )
    def test_missing_root_tag(self, xml_deserializer):
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


class TestXmlSerializer:
    req = XmlRpcRequest(method_name="foo")

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

    def test_result_bool(self, xml_serializer):
        result = xml_serializer.dumps(XmlRpcSuccessResult(request=self.req, data=False))
        expected = """<?xml version='1.0'?>
            <methodResponse>
                <params>
                    <param>
                        <value><boolean>0</boolean></value>
                    </param>
                </params>
            </methodResponse>
        """
        assert_xml_data_are_equal(result, expected)

    def test_result_int(self, xml_serializer):
        result = xml_serializer.dumps(XmlRpcSuccessResult(request=self.req, data=55))
        expected = """<?xml version='1.0'?>
            <methodResponse>
                <params>
                    <param>
                        <value><int>55</int></value>
                    </param>
                </params>
            </methodResponse>
        """
        assert_xml_data_are_equal(result, expected)

    def test_result_str(self, xml_serializer):
        result = xml_serializer.dumps(XmlRpcSuccessResult(request=self.req, data="foo.bar"))
        expected = """<?xml version='1.0'?>
            <methodResponse>
                <params>
                    <param>
                        <value><string>foo.bar</string></value>
                    </param>
                </params>
            </methodResponse>
        """
        assert_xml_data_are_equal(result, expected)

    def test_result_double(self, xml_serializer):
        result = xml_serializer.dumps(XmlRpcSuccessResult(request=self.req, data=9.6))
        expected = """<?xml version='1.0'?>
            <methodResponse>
                <params>
                    <param>
                        <value><double>9.6</double></value>
                    </param>
                </params>
            </methodResponse>
        """
        assert_xml_data_are_equal(result, expected)

    def test_result_datetime(self, xml_serializer):
        result = xml_serializer.dumps(XmlRpcSuccessResult(request=self.req, data=datetime(2025, 1, 1, 5, 6, 8)))
        expected = """<?xml version='1.0'?>
            <methodResponse>
              <params>
                <param>
                  <value>
                    <dateTime.iso8601>
                      20250101T05:06:08
                    </dateTime.iso8601>
                  </value>
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

    def test_result_array(self, xml_serializer):
        result = xml_serializer.dumps(XmlRpcSuccessResult(request=self.req, data=[1, 3, 5, "foo", "bar", 3.14]))
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

    def test_result_dict(self, xml_serializer):
        res_data = {"a": 12, "b": ["1", "2", "3"], "final": None}
        result = xml_serializer.dumps(XmlRpcSuccessResult(request=self.req, data=res_data))
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
                        <value><nil></nil></value>
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


class TestXmlSerializerErrors:
    req = XmlRpcRequest(method_name="foo")

    # @pytest.mark.parametrize("val", [2**32, 2**31 + 5, -(2**31) - 1])
    # def test_invalid_int_value(self, xml_deserializer, val):
    #     payload = f"""
    #         <?xml version="1.0"?>
    #         <methodCall>
    #           <methodName>foo.bar</methodName>
    #           <params>
    #             <param><value><int>{val}</int></value></param>
    #           </params>
    #         </methodCall>
    #     """
    #     with pytest.raises(RPCInvalidRequest):
    #         xml_deserializer.loads(dedent(payload).strip())

    @pytest.mark.parametrize("val", [2**32, 2**31 + 5, -(2**31) - 1])
    def test_int_overflow_result(self, xml_serializer, val):
        result = XmlRpcSuccessResult(request=self.req, data=val)

        with pytest.raises(RPCInternalError):
            xml_serializer.dumps(result)
