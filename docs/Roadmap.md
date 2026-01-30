# schemalution — Codex Charter

## Purpose
schemalution is an open-source Python toolkit for evolving document schemas across versions and composing multi-domain documents into projections, while keeping:
- domain autonomy (schema packs per domain),
- stable read models (upcast-to-latest),
- optional adapters for MongoDB and Spark,
- optional composition utilities for projection services.

## Repository layout
This repo is a monorepo with independently installable packages under `/packages`:

- schemalution-core      -> src/schemalution_core
- schemalution-pack      -> src/schemalution_pack
- schemalution-mongo     -> src/schemalution_mongo
- schemalution-spark     -> src/schemalution_spark
- schemalution-compose   -> src/schemalution_compose
- schemalution-pack-example-crm -> src/schemalution_pack_example_crm (example domain pack)

## Design principles
1) Core is pure: `schemalution-core` must not depend on Mongo, Spark, FastAPI, etc.
2) Domain logic lives in schema packs: migrations + latest models + registration.
3) Adapters are thin: mongo/spark packages wrap the core; they do not reimplement it.
4) Public APIs are stable and small; internal modules can change freely.
5) Deterministic transformations: migrations should be pure functions (dict -> dict) with no I/O.
6) Every record uses an envelope convention:
   - `schema_id: str` (e.g., "crm.customer")
   - `schema_version: int` (or semver later; v1 uses int)
   - payload is dict-like.
7) Upcasting is the default: consumers call `upcast_to_latest(schema_id, record)`.

## Versioning & support policy
- Each schema_id has a LATEST version.
- Optional MIN_SUPPORTED version.
- Upcaster errors clearly on unsupported or missing paths.

## Testing policy
- pytest for unit tests.
- Every new feature must add tests.
- Prefer table-driven tests for migrations (before/after fixtures).
- CI must pass: ruff, pyright, pytest.

## Tooling & style
- Python >= 3.10
- ruff: lint + formatting
- pyright: type checking
- Use `src/` layout
- Prefer dataclasses / TypedDict / pydantic only in schema packs (core stays dependency-light).
- Keep functions small; avoid overengineering.

## Implementation roadmap (milestones)
M0: Scaffolding (done)
  - Risk loop: during work, log risks and mitigations in docs/Risks.md.
M1: Core MVP (done)
  - MigrationRegistry
  - register_migration(schema_id, from_version, to_version, fn)
  - upcast(record, schema_id, to_version)
  - upcast_to_latest(record, schema_id)
  - linear routing (v1 -> v2 -> v3 ...), clear errors
  - rich error messages and unit tests
  - Risk loop: during work, log risks and mitigations in docs/Risks.md.

M2: Diagnostics and hooks (done)
  - context object (warnings, unknown fields)
  - optional logger hook
  - Risk loop: during work, log risks and mitigations in docs/Risks.md.

M3: Declarative ops DSL (rename/default/move/cast/coalesce) layered on top of M1 (done)
  - Risk loop: during work, log risks and mitigations in docs/Risks.md.

M4: Example schema pack (crm.customer with 3 versions) using M1/M3 (done)
  - Risk loop: during work, log risks and mitigations in docs/Risks.md.

M4.1: refinements to schemalution-pack-example-crm (done)
  - Risk loop: during work, log risks and mitigations in docs/Risks.md.

M4.2: Core API & Semantics Refinements (done)
  - Risk loop: during work, log risks and mitigations in docs/Risks.md.

M4.5: schemalution-pack package. Keep it small and useful (done)
  - Risk loop: during work, log risks and mitigations in docs/Risks.md.

M5: Mongo adapter (read_latest/write_latest/backfill skeleton) (done)
  - Risk loop: during work, log risks and mitigations in docs/Risks.md.

M6: Spark adapter (UDF wrapper returning JSON) (done)
  - Risk loop: during work, log risks and mitigations in docs/Risks.md.

M7: Compose utilities (fragments + merge strategies) (done)
  - Risk loop: during work, log risks and mitigations in docs/Risks.md.

M8.A: Public API freeze and guardrails. (done)
  - Risk loop: during work, log risks and mitigations in docs/Risks.md.

## AI interop & automation roadmap (milestones)
M9: Registry export + CLI JSON I/O
  - Product fit: make schemalution usable by any tool or agent that can call a CLI with JSON.
  - Deliverables: `schemalution registry export` (JSON + optional DOT), `schemalution upcast` and `validate` with stdin/stdout JSON, versioned `--format` flag, stable output schema.
  - Success looks like: non-Python tools can upcast/validate without importing schemalution, and registry export is consumed by at least one downstream tool.
  - Verify/review: CLI golden-output tests, schema versioning tests, docs updated with examples.
  - Risk loop: during work, log risks and mitigations in docs/Risks.md.

