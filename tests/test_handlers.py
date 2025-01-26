from modernrpc.handlers import JSONRPCHandler, XMLRPCHandler


class TestJsonHandler:
    handler = JSONRPCHandler()

    def test_correct_content_type(self):
        assert self.handler.response_content_type() == "application/json"


class TestXmlHandler:
    handler = XMLRPCHandler()

    def test_correct_content_type(self):
        assert self.handler.response_content_type() == "application/xml"
