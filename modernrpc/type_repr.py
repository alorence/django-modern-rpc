"""
Utilities to build a stable, cross-version string representation of Python type hints.

The main entry point is `type_hint_to_str(hint)` which returns a canonical string
that is consistent across Python 3.8-3.14 for common and container/union types.

Handled constructs:
- Builtins and common typing aliases: `int`, `str`, `float`, `bool`, `bytes`, `None`, `Any`
- `Union` (including PEP 604 syntax `A | B`), with deterministic ordering
- `Optional[T]` (rendered as syntactic sugar for `Union[T, None]`)
- Generic containers and ABCs: `List[T]`, `Dict[K, V]`, `Set[T]`, `FrozenSet[T]`,
  `Tuple[... or T1, T2, ...]`, `Sequence[T]`, `Mapping[K, V]`, `Iterable[T]`
- `Literal[...]` — rendered as `Literal[...]`
- `Annotated[T, ...]` — rendered as the underlying `T` (annotations are dropped for stability)
- Forward references and string annotations

If an unknown or less common typing construct is encountered, it falls back to a
best-effort readable form using its origin and arguments, or `repr(hint)`.
"""

from __future__ import annotations

import typing
from typing import Any

# Optional support for Python < 3.9 features via typing_extensions
try:  # pragma: no cover - import variability
    from typing_extensions import (
        Annotated as _TE_Annotated,
    )
    from typing_extensions import (
        Literal as _TE_Literal,
    )
    from typing_extensions import (
        get_args as _te_get_args,
    )
    from typing_extensions import (
        get_origin as _te_get_origin,
    )
except Exception:  # pragma: no cover - not available
    _te_get_origin = None
    _te_get_args = None
    _TE_Annotated = None
    _TE_Literal = None

# Prefer stdlib typing helpers if present, otherwise fallback to typing_extensions
try:  # pragma: no cover - availability depends on Python version
    from typing import get_args as _py_get_args  # type: ignore[attr-defined]
    from typing import get_origin as _py_get_origin  # type: ignore[attr-defined]
except Exception:  # pragma: no cover
    _py_get_origin = None
    _py_get_args = None

get_origin = _py_get_origin or _te_get_origin  # type: ignore[assignment]
get_args = _py_get_args or _te_get_args  # type: ignore[assignment]

# Optional types for detection across versions
try:  # pragma: no cover - Python 3.10+
    from types import UnionType as _UnionType
except Exception:  # pragma: no cover - older Pythons
    _UnionType = None  # type: ignore[assignment]

# Typing constructs (may come from stdlib or typing_extensions)
Annotated = getattr(typing, "Annotated", _TE_Annotated)
Literal = getattr(typing, "Literal", _TE_Literal)

# Constant for NoneType
NoneType = type(None)


# Map various origins (PEP 585 builtins and typing ABCs) to canonical names
_CANONICAL_NAMES = {
    list: "List",
    typing.List: "List",
    dict: "Dict",
    typing.Dict: "Dict",
    set: "Set",
    typing.Set: "Set",
    frozenset: "FrozenSet",
    typing.FrozenSet: "FrozenSet",
    tuple: "Tuple",
    typing.Tuple: "Tuple",
    typing.Sequence: "Sequence",
    typing.MutableSequence: "MutableSequence",
    typing.Mapping: "Mapping",
    typing.MutableMapping: "MutableMapping",
    typing.Iterable: "Iterable",
    typing.Collection: "Collection",
}


def _simple_name(t: Any) -> str:
    """Return a clean name for a non-generic type or typing object.

    Examples: int -> "int", NoneType -> "None", typing.Any -> "Any"
    """
    if t is Any or t is typing.Any:
        return "Any"
    if t is None or t is NoneType:
        return "None"

    # typing module classes (e.g., typing.Dict without args) often have _name
    n = getattr(t, "__name__", None) or getattr(t, "_name", None)
    if n:
        return n

    # For forward refs
    if isinstance(t, typing.ForwardRef):  # type: ignore[attr-defined]
        return str(t.__forward_arg__)  # type: ignore[attr-defined]

    # For strings used as annotations
    if isinstance(t, str):
        return t

    # Fallback to repr but strip typing. prefix when obvious
    r = repr(t)
    if r.startswith("typing."):
        return r[len("typing.") :]
    return r


def _format_args(args: tuple[Any, ...]) -> str:
    return ", ".join(type_hint_to_str(a) for a in args)