M10: MCP server package (schemalution-mcp)
  - Product fit: first-class MCP bridge so AI tools can reason over packs and run upcasts deterministically.
  - Deliverables: MCP server with tools (list_schema_ids, get_latest_version, get_migrations, upcast_record, validate_record, diff_versions, simulate_upcast), config/auth hooks, structured logging.
  - Success looks like: an MCP client can complete end-to-end upcast + diff flows using only tool calls.
  - Verify/review: integration tests with a mock MCP client, determinism checks, security review for config inputs.
  - Risk loop: during work, log risks and mitigations in docs/Risks.md.

M11: Contract export (JSON Schema / OpenAPI)
  - Product fit: provide formal latest-shape contracts for clients, docs, and AI reasoning.
  - Deliverables: pack-level JSON Schema export, optional OpenAPI components for latest-only models, versioned artifacts with schema_id mapping.
  - Success looks like: contracts can validate latest records and be published alongside packs.
  - Verify/review: schema validation tests against fixtures, artifact snapshot tests, README/docs additions.
  - Risk loop: during work, log risks and mitigations in docs/Risks.md.

M12: Migration intelligence (AI-assistable)
  - Product fit: reduce migration authoring cost and enable agent-assisted changes.
  - Deliverables: schema diffing engine with rename/move/cast/default/coalesce heuristics, migration stub generator using ops DSL, actionable "unhandled diff" report.
  - Success looks like: common changes are scaffolded automatically with minimal manual edits.
  - Verify/review: unit tests for diff heuristics, fixture-based migration generation tests, reviewer checklist for false positives.
  - Risk loop: during work, log risks and mitigations in docs/Risks.md.

M13: Breaking-change analyzer
  - Product fit: make schema evolution safe by detecting consumer-breaking changes early.
  - Deliverables: detector for removals, required-field additions, type narrowing; risk scoring; CI policy enforcement with allowlist and overrides.
  - Success looks like: breaking changes are flagged before release and can be suppressed only with explicit justification.
  - Verify/review: unit tests for each rule, CI integration test, docs on policy configuration.
  - Risk loop: during work, log risks and mitigations in docs/Risks.md.

M14: Fixture and test automation
  - Product fit: make migration correctness cheap to verify for every pack.
  - Deliverables: golden fixture generator (before/after), migration replay test harness, pack-level test scaffolding templates.
  - Success looks like: new migrations can be tested by generating fixtures in minutes with no manual boilerplate.
  - Verify/review: template snapshot tests, sample pack using scaffolds, instructions in docs.
  - Risk loop: during work, log risks and mitigations in docs/Risks.md.

M15: Backfill simulation tooling
  - Product fit: de-risk production rollouts by simulating real data upgrades.
  - Deliverables: sample dataset runner with error/warning stats, reports for unknown fields/missing paths/invalid types, CSV/JSON summary export.
  - Success looks like: teams can run a dry-run and decide rollout readiness from the report.
  - Verify/review: fixture-driven simulation tests, output schema tests, example report in docs.
  - Risk loop: during work, log risks and mitigations in docs/Risks.md.

M16: Schema linting + policy checks
  - Product fit: enforce hygiene and determinism across packs and core.
  - Deliverables: envelope validation, monotonic versioning checks, migration path completeness, determinism guard (no I/O or nondeterministic calls).
  - Success looks like: lint can be run in CI to catch errors before merge.
  - Verify/review: unit tests for each lint rule, CLI exit-code tests, docs for rule configuration.
  - Risk loop: during work, log risks and mitigations in docs/Risks.md.

M17: Pack metadata for AI reasoning
  - Product fit: add machine-readable intent so AIs can explain and automate schema changes.
  - Deliverables: migration intent annotations, field lineage map with notes, semantic version hints (breaking/deprecated/removed_in).
  - Success looks like: metadata is exported with packs and used by at least one tool (CLI/MCP/contract export).
  - Verify/review: schema for metadata, serialization tests, migration examples in docs.
  - Risk loop: during work, log risks and mitigations in docs/Risks.md.

M18: Agent workflow blueprints
  - Product fit: codify repeatable AI-assisted workflows that map to real team tasks.
  - Deliverables: workflows for add field, deprecate field, split/merge field; each includes required inputs, generated outputs, and human review steps.
  - Success looks like: an agent can follow a workflow end-to-end with deterministic outputs and a clear review checklist.
  - Verify/review: example runs on sample packs, workflow docs, reviewer checklist for each flow.
  - Risk loop: during work, log risks and mitigations in docs/Risks.md.

M19: Auditability + replay logs
  - Product fit: preserve traceability for schema interpretation across time and environments.
  - Deliverables: standardized run metadata (versions, warnings, unknowns), optional append-only audit sink, deterministic replay tooling.
  - Success looks like: a recorded run can be replayed to reproduce outputs exactly.
  - Verify/review: replay tests with fixed inputs, log format schema tests, security review for log sinks.
  - Risk loop: during work, log risks and mitigations in docs/Risks.md.

## Definition of Done for each milestone PR
- Code implemented with tests
- Types pass (pyright)
- Lint/format pass (ruff)
- README updated if public behavior changes
- No unrelated refactors
