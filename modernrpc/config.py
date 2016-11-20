# coding: utf-8
import django.conf


class DefaultValues(object):

    #: Set the list of python modules that must be looked up to find RPC methods
    MODERNRPC_METHODS_MODULES = []

    #: Set the class used to convert python data to JSON
    MODERNRPC_JSON_DECODER = 'json.decoder.JSONDecoder'
    #: Set the class used to convert JSON data to python values
    MODERNRPC_JSON_ENCODER = 'django.core.serializers.json.DjangoJSONEncoder'

    #: Set to False if you want to manipulate dates with DateTime class from Python XML RPC builtin lib.
    #: If set to True, dates will be passed as datetime to the RPC function.
    MODERNRPC_XML_USE_BUILTIN_TYPES = True
    #: Set to False if you want to raise an exception when a None value is passed to XML encoder
    MODERNRPC_XMLRPC_ALLOW_NONE = True
    #: Configure the default encoding used by XML encoder
    MODERNRPC_XMLRPC_DEFAULT_ENCODING = None

    #: Set the list of handler classes used by default in any ``RPCEntryPoint`` instance
    MODERNRPC_HANDLERS = [
        'modernrpc.handlers.JSONRPCHandler',
        'modernrpc.handlers.XMLRPCHandler',
    ]

    #: Default name associated with anonymous ``RPCEntryPoint``
    MODERNRPC_DEFAULT_ENTRYPOINT_NAME = '__default_entry_point__'

    #: Configure the format of the docstring used to document your RPC methods.
    #: Possible values are: '', 'rst' or 'md'
    MODERNRPC_DOC_FORMAT = ''


class SettingsWrapper(object):
    def __getattr__(self, item):
        result = getattr(django.conf.settings, item, None)
        if result:
            return result
        return getattr(DefaultValues, item)


settings = SettingsWrapper()
