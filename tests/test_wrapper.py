from modernrpc.core import ProcedureWrapper


def dummy_empty():
    pass


# class TestRpcMethodEntryPointProtocol:
#     """Check whether entry_points and protocol specifications works as expected when registering method"""
#
#     def test_method_always_available(self):
#         rpc_method(dummy_empty, "dummy_name")
#         wrapper = ProcedureWrapper(dummy_empty)
#
#         assert wrapper.is_available_in_xml_rpc()
#         assert wrapper.is_available_in_json_rpc()
#
#     def test_method_xmlrpc_only(self):
#         rpc_method(dummy_empty, "dummy_name", protocol=Protocol.XML_RPC)
#         wrapper = ProcedureWrapper(dummy_empty)
#
#         assert wrapper.is_available_in_xml_rpc()
#         assert not wrapper.is_available_in_json_rpc()
#
#     def test_method_jsonrpc_only(self):
#         rpc_method(dummy_empty, "dummy_name", protocol=Protocol.JSON_RPC)
#         wrapper = ProcedureWrapper(dummy_empty)
#
#         assert not wrapper.is_available_in_xml_rpc()
#         assert wrapper.is_available_in_json_rpc()
#
#     def test_method_repr(self):
#         rpc_method(dummy_empty, "dummy_name", protocol=Protocol.JSON_RPC)
#         wrapper = ProcedureWrapper(dummy_empty)
#         assert "dummy_name" in repr(wrapper)


def dummy_no_doc_no_args():
    pass


class TestNoDocNoArgs:
    """Make sure docstring and introspection works as expected"""

    def test_args_and_return(self):
        wrapper = ProcedureWrapper(dummy_no_doc_no_args)
        assert wrapper.args == []
        assert wrapper.args_doc == {}
        assert wrapper.return_doc == {"type": "", "text": ""}

    def test_doc(self):
        wrapper = ProcedureWrapper(dummy_no_doc_no_args)
        assert wrapper.raw_docstring == ""
        assert wrapper.html_doc == ""


def dummy_no_doc_with_args(a, b, c):
    pass


class TestNoDocWithArgs:
    """Make sure docstring and introspection works as expected"""

    def test_args_and_return(self):
        wrapper = ProcedureWrapper(dummy_no_doc_with_args)
        assert wrapper.args == ["a", "b", "c"]
        assert wrapper.args_doc == {
            "a": {"type": "", "text": ""},
            "b": {"type": "", "text": ""},
            "c": {"type": "", "text": ""},
        }
        assert wrapper.return_doc == {"type": "", "text": ""}

    def test_doc(self):
        wrapper = ProcedureWrapper(dummy_no_doc_with_args)
        assert wrapper.raw_docstring == ""
        assert wrapper.html_doc == ""


def dummy_args_with_typehints(a: int, b: str, c: list) -> dict:
    pass


class TestArgsTypeHint:
    """Type hinting is correctly returned using introspection module"""

    def test_args_and_return(self):
        wrapper = ProcedureWrapper(dummy_args_with_typehints)
        assert wrapper.args == ["a", "b", "c"]
        assert wrapper.args_doc == {
            "a": {"type": "int", "text": ""},
            "b": {"type": "str", "text": ""},
            "c": {"type": "list", "text": ""},
        }
        assert wrapper.return_doc == {"type": "dict", "text": ""}

    def test_doc(self):
        wrapper = ProcedureWrapper(dummy_args_with_typehints)
        assert wrapper.raw_docstring == ""
        assert wrapper.html_doc == ""


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
        wrapper = ProcedureWrapper(dummy_typehints_and_standard_docstring)

        assert wrapper.args == ["a", "b", "c"]
        assert wrapper.args_doc == {
            "a": {"type": "str", "text": "param A"},
            "b": {"type": "dict", "text": "param B"},
            "c": {"type": "float", "text": "param C"},
        }
        assert wrapper.return_doc == {"type": "float", "text": "A decimal value"}

    def test_doc(self):
        wrapper = ProcedureWrapper(dummy_typehints_and_standard_docstring)

        assert wrapper.raw_docstring == ""
        assert wrapper.html_doc == ""


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
        wrapper = ProcedureWrapper(dummy_typehints_and_rst_docstring_types)

        assert wrapper.args == ["x", "y"]
        assert wrapper.args_doc == {
            "x": {"type": "float", "text": "abcd"},
            "y": {"type": "int", "text": "xyz"},
        }
        assert wrapper.return_doc == {"type": "str", "text": "efgh"}

    def test_doc(self):
        wrapper = ProcedureWrapper(dummy_typehints_and_rst_docstring_types)

        assert wrapper.raw_docstring == (
            "This is the docstring part of the function\n\nIt also contains a multi-line description"
        )
        assert wrapper.html_doc == (
            "<p>This is the docstring part of the function</p><p>It also contains a multi-line description</p>"
        )


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
        wrapper = ProcedureWrapper(dummy_rst_docstring)

        assert wrapper.args == ["name", "birthdate", "sex"]
        assert wrapper.args_doc == {
            "name": {"type": "str", "text": "A name"},
            "birthdate": {"type": "datetime.datetime", "text": "A birthdate"},
            "sex": {"type": "str", "text": "Male or Female"},
        }
        assert wrapper.return_doc == {
            "type": "",
            "text": "A string representation of given arguments",
        }

    def test_doc(self):
        wrapper = ProcedureWrapper(dummy_rst_docstring)
        assert wrapper.raw_docstring == "This is the textual doc of the method"
        assert wrapper.html_doc == "<p>This is the textual doc of the method</p>"
