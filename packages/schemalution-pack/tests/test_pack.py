from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from schemalution_core import MigrationRegistry, upcast
from schemalution_pack import BasePack, SchemaSpec, register_schema


def _noop(record: Mapping[str, Any]) -> dict[str, Any]:
    return dict(record)


def test_register_schema_registers_latest_and_migrations() -> None:
    registry = MigrationRegistry()
    spec = SchemaSpec(schema_id="example.schema", latest_version=2)

    register_schema(registry, spec, [(1, 2, _noop)])

    assert registry.latest_version("example.schema") == 2
    result = upcast({"schema_version": 1, "value": "ok"}, "example.schema", registry, 2)
    assert result["schema_version"] == 2
    assert result["value"] == "ok"


def test_basepack_registers_all_schemas() -> None:
    registry = MigrationRegistry()
    pack = BasePack("example")
    first = SchemaSpec(schema_id="example.first", latest_version=2)
    second = SchemaSpec(schema_id="example.second", latest_version=1)

    pack.add_schema(first, [(1, 2, _noop)])
    pack.add_schema(second, [])
    pack.register(registry)

    assert registry.latest_version("example.first") == 2
    assert registry.latest_version("example.second") == 1
    result = upcast({"schema_version": 1, "value": "ok"}, "example.first", registry, 2)
    assert result["schema_version"] == 2
    assert result["value"] == "ok"
