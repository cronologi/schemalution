from __future__ import annotations

import io
import json
import sys
import types
from collections.abc import Mapping
from pathlib import Path
from typing import Any, cast

from jsonschema import validate
from schemalution_cli.cli import main
from schemalution_core import MigrationRegistry

_ROOT = Path(__file__).resolve().parents[3]
_SCHEMA = json.loads((_ROOT / "docs/cli/format-v1.schema.json").read_text(encoding="utf-8"))


def _install_fake_pack(name: str = "tests_fake_pack") -> str:
    module = cast(Any, types.ModuleType(name))

    def register(registry: MigrationRegistry) -> None:
        def _v1_to_v2(record: Mapping[str, Any]) -> dict[str, Any]:
            updated = dict(record)
            updated["full_name"] = updated.pop("name", "unknown")
            return updated

        registry.register_migration("crm.customer", 1, 2, _v1_to_v2)
        registry.set_latest_version("crm.customer", 2)

    module.register = register
    module.SCHEMA_ID = "crm.customer"
    module.__version__ = "0.1.0"
    sys.modules[name] = module
    return name


def _run_cli(monkeypatch, args: list[str], stdin_payload: dict[str, Any] | None = None) -> str:
    stdout = io.StringIO()
    monkeypatch.setattr(sys, "stdout", stdout)
    if stdin_payload is not None:
        monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(stdin_payload)))
    exit_code = main(args)
    assert exit_code == 0
    return stdout.getvalue()


def test_upcast_command(monkeypatch) -> None:
    pack = _install_fake_pack()
    output = _run_cli(
        monkeypatch,
        ["upcast", "--schema-id", "crm.customer", "--pack", pack, "--format", "v1"],
        {"schema_version": 1, "name": "Ada"},
    )
    payload = json.loads(output)
    validate(payload, _SCHEMA)
    assert payload["success"] is True
    assert payload["output_version"] == 2
    assert payload["record"]["full_name"] == "Ada"


def test_validate_command(monkeypatch) -> None:
    pack = _install_fake_pack("tests_fake_pack_validate")
    output = _run_cli(
        monkeypatch,
        ["validate", "--schema-id", "crm.customer", "--pack", pack, "--format", "v1"],
        {"schema_version": 1, "name": "Ada"},
    )
    payload = json.loads(output)
    validate(payload, _SCHEMA)
    assert payload["success"] is True
    assert payload["is_valid"] is True


def test_registry_export_json(monkeypatch) -> None:
    pack = _install_fake_pack("tests_fake_pack_registry")
    output = _run_cli(
        monkeypatch,
        ["registry", "export", "--pack", pack, "--format", "v1"],
    )
    payload = json.loads(output)
    validate(payload, _SCHEMA)
    assert payload["success"] is True
    assert "crm.customer" in payload["schema_ids"]


def test_registry_export_dot(monkeypatch) -> None:
    pack = _install_fake_pack("tests_fake_pack_dot")
    output = _run_cli(
        monkeypatch,
        ["registry", "export", "--pack", pack, "--dot"],
    )
    assert output.strip().startswith("digraph schemalution")
