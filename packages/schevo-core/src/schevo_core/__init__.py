"""Public API for schevo-core."""

from __future__ import annotations

from . import ops
from .ops import compile_ops
from .registry import MigrationRegistry, UpcastContext, upcast, upcast_to_latest

__all__ = [
    "MigrationRegistry",
    "UpcastContext",
    "compile_ops",
    "ops",
    "upcast",
    "upcast_to_latest",
    "__version__",
]

__version__ = "0.0.0"
