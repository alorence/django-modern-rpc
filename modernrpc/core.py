# coding: utf-8
import collections
import importlib
import logging
import re

from django.contrib.admindocs.utils import trim_docstring
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.utils import inspect
from django.utils import six

from modernrpc.compat import standardize_strings
from modernrpc.conf import settings
from modernrpc.handlers import XMLRPC, JSONRPC

logger = logging.getLogger(__name__)
# warnings.simplefilter('once', DeprecationWarning)

# The registry keys in current cache
RPC_REGISTRY_PREFIX = 'modernrpc'
RPC_REGISTRY_INDEX = RPC_REGISTRY_PREFIX + '_index'
RPC_REGISTRY_VERSION = 2
# Default timeout set to registry in cache
DEFAULT_REGISTRY_TIMEOUT = None

# Keys used in kwargs dict given to RPC methods
REQUEST_KEY = 'request'
ENTRY_POINT_KEY = 'entry_point'
PROTOCOL_KEY = 'protocol'
HANDLER_KEY = 'handler'

# Special constant meaning "all protocols" or "all entry points"
ALL = "__all__"


class RPCMethod(object):

    def __init__(self, function=None):

        if function is None:
            return

        self.module = function.__module__
        self.func_name = function.__name__

        # @rpc_method decorator parameters
        self.external_name = getattr(function, 'modernrpc_name', self.func_name)
        self.entry_point = getattr(function, 'modernrpc_entry_point')
        self.protocol = getattr(function, 'modernrpc_protocol')
        self.str_standardization = getattr(function, 'str_standardization')
        self.str_std_encoding = getattr(function, 'str_standardization_encoding')

        if not isinstance(self.str_standardization, six.string_types):
            # unicode => "unicode"
            # str => "str"
            self.str_standardization = self.str_standardization.__name__

        # List method's positional arguments
        self.args = inspect.get_func_args(function)
        # Flag the method to accept additional kwargs dict
        self.accept_kwargs = inspect.func_accepts_kwargs(function)

        # Contains the signature of the method, as returned by "system.methodSignature"
        self.signature = []
        # Contains the method's docstring, in HTML form
        self.html_doc = ''
        # Contains doc about argumetns and their type. We store this in an ordered dict, so the args documentation
        # keep the order defined in docstring
        self.args_doc = collections.OrderedDict()
        # Contains doc about return type and return value
        self.return_doc = {}

        # Docstring parsing
        self.raw_docstring = self.parse_docstring(function.__doc__)
        self.html_doc = self.raw_docstring_to_html(self.raw_docstring)

    def to_dict(self):
        return {
            'location': [self.module, self.func_name],

            'external_name': self.external_name,
            'entry_point': self.entry_point,
            'protocol': self.protocol,
            'str_standardization': self.str_standardization,
            'str_std_encoding': self.str_std_encoding,

            'args': self.args,
            'accept_kwargs': self.accept_kwargs,

            'signature': self.signature,
            'args_doc': dict(self.args_doc),
            'return_doc': self.return_doc,
            'raw_docstring': self.raw_docstring,
            'html_doc': self.html_doc,
        }

    @classmethod
    def from_dict(cls, data_dict):
        o = cls()
        o.module, o.func_name = data_dict['location']

        o.external_name = data_dict['external_name']
        o.entry_point = data_dict['entry_point']
        o.protocol = data_dict['protocol']
        o.str_standardization = data_dict['str_standardization']
        o.str_std_encoding = data_dict['str_std_encoding']

        o.args = data_dict['args']
        o.accept_kwargs = data_dict['accept_kwargs']

        o.signature = data_dict['signature']
        o.args_doc = collections.OrderedDict(data_dict['args_doc'])
        o.return_doc = data_dict['return_doc']
        o.raw_docstring = data_dict['raw_docstring']
        o.html_doc = data_dict['html_doc']

        return o

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

    def check_permissions(self, request):
        """Call the predicate(s) associated with the RPC method, to check if the current request
        can actually call the method.
        Return a boolean indicating if the method should be executed (True) or not (False)"""

        module = importlib.import_module(self.module)
        func = getattr(module, self.func_name)

        predicates = getattr(func, 'modernrpc_auth_predicates', None)

        if not predicates:
            return True

        predicates_params = getattr(func, 'modernrpc_auth_predicates_params', None)

        # All registered authentication predicates must return True
        return all(
            predicate(request, *predicates_params[i])
            for i, predicate in enumerate(predicates)
        )

    def execute(self, *args, **kwargs):
        """
        Call the function encapsulated by the current instance

        :return:
        """
        # Try to load the method address
        module = importlib.import_module(self.module)
        func = getattr(module, self.func_name)

        if six.PY2:
            args = standardize_strings(args, strtype=self.str_standardization, encoding=self.str_std_encoding)

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
        return available_for_protocol(self.protocol, JSONRPC)

    def is_available_in_xml_rpc(self):
        return available_for_protocol(self.protocol, XMLRPC)


def make_key(key):
    return RPC_REGISTRY_PREFIX + '_' + key


def available_for_protocol(method_protocol, protocol):
    """Check if given method summary can be executed on the given protocol"""
    if method_protocol == ALL or protocol == ALL:
        return True

    method_protocols = method_protocol if isinstance(method_protocol, list) else [method_protocol]
    return protocol in method_protocols


def available_for_entry_point(method_entry_point, entry_point):
    """Check if given method summary can be executed on the given entry point"""
    if method_entry_point == ALL or entry_point == ALL:
        return True

    method_entry_points = method_entry_point if isinstance(method_entry_point, list) else [method_entry_point]
    return entry_point in method_entry_points


