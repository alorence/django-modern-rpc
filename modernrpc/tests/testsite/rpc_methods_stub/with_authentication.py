from modernrpc.auth import login_required
from modernrpc.core import rpc_method


@login_required
@rpc_method
def method_need_login(x):
    return x*x
