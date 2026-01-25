"""Public API for schevo-core."""

from __future__ import annotations

from .registry import MigrationRegistry, UpcastContext, upcast_to_latest

__all__ = ["MigrationRegistry", "UpcastContext", "upcast_to_latest", "__version__"]

__version__ = "0.0.0"
