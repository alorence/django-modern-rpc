from django.conf.urls import url

from modernrpc.handlers import JSONRPC, XMLRPC
from modernrpc.views import RPCEntryPoint

urlpatterns = [
    url(r'^all-rpc/', RPCEntryPoint.as_view(), name="generic_rpc_entry_point"),

    url(r'^json-only/', RPCEntryPoint.as_view(protocol=JSONRPC), name="json_rpc_entry_point"),
    url(r'^xml-only/', RPCEntryPoint.as_view(protocol=XMLRPC), name="xml_rpc_entry_point"),
]
