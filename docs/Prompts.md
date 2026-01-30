# Milestone implementation prompts

Use the prompts below as copy/paste templates to implement each roadmap milestone. Each prompt bakes in best practices: clear goal, explicit scope, constraints, success criteria, test/verification, and the risk log loop.

## How to use
- Replace placeholders like `{milestone}`, `{context}`, `{constraints}`, `{tests}` with real info.
- Keep the prompt scoped: list only files you want touched, and mention any files that must not be changed.
- Always ask for a brief plan first on larger milestones (M9+), then implement.
- Include the risk loop instruction so risks and mitigations are logged in `docs/Risks.md`.

---

## M0: Scaffolding (done)

```
You are Codex. Implement M0: Scaffolding for schemalution.

Goal
- Establish the minimal monorepo scaffold and dev tooling required for the project to compile, lint, typecheck, and run tests.

Context
- Repo root: {context}
- Expected layout: monorepo under `packages/` with `src/` layout.

Scope
- Create or verify repo structure, baseline configs (pyproject, ruff/pyright), and a minimal Makefile/CI hooks if missing.
- Do not add core logic yet; only scaffolding.

Constraints
- Keep core dependency-light.
- Python >= 3.10; ruff + pyright + pytest.

Deliverables
- Directory structure for packages + baseline configs.
- Minimal README/Docs updates if necessary.

Success criteria
- `make lint`, `make typecheck`, `make test` pass or are runnable with empty tests.

Verify/review
- Run lint/typecheck/test or explain why they cannot run.

Risk loop
- During the work, log risks and mitigations in `docs/Risks.md`.

Ask
- If any scaffold expectations are unclear, ask a single clarification question before editing.
```

---

## M1: Core MVP (done)

```
You are Codex. Implement M1: Core MVP for schemalution.

Goal
- Provide the minimal migration engine with registration and upcasting APIs.

Scope
- Implement `MigrationRegistry`, `register_migration`, `upcast`, `upcast_to_latest` in `schemalution-core`.
- Add clear error handling for missing paths or unsupported versions.

Constraints
- Pure functions only (dict -> dict), no I/O.
- Keep APIs small and stable.

Deliverables
- Core engine code + unit tests.

Success criteria
- Can register migrations and upcast a record v1 -> latest deterministically.

Verify/review
- Add unit tests for linear routing, errors, and success path.

Risk loop
- During the work, log risks and mitigations in `docs/Risks.md`.
```

---

## M2: Diagnostics and hooks (done)

```
You are Codex. Implement M2: Diagnostics and hooks.

Goal
- Add diagnostics (warnings, unknown fields) and optional logger hooks.

Scope
- Introduce a context object returned or passed through upcasts.
- Add optional logging hooks without changing core semantics.

Constraints
- Do not add external dependencies.

Deliverables
- Diagnostics data structures + tests.

Success criteria
- Users can inspect warnings/unknowns after upcast.

Verify/review
- Unit tests for diagnostics, logger hook behavior.

Risk loop
- During the work, log risks and mitigations in `docs/Risks.md`.
```

---

## M3: Declarative ops DSL (done)

```
You are Codex. Implement M3: Declarative ops DSL.

Goal
- Provide a small DSL for migration operations (rename/move/cast/default/coalesce).

Scope
- Build ops DSL layered on core engine; no runtime or storage dependencies.

Constraints
- Preserve determinism and testability.

Deliverables
- Ops primitives + composition helpers + unit tests.

Success criteria
- Typical migrations can be expressed with DSL and produce expected outputs.

Verify/review
- Fixture-based tests for each op and a composed pipeline.

Risk loop
- During the work, log risks and mitigations in `docs/Risks.md`.
```

---

## M4: Example schema pack (done)

```
You are Codex. Implement M4: Example schema pack.

Goal
- Provide a `crm.customer` example pack with 3 versions using core + DSL.

Scope
- Create `schemalution-pack-example-crm` with schema spec, migrations, register function, fixtures.

Constraints
- Pack uses only schemalution core/pack utilities.

Deliverables
- Pack code + tests + fixtures.

Success criteria
- Example records upcast cleanly to latest.

Verify/review
- Table-driven tests across versions.

Risk loop
- During the work, log risks and mitigations in `docs/Risks.md`.
```

---

## M4.1: Example pack refinements (done)

