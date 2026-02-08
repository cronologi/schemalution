# Risks

- [M9] Pack discovery depends on explicit `--pack`/`SCHEMALUTION_PACKS` lists; missing packs can yield false errors.
  Mitigation: clear CLI error messages and README guidance; consider discovery hooks later.
  Status: resolved.
- [M9] CLI `validate` runs actual migrations, so failures in migration logic surface as validation errors.
  Mitigation: keep migrations pure/deterministic; document that validate is a dry-run upcast.
  Status: resolved.
- [M9] Registry export output could be non-deterministic without sorting.
  Mitigation: sort schema IDs and migration edges before emitting JSON.
  Status: resolved.
- [M9] Registry export migration edge ordering currently depends on pack registration order.
  Mitigation: sort edges by schema_id and from_version before emitting JSON/DOT.
  Status: resolved.
- [M9] CLI `validate` only verifies upcastability, not semantic/contract validity.
  Mitigation: document scope clearly; extend to contract checks in M11 if available.
  Status: resolved.
- [M9] Open question: should `validate` gain a `--strict` mode (warnings become failures)?
  Mitigation: keep current behavior for M9; revisit in M10/M11 with contract validation scope.
  Status: open.