def is_valid_for(method_summary, entry_point, protocol):
    return \
        available_for_entry_point(method_summary['entry_point'], entry_point) \
        and \
        available_for_protocol(method_summary['protocol'], protocol)


def get_method(name, entry_point, protocol):
    """Retrieve a method from the given name"""
    # Get the current RPC registry from internal cache
    methods_index = cache.get(RPC_REGISTRY_INDEX, default={}, version=RPC_REGISTRY_VERSION)

    # Try to find the given method in cache
    if name in methods_index:
        method_summary = methods_index[name]
        # Ensure the method can be returned for given entry_point and protocol
        if is_valid_for(method_summary, entry_point, protocol):

            method_dump = cache.get(make_key(name), default={}, version=RPC_REGISTRY_VERSION)
            if not method_dump:
                # Oops, a method found in index doesn't have corresponding info in global registry.
                # It must be unregistered
                unregister_rpc_method(name)
                return None

            return RPCMethod.from_dict(method_dump)

    return None


def unregister_rpc_method(name):
    """Remove a method from registry"""
    # Get the current RPC registry from internal cache
    methods_index = cache.get(RPC_REGISTRY_INDEX, default={}, version=RPC_REGISTRY_VERSION)

    if name in methods_index:
        logger.debug('Unregister RPC method {}'.format(name))
        del methods_index[name]
        cache.set(RPC_REGISTRY_INDEX, methods_index, version=RPC_REGISTRY_VERSION, timeout=DEFAULT_REGISTRY_TIMEOUT)

    # In all case, delete the entry for the corresponding method
    cache.delete(make_key(name), version=RPC_REGISTRY_VERSION)


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

    # Encapsulate the function in a RPCMethod object
    method = RPCMethod(function)

    # Get the current RPC registry from internal cache

    # Ensure method names are unique in the registry
    existing_method = get_method(method.name, ALL, ALL)
    if existing_method is not None:
        # Trying to register many times the same function is OK, because if a method is decorated
        # with @rpc_method(), it could be imported in different places of the code
        if method == existing_method:
            return method.name
        # But if we try to use the same name to register 2 different methods, we
        # must inform the developer there is an error in the code
        else:
            raise ImproperlyConfigured("A RPC method with name {} has already been registered".format(method.name))

    # Store the method in cache
    methods_index = cache.get(RPC_REGISTRY_INDEX, default={}, version=RPC_REGISTRY_VERSION)
    methods_index[method.name] = {
        'entry_point': method.entry_point,
        'protocol': method.protocol,
    }
    cache.set(RPC_REGISTRY_INDEX, methods_index, timeout=DEFAULT_REGISTRY_TIMEOUT, version=RPC_REGISTRY_VERSION)    
    cache.set(make_key(method.name), method.to_dict(), timeout=DEFAULT_REGISTRY_TIMEOUT, version=RPC_REGISTRY_VERSION)

    return method.name


def get_all_method_names(entry_point=ALL, protocol=ALL, sort_methods=False):
    """Return the list of all RPC methods registered"""

    # Get the current RPC registry from internal cache
    methods_index = cache.get(RPC_REGISTRY_INDEX, version=RPC_REGISTRY_VERSION, default=[])

    names = [m for m in methods_index if is_valid_for(methods_index[m], entry_point=entry_point, protocol=protocol)]

    if sort_methods:
        names = sorted(names)

    return names


def get_all_methods(entry_point=ALL, protocol=ALL, sort_methods=False):
    """Return a list of all methods in the registry supported by the given entry_point / protocol pair"""

    names = get_all_method_names(entry_point=entry_point, protocol=protocol, sort_methods=sort_methods)

    return [
        RPCMethod.from_dict(cache.get(make_key(method_name), version=RPC_REGISTRY_VERSION)) for method_name in names
    ]


def rpc_method(func=None, name=None, entry_point=ALL, protocol=ALL,
               str_standardization=settings.MODERNRPC_PY2_STR_TYPE,
               str_standardization_encoding=settings.MODERNRPC_PY2_STR_ENCODING):
    """
    Mark a standard python function as RPC method.

    All arguments are optional

    :param func: A standard function
    :param name: Used as RPC method name instead of original function name
    :param entry_point: Default: ALL. Used to limit usage of the RPC method for a specific set of entry points
    :param protocol: Default: ALL. Used to limit usage of the RPC method for a specific protocol (JSONRPC or XMLRPC)
    :param str_standardization: Default: settings.MODERNRPC_PY2_STR_TYPE. Configure string standardization on python 2.
    Ignored on python 3.
    :param str_standardization_encoding: Default: settings.MODERNRPC_PY2_STR_ENCODING. Configure the encoding used
    to perform string standardization conversion
    :type name: str
    :type entry_point: str
    :type protocol: str
    :type str_standardization: type str or unicode
    :type str_standardization_encoding: str
    """

    def decorated(function):

        function.modernrpc_enabled = True
        function.modernrpc_name = name or function.__name__
        function.modernrpc_entry_point = entry_point
        function.modernrpc_protocol = protocol
        function.str_standardization = str_standardization
        function.str_standardization_encoding = str_standardization_encoding

        return function

    # If @rpc_method() is used with parenthesis (with or without argument)
    if func is None:
        return decorated

    # If @rpc_method is used without parenthesis
    return decorated(func)


def clean_old_cache_content():
    """Clean CACHE data from old versions of django-modern-rpc"""
    if cache.has_key('__rpc_registry__', version=1):
        cache.delete('__rpc_registry__', version=1)