```
You are Codex. Implement M4.1: refinements to schemalution-pack-example-crm.

Goal
- Improve readability, tests, and correctness of the example pack.

Scope
- Clean up fixtures, enrich tests, tighten docs.

Constraints
- No breaking changes to core APIs.

Deliverables
- Updated example pack with clearer fixtures and tests.

Success criteria
- Example pack acts as canonical reference for other packs.

Verify/review
- Run tests; validate docs examples compile.

Risk loop
- During the work, log risks and mitigations in `docs/Risks.md`.
```

---

## M4.2: Core API & semantics refinements (done)

```
You are Codex. Implement M4.2: Core API & semantics refinements.

Goal
- Tighten core semantics, improve error messages, and align public API naming.

Scope
- Adjust core APIs only where needed; update docs/tests for public changes.

Constraints
- Minimize breaking changes.

Deliverables
- Refined core APIs + updated tests + updated docs.

Success criteria
- Clearer errors, consistent behavior across edge cases.

Verify/review
- Unit tests for errors and edge cases.

Risk loop
- During the work, log risks and mitigations in `docs/Risks.md`.
```

---

## M4.5: schemalution-pack package (done)

```
You are Codex. Implement M4.5: schemalution-pack package.

Goal
- Provide minimal utilities for authoring schema packs.

Scope
- Add helpers for schema specs, registry registration, and optional metadata.

Constraints
- Keep it small and dependency-light.

Deliverables
- `schemalution-pack` package + docs + tests.

Success criteria
- Packs can be authored without repeating boilerplate.

Verify/review
- Tests for helpers; example pack uses them.

Risk loop
- During the work, log risks and mitigations in `docs/Risks.md`.
```

---

## M5: Mongo adapter (done)

```
You are Codex. Implement M5: Mongo adapter.

Goal
- Provide read_latest/write_latest/backfill skeletons for MongoDB.

Scope
- Add thin helpers that wrap core; do not reimplement migration logic.

Constraints
- Keep adapter optional and minimal.

Deliverables
- `schemalution-mongo` package + docs + tests.

Success criteria
- Adapter supports upcast-on-read and write-latest workflows.

Verify/review
- Unit tests using in-memory data or mocks; no DB required.

Risk loop
- During the work, log risks and mitigations in `docs/Risks.md`.
```

---

## M6: Spark adapter (done)

```
You are Codex. Implement M6: Spark adapter.

Goal
- Provide UDF wrapper returning JSON for Spark/Databricks pipelines.

Scope
- Add `schemalution-spark` with helpers around core migrations.

Constraints
- Keep adapter thin and optional.

Deliverables
- Spark helper(s) + docs + tests for JSON transform shape.

Success criteria
- Upcasting works from JSON -> JSON in a UDF-style helper.

Verify/review
- Unit tests for JSON input/output; no Spark cluster required.

Risk loop
- During the work, log risks and mitigations in `docs/Risks.md`.
```

---

## M7: Compose utilities (done)

```
You are Codex. Implement M7: Compose utilities.

Goal
- Provide fragment composition utilities for multi-domain projections.

Scope
- Add fragment structures, merge strategies, and compose_root helpers.

Constraints
- Deterministic, pure functions.

Deliverables
- `schemalution-compose` package + tests + docs examples.

Success criteria
- Composed view created deterministically from fragments.

Verify/review
- Tests for merge strategies and composition output.

Risk loop
- During the work, log risks and mitigations in `docs/Risks.md`.
```

---

## M8.A: Public API freeze and guardrails (done)

```
You are Codex. Implement M8.A: Public API freeze and guardrails.

Goal
- Declare stable public API surface and add guardrails against accidental breakage.

Scope
- Define public modules, add `__all__`, document public functions and versions.

Constraints
- Avoid breaking changes; add deprecations if needed.

Deliverables
- Documented public API and guardrail tests or checks.

Success criteria
- Public API surface is explicit and versioned.

Verify/review
- Tests or checks to prevent accidental API changes.

Risk loop
- During the work, log risks and mitigations in `docs/Risks.md`.
```

---

## M9: Registry export + CLI JSON I/O

```
You are Codex. Implement M9: Registry export + CLI JSON I/O.

Goal
- Make schemalution usable by any tool/agent via CLI JSON.

Scope
- Add `schemalution registry export` (JSON + optional DOT).
- Add `schemalution upcast` and `schemalution validate` that read stdin JSON and emit stdout JSON.
- Add a stable, versioned output schema (`--format v1`).

Constraints
- Do not break existing CLI behavior (if any).
- Keep outputs deterministic and machine-readable.

Deliverables
- CLI commands, output schema docs, and registry export format.

Success criteria
- Non-Python tools can upcast/validate without importing schemalution.
- Registry export is consumed by at least one downstream example.

Verify/review
- Golden-output CLI tests.
- JSON schema tests for `--format v1` outputs.
- Docs with examples.

Risk loop
- During the work, log risks and mitigations in `docs/Risks.md`.

Ask
- Provide a brief plan before coding. Ask only if blocked.
```

