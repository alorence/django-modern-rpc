# coding: utf-8
import collections
import importlib
import logging
import re
import warnings

from django.contrib.admindocs.utils import trim_docstring
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.utils import inspect
from modernrpc.config import settings
from modernrpc.handlers import XMLRPC, JSONRPC

logger = logging.getLogger(__name__)
warnings.simplefilter('once', DeprecationWarning)

# The registry key in current cache
RPC_REGISTRY_KEY = '__rpc_registry__'
# Timeout set to registry in cache
DEFAULT_REGISTRY_TIMEOUT = None

# Keys used in kwargs dict given to RPC methods
REQUEST_KEY = 'request'
ENTRY_POINT_KEY = 'entry_point'
PROTOCOL_KEY = 'protocol'
HANDLER_KEY = 'handler'

# Special constant meaning "all protocols" or "all entry points"
ALL = "__all__"


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
        # Contains doc about argumetns and their type. We store this in an ordered dict, so the args documentation
        # keep the order defined in docstring
        self.args_doc = collections.OrderedDict()
        # Contains doc about return type and return value
        self.return_doc = {}

        self.args = inspect.get_func_args(function)

        # Flag the method to accept additional kwargs dict
        self.accept_kwargs = inspect.func_accepts_kwargs(function)

        # Docstring parsing
        self.raw_docstring = self.parse_docstring(function.__doc__)
        self.html_doc = self.raw_docstring_to_html(self.raw_docstring)

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

        if not content:
            return

        raw_docstring = ''
        # We use the helper defined in django admindocs app to remove indentation chars from docstring,
        # and parse it as title, body, metadata. We don't use metadata for now.
        docstring = trim_docstring(content)

        # Define regular expression used to parse docstring
        PARAM_REXP = r'^:param ([\w]+):\s?(.*)'
        RETURN_REXP = r'^:return:\s?(.*)'
        PARAM_TYPE_REXP = r'^:type ([\w]+):\s?(.*)'
        RETURN_TYPE_REXP = r'^:rtype:\s?(.*)'

        lines = docstring.split('\n')
        for line in lines:

            # Empty line
            if not line:
                raw_docstring += '\n'
                continue

            param_match = re.match(PARAM_REXP, line)
            if param_match:
                param_name, description = param_match.group(1, 2)
                if param_name == 'kwargs':
                    continue
                doc = self.args_doc.get(param_name, {})
                doc['text'] = description
                self.args_doc[param_name] = doc
                continue

            param_type_match = re.match(PARAM_TYPE_REXP, line)
            if param_type_match:
                param_name, param_type = param_type_match.group(1, 2)
                if param_name == 'kwargs':
                    continue
                doc = self.args_doc.get(param_name, {})
                doc['type'] = param_type
                self.args_doc[param_name] = doc
                self.signature.append(param_type)
                continue

            return_match = re.match(RETURN_REXP, line)
            if return_match:
                return_description = return_match.group(1)
                self.return_doc['text'] = return_description
                continue

            return_type_match = re.match(RETURN_TYPE_REXP, line)
            if return_type_match:
                return_description = return_type_match.group(1)
                self.return_doc['type'] = return_description
                self.signature.insert(0, return_description)
                continue

            # Line doesn't match with known args/return regular expression,
            # add the line to raw help text
            raw_docstring += line + '\n'
        return raw_docstring

    @staticmethod
    def raw_docstring_to_html(docstring):

        if not docstring:
            return ''

        if settings.MODERNRPC_DOC_FORMAT.lower() in ('rst', 'reStructred', 'reStructuredText'):
            from docutils.core import publish_parts
            return publish_parts(docstring, writer_name='html')['body']

        elif settings.MODERNRPC_DOC_FORMAT.lower() in ('md', 'markdown'):
            import markdown
            return markdown.markdown(docstring)

        return "<p>{}</p>".format(docstring.replace('\n\n', '</p><p>').replace('\n', '<br/'))

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

    # Helpers to simplify templates generation
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


