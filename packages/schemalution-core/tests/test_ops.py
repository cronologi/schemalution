from __future__ import annotations

import pytest
from schemalution_core import UpcastContext
from schemalution_core.ops import (
    MISSING,
    Cast,
    Coalesce,
    Drop,
    Move,
    Rename,
    SetDefault,
    compile_ops,
    get_path,
)


def test_rename_moves_field_without_mutation() -> None:
    record = {"a": 1}
    op = Rename("a", "b")

    result = op.apply(record)

    assert result == {"b": 1}
    assert record == {"a": 1}


def test_rename_keep_source_copies_field() -> None:
    record = {"a": 1}
    op = Rename("a", "b", keep_source=True)

    result = op.apply(record)

    assert result == {"a": 1, "b": 1}


def test_set_default_only_sets_when_missing() -> None:
    record = {"a": 2}
    op = SetDefault("a", 1)

    result = op.apply(record)

    assert result == {"a": 2}

    missing_result = SetDefault("b", 3).apply(record)
    assert missing_result["b"] == 3


def test_drop_removes_nested_path() -> None:
    record = {"a": {"b": 1, "c": 2}}
    op = Drop("a.b")

    result = op.apply(record)

    assert result == {"a": {"c": 2}}
    assert record == {"a": {"b": 1, "c": 2}}


def test_move_without_overwrite_warns_and_skips() -> None:
    record = {"a": 1, "b": 2}
    ctx = UpcastContext()
    op = Move("a", "b", overwrite=False)

    result = op.apply(record, ctx)

    assert result == record
    assert any("move from 'a' skipped" in warning for warning in ctx.warnings)


def test_coalesce_picks_first_present() -> None:
    record = {"a": 1, "b": 2}
    op = Coalesce("c", ["missing", "b", "a"])

    result = op.apply(record)

    assert result["c"] == 2


def test_cast_success() -> None:
    record = {"age": "42"}
    op = Cast("age", int)

    result = op.apply(record)

    assert result["age"] == 42


def test_cast_warn_keeps_value_and_adds_warning() -> None:
    record = {"age": "bad"}
    ctx = UpcastContext()
    op = Cast("age", int, on_error="warn")

    result = op.apply(record, ctx)

    assert result["age"] == "bad"
    assert any("cast failed for path 'age'" in warning for warning in ctx.warnings)


def test_cast_raise_raises_value_error() -> None:
    record = {"age": "bad"}
    op = Cast("age", int, on_error="raise")

    with pytest.raises(ValueError):
        op.apply(record)


def test_compile_ops_applies_in_order_with_nested_paths() -> None:
    record = {"a": {"b": "1"}}
    ops = [
        Rename("a.b", "a.c"),
        SetDefault("x.y", 3),
        Cast("a.c", int),
        Coalesce("a.d", ["missing", "a.c"]),
    ]

    fn = compile_ops(ops)
    result = fn(record, UpcastContext())

    assert result["a"]["c"] == 1
    assert result["a"]["d"] == 1
    assert result["x"]["y"] == 3


def test_get_path_returns_missing_sentinel() -> None:
    record = {"a": {"b": 1}}

    assert get_path(record, "a.c") is MISSING
