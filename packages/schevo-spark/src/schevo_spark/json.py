"""JSON helpers for schema evolution in projection pipelines."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from schevo_core import MigrationRegistry, UpcastContext, upcast_to_latest


def upcast_record_to_latest_json(
    record: Mapping[str, Any] | None,
    schema_id: str,
    registry: MigrationRegistry,
    *,
    context: UpcastContext | None = None,
) -> str:
    """Return upcasted record as JSON for projection workloads.

    If record is None, returns JSON null ("null") to remain UDF-friendly.
    Non-serializable values are coerced to string via json.dumps(default=str).
    """

    if record is None:
        return "null"
    upcasted = upcast_to_latest(record, schema_id, registry, context=context)
    return json.dumps(upcasted, default=str)


def from_json_to_column(json_col: Any, schema: Any) -> Any:
    """Apply pyspark.sql.functions.from_json with lazy import."""

    try:
        from pyspark.sql.functions import from_json
    except ImportError as exc:
        raise RuntimeError(
            "pyspark is required for from_json_to_column; install schevo-spark with the "
            "pyspark extra (e.g. `pip install schevo-spark[spark]`)."
        ) from exc
    return from_json(json_col, schema)
