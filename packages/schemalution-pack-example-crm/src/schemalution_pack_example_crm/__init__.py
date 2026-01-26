"""Public API for schemalution-pack-example-crm."""

from __future__ import annotations

from .pack import LATEST_VERSION, SCHEMA_ID, register

__all__ = ["EXAMPLE_PACK", "LATEST_VERSION", "SCHEMA_ID", "register", "__version__"]

__version__ = "0.0.1"

EXAMPLE_PACK = "example_crm"
