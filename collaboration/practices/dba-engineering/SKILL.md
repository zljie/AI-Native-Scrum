---
name: dba-engineering
description: Apply DBA practices for evidenced schema and persistence work, including audit columns, transactional IDs, master-data ID issuance and seed/allocator integrity.
---
# DBA engineering practice

Read `.ai/skills/professional-baseline/SKILL.md` before this specialty. Keep project decisions, source versions and verification gaps in the existing assignment and handoff; the method does not authorize a schema migration or production access.

The existing database_agent is the independent DBA specialist. Apply only to evidenced data-model, persistence or migration impact. Read actual project DB dialect/version, schema/migrations, SDD/API conventions, data dictionary, access scope and business rules. Bind sources and versions; no live access means NOT_INSPECTED.

## Table design baseline
Classify each affected persisted table: master/reference, transactional/business flow, relation/detail, append-only history/audit or infrastructure/allocator. Document purpose, grain, PK, business key, uniqueness, FK/integrity constraints, null/default semantics, lifecycle and access pattern.

The owner's baseline is four semantic audit fields on every persisted application table, including master, transactional, relation and seed tables: created_by, created_at, updated_by, updated_at (illustrative names; bind project names/types). Derive actors from trusted server/service identity, not spoofable client input; creation values remain immutable, update fields advance atomically on actual modification. Set initial update values consistently with creation. Append-only tables retain initial values and prohibit ordinary updates. Record timezone, precision, service actor and historical backfill semantics. Never fabricate missing historical actors/timestamps. Legacy/external/engine-managed exceptions require documented review; no silent omission or destructive blanket retrofit.

## ID and seed strategies
- Transactional/business-flow tables: prefer database identity/sequence/auto-increment or approved equivalent; enforce uniqueness at storage. Increasing allocation is not gapless IDs or commit-order chronology. Never use MAX(id)+1 or row count. Legally gapless business numbering is a separate requirement, not the technical PK.
- Master data: reuse the approved central ID issuance service/allocator; keep technical PK distinct from mutable business code/display sequence. Namespace, identifier format, initial value, step, bounds and tenant boundaries are project decisions. Do not create a second issuer when one exists.
- Seed/allocator table: when master-data issuance needs a DB-backed allocator, propose unique namespace (and tenant only if required), next_value or high-water mark (choose explicitly), step/segment size if applicable, bounds/version and the four audit fields. Initialize namespace records through controlled, repeatable migrations; reruns must not reset a counter to a lower value. Use dialect-appropriate atomic update/locking/sequence, uniqueness, overflow checks and documented transactional/retry/idempotency semantics. Never expose an uncommitted allocation as a permanent ID, reuse an externally issued ID, or issue via non-atomic read-then-write. Range allocation needs crash/retry policy. Business reference-data seeding is separate: deterministic business keys and idempotent inserts/upserts with ownership and upgrade semantics.

## Migration and quality
Coordinate design with architecture and developer; deliver versioned DDL/migration, compatibility, backfill, rollback or forward recovery, reconciliation, indexing and query assumptions. Preserve data and migration ordering; prefer expand/migrate/contract when needed. No undocumented destructive changes. Do not change production, credentials, business semantics or grant access. Propose a no-schema-change alternative where evidence supports it.

Independent Test receives cases for four audit fields and actor/time behavior, stable master IDs, unique transaction IDs, concurrent allocation and namespace isolation where applicable, allocator initialization/rerun, failure/retry/rollback/overflow, migration compatibility and data preservation. Use actual dialect and authorized isolated environment; SQLite-only or fixture results cannot prove another DB's concurrency. Return commands/results, migration revision, affected tables, mapping, risks and NOT_RUN/NOT_INSPECTED; no self-acceptance.

## Project initialization decisions
Confirm column names/types/defaults, actor/timezone convention, table classification, ID strategy, master ID issuer ownership, seed table name/schema/namespace/initial value/step/format/ranges/tenant rules, reference-data seeding, dialect/migration tool, exception policy and tests. Four audit semantics, increasing flow IDs, master-data issuance and a seed table are user requirements. Exact generator/naming/allocation details remain proposed until confirmed. Apply to new designs; do not silently change legacy IDs or schemas.
