"""Deterministic merge helpers."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .model import ComposeContext, Fragment


def deep_merge(
    base: dict[str, Any],
    patch: Mapping[str, Any],
    *,
    overwrite: bool = True,
    context: ComposeContext | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = dict(base)
    for key, value in patch.items():
        if key in result and isinstance(result[key], Mapping) and isinstance(value, Mapping):
            result[key] = deep_merge(
                dict(result[key]),
                value,
                overwrite=overwrite,
                context=context,
            )
            continue
        if key in result and not overwrite:
            if context is not None:
                context.warnings.append(f"deep_merge skipped key '{key}' due to overwrite=False.")
            continue
        result[key] = value
    return result


def merge_arrays_by_key(
    base_list: list[dict[str, Any]],
    patch_list: list[dict[str, Any]],
    *,
    key: str,
    overwrite: bool = True,
    context: ComposeContext | None = None,
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = [dict(item) for item in base_list]
    index_by_key: dict[Any, int] = {}
    for idx, item in enumerate(result):
        if key in item:
            index_by_key[item[key]] = idx
        else:
            if context is not None:
                context.warnings.append("merge_arrays_by_key base item missing key.")

    for item in patch_list:
        if key not in item:
            if context is not None:
                context.warnings.append("merge_arrays_by_key patch item missing key.")
            result.append(dict(item))
            continue
        item_key = item[key]
        if item_key in index_by_key:
            base_item = result[index_by_key[item_key]]
            result[index_by_key[item_key]] = deep_merge(
                base_item,
                item,
                overwrite=overwrite,
                context=context,
            )
        else:
            index_by_key[item_key] = len(result)
            result.append(dict(item))
    return result


def choose_newer(base_fragment: Fragment, patch_fragment: Fragment) -> Fragment:
    if base_fragment.updated_at and patch_fragment.updated_at:
        return (
            patch_fragment
            if patch_fragment.updated_at > base_fragment.updated_at
            else base_fragment
        )  # noqa: E501
    if base_fragment.updated_at and patch_fragment.updated_at is None:
        return base_fragment
    if patch_fragment.updated_at and base_fragment.updated_at is None:
        return patch_fragment
    return patch_fragment