---

## M10: MCP server package (schemalution-mcp)

```
You are Codex. Implement M10: MCP server package.

Goal
- Provide a first-class MCP bridge for AI tools.

Scope
- Create `schemalution-mcp` with tools: list_schema_ids, get_latest_version, get_migrations, upcast_record, validate_record, diff_versions, simulate_upcast.
- Add config/auth hooks and structured logging.

Constraints
- Deterministic tool execution; no hidden I/O.

Deliverables
- MCP server package, tool specs, and minimal documentation.

Success criteria
- An MCP client can complete end-to-end upcast + diff flows using only tool calls.

Verify/review
- Integration tests with a mock MCP client.
- Determinism checks.
- Config/security review.

Risk loop
- During the work, log risks and mitigations in `docs/Risks.md`.

Ask
- Provide a brief plan before coding.
```

---

## M11: Contract export (JSON Schema / OpenAPI)

```
You are Codex. Implement M11: Contract export.

Goal
- Export latest-shape contracts for clients/docs/AI.

Scope
- Pack-level JSON Schema export.
- Optional OpenAPI components for latest-only models.
- Versioned artifact publishing + schema_id mapping.

Constraints
- Keep core dependency-light; add optional extras only where needed.

Deliverables
- Export functions/CLI, schema_id mapping, docs.

Success criteria
- Exported schemas validate latest fixtures correctly.

Verify/review
- JSON Schema validation tests.
- Artifact snapshot tests.
- Docs updates.

Risk loop
- During the work, log risks and mitigations in `docs/Risks.md`.

Ask
- Provide a brief plan before coding.
```

---

## M12: Migration intelligence (AI-assistable)

```
You are Codex. Implement M12: Migration intelligence.

Goal
- Reduce migration authoring cost with schema diff + stub generation.

Scope
- Schema diffing engine with rename/move/cast/default/coalesce heuristics.
- Generate migration stubs using the ops DSL.
- Emit actionable "unhandled diff" reports.

Constraints
- Do not guess when the diff is ambiguous; surface as review required.

Deliverables
- Diff engine + stub generator + report output.

Success criteria
- Common changes can be scaffolded automatically with minimal edits.

Verify/review
- Unit tests for each heuristic.
- Fixture-based tests for generated migrations.
- Reviewer checklist for false positives.

Risk loop
- During the work, log risks and mitigations in `docs/Risks.md`.

Ask
- Provide a brief plan before coding.
```

---

## M13: Breaking-change analyzer

```
You are Codex. Implement M13: Breaking-change analyzer.

Goal
- Detect consumer-breaking changes early and enforce policy in CI.

Scope
- Rules: removals, required-field additions, type narrowing.
- Risk scoring with actionable hints.
- CI enforcement with allowlist and explicit overrides.

Constraints
- False negatives are worse than false positives; be conservative.

Deliverables
- Analyzer + CLI/CI integration + docs.

Success criteria
- Breaking changes are flagged before release; overrides are explicit.

Verify/review
- Unit tests for each rule.
- CI integration tests.
- Docs for policy configuration.

Risk loop
- During the work, log risks and mitigations in `docs/Risks.md`.

Ask
- Provide a brief plan before coding.
```

---

## M14: Fixture and test automation

```
You are Codex. Implement M14: Fixture and test automation.

Goal
- Make migration correctness cheap to verify in every pack.

Scope
- Golden fixture generator (before/after) from sample records.
- Migration replay test harness (table-driven).
- Pack-level test scaffolding templates.

Constraints
- Keep fixtures deterministic and diff-friendly.

Deliverables
- CLI/tooling for fixture generation + template files.

Success criteria
- New migrations can be tested in minutes with minimal boilerplate.

Verify/review
- Template snapshot tests.
- Sample pack using scaffolds.
- Docs with instructions.

Risk loop
- During the work, log risks and mitigations in `docs/Risks.md`.

Ask
- Provide a brief plan before coding.
```

---

## M15: Backfill simulation tooling

