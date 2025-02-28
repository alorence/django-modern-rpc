from modernrpc import Protocol

# In 1.0.0, following constants were replaced by Protocol enum class
# Redefine them for backward compatibility
JSONRPC_PROTOCOL, XMLRPC_PROTOCOL = Protocol.JSON_RPC, Protocol.XML_RPC
GENERIC_ALL = ALL = Protocol.ALL
