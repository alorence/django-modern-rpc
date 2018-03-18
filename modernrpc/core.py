# coding: utf-8
import collections
import re

from django.contrib.admindocs.utils import trim_docstring
from django.core.exceptions import ImproperlyConfigured
from django.utils import inspect, six
from django.utils.functional import cached_property

from modernrpc.conf import settings
from modernrpc.utils import ensure_sequence, get_modernrpc_logger

# Special constant meaning "all protocols" or "all entry points"
ALL = "__all__"

# Protocols identifiers
JSONRPC_PROTOCOL = '__json_rpc'
XMLRPC_PROTOCOL = '__xml_rpc'

# Keys used in kwargs dict given to RPC methods
REQUEST_KEY = settings.MODERNRPC_KWARGS_REQUEST_KEY
ENTRY_POINT_KEY = settings.MODERNRPC_KWARGS_ENTRY_POINT_KEY
PROTOCOL_KEY = settings.MODERNRPC_KWARGS_PROTOCOL_KEY
HANDLER_KEY = settings.MODERNRPC_KWARGS_HANDLER_KEY

# Define regular expressions used to parse docstring
PARAM_REXP = re.compile(r'^:param ([\w]+):\s?(.*)')
PARAM_TYPE_REXP = re.compile(r'^:type ([\w]+):\s?(.*)')

RETURN_REXP = re.compile(r'^:return:\s?(.*)')
RETURN_TYPE_REXP = re.compile(r'^:rtype:\s?(.*)')

logger = get_modernrpc_logger(__name__)


class RPCMethod(object):

    def __init__(self, func):

        # Store the reference to the registered function
        self.function = func

        # @rpc_method decorator parameters
        self._external_name = getattr(func, 'modernrpc_name', func.__name__)
        self.entry_point = getattr(func, 'modernrpc_entry_point')
        self.protocol = getattr(func, 'modernrpc_protocol')
        self.str_standardization = getattr(func, 'str_standardization')
        self.str_std_encoding = getattr(func, 'str_standardization_encoding')
        # Authentication related attributes
        self.predicates = getattr(func, 'modernrpc_auth_predicates', None)
        self.predicates_params = getattr(func, 'modernrpc_auth_predicates_params', ())

        # List method's positional arguments
        # We can't use django.utils.inspect.get_func_args() with Python 2, because this function remove the first
        # argument in returned list. This is supposed to remove the first 'self' argument, but doesn't fork well
        # for global functions.
        # For Python 2, we will prefer django.utils.inspect.getargspec(func)[0]. This will work as expected, even if
        # the function has been removed in Django 2.0, since Django 2 doesn't work with Python 2
        self.args = inspect.get_func_args(func) if six.PY3 else inspect.getargspec(func)[0]
        # Does the method accept additional kwargs dict?
        self.accept_kwargs = inspect.func_accepts_kwargs(func)

        # Contains the signature of the method, as returned by "system.methodSignature"
        self.signature = []
        # Contains doc about arguments and their type. We store this in an ordered dict, so the args documentation
        # keep the order defined in docstring
        self.args_doc = collections.OrderedDict()
        # Contains doc about return type and return value
        self.return_doc = {}
        # Docstring parsing. This will initialize self.signature, self.args_doc and self.return_doc
        self.raw_docstring = self.parse_docstring(self.function.__doc__)

    @property
    def name(self):
        return self._external_name

    def __repr__(self):
        return 'RPC Method ' + self.name

    def __str__(self):
        return '{}({})'.format(self._external_name, ', '.join(self.args))

    def __eq__(self, other):
        return \
            self.function == other.function and \
            self.name == other.name and \
            self.entry_point == other.entry_point and \
            self.protocol == other.protocol and \
            self.predicates == other.predicates and \
            self.predicates_params == other.predicates_params

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

        for line in docstring.split('\n'):

            # Empty line
            if not line:
                raw_docstring += '\n'
                continue

            param_match = PARAM_REXP.match(line)
            if param_match:

                param_name, description = param_match.group(1, 2)
                if param_name == 'kwargs':
                    continue

                doc = self.args_doc.setdefault(param_name, {})
                doc['text'] = description
                continue

            param_type_match = PARAM_TYPE_REXP.match(line)
            if param_type_match:

                param_name, param_type = param_type_match.group(1, 2)
                if param_name == 'kwargs':
                    continue

                doc = self.args_doc.setdefault(param_name, {})
                doc['type'] = param_type
                self.signature.append(param_type)
                continue

            return_match = RETURN_REXP.match(line)
            if return_match:
                return_description = return_match.group(1)
                self.return_doc['text'] = return_description
                continue

            return_type_match = RETURN_TYPE_REXP.match(line)
            if return_type_match:
                return_description = return_type_match.group(1)
                self.return_doc['type'] = return_description
                self.signature.insert(0, return_description)
                continue

            # Line doesn't match with known args/return regular expressions,
            # add the line to raw help text
            raw_docstring += line + '\n'
        return raw_docstring

    @cached_property
    def html_doc(self):
        """Methods docstring, as HTML"""
        if not self.raw_docstring:
            result = ''

        elif settings.MODERNRPC_DOC_FORMAT.lower() in ('rst', 'restructred', 'restructuredtext'):
            from docutils.core import publish_parts
            result = publish_parts(self.raw_docstring, writer_name='html')['body']

        elif settings.MODERNRPC_DOC_FORMAT.lower() in ('md', 'markdown'):
            import markdown
            result = markdown.markdown(self.raw_docstring)

        else:
            result = "<p>{}</p>".format(self.raw_docstring.replace('\n\n', '</p><p>').replace('\n', ' '))

        return result

    def check_permissions(self, request):
        """Call the predicate(s) associated with the RPC method, to check if the current request
        can actually call the method.
        Return a boolean indicating if the method should be executed (True) or not (False)"""

        if not self.predicates:
            return True

        # All registered authentication predicates must return True
        return all(
            predicate(request, *self.predicates_params[i])
            for i, predicate in enumerate(self.predicates)
        )

    def available_for_protocol(self, protocol):
        """Check if the current function can be executed from a request defining the given protocol"""
        if self.protocol == ALL or protocol == ALL:
            return True

        return protocol in ensure_sequence(self.protocol)

    def available_for_entry_point(self, entry_point):
        """Check if the current function can be executed from a request to the given entry point"""
        if self.entry_point == ALL or entry_point == ALL:
            return True

        return entry_point in ensure_sequence(self.entry_point)

    def is_valid_for(self, entry_point, protocol):
        """Check if the current function can be executed from a request to the given entry point
        and with the given protocol"""
        return self.available_for_entry_point(entry_point) and self.available_for_protocol(protocol)

    def is_available_in_json_rpc(self):
        """Shortcut checking if the current method can be executed on JSONRPC protocol.
        Used in HTML documentation to easily display protocols supported by a RPC method"""
        return self.available_for_protocol(JSONRPC_PROTOCOL)

    def is_available_in_xml_rpc(self):
        """Shortcut checking if the current method can be executed on XMLRPC protocol.
        Used in HTML documentation to easily display protocols supported by a RPC method"""
        return self.available_for_protocol(XMLRPC_PROTOCOL)

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