```
You are Codex. Implement M15: Backfill simulation tooling.

Goal
- De-risk production rollouts by simulating real data upgrades.

Scope
- Sample dataset runner with error/warning stats.
- Report unknown fields, missing paths, invalid types.
- Export CSV/JSON summaries.

Constraints
- No production data required; support sampled JSON input.

Deliverables
- CLI or library runner + report formats + docs.

Success criteria
- Teams can run a dry run and make rollout decisions from the report.

Verify/review
- Fixture-driven simulation tests.
- Output schema tests.
- Example report in docs.

Risk loop
- During the work, log risks and mitigations in `docs/Risks.md`.

Ask
- Provide a brief plan before coding.
```

---

## M16: Schema linting + policy checks

```
You are Codex. Implement M16: Schema linting + policy checks.

Goal
- Enforce hygiene and determinism across packs and core.

Scope
- Envelope validation, monotonic versioning checks, migration path completeness.
- Determinism guard (no I/O or nondeterministic calls).

Constraints
- Lint must be fast and CI-friendly.

Deliverables
- Lint rules + CLI + docs.

Success criteria
- CI catches schema hygiene issues before merge.

Verify/review
- Unit tests for each lint rule.
- CLI exit-code tests.
- Docs for rule configuration.

Risk loop
- During the work, log risks and mitigations in `docs/Risks.md`.

Ask
- Provide a brief plan before coding.
```

---

## M17: Pack metadata for AI reasoning

```
You are Codex. Implement M17: Pack metadata for AI reasoning.

Goal
- Add machine-readable intent and lineage to support AI tooling.

Scope
- Migration intent annotations (rename/move/cast/default/split/merge).
- Field lineage map (old -> new) with notes.
- Semantic version hints (breaking/deprecated/removed_in).

Constraints
- Metadata must be optional and non-breaking.

Deliverables
- Metadata schema + serialization + docs.

Success criteria
- Metadata is exported and consumed by at least one tool (CLI/MCP/contract export).

Verify/review
- Serialization tests.
- Metadata schema tests.
- Examples in docs.

Risk loop
- During the work, log risks and mitigations in `docs/Risks.md`.

Ask
- Provide a brief plan before coding.
```

---

## M18: Agent workflow blueprints

```
You are Codex. Implement M18: Agent workflow blueprints.

Goal
- Provide repeatable AI-assisted workflows for common schema tasks.

Scope
- Workflows for add field, deprecate field, split/merge field.
- Each workflow includes inputs, outputs, steps, and human review checkpoints.

Constraints
- Workflows must be deterministic and auditable.

Deliverables
- Workflow docs + templates + example runs on sample packs.

Success criteria
- An agent can follow a workflow end-to-end with clear review steps.

Verify/review
- Example runs and checklists for each workflow.
- Docs review for clarity and completeness.

Risk loop
- During the work, log risks and mitigations in `docs/Risks.md`.

Ask
- Provide a brief plan before coding.
```

---

## M19: Auditability + replay logs

```
You are Codex. Implement M19: Auditability + replay logs.

Goal
- Preserve traceability for schema interpretation across time/environments.

Scope
- Standardized run metadata (versions, warnings, unknowns).
- Optional append-only audit log sink.
- Deterministic replay tooling.

Constraints
- Logging must be opt-in and privacy-aware.

Deliverables
- Log schema + sink interface + replay tool + docs.

Success criteria
- A recorded run can be replayed to reproduce outputs exactly.

Verify/review
- Replay tests with fixed inputs.
- Log format schema tests.
- Security review for log sinks.

Risk loop
- During the work, log risks and mitigations in `docs/Risks.md`.

Ask
- Provide a brief plan before coding.
```

---

## Review prompt (post-implementation)

```
You are Codex. Review the most recent milestone implementation.

Goal
- Identify defects, regressions, missing tests, or spec gaps.
- Update `docs/Risks.md` with any new risks and mitigation ideas that surfaced.
- Suggest concrete implementation measures or follow-up fixes if needed.

Scope
- Review only the files changed in the last implementation unless you find cross-cutting risks.
- Do not refactor unless a fix is required to resolve a defect.

Review focus
- Correctness and determinism of migrations and tooling.
- API stability and backward compatibility risks.
- Test coverage and verification gaps.
- CLI/MCP/contract export correctness and format stability.
- Security and data safety concerns (inputs, logging, config).

Output
- Findings ordered by severity, with file references and brief rationale.
- Explicit note if no issues were found, plus residual risks or test gaps.
- Summary of any `docs/Risks.md` updates.

Risk loop
- If any new risks are discovered, add them to `docs/Risks.md` with mitigation notes.

Ask
- If any ambiguity affects the review, ask one clarification question.
```
