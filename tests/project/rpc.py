from modernrpc import RpcNamespace

math = RpcNamespace()


@math.register_procedure
def add(*args: float) -> float:
    return sum(args)


@math.register_procedure
def divide(a: float, b: float) -> float:
    return a / b
