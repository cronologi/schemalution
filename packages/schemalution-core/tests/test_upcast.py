from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest
from schemalution_core import MigrationRegistry, UpcastContext, upcast, upcast_to_latest
from schemalution_core.errors import (
    InvalidSchemaVersionError,
    MissingSchemaVersionError,
    NoMigrationPathError,
    UnsupportedSchemaIdError,
)


def _v1_to_v2(record: Mapping[str, Any]) -> dict[str, Any]:
    updated = dict(record)
    updated["full_name"] = updated.pop("name")
    return updated


def _v2_to_v3(record: Mapping[str, Any]) -> dict[str, Any]:
    updated = dict(record)
    updated["email"] = f"{updated['full_name']}@example.com"
    return updated


def _build_registry() -> MigrationRegistry:
    registry = MigrationRegistry()
    registry.register_migration("crm.customer", 1, 2, _v1_to_v2)
    registry.register_migration("crm.customer", 2, 3, _v2_to_v3)
    registry.set_latest_version("crm.customer", 3)
    return registry


def test_upcast_happy_path_v1_to_v3() -> None:
    registry = _build_registry()
    record = {"schema_version": 1, "name": "Ada"}

    result = upcast(record, "crm.customer", registry, to_version=3)

    assert result["schema_version"] == 3
    assert result["full_name"] == "Ada"
    assert result["email"] == "Ada@example.com"
    assert record == {"schema_version": 1, "name": "Ada"}


def test_upcast_already_latest_returns_copy() -> None:
    registry = _build_registry()
    record = {"schema_version": 3, "full_name": "Ada", "email": "Ada@example.com"}

    result = upcast_to_latest(record, "crm.customer", registry)

    assert result == record
    assert result is not record


def test_upcast_context_collects_steps() -> None:
    registry = _build_registry()
    record = {"schema_version": 1, "name": "Ada"}
    context = UpcastContext()

    result = upcast(record, "crm.customer", registry, context=context)

    assert result["schema_version"] == 3
    assert context.applied_steps == [(1, 2), (2, 3)]


def test_upcast_on_step_hook_called() -> None:
    registry = _build_registry()
    record = {"schema_version": 1, "name": "Ada"}
    calls: list[tuple[str, int, int]] = []

    def on_step(schema_id: str, from_v: int, to_v: int) -> None:
        calls.append((schema_id, from_v, to_v))

    result = upcast(record, "crm.customer", registry, on_step=on_step)

    assert result["schema_version"] == 3
    assert calls == [("crm.customer", 1, 2), ("crm.customer", 2, 3)]


def test_upcast_without_context_or_hook_behaves_same() -> None:
    registry = _build_registry()
    record = {"schema_version": 1, "name": "Ada"}

    result = upcast(record, "crm.customer", registry)

    assert result["schema_version"] == 3
    assert result["full_name"] == "Ada"
    assert result["email"] == "Ada@example.com"


def test_upcast_to_latest_forwards_context_and_hook() -> None:
    registry = _build_registry()
    record = {"schema_version": 1, "name": "Ada"}
    context = UpcastContext()
    calls: list[tuple[str, int, int]] = []

    def on_step(schema_id: str, from_v: int, to_v: int) -> None:
        calls.append((schema_id, from_v, to_v))

    result = upcast_to_latest(record, "crm.customer", registry, context=context, on_step=on_step)

    assert result["schema_version"] == 3
    assert context.applied_steps == [(1, 2), (2, 3)]
    assert calls == [("crm.customer", 1, 2), ("crm.customer", 2, 3)]


def test_missing_schema_version_raises() -> None:
    registry = _build_registry()

    with pytest.raises(MissingSchemaVersionError):
        upcast_to_latest({"name": "Ada"}, "crm.customer", registry)


def test_invalid_schema_version_type_raises() -> None:
    registry = _build_registry()

    with pytest.raises(InvalidSchemaVersionError):
        upcast_to_latest({"schema_version": "1"}, "crm.customer", registry)


def test_missing_migration_step_raises() -> None:
    registry = MigrationRegistry()
    registry.register_migration("crm.customer", 1, 2, _v1_to_v2)
    registry.set_latest_version("crm.customer", 3)

    with pytest.raises(NoMigrationPathError):
        upcast_to_latest({"schema_version": 1, "name": "Ada"}, "crm.customer", registry)


def test_unknown_schema_id_raises() -> None:
    registry = MigrationRegistry()

    with pytest.raises(UnsupportedSchemaIdError):
        upcast_to_latest({"schema_version": 1}, "crm.customer", registry)
