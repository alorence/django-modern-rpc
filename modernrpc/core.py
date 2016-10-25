# coding: utf-8
import importlib
import logging
import re

from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.utils import inspect

from modernrpc import modernrpc_settings
from modernrpc.exceptions import RPCInvalidParams, RPCUnknownMethod, RPCException, RPC_INTERNAL_ERROR
from modernrpc.handlers import XMLRPC, JSONRPC

logger = logging.getLogger(__name__)

RPC_REGISTRY_KEY = '__rpc_registry__'
DEFAULT_REGISTRY_TIMEOUT = None
ALL = "__all__"

REQUEST_KEY = 'request'
ENTRY_POINT_KEY = 'entry_point'
PROTOCOL_KEY = 'protocol'
HANDLER_KEY = 'handler'

PARAM_REXP = r':param ([\w]+):\s?(.*)'
RETURN_REXP = r':return:\s?(.*)'
PARAM_TYPE_REXP = r':type ([\w]+):\s?(.*)'
RETURN_TYPE_REXP = r':rtype:\s?(.*)'


class RPCMethod(object):

    def __init__(self, function, external_name, entry_point=ALL, protocol=ALL):
        self.module = function.__module__
        self.func_name = function.__name__
        self.external_name = external_name
        self.entry_point = entry_point
        self.protocol = protocol

        # Contains the signature of the method, as returned by "system.methodSignature"
        self.signature = []
        # Contains the method's docstring, in HTML form
        self.html_doc = ''
        # Contains doc about argumetns and their type
        self.args_doc = {}
        # Contains doc about return type and return value
        self.return_doc = {}

        self.args = inspect.get_func_args(function)
        raw_docstring = self.parse_docstring(function.__doc__)
        self.html_doc = self.to_html(raw_docstring)

        # Flag the method to accept additional kwargs dict
        self.accept_kwargs = inspect.func_accepts_kwargs(function)

    @property
    def name(self):
        return self.external_name

    def __repr__(self):
        return 'RPC Method ' + self.name

    def parse_docstring(self, content):
        """
        Parse the given full docstring, and extract method description, arguments, and return documentation.

        This method try to find arguments description and types, and put the information in "args_doc" and "signature"
        members. Also parse return type and description, and put the information in "return_doc" member.
        All other lines are added to the returned string
        :param content: The full docstring
        :type content: str
        :return: The parsed method description
        :rtype: str
        """
        raw_docstring = ''

        if content is None:
            return raw_docstring

        lines = content.split('\n')
        for line in lines:
            sline = line.strip()

            param_match = re.match(PARAM_REXP, sline)
            return_match = re.match(RETURN_REXP, sline)
            param_type_match = re.match(PARAM_TYPE_REXP, sline)
            return_type_match = re.match(RETURN_TYPE_REXP, sline)

            if param_match:
                param_name, description = param_match.group(1, 2)
                if param_name == 'kwargs':
                    continue
                doc = self.args_doc.get(param_name, {})
                doc['text'] = description
                self.args_doc[param_name] = doc

            elif param_type_match:
                param_name, param_type = param_type_match.group(1, 2)
                if param_name == 'kwargs':
                    continue
                doc = self.args_doc.get(param_name, {})
                doc['type'] = param_type
                self.args_doc[param_name] = doc
                self.signature.append(param_type)

            elif return_match:
                return_description = return_match.group(1)
                self.return_doc['text'] = return_description

            elif return_type_match:
                return_description = return_type_match.group(1)
                self.return_doc['type'] = return_description
                self.signature.insert(0, return_description)

            else:
                # Add the line to help text
                raw_docstring += line + '\n'

        return raw_docstring

    def to_html(self, docstring):

        if not docstring:
            return ''

        if modernrpc_settings.MODERNRPC_DOC_FORMAT.lower() in ('rst', 'reStructred', 'reStructuredText'):
            from docutils.core import publish_parts
            return publish_parts(docstring, writer_name='html')
        elif modernrpc_settings.MODERNRPC_DOC_FORMAT.lower() in ('md', 'markdown'):
            import markdown
            return markdown.markdown(docstring)
        else:
            return "<p>{}</p>".format(docstring.replace('\n\n', '</p><p>'))

    def execute(self, *args, **kwargs):
        """
        Call the function encapsulated by the current instance

        :return:
        """
        # Try to load the method address
        module = importlib.import_module(self.module)
        func = getattr(module, self.func_name)

        # Call the rpc method, as standard python function
        if self.accept_kwargs:
            return func(*args, **kwargs)
        else:
            return func(*args)

    def __eq__(self, other):
        return \
            self.external_name == other.external_name and \
            self.module == other.module and \
            self.func_name == other.func_name and \
            self.entry_point == other.entry_point and \
            self.protocol == other.protocol

    def available_for_protocol(self, protocol):
        if self.protocol == ALL or protocol == ALL:
            return True
        else:
            valid_protocols = self.protocol if isinstance(self.protocol, list) else [self.protocol]
            return protocol in valid_protocols

    def available_for_entry_point(self, entry_point):
        if self.entry_point == ALL or entry_point == ALL:
            return True
        else:
            valid_entry_points = self.entry_point if isinstance(self.entry_point, list) else [self.entry_point]
            return entry_point in valid_entry_points

    def is_valid_for(self, entry_point, protocol):
        return self.available_for_entry_point(entry_point) and self.available_for_protocol(protocol)

    # Helpers to make tests in template easier
    def is_doc_available(self):
        """Returns True if a textual documentation is available for this method"""
        return bool(self.html_doc)

    def is_return_doc_available(self):
        """Returns True if this method's return is documented"""
        return bool(self.return_doc and (self.return_doc.get('text') or self.return_doc.get('type')))

    def is_args_doc_available(self):
        """Returns True if any of the method's arguments is documented"""
        return self.args_doc

    def is_any_doc_available(self):
        """Returns True if there is a textual documentation or a documentation on arguments or return of the method."""
        return self.is_args_doc_available() or self.is_return_doc_available() or self.is_doc_available()

    def is_available_in_json_rpc(self):
        return self.available_for_protocol(JSONRPC)

    def is_available_in_xml_rpc(self):
        return self.available_for_protocol(XMLRPC)


