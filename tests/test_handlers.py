from modernrpc.handlers import JsonRpcHandler, XmlRpcHandler


class TestJsonRpcHandler:
    handler = JsonRpcHandler()

    def test_correct_content_type(self):
        assert self.handler.response_content_type() == "application/json"


class TestXmlRpcHandler:
    handler = XmlRpcHandler()

    def test_correct_content_type(self):
        assert self.handler.response_content_type() == "application/xml"
