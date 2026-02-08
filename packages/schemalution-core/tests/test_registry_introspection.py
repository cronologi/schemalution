from __future__ import annotations

from schemalution_core import MigrationRegistry


def _v1_to_v2(record: dict[str, object]) -> dict[str, object]:
    updated = dict(record)
    updated["v"] = 2
    return updated


def test_registry_introspection_methods() -> None:
    registry = MigrationRegistry()
    registry.register_migration("crm.customer", 1, 2, _v1_to_v2)
    registry.set_latest_version("crm.customer", 2)
    registry.register_migration("billing.invoice", 1, 2, _v1_to_v2)
    registry.set_latest_version("billing.invoice", 2)

    assert registry.schema_ids() == ["billing.invoice", "crm.customer"]
    assert registry.latest_versions() == {"crm.customer": 2, "billing.invoice": 2}

    edges = registry.list_migrations()
    assert [(edge.schema_id, edge.from_version, edge.to_version) for edge in edges] == [
        ("billing.invoice", 1, 2),
        ("crm.customer", 1, 2)
    ]
