from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, cast

from pymongo.collection import Collection
from schevo_core import MigrationRegistry
from schevo_mongo import backfill_to_latest, read_latest, write_latest
from schevo_pack_example_crm import SCHEMA_ID, register


class FakeInsertResult:
    def __init__(self, inserted_id: Any) -> None:
        self.inserted_id = inserted_id


class FakeReplaceResult:
    def __init__(self, matched_count: int, modified_count: int, upserted_id: Any) -> None:
        self.matched_count = matched_count
        self.modified_count = modified_count
        self.upserted_id = upserted_id


class FakeCollection:
    def __init__(self, docs: Iterable[Mapping[str, Any]] | None = None) -> None:
        self._docs: list[dict[str, Any]] = [dict(doc) for doc in (docs or [])]

    def find_one(self, query: Mapping[str, Any]) -> dict[str, Any] | None:
        for doc in self._docs:
            if all(doc.get(key) == value for key, value in query.items()):
                return dict(doc)
        return None

    def insert_one(self, record: Mapping[str, Any]) -> FakeInsertResult:
        doc = dict(record)
        self._docs.append(doc)
        return FakeInsertResult(doc.get("_id"))

    def replace_one(
        self, query: Mapping[str, Any], record: Mapping[str, Any], *, upsert: bool
    ) -> FakeReplaceResult:
        for index, doc in enumerate(self._docs):
            if all(doc.get(key) == value for key, value in query.items()):
                self._docs[index] = dict(record)
                return FakeReplaceResult(1, 1, None)
        if upsert:
            self._docs.append(dict(record))
            return FakeReplaceResult(0, 0, record.get("_id"))
        return FakeReplaceResult(0, 0, None)

    def find(self, query: Mapping[str, Any], *, batch_size: int = 500) -> Iterable[dict[str, Any]]:
        _ = batch_size
        for doc in self._docs:
            if all(doc.get(key) == value for key, value in query.items()):
                yield dict(doc)

    def all_docs(self) -> list[dict[str, Any]]:
        return [dict(doc) for doc in self._docs]


def _registry() -> MigrationRegistry:
    registry = MigrationRegistry()
    register(registry)
    return registry


def _collection(fake: FakeCollection) -> Collection:
    return cast(Collection, fake)


def test_read_latest_returns_upcasted_doc() -> None:
    registry = _registry()
    collection = FakeCollection(
        [
            {
                "_id": "c-1",
                "schema_version": 1,
                "customerId": "c-1",
                "name": "Ada",
                "age": "42",
            }
        ]
    )

    result = read_latest(_collection(collection), SCHEMA_ID, registry, {"_id": "c-1"})

    assert result is not None
    assert result["schema_version"] == 3
    assert result["customer_id"] == "c-1"
    assert result["full_name"] == "Ada"


def test_write_latest_upcasts_before_writing() -> None:
    registry = _registry()
    collection = FakeCollection()
    record = {
        "_id": "c-2",
        "schema_version": 1,
        "customerId": "c-2",
        "name": "Grace",
        "age": "30",
    }

    write_latest(_collection(collection), SCHEMA_ID, registry, record)

    stored = collection.find_one({"_id": "c-2"})
    assert stored is not None
    assert stored["schema_version"] == 3
    assert stored["customer_id"] == "c-2"
    assert stored["full_name"] == "Grace"


def test_write_latest_stamps_schema_version_when_missing() -> None:
    registry = _registry()
    collection = FakeCollection()
    record = {
        "_id": "c-3",
        "customerId": "c-3",
        "name": "Rene",
        "age": "31",
    }

    write_latest(_collection(collection), SCHEMA_ID, registry, record)

    stored = collection.find_one({"_id": "c-3"})
    assert stored is not None
    assert stored["schema_version"] == 3


def test_backfill_updates_only_changed_docs() -> None:
    registry = _registry()
    collection = FakeCollection(
        [
            {
                "_id": "c-4",
                "schema_version": 1,
                "customerId": "c-4",
                "name": "Lee",
                "age": "28",
            },
            {
                "_id": "c-5",
                "schema_version": 3,
                "customer_id": "c-5",
                "full_name": "Kai",
                "age": 44,
            },
        ]
    )

    summary = backfill_to_latest(_collection(collection), SCHEMA_ID, registry, {})

    assert summary["total"] == 2
    assert summary["changed"] == 1
    assert summary["unchanged"] == 1
    assert summary["failures"] == 0

    updated = collection.find_one({"_id": "c-4"})
    assert updated is not None
    assert updated["schema_version"] == 3
    assert updated["full_name"] == "Lee"
