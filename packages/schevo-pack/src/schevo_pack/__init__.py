"""Public API for schevo-pack.

Only the symbols exported here are considered public and stable.
"""

from __future__ import annotations

from .pack import BasePack, Pack, SchemaSpec, register_schema

__all__ = ["BasePack", "Pack", "SchemaSpec", "register_schema", "__version__"]

__version__ = "0.0.1"
