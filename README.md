# schevo

Monorepo for the Schevo Python packages.

## Repo layout

```
packages/
  schevo-core/
  schevo-pack/
  schevo-mongo/
  schevo-spark/
  schevo-compose/
  schevo-pack-example-crm/
```

Each package is independently installable and uses a src/ layout.

## Core MVP (schevo-core)

The core package provides a migration registry and upcast helpers for evolving records
linearly from vN to vN+1. Upcast also supports an optional context and per-step hook for
diagnostics. Example usage:

```python
from schevo_core import MigrationRegistry, upcast_to_latest


def v1_to_v2(record: dict) -> dict:
    updated = dict(record)
    updated["full_name"] = updated.pop("name")
    return updated


registry = MigrationRegistry()
registry.register_migration("crm.customer", 1, 2, v1_to_v2)
registry.set_latest_version("crm.customer", 2)

record = {"schema_version": 1, "name": "Ada"}
latest = upcast_to_latest(record, "crm.customer", registry)
```

## Dev setup

From the repo root:

```
python -m pip install -e .[dev]
python -m pip install -e ./packages/schevo-core
python -m pip install -e ./packages/schevo-pack-example-crm
```

Using uv instead:

```
uv pip install -e .[dev]
uv pip install -e ./packages/schevo-core
uv pip install -e ./packages/schevo-pack-example-crm
```

## Tests, linting, typing

```
make lint
make format
make typecheck
make test
```

Or run directly:

```
ruff check .
ruff format --check .
pyright
pytest
```
