"""Declarative migration operations."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Literal, Protocol

from .registry import UpcastContext

MISSING = object()


class Op(Protocol):
    """Protocol for declarative migration operations."""

    def apply(self, record: Mapping[str, Any], ctx: UpcastContext | None = None) -> dict[str, Any]:  # type: ignore
        """Apply the operation and return a new record."""


def get_path(record: Mapping[str, Any], path: str) -> Any:
    current: Any = record
    for part in path.split("."):
        if not isinstance(current, Mapping):
            return MISSING
        if part not in current:
            return MISSING
        current = current[part]
    return current


def set_path(record: Mapping[str, Any], path: str, value: Any) -> dict[str, Any]:
    parts = path.split(".")
    updated: dict[str, Any] = dict(record)
    current: dict[str, Any] = updated
    for part in parts[:-1]:
        next_value = current.get(part, MISSING)
        if isinstance(next_value, Mapping):
            next_dict: dict[str, Any] = dict(next_value)
        else:
            next_dict = {}
        current[part] = next_dict
        current = next_dict
    current[parts[-1]] = value
    return updated


def del_path(record: Mapping[str, Any], path: str) -> dict[str, Any]:
    parts = path.split(".")
    updated: dict[str, Any] = dict(record)
    current: dict[str, Any] = updated
    for part in parts[:-1]:
        next_value = current.get(part, MISSING)
        if not isinstance(next_value, Mapping):
            return updated
        next_dict: dict[str, Any] = dict(next_value)
        current[part] = next_dict
        current = next_dict
    if parts[-1] in current:
        current.pop(parts[-1], None)
    return updated


@dataclass(frozen=True)
class Rename:
    from_path: str
    to_path: str
    keep_source: bool = False

    def apply(self, record: Mapping[str, Any], ctx: UpcastContext | None = None) -> dict[str, Any]:
        value = get_path(record, self.from_path)
        if value is MISSING or self.from_path == self.to_path:
            return dict(record)
        if self.keep_source:
            return set_path(record, self.to_path, value)
        updated = del_path(record, self.from_path)
        return set_path(updated, self.to_path, value)


@dataclass(frozen=True)
class SetDefault:
    path: str
    default: Any

    def apply(self, record: Mapping[str, Any], ctx: UpcastContext | None = None) -> dict[str, Any]:
        if get_path(record, self.path) is MISSING:
            return set_path(record, self.path, self.default)
        return dict(record)


@dataclass(frozen=True)
class Drop:
    path: str

    def apply(self, record: Mapping[str, Any], ctx: UpcastContext | None = None) -> dict[str, Any]:
        if get_path(record, self.path) is MISSING:
            return dict(record)
        return del_path(record, self.path)


@dataclass(frozen=True)
class Move:
    from_path: str
    to_path: str
    overwrite: bool = False

    def apply(self, record: Mapping[str, Any], ctx: UpcastContext | None = None) -> dict[str, Any]:
        value = get_path(record, self.from_path)
        if value is MISSING or self.from_path == self.to_path:
            return dict(record)
        destination_value = get_path(record, self.to_path)
        if destination_value is not MISSING and not self.overwrite:
            if ctx is not None:
                ctx.warnings.append(
                    f"destination '{self.to_path}' exists; move from '{self.from_path}' skipped."
                )
            return dict(record)
        updated = del_path(record, self.from_path)
        return set_path(updated, self.to_path, value)


@dataclass(frozen=True)
class Coalesce:
    to_path: str
    from_paths: Sequence[str]

    def apply(self, record: Mapping[str, Any], ctx: UpcastContext | None = None) -> dict[str, Any]:
        if get_path(record, self.to_path) is not MISSING:
            return dict(record)
        for candidate in self.from_paths:
            value = get_path(record, candidate)
            if value is not MISSING:
                return set_path(record, self.to_path, value)
        return dict(record)


@dataclass(frozen=True)
class Cast:
    path: str
    cast: Callable[[Any], Any]
    on_error: Literal["raise", "warn", "skip"] = "raise"

    def apply(self, record: Mapping[str, Any], ctx: UpcastContext | None = None) -> dict[str, Any]:
        value = get_path(record, self.path)
        if value is MISSING or value is None:
            return dict(record)
        try:
            casted = self.cast(value)
        except Exception as exc:  # noqa: BLE001 - surface in warning/ValueError by design
            if self.on_error == "raise":
                raise ValueError(f"cast failed for path '{self.path}'.") from exc
            if self.on_error == "warn" and ctx is not None:
                ctx.warnings.append(f"cast failed for path '{self.path}': {exc}")
            return dict(record)
        return set_path(record, self.path, casted)


def compile_ops(
    ops: Sequence[Op],
) -> Callable[[Mapping[str, Any], UpcastContext | None], dict[str, Any]]:
    def _apply(record: Mapping[str, Any], ctx: UpcastContext | None = None) -> dict[str, Any]:
        current: dict[str, Any] = dict(record)
        for op in ops:
            current = op.apply(current, ctx)
        return current

    return _apply
