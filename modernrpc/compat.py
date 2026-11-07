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

    _F = typing.TypeVar("_F", bound=typing.Callable[..., typing.Any])

    def async_csrf_exempt(view_func: _F) -> _F:
        view_func.csrf_exempt = True  # type: ignore[attr-defined]  # ty: ignore[unresolved-attribute]
        return view_func


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
