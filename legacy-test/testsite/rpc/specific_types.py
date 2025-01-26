import datetime

from django.contrib.auth import get_user_model

from modernrpc.server import RPCNamespace

bp = RPCNamespace()


@bp.register_procedure()
def get_true():
    return True


@bp.register_procedure()
def get_false():
    return False


@bp.register_procedure()
def get_null():
    return None


@bp.register_procedure()
def get_int():
    return 42


@bp.register_procedure()
def get_negative_int():
    return -42


@bp.register_procedure()
def get_float():
    return 3.14


@bp.register_procedure()
def get_string():
    return "abcde"


@bp.register_procedure()
def get_bytes():
    return b"abcde"


@bp.register_procedure()
def get_date():
    return datetime.datetime(1987, 6, 2, 8, 45, 00)


@bp.register_procedure()
def get_data_type(data):
    """Returns a string representation of input argument type"""
    return type(data).__name__


@bp.register_procedure()
def get_list():
    return [1, 2, 3]


@bp.register_procedure()
def get_struct():
    return {"x": 1, "y": 2, "z": 3}


@bp.register_procedure
def user_instance(pk):
    return get_user_model().objects.get(pk=pk)
