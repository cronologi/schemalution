# Coding standards

This document defines coding standards for schemalution. It is the default reference for all project work.

## Guiding principles
- Deterministic and pure: migrations are pure functions (dict -> dict), no I/O.
- Small and stable API surface: keep public APIs explicit and minimal.
- Dependency-light core: avoid heavyweight dependencies in `schemalution-core`.
- Readability over cleverness: favor clear, testable code.
- Backward compatibility by default: avoid breaking changes unless explicitly planned.
- Open-source mindset: write for public consumption, document decisions, and avoid private or proprietary assumptions.

## Language and tooling
- Python >= 3.10.
- Ruff for linting and formatting.
- Pyright for static typing.
- Pytest for tests.
- `src/` layout for all packages.

## Project structure
- Each package lives under `packages/<name>/src/<package_name>`.
- Public API exports live in package `__init__.py` with explicit `__all__`.
- Keep adapters thin and focused on boundaries (Mongo, Spark, MCP, CLI).

## Code style
- Keep functions small and focused.
- Use clear names; avoid abbreviations unless widely understood.
- Prefer `TypedDict`, `dataclass`, or pydantic models in packs; avoid in core.
- Avoid global state except for stable constants.
- Use consistent error types and messages (see Error handling).

## Typing
- All public functions must have type annotations.
- Internal functions should be typed unless trivial.
- Prefer `Mapping[str, Any]` for inputs and `dict[str, Any]` for outputs.
- Avoid `Any` in public APIs unless unavoidable.

## Error handling
- Raise clear, specific exceptions for unsupported versions, missing paths, or invalid schema IDs.
- Error messages should include schema_id, from_version, to_version, and migration path when applicable.
- Avoid swallowing exceptions; re-raise with context.

## Determinism and purity
- Migrations must not read the filesystem, environment, network, or time.
- No randomness or non-deterministic behaviors inside migrations.
- Side effects are allowed only at boundaries (CLI, adapters), never in core logic.

## Testing
- Every new feature includes tests.
- Prefer table-driven tests with before/after fixtures for migrations.
- Tests should cover: happy paths, edge cases, and error conditions.
- Keep fixtures small and readable; use JSON files when clarity improves.

## Documentation
- Update README or docs when public behavior changes.
- Include minimal usage examples for new APIs.
- Prefer short, focused sections over long prose.

## CLI and MCP standards
- CLI outputs must be machine-readable and versioned when JSON.
- CLI commands must be deterministic given identical inputs.
- MCP tools must be deterministic and side-effect free unless explicitly documented.
- Log structured metadata; avoid leaking sensitive data.

## Security and safety
- Treat inputs as untrusted; validate before processing.
- Avoid executing arbitrary code or dynamic imports based on user input.
- Log minimal data needed for diagnosis.

## Review expectations
- Prefer incremental, focused changes.
- No unrelated refactors in milestone PRs.
- Keep public API compatibility unless explicitly noted.
- Add tests for new functionality and bug fixes.

## Risk loop
- During any milestone work, document risks and mitigations in `docs/Risks.md`.