class _RPCRegistry(object):

    def __init__(self):
        self._registry = {}

    def reset(self):
        self._registry.clear()

    def register_method(self, func):
        """
        Register a function to be available as RPC method.

        The given function will be inspected to find external_name, protocol and entry_point values set by the decorator
        @rpc_method.
        :param func: A function previously decorated using @rpc_method
        :return: The name of registered method
        """
        if not getattr(func, 'modernrpc_enabled', False):
            raise ImproperlyConfigured('Error: trying to register {} as RPC method, but it has not been decorated.'
                                       .format(func.__name__))

        # Define the external name of the function
        name = getattr(func, 'modernrpc_name', func.__name__)

        logger.debug('Register RPC method "{}"'.format(name))

        if name.startswith('rpc.'):
            raise ImproperlyConfigured('According to RPC standard, method names starting with "rpc." are reserved for '
                                       'system extensions and must not be used. See '
                                       'http://www.jsonrpc.org/specification#extensions for more information.')

        # Encapsulate the function in a RPCMethod object
        method = RPCMethod(func)

        # Ensure method names are unique in the registry
        existing_method = self.get_method(method.name, ALL, ALL)
        if existing_method is not None:
            # Trying to register many times the same function is OK, because if a method is decorated
            # with @rpc_method(), it could be imported in different places of the code
            if method == existing_method:
                return method.name
            # But if we try to use the same name to register 2 different methods, we
            # must inform the developer there is an error in the code
            else:
                raise ImproperlyConfigured("A RPC method with name {} has already been registered".format(method.name))

        # Store the method
        self._registry[method.name] = method
        logger.debug('Method registered. len(registry): {}'.format(len(self._registry)))

        return method.name

    def total_count(self):
        return len(self._registry)

    def get_all_method_names(self, entry_point=ALL, protocol=ALL, sort_methods=False):
        """Return the names of all RPC methods registered supported by the given entry_point / protocol pair"""

        method_names = [
            name for name, method in self._registry.items() if method.is_valid_for(entry_point, protocol)
        ]

        if sort_methods:
            method_names = sorted(method_names)

        return method_names

    def get_all_methods(self, entry_point=ALL, protocol=ALL, sort_methods=False):
        """Return a list of all methods in the registry supported by the given entry_point / protocol pair"""

        if sort_methods:
            return [
                method for (_, method) in sorted(self._registry.items()) if method.is_valid_for(entry_point, protocol)
            ]

        return self._registry.values()

    def get_method(self, name, entry_point, protocol):
        """Retrieve a method from the given name"""

        if name in self._registry and self._registry[name].is_valid_for(entry_point, protocol):
            return self._registry[name]

        return None


registry = _RPCRegistry()


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
    to perform string standardization conversion. Ignored on python 3.
    :type name: str
    :type entry_point: str
    :type protocol: str
    :type str_standardization: type str or unicode
    :type str_standardization_encoding: str
    """

    def decorated(_func):

        _func.modernrpc_enabled = True
        _func.modernrpc_name = name or _func.__name__
        _func.modernrpc_entry_point = entry_point
        _func.modernrpc_protocol = protocol
        _func.str_standardization = str_standardization
        _func.str_standardization_encoding = str_standardization_encoding

        return _func

    # If @rpc_method() is used with parenthesis (with or without argument)
    if func is None:
        return decorated

    # If @rpc_method is used without parenthesis
    return decorated(func)
