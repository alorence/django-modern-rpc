from __future__ import annotations

from enum import Flag, auto

SYSTEM_NAMESPACE_DOTTED_PATH = "modernrpc.system_procedures.system"


class Protocol(Flag):
    """Define a custom type to use everywhere a protocol (JSON-RPC or XML-RPC) is expected"""

    JSON_RPC = auto()
    XML_RPC = auto()

    ALL = JSON_RPC | XML_RPC


class Id:
    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self):
        return self.name


NOT_SET = Id("NOT_SET")