def get_all_method_names(entry_point=ALL, protocol=ALL, sort_methods=False):
    """"""
    # Get the current RPC registry from internal cache
    registry = cache.get(RPC_REGISTRY_KEY, default={})

    method_namess = [
        name for name, method in registry.items() if method.is_valid_for(entry_point, protocol)
    ]

    if sort_methods:
        method_namess = sorted(method_namess)

    return method_namess


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


def unregister_rpc_method(method_name):
    """Remove a method from registry"""
    # Get the current RPC registry from internal cache
    registry = cache.get(RPC_REGISTRY_KEY, default={})

    if method_name in registry:
        logger.debug('Unregister RPC method {}'.format(method_name))
        del registry[method_name]

    # Update the registry in internal cache
    cache.set(RPC_REGISTRY_KEY, registry, timeout=DEFAULT_REGISTRY_TIMEOUT)


def register_rpc_method(function):
    """
    Register a function to be available as RPC method.

    The given function will be inspected to find external_name, protocol and entry_point values set by the decorator
    @rpc_method.
    :param function: A function previously decorated using @rpc_method
    :return: The name of registered method
    """
    if not getattr(function, 'modernrpc_enabled', False):
        raise ImproperlyConfigured('Error: trying to register {} as RPC method, but it has not been decorated.'
                                   .format(function.__name__))

    # Define the external name of the function
    name = getattr(function, 'modernrpc_name', function.__name__)

    logger.debug('Register RPC method {}'.format(name))

    if name.startswith('rpc.'):
        raise ImproperlyConfigured('According to RPC standard, method names starting with "rpc." are reserved for '
                                   'system extensions and must not be used. See '
                                   'http://www.jsonrpc.org/specification#extensions for more information.')

    entry_point = getattr(function, 'modernrpc_entry_point')
    protocol = getattr(function, 'modernrpc_protocol')

    # Encapsulate the function in a RPCMethod object
    method = RPCMethod(function, name, entry_point, protocol)

    # Get the current RPC registry from internal cache
    registry = cache.get(RPC_REGISTRY_KEY, default={})

    # Ensure method names are unique in the registry
    if method.external_name in registry:
        # Trying to register many times the same function is OK, because if a method is decorated
        # with @rpc_method(), it could be imported in different places of the code
        if method == registry[method.external_name]:
            return method.external_name
        # But if we try to use the same name to register 2 different methods, we
        # must inform the developer there is an error in the code
        else:
            raise ImproperlyConfigured("A RPC method with name {} has already been registered"
                                       .format(method.external_name))

    # Store the method
    registry[method.external_name] = method

    # Update the registry in internal cache
    cache.set(RPC_REGISTRY_KEY, registry, timeout=DEFAULT_REGISTRY_TIMEOUT)

    return method.external_name


def rpc_method(func=None, name=None, entry_point=ALL, protocol=ALL):
    """
    Mark a standard python function as RPC method.

    All arguments are optional

    :param func: A standard function
    :param name: Used as RPC method name instead of original function name
    :param entry_point: Default: ALL. Used to limit usage of the RPC method for a specific set of entry points
    :param protocol: Default: ALL. Used to limit usage of the RPC method for a specific protocol (JSONRPC or XMLRPC)
    :type name: str
    :type entry_point: str
    :type protocol: str
    """

    def decorated(function):

        function.modernrpc_enabled = True
        function.modernrpc_name = name or function.__name__
        function.modernrpc_entry_point = entry_point
        function.modernrpc_protocol = protocol

        return function

    # If @rpc_method is used without any argument nor parenthesis
    if func is None:
        def decorator(f):
            return decorated(f)
        return decorator
    # If @rpc_method() is used with parenthesis (with or without arguments)
    return decorated(func)


# Deprecated method: will be removed in version 1.0
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

    warnings.warn('"register_method" is deprecated and will be removed in a future version.\nUse settings.'
                  'MODERNRPC_METHODS_MODULES to declare modules containing RPC method, and decorate each method '
                  'with @rpc_method. Refer\nto the documentation for more info.', DeprecationWarning, stacklevel=2)

    function.modernrpc_enabled = True
    function.modernrpc_name = name or function.__name__
    function.modernrpc_entry_point = entry_point
    function.modernrpc_protocol = protocol

    register_rpc_method(function)
