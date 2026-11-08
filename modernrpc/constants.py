from enum import Flag, auto

from typing_extensions import Sentinel

NOT_SET = Sentinel("NOT_SET")
SYSTEM_NAMESPACE_DOTTED_PATH = "modernrpc.system_procedures.system"


class Protocol(Flag):
    """Define a custom type to use everywhere a protocol (JSON-RPC or XML-RPC) is expected"""

    JSON_RPC = auto()
    XML_RPC = auto()

    ALL = JSON_RPC | XML_RPC