def get_all_methods(entry_point=ALL, protocol=ALL, sort_methods=False):
    """Return a list of all methods in the registry supported by the given entry_point / protocol pair"""
    # Get the current RPC registry from internal cache
    registry = cache.get(RPC_REGISTRY_KEY, default={})

    if sort_methods:
        methods = [method for (_, method) in sorted(registry.items())]
    else:
        methods = registry.values()

    return [
        method for method in methods if method.is_valid_for(entry_point, protocol)
    ]


def get_method(name, entry_point, protocol):
    """Retrieve a method from the given name"""
    # Get the current RPC registry from internal cache
    registry = cache.get(RPC_REGISTRY_KEY, default={})

    # Try to find the given method in cache
    if name in registry:
        method = registry.get(name)
        # Ensure the method can be returned for given entry_point and protocol
        if method and method.is_valid_for(entry_point, protocol):
            return method

    return None


def register_method(function, name=None, entry_point=ALL, protocol=ALL):
    """
    Register a function to be available as RPC method.

    All arguments but ``function`` are optional

    :param function: The python function to register
    :param name: Used as RPC method name instead of original function name
    :param entry_point: Default: ALL. Used to limit usage of the RPC method for a specific set of entry points
    :param protocol: Default: ALL. Used to limit usage of the RPC method for a specific protocol (JSONRPC or XMLRPC)
    :type function: func
    :type name: str
    :type entry_point: str
    :type protocol: str
    :return: None
    """
    # Define the external name of the function
    if not name:
        name = getattr(function, '__name__')
    logger.debug('Register method {}'.format(name))

    if name and name.startswith('rpc.'):
        raise ImproperlyConfigured('According to RPC standard, method names starting with "rpc." are reserved for '
                                   'system extensions and must not be used. See '
                                   'http://www.jsonrpc.org/specification#extensions for more information.')

    # Encapsulate the function in a RPCMethod object
    method = RPCMethod(function, name, entry_point, protocol)

    # Get the current RPC registry from internal cache
    registry = cache.get(RPC_REGISTRY_KEY, default={})

    # Ensure method names are unique in the registry
    if method.external_name in registry:
        # Trying to register many times the same function is OK, because if a method is decorated
        # with @rpc_method(), it could be imported in different places of the code
        if method == registry[method.external_name]:
            return
        # But if we try to use the same name to register 2 different methods, we
        # must inform the developer there is an error in the code
        else:
            raise ImproperlyConfigured("A RPC method with name {} has already been registered"
                                       .format(method.external_name))

    # Store the method
    registry[method.external_name] = method
    # Update the registry in internal cache
    cache.set(RPC_REGISTRY_KEY, registry, timeout=DEFAULT_REGISTRY_TIMEOUT)


