from modernrpc.handlers import JSONRPCHandler, XMLRPCHandler


class TestJsonHandler:
    handler = JSONRPCHandler(entry_point="dummy")

    def test_correct_content_type(self):
        assert self.handler.response_content_type() == "application/json"


class TestXmlHandler:
    handler = XMLRPCHandler(entry_point="dummy")

    def test_correct_content_type(self):
        assert self.handler.response_content_type() == "application/xml"
