# schevo

Monorepo for the Schevo Python packages.

Schevo is a schema evolution toolkit: migrations are pure dict → dict transforms,
schema packs own evolution logic, and consumers upcast records to the latest version.

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

## Core (schevo-core)

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

Declarative ops can be compiled into migrations:

```python
from schevo_core import compile_ops
from schevo_core.ops import Rename, SetDefault

ops = [Rename("name", "full_name"), SetDefault("status", "active")]
fn = compile_ops(ops)
```

## Pack helpers (schevo-pack)

schevo-pack provides lightweight helpers to register schema packs consistently.

```python
from schevo_pack import SchemaSpec, register_schema

spec = SchemaSpec(schema_id="crm.customer", latest_version=3)
register_schema(registry, spec, [(1, 2, v1_to_v2), (2, 3, v2_to_v3)])
```

## Example pack (schevo-pack-example-crm)

The CRM example pack implements `crm.customer` with 3 versions and demonstrates
ops-based migrations. It exposes `register(registry)` and is used in tests.

```python
from schevo_core import MigrationRegistry, upcast_to_latest
from schevo_pack_example_crm import SCHEMA_ID, register

registry = MigrationRegistry()
register(registry)
latest = upcast_to_latest({"schema_version": 1, "customerId": "c-1", "name": "Ada"}, SCHEMA_ID, registry)
```

## Mongo adapter (schevo-mongo)

schevo-mongo provides thin helpers for MongoDB read/upcast/write workflows.

```python
from schevo_mongo import read_latest, write_latest

doc = read_latest(collection, SCHEMA_ID, registry, {"_id": "c-1"})
write_latest(collection, SCHEMA_ID, registry, doc)
```

## Spark adapter (schevo-spark)

schevo-spark supports projection pipelines (Architecture B). It can upcast records
to JSON and provides a Spark UDF helper with lazy pyspark imports.

```python
from schevo_spark import make_upcast_to_latest_json_udf

udf = make_upcast_to_latest_json_udf(SCHEMA_ID, registry)
```

## Dev setup

From the repo root:

```
make setup
make venv
make sync
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
