from modernrpc import RPCNamespace

math = RPCNamespace()


@math.register_procedure
def add(*args: float):
    return sum(args)


@math.register_procedure
def divide(a: float, b: float):
    return a / b
