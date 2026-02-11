import sys
import types
import typing

import django
from django.views.decorators.csrf import csrf_exempt

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self  # noqa: F401


if django.VERSION >= (5, 0):
    # Django updated its decorators to support wrapping asynchronous method in release 5.0
    # REF: https://docs.djangoproject.com/en/5.2/releases/5.0/#decorators

    async_csrf_exempt = csrf_exempt

else:
    # Fore Django version < 5.0, we partially redefine decorators to support async view

    def async_csrf_exempt(view):
        view.csrf_exempt = True
        return view


if sys.version_info >= (3, 14):

    def is_union_type(_type) -> bool:
        return isinstance(_type, types.UnionType)

else:

    def is_union_type(_type) -> bool:
        return typing.get_origin(_type) in (types.UnionType, typing.Union)


if sys.version_info >= (3, 14):

    def union_str_repr(obj: typing.Any) -> str:
        return str(obj)

else:

    def union_str_repr(obj: typing.Any) -> str:
        return " | ".join(t.__name__ for t in typing.get_args(obj))
