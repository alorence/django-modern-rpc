from django.urls import path

from modernrpc.core import Protocol
from modernrpc.views import RPCEntryPoint

urlpatterns = [
    path('all-rpc/', RPCEntryPoint.as_view(), name="generic_rpc_entry_point"),
    path('all-rpc-doc/', RPCEntryPoint.as_view(enable_doc=True, enable_rpc=False), name="generic_entry_point_doc"),
    path('all-rpc-doc-bs4/',
         RPCEntryPoint.as_view(
             enable_doc=True,
             enable_rpc=False,
             template_name='modernrpc/bootstrap4/doc_index.html',

         ),
         name="bootstrap4_entry_point_doc"
         ),

    path('json-only/', RPCEntryPoint.as_view(protocol=Protocol.JSON_RPC), name="json_rpc_entry_point"),
    path('xml-only/', RPCEntryPoint.as_view(protocol=Protocol.XML_RPC), name="xml_rpc_entry_point"),
]
