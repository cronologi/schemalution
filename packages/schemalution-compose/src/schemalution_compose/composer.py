"""Composition helper for deterministic root documents."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Literal

from .merge import choose_newer, deep_merge
from .model import ComposeContext, Fragment


def compose_root(
    fragments: Sequence[Fragment],
    *,
    root_schema_id: str,
    strategy: Literal["deep_merge"] = "deep_merge",
    context: ComposeContext | None = None,
) -> dict[str, Any]:
    if strategy != "deep_merge":
        raise ValueError(f"unsupported strategy '{strategy}'.")

    root: dict[str, Any] = {
        "schema_id": root_schema_id,
        "schema_version": 1,
        "components": {},
    }
    components: dict[str, Fragment] = {}

    for fragment in fragments:
        if fragment.schema_id in components:
            if context is not None:
                context.warnings.append(
                    f"duplicate fragment for '{fragment.schema_id}' encountered; choosing newer."
                )
            chosen = choose_newer(components[fragment.schema_id], fragment)
            components[fragment.schema_id] = chosen
        else:
            components[fragment.schema_id] = fragment

        root = deep_merge(root, fragment.payload, overwrite=True, context=context)
        if context is not None:
            context.applied.append(f"merged:{fragment.schema_id}")

    root["components"] = {schema_id: frag.payload for schema_id, frag in components.items()}
    return root
