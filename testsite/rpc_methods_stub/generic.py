from modernrpc.core import rpc_method


@rpc_method()
def add(a, b):
    return a + b


@rpc_method()
def basic_types():
    return {
        'bool': True,
        'int': 42,
        'float': 51.2,
        'string': 'abcde',
        'list': [1, 2, 3],
        'struct': {'a': 6, 'b': 21},
    }


