"""Pack loading helpers for the CLI."""

from __future__ import annotations

import importlib
import os
from dataclasses import dataclass
from typing import Any, Iterable

from schemalution_core import MigrationRegistry


@dataclass(frozen=True, slots=True)
class LoadedPack:
    module: str
    pack_id: str
    version: str | None
    schema_ids: list[str]


def resolve_pack_modules(pack_args: Iterable[str] | None) -> list[str]:
    modules: list[str] = []
    env_value = os.getenv("SCHEMALUTION_PACKS", "")
    if env_value:
        modules.extend([item.strip() for item in env_value.split(",") if item.strip()])
    if pack_args:
        for entry in pack_args:
            modules.extend([item.strip() for item in entry.split(",") if item.strip()])
    seen: set[str] = set()
    ordered: list[str] = []
    for module in modules:
        if module in seen:
            continue
        seen.add(module)
        ordered.append(module)
    return ordered


def load_packs(registry: MigrationRegistry, module_names: Iterable[str]) -> list[LoadedPack]:
    loaded: list[LoadedPack] = []
    for module_name in module_names:
        module = importlib.import_module(module_name)
        before = set(registry.schema_ids())
        pack_id = _pack_id(module, module_name)
        version = _pack_version(module)

        pack_obj = getattr(module, "PACK", None)
        if pack_obj is not None and hasattr(pack_obj, "register"):
            pack_obj.register(registry)
            schema_ids = _schema_ids_from_pack(pack_obj)
        elif hasattr(module, "register"):
            module.register(registry)
            schema_ids = _schema_ids_from_module(module)
        else:
            raise ValueError(f"pack module '{module_name}' does not expose register() or PACK.")

        after = set(registry.schema_ids())
        registered = sorted(after - before)
        merged = sorted(set(schema_ids) | set(registered))
        loaded.append(
            LoadedPack(
                module=module_name,
                pack_id=pack_id,
                version=version,
                schema_ids=merged,
            )
        )
    return loaded


def _pack_id(module: Any, module_name: str) -> str:
    for attr in ("PACK_ID", "PACK_NAME", "EXAMPLE_PACK"):
        value = getattr(module, attr, None)
        if isinstance(value, str) and value:
            return value
    pack_obj = getattr(module, "PACK", None)
    if pack_obj is not None:
        value = getattr(pack_obj, "pack_id", None)
        if isinstance(value, str) and value:
            return value
    return module_name


def _pack_version(module: Any) -> str | None:
    value = getattr(module, "__version__", None)
    if isinstance(value, str) and value:
        return value
    try:
        from importlib import metadata

        return metadata.version(module.__name__)
    except Exception:
        return None


def _schema_ids_from_pack(pack_obj: Any) -> list[str]:
    schemas = getattr(pack_obj, "schemas", None)
    if callable(schemas):
        result = schemas()
        if isinstance(result, list):
            return _schema_ids_from_specs(result)
        return _schema_ids_from_specs([result])
    return []


def _schema_ids_from_module(module: Any) -> list[str]:
    for attr in ("SCHEMA_SPECS", "SCHEMA_SPEC"):
        value = getattr(module, attr, None)
        if value is None:
            continue
        if isinstance(value, list):
            return _schema_ids_from_specs(value)
        return _schema_ids_from_specs([value])
    schema_id = getattr(module, "SCHEMA_ID", None)
    if isinstance(schema_id, str) and schema_id:
        return [schema_id]
    schemas_fn = getattr(module, "schemas", None)
    if callable(schemas_fn):
        result = schemas_fn()
        if isinstance(result, list):
            return _schema_ids_from_specs(result)
        return _schema_ids_from_specs([result])
    return []


def _schema_ids_from_specs(specs: Iterable[Any]) -> list[str]:
    schema_ids: list[str] = []
    for spec in specs:
        schema_id = getattr(spec, "schema_id", None)
        if isinstance(schema_id, str) and schema_id:
            schema_ids.append(schema_id)
    return sorted(set(schema_ids))
