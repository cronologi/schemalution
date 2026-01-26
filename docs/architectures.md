# schemalution Deployment Architectures

schemalution is a **schema evolution engine**, not a database library.

Its purpose is to deterministically evolve records across schema versions and enable stable “latest” contracts—without prescribing *where* that evolution must happen.

This allows schemalution to be deployed at different architectural boundaries depending on organizational needs, scale, and governance requirements.

This document describes the **four recommended deployment architectures** and when to use each.

---

## Core Principles (applies to all architectures)

Regardless of deployment style:

- schemalution performs **pure, deterministic transformations** (dict → dict).
- Schema evolution logic lives in **schema packs**, not in application code.
- Systems always operate on a **single canonical “latest” schema** internally.
- Older stored versions are handled via **upcast-to-latest**, not branching logic.
- Contracts (e.g. Pydantic models) are **separate from migrations**.

schemalution can be placed wherever that boundary makes sense.

---

## Architecture A: Embedded Schema-on-Read (Library Mode)

Each consumer that reads from the database applies schema evolution locally.

MongoDB → schemalution-core → latest dict → domain contract → service logic


schemalution is used as a **library dependency** inside services.

### Key Decision Point
You want teams to move fast with minimal infrastructure, and you can tolerate schema evolution at read time.

### Watch-outs
- Drift risk if some consumers forget to upcast
- Hot paths may pay the upcast cost repeatedly
- Multiple services must keep schema packs in sync

---

## Architecture B: Canonical Projection (Materialized View Mode)

Schema evolution is applied once, centrally, and written into a **canonical “latest” collection or table**.

Raw data (mixed versions)
↓
Projection job (schemalution)
↓
Canonical latest store
↓
Consumers (no schemalution dependency)

### Key Decision Point
You prefer centralized evolution so consumers can be simple and fast, even if the projection is eventually consistent.

### Watch-outs
- Projection failures can stall freshness
- Backfills and pipeline retries need clear ownership
- Consumers may over‑trust “latest” even if pipeline lags

---

## Architecture C: Schema Gateway (Contract Boundary Mode)

Schema evolution is centralized behind a **service boundary**.

MongoDB → Schema Gateway (schemalution)
↓
Latest contract API
↓
Consumers


Consumers never read the database directly.

### Key Decision Point
You want a strict contract boundary with governance and access control at the data edge.

### Watch-outs
- Gateway becomes a critical dependency and must scale
- Latency budgets must account for the extra hop
- Schema rules and auth policy can become tightly coupled

---

## Architecture D: Write-Latest + Backfill (Convergence Mode)

All writers enforce writing the **latest schema only**.
Older records are gradually migrated via background jobs until the database converges.

Writers → latest only
↓
Background backfill (schemalution)
↓
Fully latest store

### Key Decision Point
You want to converge to a fully “latest” store and reduce long‑term read complexity.

### Watch-outs
- Backfills can be operationally heavy and long‑running
- Mixed versions can linger if writers drift
- Requires discipline in writer services

---

## Architecture Comparison (repeated sections consolidated)

| Architecture | Where schemalution lives | When to use | Pros | Cons | Typical users |
|---|---|---|---|---|---|
| Embedded Schema-on-Read | Inside application code; typically via `schemalution-core` + schema packs; often with `schemalution-mongo` | Small to medium systems; few independent consumers; fast adoption with minimal infrastructure; services already share libs | Minimal moving parts; no extra services/pipelines; deterministic and testable; easy incremental adoption | Each consumer must adopt schemalution (or shared data lib); schema evolution runs at read time | APIs; background workers; internal tools |
| Canonical Projection | Projection service or ETL job; batch or streaming (e.g. Spark / Databricks); not in consumers | Many independent consumers; performance-sensitive reads; analytics/dashboards/context stores; want to remove schema logic from apps | Consumers don’t need schemalution; fast stable reads; strong contract consistency; scales across teams | Requires projection pipelines; eventual consistency unless synchronized; additional storage | Analytics platforms; read-heavy APIs; agentic AI systems consuming “context bundles” |
| Schema Gateway | Dedicated “schema gateway” or data access service | Large orgs; many teams/external consumers; strong governance/security/audit; centralized schema policy | Single place to enforce rules; consumers stay simple; easy auth/rate limits/observability; clear ownership | Extra service to operate; added network hop; potential bottleneck without scaling | Enterprise APIs; partner integrations; regulated environments |
| Write-Latest + Backfill | In writers and backfill jobs; eventually not needed on reads | Single writer or tightly controlled writers; simplify long-term reads; willing to run migration jobs | Simple steady-state reads; evolution cost amortized; clear long-term data shape | Backfills are operationally heavy; mixed versions temporarily; requires writer discipline | Operational systems with controlled write paths; teams planning long-term schema stabilization |

---

## Choosing the Right Architecture

| Situation | Recommended Architecture |
|---------|--------------------------|
| Few services, fast adoption | Embedded Schema-on-Read |
| Many consumers, read-heavy | Canonical Projection |
| Strong governance required | Schema Gateway |
| Controlled writers, long-term simplicity | Write-Latest + Backfill |

These architectures are **not mutually exclusive**.
Many organizations evolve from Embedded → Projection or Gateway over time.

schemalution supports all of them without changing core semantics.

---

schemalution does not force a single organizational model.

Instead, it provides:
- A **neutral evolution engine**
- Clear boundaries between **evolution, contracts, and storage**
- The freedom to place schema logic where it fits your architecture

This makes schemalution suitable for:
- Small teams
- Large enterprises
- Data platforms
- Agentic AI systems
- Regulated environments

---

schemalution is not “a Mongo library” or "a Spark library".

It is a **schema evolution primitive** that can be embedded, centralized, projected, or phased out—depending on your needs.
