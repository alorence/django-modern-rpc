from django.urls import path
from testsite.rpc.servers import jsonrpc_server, server, xmlrpc_server

urlpatterns = [
    path("all-rpc/", server.view, name="generic_rpc_entry_point"),
    path("json-only/", jsonrpc_server.view, name="json_rpc_entry_point"),
    path("xml-only/", xmlrpc_server.view, name="xml_rpc_entry_point"),
]
