"""Public API for schevo-compose.

Only the symbols exported here are considered public and stable.
"""

from __future__ import annotations

from .composer import compose_root
from .merge import choose_newer, deep_merge, merge_arrays_by_key
from .model import ComposeContext, Fragment

__all__ = [
    "ComposeContext",
    "Fragment",
    "choose_newer",
    "compose_root",
    "deep_merge",
    "merge_arrays_by_key",
    "__version__",
]

__version__ = "0.0.1"