def rpc_method(name=None, entry_point=ALL, protocol=ALL):
    """
    Decorator used to define any global function as RPC method.

    All arguments are optional

    :param name: Used as RPC method name instead of original function name
    :param entry_point: Default: ALL. Used to limit usage of the RPC method for a specific set of entry points
    :param protocol: Default: ALL. Used to limit usage of the RPC method for a specific protocol (JSONRPC or XMLRPC)
    :type name: str
    :type entry_point: str
    :type protocol: str
    """

    def __register(function):
        register_method(function, name, entry_point, protocol)
        return function

    return __register


@rpc_method(name='system.listMethods')
def __system_listMethods(**kwargs):

    entry_point = kwargs.get(ENTRY_POINT_KEY)
    protocol = kwargs.get(PROTOCOL_KEY)

    names = [method.name for method in get_all_methods(entry_point, protocol, sort_methods=True)]

    return names


@rpc_method(name='system.methodSignature')
def __system_methodSignature(method_name, **kwargs):

    entry_point = kwargs.get(ENTRY_POINT_KEY)
    protocol = kwargs.get(PROTOCOL_KEY)

    method = get_method(method_name, entry_point, protocol)
    if method is None:
        raise RPCInvalidParams('The method {} is not found in the system. Unable to retrieve signature.')
    return method.signature


@rpc_method(name='system.methodHelp')
def __system_methodHelp(method_name, **kwargs):

    entry_point = kwargs.get(ENTRY_POINT_KEY)
    protocol = kwargs.get(PROTOCOL_KEY)

    method = get_method(method_name, entry_point, protocol)
    if method is None:
        raise RPCInvalidParams('The method {} is not found in the system. Unable to retrieve method help.')
    return method.html_doc


@rpc_method(name='system.multicall', protocol=XMLRPC)
def __system_multiCall(calls, **kwargs):
    """
    Call multiple RPC methods at once.

    :param calls: An array of struct like {"methodName": string, "params": array }
    :param kwargs:
    :return:
    """
    if not isinstance(calls, list):
        raise RPCInvalidParams('method_names must be a list')

    entry_point = kwargs.get(ENTRY_POINT_KEY)
    protocol = kwargs.get(PROTOCOL_KEY)

    results = []
    for call in calls:
        method_name, params = call['methodName'], call['params']
        method = get_method(method_name, entry_point, protocol)

        try:
            if not method:
                raise RPCUnknownMethod(method_name)

            result = method.execute(*params, **kwargs)
            # From https://mirrors.talideon.com/articles/multicall.html:
            # "Notice that regular return values are always nested inside a one-element array. This allows you to
            # return structs from functions without confusing them with faults."
            results.append([result])
        except RPCException as e:
            results.append({
                'faultCode': e.code,
                'faultString': e.message,
            })
        except Exception as e:
            results.append({
                'faultCode': RPC_INTERNAL_ERROR,
                'faultString': str(e),
            })

    return results
