from modernrpc.core import Protocol, RPCMethod, rpc_method


def dummy_empty():
    pass


class TestRpcMethodEntryPointProtocol:
    """Check whether entry_points and protocol specifications works as expected when registering method"""

    def test_method_always_available(self):
        rpc_method(dummy_empty, "dummy_name")
        m = RPCMethod(dummy_empty)

        assert m.is_available_in_xml_rpc()
        assert m.is_available_in_json_rpc()

    def test_method_xmlrpc_only(self):
        rpc_method(dummy_empty, "dummy_name", protocol=Protocol.XML_RPC)
        m = RPCMethod(dummy_empty)

        assert m.is_available_in_xml_rpc()
        assert not m.is_available_in_json_rpc()

    def test_method_jsonrpc_only(self):
        rpc_method(dummy_empty, "dummy_name", protocol=Protocol.JSON_RPC)
        m = RPCMethod(dummy_empty)

        assert not m.is_available_in_xml_rpc()
        assert m.is_available_in_json_rpc()

    def test_method_repr(self):
        rpc_method(dummy_empty, "dummy_name", protocol=Protocol.JSON_RPC)
        m = RPCMethod(dummy_empty)
        assert "dummy_name" in repr(m)


@rpc_method
def dummy_no_doc_no_args():
    pass


class TestNoDocNoArgs:
    """Make sure docstring and introspection works as expected"""

    def test_args_and_return(self):
        m = RPCMethod(dummy_no_doc_no_args)
        assert m.args == []
        assert m.args_doc == {}
        assert m.return_doc == {"type": "", "text": ""}

    def test_doc(self):
        m = RPCMethod(dummy_no_doc_no_args)
        assert m.raw_docstring == ""
        assert m.html_doc == ""


@rpc_method
def dummy_no_doc_with_args(a, b, c):
    pass


class TestNoDocWithArgs:
    """Make sure docstring and introspection works as expected"""

    def test_args_and_return(self):
        m = RPCMethod(dummy_no_doc_with_args)
        assert m.args == ["a", "b", "c"]
        assert m.args_doc == {
            "a": {"type": "", "text": ""},
            "b": {"type": "", "text": ""},
            "c": {"type": "", "text": ""},
        }
        assert m.return_doc == {"type": "", "text": ""}

    def test_doc(self):
        m = RPCMethod(dummy_no_doc_with_args)
        assert m.raw_docstring == ""
        assert m.html_doc == ""


@rpc_method
def dummy_args_with_typehints(a: int, b: str, c: list) -> dict:
    pass


class TestArgsTypeHint:
    """Type hinting is correctly returned using introspection module"""

    def test_args_and_return(self):
        m = RPCMethod(dummy_args_with_typehints)
        assert m.args == ["a", "b", "c"]
        assert m.args_doc == {
            "a": {"type": "int", "text": ""},
            "b": {"type": "str", "text": ""},
            "c": {"type": "list", "text": ""},
        }
        assert m.return_doc == {"type": "dict", "text": ""}

    def test_doc(self):
        m = RPCMethod(dummy_args_with_typehints)
        assert m.raw_docstring == ""
        assert m.html_doc == ""


@rpc_method
def dummy_typehints_and_standard_docstring(a: str, b: dict, c: float) -> float:
    """

    :param a: param A
    :param b: param B
    :param c: param C
    :return: A decimal value
    """


class TestWithTypeHintAndDocstring:
    """Typehint + standard reStructuredText docstring"""

    def test_args_and_return(self):
        m = RPCMethod(dummy_typehints_and_standard_docstring)

        assert m.args == ["a", "b", "c"]
        assert m.args_doc == {
            "a": {"type": "str", "text": "param A"},
            "b": {"type": "dict", "text": "param B"},
            "c": {"type": "float", "text": "param C"},
        }
        assert m.return_doc == {"type": "float", "text": "A decimal value"}

    def test_doc(self):
        m = RPCMethod(dummy_typehints_and_standard_docstring)

        assert m.raw_docstring == ""
        assert m.html_doc == ""


@rpc_method
def dummy_typehints_and_rst_docstring_types(x: list, y: str) -> dict:
    """This is the docstring part of the function

    It also contains a multi-line description
    :param x: abcd
    :param y: xyz
    :return: efgh
    :type x: float
    :type y: int
    :rtype: str
    """


class TestWithTypeHintAndDocstringTypes:
    """Legacy standard docstring must override typehint"""

    def test_args_and_return(self):
        m = RPCMethod(dummy_typehints_and_rst_docstring_types)

        assert m.args == ["x", "y"]
        assert m.args_doc == {
            "x": {"type": "float", "text": "abcd"},
            "y": {"type": "int", "text": "xyz"},
        }
        assert m.return_doc == {"type": "str", "text": "efgh"}

    def test_doc(self):
        m = RPCMethod(dummy_typehints_and_rst_docstring_types)

        assert m.raw_docstring == (
            "This is the docstring part of the function\n\nIt also contains a multi-line description"
        )
        assert m.html_doc == (
            "<p>This is the docstring part of the function</p><p>It also contains a multi-line description</p>"
        )


@rpc_method
def dummy_rst_docstring(name, birthdate, sex):
    """
    This is the textual doc of the method
    :param name: A name
    :param birthdate: A birthdate
    :param sex: Male or Female
    :type name: str
    :type birthdate: datetime.datetime
    :type sex: str
    :return: A string representation of given arguments
    """
    return f"{name} ({sex!s}) born on {birthdate!s}"


class TestWithDoctstringOnlyFunction:
    """No typehint but everything in reStructuredText docstring"""

    def test_args_and_return(self):
        m = RPCMethod(dummy_rst_docstring)

        assert m.args == ["name", "birthdate", "sex"]
        assert m.args_doc == {
            "name": {"type": "str", "text": "A name"},
            "birthdate": {"type": "datetime.datetime", "text": "A birthdate"},
            "sex": {"type": "str", "text": "Male or Female"},
        }
        assert m.return_doc == {
            "type": "",
            "text": "A string representation of given arguments",
        }

    def test_doc(self):
        m = RPCMethod(dummy_rst_docstring)
        assert m.raw_docstring == "This is the textual doc of the method"
        assert m.html_doc == "<p>This is the textual doc of the method</p>"
