# coding: utf-8

# Currently, test environment installs 'jsonrpcclient', which pulls 'future' package from pypi
# As a result, the following Python 3 only import works well on Python2 too.
# That's fine, let's work with that, but if for any reason, 'future' is not anymore installed
# in test environment, this import should be securized with a try except, falling back to 'import xmlrpclib'
# on Python 2.
import xmlrpc.client as xmlrpclib

import jsonrpcclient.http_client as jsonrpclib

__all__ = ['xmlrpclib', 'jsonrpclib']
