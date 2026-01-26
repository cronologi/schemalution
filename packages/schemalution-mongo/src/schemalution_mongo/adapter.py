"""Thin PyMongo-first helpers for schemalution-core migrations."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pymongo.collection import Collection
from schemalution_core import MigrationRegistry, UpcastContext, upcast_to_latest


def read_latest(
    collection: Collection,
    schema_id: str,
    registry: MigrationRegistry,
    query: Mapping[str, Any],
    *,
    context: UpcastContext | None = None,
) -> dict[str, Any] | None:
    doc = collection.find_one(dict(query))
    if doc is None:
        return None
    return upcast_to_latest(doc, schema_id, registry, context=context)


def write_latest(
    collection: Collection,
    schema_id: str,
    registry: MigrationRegistry,
    record: Mapping[str, Any],
    *,
    upsert: bool = True,
    id_field: str = "_id",
    context: UpcastContext | None = None,
) -> Any:
    latest_version = registry.latest_version(schema_id)
    doc: dict[str, Any] = dict(record)
    if "schema_version" not in doc:
        doc["schema_version"] = latest_version
    else:
        version = doc["schema_version"]
        if isinstance(version, bool) or not isinstance(version, int):
            raise ValueError("schema_version must be an int.")
        if version > latest_version:
            raise ValueError(
                f"record schema_version {version} exceeds latest version {latest_version}."
            )
        if version < latest_version:
            doc = upcast_to_latest(doc, schema_id, registry, context=context)

    if id_field in doc:
        value = doc[id_field]
        return collection.replace_one({id_field: value}, doc, upsert=upsert)
    return collection.insert_one(doc)


def backfill_to_latest(
    collection: Collection,
    schema_id: str,
    registry: MigrationRegistry,
    query: Mapping[str, Any],
    *,
    batch_size: int = 500,
) -> dict[str, Any]:
    totals = {
        "total": 0,
        "changed": 0,
        "unchanged": 0,
        "failures": 0,
        "failure_samples": [],
    }
    for doc in collection.find(dict(query), batch_size=batch_size):
        totals["total"] += 1
        try:
            if "_id" not in doc:
                raise ValueError("document missing _id.")
            context = UpcastContext()
            upcasted = upcast_to_latest(doc, schema_id, registry, context=context)
            if doc != upcasted:
                collection.replace_one({"_id": doc["_id"]}, upcasted, upsert=False)
                totals["changed"] += 1
            else:
                totals["unchanged"] += 1
        except Exception as exc:  # noqa: BLE001 - summarize failures for backfill
            totals["failures"] += 1
            if len(totals["failure_samples"]) < 20:
                totals["failure_samples"].append(str(exc))
    return totals
