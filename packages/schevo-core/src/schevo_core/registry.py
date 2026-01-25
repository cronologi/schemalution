"""Migration registry and upcast helpers."""

from __future__ import annotations

import inspect
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any, Literal, cast

from .errors import (
    InvalidSchemaVersionError,
    MissingSchemaVersionError,
    NoMigrationPathError,
    UnsupportedSchemaIdError,
)

LatestLiteral = Literal["latest"]


@dataclass(slots=True)
class UpcastContext:
    """Collect diagnostics during upcast."""

    applied_steps: list[tuple[int, int]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    notes: dict[str, Any] = field(default_factory=dict)


MigrationFn = (
    Callable[[Mapping[str, Any]], dict[str, Any]]
    | Callable[
        [Mapping[str, Any], UpcastContext | None],
        dict[str, Any],
    ]
)


def _ensure_int_version(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise InvalidSchemaVersionError(f"{label} must be an int; got {type(value).__name__}.")
    return value


class MigrationRegistry:
    """Registry for linear migrations and latest version tracking."""

    def __init__(self) -> None:
        self._migrations: dict[str, dict[int, MigrationFn]] = {}
        self._latest_versions: dict[str, int] = {}

    def register_migration(
        self,
        schema_id: str,
        from_version: int,
        to_version: int,
        fn: MigrationFn,
    ) -> None:
        """Register a sequential migration step (vN -> vN+1)."""
        from_version = _ensure_int_version(from_version, "from_version")
        to_version = _ensure_int_version(to_version, "to_version")
        if to_version != from_version + 1:
            raise ValueError(
                "Only sequential migrations are supported; to_version must equal from_version + 1."
            )
        self._migrations.setdefault(schema_id, {})[from_version] = fn

    def set_latest_version(self, schema_id: str, version: int) -> None:
        version = _ensure_int_version(version, "version")
        self._latest_versions[schema_id] = version

    def latest_version(self, schema_id: str) -> int:
        try:
            return self._latest_versions[schema_id]
        except KeyError as exc:  # pragma: no cover - defensive clarity
            raise UnsupportedSchemaIdError(
                f"schema_id '{schema_id}' is not registered with a latest version."
            ) from exc

    def _has_schema(self, schema_id: str) -> bool:
        return schema_id in self._latest_versions or schema_id in self._migrations

    def _migration_for(self, schema_id: str, from_version: int) -> MigrationFn | None:
        return self._migrations.get(schema_id, {}).get(from_version)


def _can_accept_positional_context(signature: inspect.Signature) -> bool:
    positional = 0
    for param in signature.parameters.values():
        if param.kind in (param.POSITIONAL_ONLY, param.POSITIONAL_OR_KEYWORD):
            positional += 1
        elif param.kind == param.VAR_POSITIONAL:
            return True
    return positional >= 2


def _apply_migration(
    migration: MigrationFn,
    record: Mapping[str, Any],
    context: UpcastContext | None,
) -> dict[str, Any]:
    migration_callable = cast(Callable[..., dict[str, Any]], migration)
    if context is None:
        return migration_callable(record)

    try:
        signature = inspect.signature(migration)
    except (TypeError, ValueError):
        return migration_callable(record, context)

    params = signature.parameters
    if any(param.kind == param.VAR_KEYWORD for param in params.values()):
        return migration_callable(record, ctx=context)
    if "ctx" in params:
        return migration_callable(record, ctx=context)
    if "context" in params:
        return migration_callable(record, context=context)
    if _can_accept_positional_context(signature):
        return migration_callable(record, context)
    return migration_callable(record)


def upcast(
    record: Mapping[str, Any],
    schema_id: str,
    registry: MigrationRegistry,
    to_version: int | LatestLiteral = "latest",
    context: UpcastContext | None = None,
    on_step: Callable[[str, int, int], None] | None = None,
) -> dict[str, Any]:
    """Upcast a record to a target version (or latest), stamping schema_version each step."""

    if "schema_version" not in record:
        raise MissingSchemaVersionError("record is missing required 'schema_version'.")
    from_version = _ensure_int_version(record["schema_version"], "schema_version")

    if to_version == "latest":
        target_version = registry.latest_version(schema_id)
    else:
        target_version = _ensure_int_version(to_version, "to_version")
        if not registry._has_schema(schema_id):
            raise UnsupportedSchemaIdError(f"schema_id '{schema_id}' is not registered.")

    if from_version == target_version:
        return dict(record)

    if from_version > target_version:
        raise NoMigrationPathError(
            f"cannot downcast from v{from_version} to v{target_version} for '{schema_id}'."
        )

    current_version = from_version
    current_record: dict[str, Any] = dict(record)
    while current_version < target_version:
        from_version = current_version
        to_version_step = current_version + 1
        migration = registry._migration_for(schema_id, current_version)
        if migration is None:
            raise NoMigrationPathError(
                f"missing migration step v{current_version} -> v{current_version + 1} "
                f"for '{schema_id}'."
            )
        current_record = dict(_apply_migration(migration, current_record, context))
        current_version += 1
        current_record["schema_version"] = current_version
        if context is not None:
            context.applied_steps.append((from_version, to_version_step))
        if on_step is not None:
            on_step(schema_id, from_version, to_version_step)
    return current_record


def upcast_to_latest(
    record: Mapping[str, Any],
    schema_id: str,
    registry: MigrationRegistry,
) -> dict[str, Any]:
    """Upcast a record to the latest schema version for schema_id."""

    return upcast(record, schema_id, registry, "latest")
