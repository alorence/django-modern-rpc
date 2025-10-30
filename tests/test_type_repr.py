import sys
import typing
from typing import Any

import pytest

from modernrpc.type_repr import NoneType, type_hint_to_str


# Helpers to obtain Annotated and Literal regardless of Python version
try:  # Prefer stdlib if present
    from typing import Annotated as _Annotated  # type: ignore[attr-defined]
except Exception:  # pragma: no cover - fallback to typing_extensions
    try:
        from typing_extensions import Annotated as _Annotated  # type: ignore
    except Exception:  # pragma: no cover
        _Annotated = None  # type: ignore

try:  # Prefer stdlib if present
    from typing import Literal as _Literal  # type: ignore[attr-defined]
except Exception:  # pragma: no cover - fallback to typing_extensions
    try:
        from typing_extensions import Literal as _Literal  # type: ignore
    except Exception:  # pragma: no cover
        _Literal = None  # type: ignore


@pytest.mark.parametrize(
    "hint, expected",
    [
        (Any, "Any"),
        (typing.Any, "Any"),
        (None, "None"),
        (NoneType, "None"),
        (int, "int"),
        (float, "float"),
        (str, "str"),
        (bool, "bool"),
        (bytes, "bytes"),
        (complex, "complex"),
    ],
)
def test_primitives_and_simple(hint, expected):
    assert type_hint_to_str(hint) == expected


@pytest.mark.parametrize(
    "hint, expected",
    [
        (typing.List[int], "List[int]"),
        (list[int] if hasattr(list, "__class_getitem__") else typing.List[int], "List[int]"),
        (typing.Dict[str, int], "Dict[str, int]"),
        (dict[str, int] if hasattr(dict, "__class_getitem__") else typing.Dict[str, int], "Dict[str, int]"),
        (typing.Set[int], "Set[int]"),
        (set[int] if hasattr(set, "__class_getitem__") else typing.Set[int], "Set[int]"),
        (typing.FrozenSet[int], "FrozenSet[int]"),
        (
            frozenset[int] if hasattr(frozenset, "__class_getitem__") else typing.FrozenSet[int],
            "FrozenSet[int]",
        ),
        (typing.Tuple[int, str], "Tuple[int, str]"),
        (typing.Tuple[int, ...], "Tuple[int, ...]"),
        (typing.Sequence[int], "Sequence[int]"),
        (typing.Mapping[str, int], "Mapping[str, int]"),
        (typing.Iterable[int], "Iterable[int]"),
        (typing.Dict, "Dict"),
        (typing.List, "List"),
    ],
)
def test_collections_and_unsubscripted(hint, expected):
    assert type_hint_to_str(hint) == expected


@pytest.mark.parametrize(
    "hint, expected",
    [
        (typing.Union[int, str], "Union[int, str]"),
        (typing.Union[str, int, int], "Union[int, str]"),  # dedup + order
        (typing.Union[int, None], "Optional[int]"),  # Optional sugar
        (typing.Union[None, int], "Optional[int]"),
        (typing.Union[int, str, None], "Union[None, int, str]"),  # not Optional — 2 non-None
    ],
)
def test_union_typing(hint, expected):
    assert type_hint_to_str(hint) == expected


def test_union_pep604_if_available():
    # PEP 604 syntax only on Python 3.10+
    if sys.version_info >= (3, 10):
        hint = int | str
        assert type_hint_to_str(hint) == "Union[int, str]"
        hint2 = int | None
        assert type_hint_to_str(hint2) == "Optional[int]"
        hint3 = int | str | None
        assert type_hint_to_str(hint3) == "Union[None, int, str]"
    else:
        pytest.skip("PEP 604 unions not available before Python 3.10")


@pytest.mark.skipif(_Annotated is None, reason="Annotated not available")
def test_annotated_drops_metadata():
    hint = _Annotated[int, "meta", 123]
    assert type_hint_to_str(hint) == "int"


@pytest.mark.skipif(_Literal is None, reason="Literal not available")
def test_literal_sorted_and_repr_values():
    # Order independent, will be sorted by repr
    hint = _Literal["b", "a", 2, 1]
    s = type_hint_to_str(hint)
    # Sorted by repr -> strings before integers on Python 3.13: 'a', 'b', 1, 2
    assert s == "Literal['a', 'b', 1, 2]"


def test_forward_ref_and_string_annotation():
    fr = typing.ForwardRef("User") if hasattr(typing, "ForwardRef") else None
    if fr is not None:
        assert type_hint_to_str(fr) == "User"
    # String annotations should be returned as-is
    assert type_hint_to_str("User") == "User"


def test_custom_class_name():
    class Foo:
        pass

    assert type_hint_to_str(Foo) == "Foo"
