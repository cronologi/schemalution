"""Public API for schevo-mongo."""

from __future__ import annotations

from .adapter import backfill_to_latest, read_latest, write_latest

__all__ = ["backfill_to_latest", "read_latest", "write_latest", "__version__"]

__version__ = "0.0.0"
