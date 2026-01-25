"""Example CRM schema pack."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from schevo_core import MigrationRegistry, UpcastContext, compile_ops
from schevo_core.ops import Cast, Move, Rename, SetDefault
from schevo_pack import SchemaSpec, register_schema

SCHEMA_ID = "crm.customer"
LATEST_VERSION = 3
SCHEMA_SPEC = SchemaSpec(
    schema_id=SCHEMA_ID,
    latest_version=LATEST_VERSION,
    description="Example CRM customer schema.",
)


@dataclass(frozen=True)
class SetSchemaVersion:
    version: int

    def apply(self, record: Mapping[str, Any], ctx: UpcastContext | None = None) -> dict[str, Any]:
        updated = dict(record)
        updated["schema_version"] = self.version
        return updated


def _v1_to_v2() -> Callable[[Mapping[str, Any], UpcastContext | None], dict[str, Any]]:
    # Preserve existing contact.email by skipping the move when it already exists.
    ops = [
        Rename("customerId", "customer_id"),
        Move("email", "contact.email", overwrite=False),
        Cast("age", int, on_error="warn"),
        SetSchemaVersion(2),
    ]
    return compile_ops(ops)


def _v2_to_v3() -> Callable[[Mapping[str, Any], UpcastContext | None], dict[str, Any]]:
    ops = [
        Rename("name", "full_name"),
        Move("contact.email", "contact.primary.email", overwrite=False),
        SetDefault("contact.primary.verified", False),
        SetSchemaVersion(3),
    ]
    return compile_ops(ops)


def register(registry: MigrationRegistry) -> None:
    """Register CRM customer migrations and latest version."""

    register_schema(
        registry,
        SCHEMA_SPEC,
        [
            (1, 2, _v1_to_v2()),
            (2, 3, _v2_to_v3()),
        ],
    )
