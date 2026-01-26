"""Schema pack helpers."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any, Protocol

from schemalution_core import MigrationRegistry, UpcastContext

MigrationFn = (
    Callable[[Mapping[str, Any]], dict[str, Any]]
    | Callable[[Mapping[str, Any], UpcastContext | None], dict[str, Any]]
)


@dataclass(frozen=True, slots=True)
class SchemaSpec:
    schema_id: str
    latest_version: int
    min_supported_version: int | None = None
    description: str | None = None


class Pack(Protocol):
    pack_id: str

    def schemas(self) -> list[SchemaSpec]:  # type: ignore
        """Return schema specs belonging to this pack."""

    def register(self, registry: MigrationRegistry) -> None:
        """Register pack migrations in the given registry."""


_MIN_SUPPORTED: dict[str, int] = {}


def register_schema(
    registry: MigrationRegistry,
    spec: SchemaSpec,
    migrations: list[tuple[int, int, MigrationFn]],
) -> None:
    registry.set_latest_version(spec.schema_id, spec.latest_version)
    for from_version, to_version, fn in migrations:
        registry.register_migration(spec.schema_id, from_version, to_version, fn)
    if spec.min_supported_version is not None:
        _MIN_SUPPORTED[spec.schema_id] = spec.min_supported_version


@dataclass(slots=True)
class BasePack:
    pack_id: str
    _entries: list[tuple[SchemaSpec, list[tuple[int, int, MigrationFn]]]] = field(
        default_factory=list
    )

    def add_schema(
        self,
        spec: SchemaSpec,
        migrations: list[tuple[int, int, MigrationFn]],
    ) -> None:
        self._entries.append((spec, migrations))

    def schemas(self) -> list[SchemaSpec]:
        return [spec for spec, _ in self._entries]

    def register(self, registry: MigrationRegistry) -> None:
        for spec, migrations in self._entries:
            register_schema(registry, spec, migrations)
