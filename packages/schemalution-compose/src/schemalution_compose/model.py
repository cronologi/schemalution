"""Data models for composition."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class Fragment:
    schema_id: str
    payload: Mapping[str, Any]
    updated_at: datetime | None = None
    source: str | None = None


@dataclass(slots=True)
class ComposeContext:
    warnings: list[str] = field(default_factory=list)
    notes: dict[str, Any] = field(default_factory=dict)
    applied: list[str] = field(default_factory=list)
