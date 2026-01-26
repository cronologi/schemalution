"""Public API for schemalution-mongo.

Only the symbols exported here are considered public and stable.
"""

from __future__ import annotations

from .adapter import backfill_to_latest, read_latest, write_latest

__all__ = ["backfill_to_latest", "read_latest", "write_latest", "__version__"]

__version__ = "0.0.1"
