from __future__ import annotations

import builtins
import importlib
import json
import sys
from typing import Any

import pytest
from schemalution_core import MigrationRegistry
from schemalution_pack_example_crm import SCHEMA_ID, register
from schemalution_spark import (
    from_json_to_column,
    make_upcast_to_latest_json_udf,
    upcast_record_to_latest_json,
)


class Sentinel:
    def __str__(self) -> str:
        return "SENTINEL"


def _registry() -> MigrationRegistry:
    registry = MigrationRegistry()
    register(registry)
    return registry


def _block_pyspark(monkeypatch: pytest.MonkeyPatch) -> None:
    real_import = builtins.__import__

    def blocked_import(name: str, *args: Any, **kwargs: Any) -> Any:
        if name.startswith("pyspark"):
            raise ImportError("pyspark blocked for test")
        return real_import(name, *args, **kwargs)

    for module_name in list(sys.modules):
        if module_name.startswith("pyspark"):
            del sys.modules[module_name]

    monkeypatch.setattr(builtins, "__import__", blocked_import)


def test_upcast_record_to_latest_json_upcasts_using_example_pack() -> None:
    registry = _registry()
    record = {
        "schema_version": 1,
        "customerId": "c-1",
        "name": "Ada",
        "age": "42",
    }

    result = upcast_record_to_latest_json(record, SCHEMA_ID, registry)
    data = json.loads(result)

    assert data["schema_version"] == 3
    assert data["customer_id"] == "c-1"
    assert data["full_name"] == "Ada"
    assert data["age"] == 42


def test_upcast_record_to_latest_json_handles_non_serializable_values() -> None:
    registry = _registry()
    record = {
        "schema_version": 3,
        "customer_id": "c-2",
        "full_name": "Rene",
        "age": 31,
        "extra": Sentinel(),
    }

    result = upcast_record_to_latest_json(record, SCHEMA_ID, registry)
    data = json.loads(result)

    assert data["extra"] == "SENTINEL"


def test_import_schemalution_spark_without_pyspark(monkeypatch: pytest.MonkeyPatch) -> None:
    _block_pyspark(monkeypatch)
    for module_name in list(sys.modules):
        if module_name.startswith("schemalution_spark"):
            del sys.modules[module_name]
    module = importlib.import_module("schemalution_spark")
    assert callable(module.upcast_record_to_latest_json)


def test_make_udf_raises_without_pyspark(monkeypatch: pytest.MonkeyPatch) -> None:
    _block_pyspark(monkeypatch)
    with pytest.raises(
        RuntimeError, match="pyspark is required for make_upcast_to_latest_json_udf"
    ):
        make_upcast_to_latest_json_udf(SCHEMA_ID, _registry())


def test_from_json_to_column_raises_without_pyspark(monkeypatch: pytest.MonkeyPatch) -> None:
    _block_pyspark(monkeypatch)
    with pytest.raises(RuntimeError, match="pyspark is required for from_json_to_column"):
        from_json_to_column("col", "schema")
