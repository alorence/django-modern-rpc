# coding: utf-8
from modernrpc.core import rpc_method


@rpc_method
def dummy_remote_procedure_1():
    # Manually registered remote procedure.
    return 33


@rpc_method(name='another_name')
def dummy_remote_procedure_2():
    # Manually registered remote procedure, with custom name.
    return 33


@rpc_method(name='rpc.invalid.name')
def dummy_remote_procedure_3():
    # Manually registered remote procedure, with invalid custom name.
    return 42


@rpc_method(name='divide')
def dummy_remote_procedure_4():
    # Manually registered remote procedure, with invalid custom name (name already registered).
    return 42


def not_decorated_procedure():
    pass


def single_line_documented():
    """*italic*, **strong**, normal text"""
    return 111


def multi_line_documented_1():
    """
    This method has multi-lines documentation.

    The content is indented when raw ``__doc__`` attribute function is read.
    The indentation should not interfere with semantic interpretation of the docstring.
    """
    return 111


def multi_line_documented_2():
    """
    This method has *multi-lines* **documentation**.

    Here is a quote block:

        abcdef 123456

    """
    return "abc"


def dummy_function():
    pass


def dummy_function_with_doc(name, birth_date, sex):
    """
    This is the textual doc of the method
    :param name: A name
    :param birth_date: A birth date
    :param sex: Male or Female
    :type name: str
    :type birth_date: datetime.datetim
    :type sex: str
    :return: A string representation of given arguments
    """
    return '{} ({}) born on {}'.format(name, str(sex), str(birth_date))
