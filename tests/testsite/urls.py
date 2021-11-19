from django.urls import path

from modernrpc.core import JSONRPC_PROTOCOL, XMLRPC_PROTOCOL
from modernrpc.views import RPCEntryPoint

urlpatterns = [
    path('all-rpc/', RPCEntryPoint.as_view(), name="generic_rpc_entry_point"),
    path('all-rpc-doc/', RPCEntryPoint.as_view(enable_doc=True, enable_rpc=False), name="generic_entry_point_doc"),

    path('json-only/', RPCEntryPoint.as_view(protocol=JSONRPC_PROTOCOL), name="json_rpc_entry_point"),
    path('xml-only/', RPCEntryPoint.as_view(protocol=XMLRPC_PROTOCOL), name="xml_rpc_entry_point"),
]
