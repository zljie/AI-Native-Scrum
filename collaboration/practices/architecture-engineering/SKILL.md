---
name: architecture-engineering
description: Inspect actual architecture and design compatible technical changes with traceable decisions and verification; use for architect_agent architecture review, reconciliation and assigned data-design work.
---
# Architecture engineering baseline

Read `.ai/skills/professional-baseline/SKILL.md` first. Bind the current Goal,
Story/AC, accepted product/director handoffs, architecture rules, API/SDD sources
and relevant ADRs to their actual versions. Work only on the assigned change.
Use `.ai/skills/story-to-tasks/SKILL.md` for existing task decomposition and
dependency checks; keep the current Goal/Task/Journal as the source of status.

## Reconstruct the affected system

Inspect the real entry points, callers, implementation, data ownership, tests,
build/runtime configuration and integration boundaries before proposing changes.
Describe relevant request/data flow with source references. Separate implemented
behavior, documented intent and inferred behavior; report inaccessible systems
as uninspected. Do not present a proposed endpoint or dependency as an existing one.

Trace the change across modules and contracts. Identify actual reuse candidates,
local extension points and project conventions. Include authorization boundaries,
transaction/concurrency behavior and observability where the change affects them;
do not require every task to undergo a complete enterprise architecture exercise.

## Design the smallest adequate change

1. Relate each design choice to an AC, constraint or evidenced failure. Prefer
   existing modules and interfaces before introducing another abstraction,
   service, framework, database or queue.
2. Compare realistic alternatives when a material decision exists. Explain
   compatibility, implementation/maintenance cost, operational consequences and
   a condition that would make the recommendation unsuitable. Mark estimates
   and assumptions; do not manufacture measurements or approval.
3. Specify applicable API semantics: inputs/outputs, validation, error mapping,
   authentication/authorization, pagination, retry/idempotency and versioning.
   Extend the project's actual contract format rather than creating a rival SDD.
4. Identify data and concurrency consequences: ownership, invariants, ordering,
   transaction boundaries, contention and partial failure. Hand schema/migration
   details to the assigned DBA when activated; retain interface responsibilities.
5. Define compatibility and recovery for affected callers/data/configuration.
   Provide a bounded migration path only where needed, with failure detection and
   rollback or forward recovery constraints. Preserve existing protected rules.
6. Map design claims to verification: contract tests, behavior tests, integration
   tests, targeted performance/concurrency checks or runtime observations as
   applicable. Specify the real environment required and unknown prerequisites.

## Hand off executable design

Return source references/versions, the affected module/interface map, proposed
contract changes, reused assets, decisions, dependencies and verification needs.
Attach the smallest useful diagram or table when it clarifies a boundary.
Use existing ADRs/solution decisions for durable choices. Follow their actual
approval rules; routine implementation within approved design needs no new gate.

Give Development and Test concrete inputs, intended outputs and acceptance
conditions. Split tasks at testable boundaries; ensure dependencies are acyclic
and shared write surfaces are explicit. Refer missing product decisions to Lead
with conditional options instead of silently resolving them through architecture.

## Reconcile the implemented system

For `architecture_reconcile`, inspect current code/configuration and accepted
test evidence against the design revision. Record intentional deviations,
remaining mismatches, compatibility findings and current architecture facts.
Route a defect to its responsible task with reproduction evidence and a recheck
condition. Update only authorized records; preserve superseded decisions.

Do not accept your own design as independent implementation verification. Missing
runtime access remains NOT_RUN for runtime claims; a diagram or green unit suite
does not prove production behavior. Do not change production, expand permissions,
merge, deploy or authorize business acceptance through an architecture opinion.
