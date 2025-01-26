import xml.etree.ElementTree as ET

import pytest
import requests

from modernrpc.exceptions import RPC_INVALID_REQUEST


@pytest.mark.skip(reason="to be replaced by unit tests")
class TestXmlBomb:
    """Perform tests to ensure defusedxml is correctly used to parse incoming XML-RPC requests"""

    # This is a malicious payload, with values defined from ENTITY definitions. This kind of variable setting can
    # be used as a vecor attack to fill up server memory with hundreds of megabytes of data with a few lines of code.
    # See https://github.com/tiran/defusedxml for more information
    xml_bomb_payload = """
    <!DOCTYPE xmlbomb [
    <!ENTITY a "5">
    <!ENTITY concat_a "&a;&a;&a;">
    <!ENTITY b "6">
    <!ENTITY concat_b "&b;&b;&b;">
    ]>
    <methodCall>
      <methodName>add</methodName>
      <params>
         <param>
            <value><int>&concat_a;</int></value>
         </param>
         <param>
            <value><int>&concat_b;</int></value>
         </param>
      </params>
    </methodCall>"""

    def test_xml_bomb(self, live_server, endpoint_path):
        """defusedxml is installed by default in 'dev' environment. As a result, XML-RPC request using ENTITY defined
        variables become invalid"""
        response = requests.post(
            live_server.url + endpoint_path, data=self.xml_bomb_payload, headers={"content-type": "text/xml"}
        )
        tree = ET.fromstring(response.content)

        fault_code = tree.find("./fault/value/struct/member/name[.='faultCode']/../value/int")
        assert fault_code is not None
        assert fault_code.text == str(RPC_INVALID_REQUEST)

        fault_string = tree.find("./fault/value/struct/member/name[.='faultString']/../value/string")
        assert fault_string is not None
        assert "Invalid request" in fault_string.text

        # No result in response payload
        assert tree.find("./params/param/value/int") is None

    @pytest.mark.usefixtures("_unconfigure_defusedxml")
    def test_xml_bomb_without_defusedxml(self, live_server, endpoint_path):
        """This test uses _unconfigure_defusedxml fixture to ensure defusedxml is disabled"""
        response = requests.post(
            live_server.url + endpoint_path,
            data=self.xml_bomb_payload,
            headers={"content-type": "text/xml"},
        )
        tree = ET.fromstring(response.content)

        assert tree.find("./fault/value/struct/member/name[.='faultCode']/../value/int") is None
        assert tree.find("./fault/value/struct/member/name[.='faultString']/../value/string") is None

        result = tree.find("./params/param/value/int")
        assert result is not None
        assert result.text == "1221"
