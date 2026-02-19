from enum import Enum, Flag, auto

SYSTEM_NAMESPACE_DOTTED_PATH = "modernrpc.system_procedures.system"


class Protocol(Flag):
    """Define a custom type to use everywhere a protocol (JSON-RPC or XML-RPC) is expected"""

    JSON_RPC = auto()
    XML_RPC = auto()

    ALL = JSON_RPC | XML_RPC


# Python does not define a Sentinel class for now (maybe in 3.15+?)
# typing_extensions providees a nice one, but it required only in Python < 3.11 environments
# Let's define this using a builtin enum
# Ref: https://github.com/python/typing/issues/236#issuecomment-227180301
class Default(Enum):
    NOT_SET = 0


NOT_SET = Default.NOT_SET
