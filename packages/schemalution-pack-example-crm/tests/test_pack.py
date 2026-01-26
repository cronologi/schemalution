from __future__ import annotations

from schemalution_core import MigrationRegistry, UpcastContext, upcast
from schemalution_pack_example_crm import LATEST_VERSION, SCHEMA_ID, register


def _setup_registry() -> MigrationRegistry:
    registry = MigrationRegistry()
    register(registry)
    return registry


def test_upcast_v1_to_latest() -> None:
    registry = _setup_registry()
    record = {
        "schema_version": 1,
        "customerId": "c-1",
        "name": "Ada",
        "age": "42",
        "email": "ada@example.com",
    }

    result = upcast(record, SCHEMA_ID, registry, to_version="latest")

    assert result["schema_version"] == LATEST_VERSION
    assert result is not record
    assert result["customer_id"] == "c-1"
    assert result["full_name"] == "Ada"
    assert result["age"] == 42
    assert result["contact"]["primary"]["email"] == "ada@example.com"
    assert result["contact"]["primary"]["verified"] is False


def test_upcast_v2_to_latest() -> None:
    registry = _setup_registry()
    record = {
        "schema_version": 2,
        "customer_id": "c-2",
        "name": "Grace",
        "age": 30,
        "contact": {"email": "grace@example.com"},
    }

    result = upcast(record, SCHEMA_ID, registry, to_version="latest")

    assert result["schema_version"] == LATEST_VERSION
    assert result is not record
    assert result["customer_id"] == "c-2"
    assert result["full_name"] == "Grace"
    assert result["age"] == 30
    assert result["contact"]["primary"]["email"] == "grace@example.com"
    assert result["contact"]["primary"]["verified"] is False


def test_cast_warning_captured_in_context() -> None:
    registry = _setup_registry()
    context = UpcastContext()
    record = {
        "schema_version": 1,
        "customerId": "c-3",
        "name": "Lin",
        "age": "not-a-number",
    }

    result = upcast(record, SCHEMA_ID, registry, to_version="latest", context=context)

    assert result["schema_version"] == LATEST_VERSION
    assert result["age"] == "not-a-number"
    assert any("cast failed for path 'age'" in warning for warning in context.warnings)


def test_upcast_sets_latest_schema_version() -> None:
    registry = _setup_registry()
    record = {
        "schema_version": 1,
        "customerId": "c-5",
        "name": "Rene",
        "age": "31",
    }

    result = upcast(record, SCHEMA_ID, registry, to_version="latest")

    assert result["schema_version"] == LATEST_VERSION


def test_v1_preserves_existing_contact_email() -> None:
    registry = _setup_registry()
    record = {
        "schema_version": 1,
        "customerId": "c-4",
        "name": "Nia",
        "age": "25",
        "email": "legacy@example.com",
        "contact": {"email": "primary@example.com"},
    }

    result = upcast(record, SCHEMA_ID, registry, to_version="latest")

    assert result["contact"]["primary"]["email"] == "primary@example.com"
    assert result["email"] == "legacy@example.com"
