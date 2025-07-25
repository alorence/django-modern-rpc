"""Tests to ensure XML backends are protected against common vulnerabilities covered by defusedxml.

This file contains tests for each XML backend to verify they're protected against:
1. DTD attacks
2. Entity expansion attacks (billion-laughs)
3. External entity reference attacks
"""

import pytest

from modernrpc.exceptions import RPCInsecureRequest, RPCInvalidRequest, RPCParseError


class TestXmlBackendSecurity:
    """Test that XML backends are protected against common vulnerabilities."""

    def test_dtd_attack(self, request, xml_deserializer):
        """Test that XML backends reject DTD declarations."""
        xml_with_dtd = """<?xml version="1.0"?>
        <!DOCTYPE methodCall [
            <!ELEMENT methodCall ANY>
            <!ENTITY xxe SYSTEM "file:///etc/passwd">
        ]>
        <methodCall>
            <methodName>test</methodName>
            <params></params>
        </methodCall>
        """
        if "lxml" in xml_deserializer.__class__.__name__.lower():
            marker = pytest.mark.xfail(
                reason="lxml backend allows DTD definition, but enforce fine-grained protections on parsing",
                strict=True,
            )
            request.applymarker(marker)

        with pytest.raises(expected_exception=(RPCInsecureRequest, RPCInvalidRequest)):
            xml_deserializer.loads(xml_with_dtd)

    def test_billion_laughs_attack(self, xml_deserializer):
        """Test that XML backends are protected against entity expansion attacks."""
        billion_laughs = """<?xml version="1.0"?>
        <!DOCTYPE methodCall [
            <!ENTITY lol "lol">
            <!ENTITY lol1 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
            <!ENTITY lol2 "&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;">
            <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
            <!ENTITY lol4 "&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;">
            <!ENTITY lol5 "&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;">
            <!ENTITY lol6 "&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;">
            <!ENTITY lol7 "&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;">
            <!ENTITY lol8 "&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;">
            <!ENTITY lol9 "&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;">
        ]>
        <methodCall>
            <methodName>test</methodName>
            <params>
                <param>
                    <value>&lol9;</value>
                </param>
            </params>
        </methodCall>
        """

        with pytest.raises(expected_exception=(RPCInsecureRequest, RPCParseError)):
            xml_deserializer.loads(billion_laughs)

    def test_external_entity_attack(self, xml_deserializer):
        """Test that XML backends are protected against external entity reference attacks."""
        external_entity = """<?xml version="1.0"?>
        <!DOCTYPE methodCall [
            <!ENTITY xxe SYSTEM "file:///etc/passwd">
        ]>
        <methodCall>
            <methodName>test</methodName>
            <params>
                <param>
                    <value>&xxe;</value>
                </param>
            </params>
        </methodCall>
        """

        with pytest.raises(expected_exception=(RPCInsecureRequest, RPCInvalidRequest)):
            xml_deserializer.loads(external_entity)
