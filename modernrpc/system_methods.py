# coding: utf-8
from modernrpc.core import ENTRY_POINT_KEY, PROTOCOL_KEY, get_method, rpc_method, get_all_methods
from modernrpc.exceptions import RPCInvalidParams, RPCUnknownMethod, RPCException, RPC_INTERNAL_ERROR
from modernrpc.handlers import XMLRPC


@rpc_method(name='system.listMethods')
def __system_listMethods(**kwargs):
    """Returns a list of all methods available in the current entry point"""
    entry_point = kwargs.get(ENTRY_POINT_KEY)
    protocol = kwargs.get(PROTOCOL_KEY)

    names = [method.name for method in get_all_methods(entry_point, protocol, sort_methods=True)]

    return names


@rpc_method(name='system.methodSignature')
def __system_methodSignature(method_name, **kwargs):
    """
    Returns an array describing the signature of the given method name.

    The result is an array with:
     - Return type as first elements
     - Types of method arguments from element 1 to N
    :param method_name: Name of a method available for current entry point (and protocol)
    :param kwargs:
    :return: An array describing types of return values and method arguments
    """
    entry_point = kwargs.get(ENTRY_POINT_KEY)
    protocol = kwargs.get(PROTOCOL_KEY)

    method = get_method(method_name, entry_point, protocol)
    if method is None:
        raise RPCInvalidParams('The method {} is not found in the system. Unable to retrieve signature.')
    return method.signature


@rpc_method(name='system.methodHelp')
def __system_methodHelp(method_name, **kwargs):
    """
    Returns the documentation of the given method name.

    :param method_name: Name of a method available for current entry point (and protocol)
    :param kwargs:
    :return: Documentation text for the RPC method
    """
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
    :param kwargs: Internal data
    :type calls: list
    :type kwargs: dict
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