def _normalize_union_args(args: tuple[Any, ...]) -> list[Any]:
    """Flatten nested Unions, deduplicate, and return a stable ordered list."""
    flat: list[Any] = []

    def add(a: Any):
        # Expand nested unions
        if _is_union(a):
            for sub in _get_union_args(a):
                add(sub)
            return
        # Normalize None types
        if a is None:
            a = NoneType
        if a not in flat:
            flat.append(a)

    for a in args:
        add(a)

    # Sort deterministically by their string forms to avoid version-dependent ordering
    flat.sort(key=lambda x: type_hint_to_str(x))
    return flat


def _is_union(tp: Any) -> bool:
    if _UnionType is not None and isinstance(tp, _UnionType):
        return True
    origin = get_origin(tp) if get_origin else None
    return origin is typing.Union or origin is getattr(typing, "Union", None)


def _get_union_args(tp: Any) -> tuple[Any, ...]:
    if _UnionType is not None and isinstance(tp, _UnionType):
        # PEP 604 unions don't always expose origin/args the same way on all versions
        return typing.get_args(tp) if hasattr(typing, "get_args") else (tp,)
    if get_args:
        return get_args(tp) or ()
    return ()


def _format_union(args: tuple[Any, ...]) -> str:
    norm = _normalize_union_args(args)
    # Optional form if exactly one non-None plus None
    non_none = [a for a in norm if a is not NoneType]
    has_none = len(non_none) != len(norm)
    if has_none and len(non_none) == 1:
        return f"Optional[{type_hint_to_str(non_none[0])}]"
    # Otherwise canonical Union[...] with deterministic ordering
    return f"Union[{_format_args(tuple(norm))}]"


def _format_tuple(args: tuple[Any, ...]) -> str:
    # Tuple[] can be variadic (Tuple[T, ...])
    if len(args) == 2 and args[1] is Ellipsis:
        return f"Tuple[{type_hint_to_str(args[0])}, ...]"
    return f"Tuple[{_format_args(args)}]"


def _origin_name(origin: Any) -> str | None:
    # Map to canonical container names
    name = _CANONICAL_NAMES.get(origin)
    if name:
        return name

    # typing generics sometimes carry `_name`
    n = getattr(origin, "_name", None) or getattr(origin, "__name__", None)
    if n:
        return n
    return None


def type_hint_to_str(hint: Any) -> str:
    """Return a stable, canonical string for a type hint.

    The result aims to be consistent across Python 3.8–3.14, abstracting away
    implementation details of `typing` and PEP 585 generics.
    """
    # Fast-path for common simples
    if hint is Any or hint is typing.Any:
        return "Any"
    if hint is None or hint is NoneType:
        return "None"
    if hint in (int, float, str, bool, bytes, complex):
        return hint.__name__

    # PEP 604 union syntax: A | B
    if _UnionType is not None and isinstance(hint, _UnionType):
        return _format_union(_get_union_args(hint))

    origin = get_origin(hint) if get_origin else None
    args = get_args(hint) if get_args else ()

    # typing.Union[...] (PEP 484)
    if origin in (typing.Union, getattr(typing, "Union", None)):
        return _format_union(args)

    # Annotated[T, ...] -> represent as underlying T for stability across versions
    if Annotated is not None and (getattr(hint, "__origin__", None) is Annotated or origin is Annotated):
        inner = args[0] if args else Any
        return type_hint_to_str(inner)

    # Literal values
    if Literal is not None and (getattr(hint, "__origin__", None) is Literal or origin is Literal):
        # Stringify literal values with Python repr for determinism, but sort for stability
        values = tuple(args)
        try:
            values = tuple(sorted(values, key=repr))
        except Exception:
            pass
        inner = ", ".join(repr(v) for v in values)
        return f"Literal[{inner}]"

    # Tuple
    if origin in (tuple, typing.Tuple):
        return _format_tuple(args)

    # Dict, List, Set, FrozenSet, Mapping, Sequence, Iterable, etc.
    if origin is not None:
        name = _origin_name(origin)
        if name:
            if args:
                return f"{name}[{_format_args(args)}]"
            return name

    # Special case: unsubscripted typing objects like typing.Dict
    if getattr(hint, "_name", None) in _CANONICAL_NAMES.values():
        return hint._name  # type: ignore[attr-defined]

    # ForwardRef or string annotations
    if isinstance(hint, typing.ForwardRef):  # type: ignore[attr-defined]
        return str(hint.__forward_arg__)  # type: ignore[attr-defined]
    if isinstance(hint, str):
        return hint

    # Fallback: if it's a class/type, prefer its __name__
    if isinstance(hint, type):
        if hint is NoneType:
            return "None"
        return hint.__name__

    # Final fallback to a tidy repr
    return _simple_name(hint)


__all__ = ["NoneType", "type_hint_to_str"]
