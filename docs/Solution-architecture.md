# schemalution — Solution Architecture

## Purpose
schemalution is a Python toolkit that makes schema evolution a first-class, deterministic capability. It enables zero-downtime schema changes, stable downstream systems, and multi-domain composition by upcasting mixed-version records to a single latest schema.

This document describes the current architecture and the planned evolution of the system based on the repository roadmap and prompts.

---

## Core architectural principles
- Deterministic migrations: pure functions (dict -> dict), no I/O.
- Domain autonomy: each domain owns its schema pack and evolution path.
- Upcast-to-latest: consumers operate on a single latest schema shape.
- Thin adapters: integrations wrap core and do not reimplement it.
- Stable public APIs: small, explicit surface area, guardrails against breakage.

---

## High-level architecture

### Conceptual flow (runtime)
1) Raw data arrives with `schema_id` and `schema_version`.
2) A MigrationRegistry is built by installing one or more schema packs.
3) Records are upcast to the latest schema at the chosen boundary.
4) Downstream systems operate on stable, latest-only shapes.

### Architectural boundaries
schemalution is intentionally boundary-agnostic. It can be placed at:
- Service read paths (schema-on-read)
- Projection pipelines (upcast-on-ingest)
- Gateway services (central enforcement)
- Backfill / batch upgrade jobs
- Multi-domain composition services

---

## Current package architecture

### Core
- `schemalution-core`
  - MigrationRegistry
  - upcast / upcast_to_latest
  - diagnostics and guardrails
  - deterministic operations DSL

### Pack authoring
- `schemalution-pack`
  - helpers for defining schema specs
  - pack registration utilities
  - optional metadata hooks

### Example domain pack
- `schemalution-pack-example-crm`
  - example `crm.customer` schema pack
  - migrations and fixtures

### Adapters
- `schemalution-mongo`
  - thin helpers for MongoDB read/latest workflows
- `schemalution-spark`
  - JSON UDF helpers for Spark/Databricks pipelines

### Composition
- `schemalution-compose`
  - fragment model
  - merge strategies
  - compose_root utilities

---

## Data model and envelope
All records follow a common envelope:
- `schema_id`: string identifier (e.g. `crm.customer`)
- `schema_version`: integer version
- payload: dict-like domain fields

Upcast transforms use the registry to deterministically map any record to the latest schema version for its `schema_id`.

---

## Core workflow (minimal)
1) Create registry
2) Register schema packs
3) Upcast record to latest
4) (Optional) validate with contract models

```python
from schemalution_core import MigrationRegistry, upcast_to_latest
from schemalution_pack_example_crm import SCHEMA_ID, register

registry = MigrationRegistry()
register(registry)

record = {"schema_version": 1, "customerId": "c-1", "name": "Ada", "age": "42"}
latest = upcast_to_latest(record, SCHEMA_ID, registry)
```

---

## Deployment architectures

### 1) Embedded schema-on-read
- Services upcast records on read.
- Business logic always sees latest shape.

### 2) Canonical projection
- Upcast once during pipeline ingestion.
- Consumers read stable latest-only datasets.

### 3) Schema gateway
- Central service enforces schema upgrades and validation.

### 4) Write-latest + backfill
- Writes enforce latest; backfills converge historical data.

---

## Composition architecture
- Domain projections remain independent.
- A composition service combines fragments into a root view.
- Each fragment retains its schema identity and lineage.

Example composition flow:
- CRM latest + Risk latest + Support latest -> Customer 360 root

---

## Operational constraints and testing
- Python >= 3.10
- ruff for linting and formatting
- pyright for type checking
- pytest for unit tests
- table-driven fixtures for migration tests

---

## Future architecture (AI interop and automation)
The roadmap extends schemalution into a first-class AI and tooling substrate.

### 1) CLI and registry export (M9)
- Machine-readable registry export (JSON + optional DOT)
- CLI JSON input/output for upcast and validate
- Stable output schema with versioning

### 2) MCP server (M10)
- MCP tools for listing schema IDs, migrations, and upcasting
- Deterministic execution with structured logging
- Configurable authentication hooks

### 3) Contract export (M11)
- JSON Schema and OpenAPI exports for latest-only models
- Versioned artifacts published alongside packs

### 4) Migration intelligence (M12)
- Schema diff engine with heuristics
- Ops DSL-based migration scaffolding
- Actionable diff reports

### 5) Breaking-change analyzer (M13)
- Detection of removals, required additions, type narrowing
- CI policy enforcement with allowlists

### 6) Fixture and test automation (M14)
- Golden fixture generation
- Migration replay harness
- Pack-level scaffolding templates

### 7) Backfill simulation (M15)
- Dry-run on sampled datasets
- Detailed error/warning reporting
- CSV/JSON summaries

### 8) Schema linting + policy checks (M16)
- Envelope validation
- Migration path completeness
- Determinism guard

### 9) Pack metadata for AI reasoning (M17)
- Migration intent annotations
- Field lineage mapping
- Semantic version hints

### 10) Agent workflow blueprints (M18)
- End-to-end workflows for add/deprecate/split/merge field changes
- Human review checkpoints

### 11) Auditability + replay logs (M19)
- Standardized run metadata
- Optional audit log sink
- Deterministic replay tooling

---

## How future features relate to core product goals
- Interop and MCP features extend schemalution from a library to an automation platform.
- Diff, lint, and analyzer tools enforce safety and reduce change risk.
- Workflows and metadata make schema evolution more human- and AI-readable.
- Audit and replay ensure traceability for historical interpretation.

---

## Verification and review expectations
For each milestone, success is defined by:
- A clear set of deliverables
- Deterministic behavior and strong tests
- Integration tests for CLI/MCP/exports
- Documentation updates where behavior is exposed

All milestones include a risk loop: during implementation, risks and mitigations are logged in `docs/Risks.md`.

---

## Appendix: system boundaries and interfaces

### External interfaces
- Python API: `schemalution-core`, `schemalution-pack`
- Adapters: `schemalution-mongo`, `schemalution-spark`
- Composition: `schemalution-compose`
- Planned tooling: CLI JSON, MCP server, contract exports

### Internal boundaries
- Core must remain dependency-light and deterministic.
- Packs provide domain evolution and metadata.
- Adapters remain thin wrappers around core.

