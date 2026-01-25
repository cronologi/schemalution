"""Public API for schevo-core.

Only the symbols exported here are considered public and stable.
"""

from __future__ import annotations

from . import ops
from .errors import (
    InvalidSchemaVersionError,
    MissingSchemaVersionError,
    NoMigrationPathError,
    UnsupportedSchemaIdError,
)
from .ops import compile_ops
from .registry import MigrationRegistry, UpcastContext, upcast, upcast_to_latest

__all__ = [
    "MigrationRegistry",
    "UpcastContext",
    "compile_ops",
    "InvalidSchemaVersionError",
    "MissingSchemaVersionError",
    "NoMigrationPathError",
    "ops",
    "UnsupportedSchemaIdError",
    "upcast",
    "upcast_to_latest",
    "__version__",
]

__version__ = "0.0.1"
