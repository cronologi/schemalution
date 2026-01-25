"""Spark UDF helpers for schema evolution."""

from __future__ import annotations

from typing import Any

from schevo_core import MigrationRegistry

from .json import upcast_record_to_latest_json


def make_upcast_to_latest_json_udf(
    schema_id: str,
    registry: MigrationRegistry,
) -> Any:
    """Return a Spark UDF that upcasts records to latest JSON.

    The registry is captured in the closure; for large production jobs,
    consider broadcasting it to executors.
    """

    try:
        from pyspark.sql.functions import udf
        from pyspark.sql.types import StringType
    except ImportError as exc:
        raise RuntimeError(
            "pyspark is required for make_upcast_to_latest_json_udf; install schevo-spark "
            "with the pyspark extra (e.g. `pip install schevo-spark[spark]`)."
        ) from exc

    def _apply(record: Any) -> str:
        return upcast_record_to_latest_json(record, schema_id, registry)

    return udf(_apply, StringType())
