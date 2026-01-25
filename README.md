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
