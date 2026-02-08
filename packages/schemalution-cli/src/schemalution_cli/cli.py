"""CLI entrypoints for schemalution JSON I/O and registry export."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from typing import Any, Iterable, Sequence

from schemalution_core import (
    InvalidSchemaVersionError,
    MigrationEdge,
    MigrationRegistry,
    MissingSchemaVersionError,
    NoMigrationPathError,
    UnsupportedSchemaIdError,
    UpcastContext,
    upcast,
)

from .packs import load_packs, resolve_pack_modules


@dataclass(frozen=True, slots=True)
class CLIError(Exception):
    code: str
    message: str
    command: str
    schema_id: str | None = None
    details: dict[str, Any] | None = None


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "registry" and args.registry_command == "export":
            return _handle_registry_export(args)
        if args.command == "upcast":
            return _handle_upcast(args)
        if args.command == "validate":
            return _handle_validate(args)
        raise CLIError("invalid_command", "Unknown command.", command="unknown")
    except CLIError as exc:
        payload = _error_payload(exc)
        _emit_json(payload)
        return 1
    except Exception as exc:  # noqa: BLE001 - last-resort handler
        payload = _error_payload(
            CLIError(
                "internal_error",
                f"Unexpected error: {exc}",
                command=_command_name(args),
            )
        )
        _emit_json(payload)
        return 1


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="schemalution")
    subparsers = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--pack", action="append", help="Pack module to load (repeatable).")

    registry = subparsers.add_parser("registry")
    registry_sub = registry.add_subparsers(dest="registry_command", required=True)
    export = registry_sub.add_parser("export", parents=[common])
    export.add_argument("--format", default="v1")
    export.add_argument("--dot", action="store_true", help="Emit DOT format.")
    export.add_argument("--out", help="Write output to file (optional).")

    upcast_parser = subparsers.add_parser("upcast", parents=[common])
    upcast_parser.add_argument("--schema-id", required=False)
    upcast_parser.add_argument("--format", default="v1")
    upcast_parser.add_argument("--trace", action="store_true")

    validate_parser = subparsers.add_parser("validate", parents=[common])
    validate_parser.add_argument("--schema-id", required=False)
    validate_parser.add_argument("--format", default="v1")
    validate_parser.add_argument("--trace", action="store_true")

    return parser


def _handle_registry_export(args: argparse.Namespace) -> int:
    _ensure_format(args.format, "registry.export")
    registry, packs = _build_registry(args.pack, "registry.export")
    if args.dot:
        dot = _render_dot(registry.list_migrations())
        if args.out:
            _write_text(args.out, dot)
            return 0
        sys.stdout.write(dot)
        return 0

    payload: dict[str, Any] = {
        "format": "v1",
        "command": "registry.export",
        "schema_id": None,
        "success": True,
        "errors": [],
        "schema_ids": registry.schema_ids(),
        "latest_versions": registry.latest_versions(),
        "migrations": [
            {
                "schema_id": edge.schema_id,
                "from_version": edge.from_version,
                "to_version": edge.to_version,
                "op_count": None,
            }
            for edge in registry.list_migrations()
        ],
        "packs": [
            {
                "module": pack.module,
                "pack_id": pack.pack_id,
                "version": pack.version,
                "schema_ids": pack.schema_ids,
            }
            for pack in packs
        ],
    }
    output = json.dumps(payload, sort_keys=True)
    if args.out:
        _write_text(args.out, output)
    sys.stdout.write(output)
    return 0


def _handle_upcast(args: argparse.Namespace) -> int:
    _ensure_format(args.format, "upcast")
    schema_id = _require_schema_id(args.schema_id, "upcast")
    registry, _ = _build_registry(args.pack, "upcast")
    record = _read_json_stdin("upcast")
    context = UpcastContext()
    trace: list[dict[str, str | int]] = []

    def on_step(sid: str, from_v: int, to_v: int) -> None:
        trace.append({"schema_id": sid, "from_version": from_v, "to_version": to_v})

    try:
        output = upcast(
            record,
            schema_id,
            registry,
            to_version="latest",
            context=context,
            on_step=on_step if args.trace else None,
        )
    except Exception as exc:  # noqa: BLE001 - surfaced through CLI error mapping
        raise _map_error(exc, "upcast", schema_id) from exc

    payload: dict[str, Any] = {
        "format": "v1",
        "command": "upcast",
        "schema_id": schema_id,
        "success": True,
        "errors": [],
        "input_version": record.get("schema_version"),
        "output_version": output.get("schema_version"),
        "record": output,
        "warnings": context.warnings,
        "unknown_fields": _unknown_fields(context),
    }
    if args.trace:
        payload["trace"] = trace
    _emit_json(payload)
    return 0


def _handle_validate(args: argparse.Namespace) -> int:
    _ensure_format(args.format, "validate")
    schema_id = _require_schema_id(args.schema_id, "validate")
    registry, _ = _build_registry(args.pack, "validate")
    record = _read_json_stdin("validate")
    context = UpcastContext()
    trace: list[dict[str, str | int]] = []

    def on_step(sid: str, from_v: int, to_v: int) -> None:
        trace.append({"schema_id": sid, "from_version": from_v, "to_version": to_v})

    try:
        upcast(
            record,
            schema_id,
            registry,
            to_version="latest",
            context=context,
            on_step=on_step if args.trace else None,
        )
    except Exception as exc:  # noqa: BLE001 - surfaced through CLI error mapping
        raise _map_error(exc, "validate", schema_id) from exc

    payload: dict[str, Any] = {
        "format": "v1",
        "command": "validate",
        "schema_id": schema_id,
        "success": True,
        "errors": [],
        "is_valid": True,
        "violations": [],
        "warnings": context.warnings,
    }
    if args.trace:
        payload["trace"] = trace
    _emit_json(payload)
    return 0


def _build_registry(pack_args: Iterable[str] | None, command: str) -> tuple[MigrationRegistry, list[Any]]:
    module_names = resolve_pack_modules(pack_args)
    if not module_names:
        raise CLIError(
            "missing_packs",
            "No packs provided. Use --pack or SCHEMALUTION_PACKS.",
            command=command,
        )
    registry = MigrationRegistry()
    try:
        packs = load_packs(registry, module_names)
    except Exception as exc:  # noqa: BLE001
        raise CLIError("pack_load_failed", f"Failed to load pack: {exc}", command=command) from exc
    return registry, packs


def _render_dot(edges: Iterable[MigrationEdge]) -> str:
    lines = ["digraph schemalution {"]
    for edge in edges:
        src = f"{edge.schema_id}:v{edge.from_version}"
        dst = f"{edge.schema_id}:v{edge.to_version}"
        lines.append(f'  "{src}" -> "{dst}";')
    lines.append("}")
    return "\n".join(lines)


def _read_json_stdin(command: str) -> dict[str, Any]:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        raise CLIError("invalid_json", f"Invalid JSON input: {exc}", command=command) from exc
    if not isinstance(payload, dict):
        raise CLIError("invalid_json", "Input JSON must be an object.", command=command)
    return payload


def _emit_json(payload: dict[str, Any]) -> str:
    text = json.dumps(payload, sort_keys=True)
    sys.stdout.write(text)
    return text


def _write_text(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)


def _ensure_format(fmt: str, command: str) -> None:
    if fmt != "v1":
        raise CLIError("unsupported_format", f"Unsupported format '{fmt}'.", command=command)


def _require_schema_id(schema_id: str | None, command: str) -> str:
    if not schema_id:
        raise CLIError("missing_schema_id", "--schema-id is required.", command=command)
    return schema_id


def _unknown_fields(context: UpcastContext) -> list[str]:
    notes = context.notes.get("unknown_fields")
    if isinstance(notes, list):
        return [item for item in notes if isinstance(item, str)]
    return []


def _map_error(exc: Exception, command: str, schema_id: str | None) -> CLIError:
    if isinstance(exc, MissingSchemaVersionError):
        return CLIError("missing_schema_version", str(exc), command=command, schema_id=schema_id)
    if isinstance(exc, InvalidSchemaVersionError):
        return CLIError("invalid_schema_version", str(exc), command=command, schema_id=schema_id)
    if isinstance(exc, UnsupportedSchemaIdError):
        return CLIError("unsupported_schema_id", str(exc), command=command, schema_id=schema_id)
    if isinstance(exc, NoMigrationPathError):
        return CLIError("no_migration_path", str(exc), command=command, schema_id=schema_id)
    return CLIError("migration_error", str(exc), command=command, schema_id=schema_id)


def _error_payload(error: CLIError) -> dict[str, Any]:
    return {
        "format": "v1",
        "command": error.command,
        "schema_id": error.schema_id,
        "success": False,
        "errors": [
            {
                "code": error.code,
                "message": error.message,
                "details": error.details or {},
            }
        ],
    }


def _command_name(args: argparse.Namespace) -> str:
    if getattr(args, "command", None) == "registry":
        return "registry.export"
    if getattr(args, "command", None) in {"upcast", "validate"}:
        return args.command
    return "unknown"


if __name__ == "__main__":
    raise SystemExit(main())
