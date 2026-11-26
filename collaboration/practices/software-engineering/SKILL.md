---
name: software-engineering
description: Implement or debug a bounded ANS development assignment against actual project APIs, SDD, tests and runtime constraints. Use as developer_agent's baseline for backend, frontend or integration work, adding frontend/DBA specialist methods only when their impact applies.
---
# Software engineering baseline

Read `.ai/skills/professional-baseline/SKILL.md` and `.ai/skills/delivery-loop/SKILL.md`. Inspect the relevant implementation, callers, tests, approved design/API/SDD and received RED evidence. Reuse actual project conventions, libraries and error handling; do not impose a preferred language, framework or architecture.

## Establish a verifiable slice

Map each authorized behavior to its implementation boundary and existing acceptance/test reference. Identify compatibility requirements and affected callers. Prefer a small cohesive change using current assets. For frontend impact, also read `.ai/skills/frontend-engineering/SKILL.md` and the applicable list contract. For database impact, consume the independent DBA handoff; do not silently replace it with developer self-review.

Respect the project's required test-first gate. A valid RED demonstrates the intended behavioral failure, not a missing dependency, syntax error or broken environment. Preserve the accepted tests and command through GREEN; return an invalid test prerequisite to Test/Lead rather than weakening it. Do not delete existing working implementation to manufacture a new RED cycle.

## Implement the actual contract

For API/backend work, inspect input validation, authentication and object/tenant authorization, business invariants, transaction boundaries, retries/idempotency, timeouts/cancellation and compatible error semantics as applicable. Reuse existing conventions for pagination, serialization, observability and dependency boundaries. UI hiding is not server-side authorization. Do not add distributed infrastructure or speculative abstraction without a demonstrated requirement.

For a failure, reproduce it and read the actual trace before changing code. Trace inputs across the relevant boundary, compare a working path, state a focused hypothesis and make a discriminating check. Change one cause at a time; after repeated unsuccessful hypotheses, return the evidence and design question to Lead instead of accumulating patches. Do not invent a successful reproduction.

Preserve data, external contracts and unrelated changes. Keep new dependencies and configuration changes explicit and within authorization. Avoid logging secrets or sensitive request bodies. A backend's correctness, migration safety or performance claim needs the corresponding environment and measurement, not a similar fixture.

## Verify and hand back

Run the agreed GREEN command, then the relevant contract/integration/regression checks required by the change or project gate. Inspect their full result; a successful process exit with no relevant cases is not coverage. Use the existing evidence recorder to bind code/tests/commands when required. Record unavailable checks as NOT_RUN with the environment/tool gap.

Return changed paths, behavior-to-contract mapping, reused assets, actual commands/results, current source/test revisions, remaining risks and the independent receiving reviewer. Do not accept your own implementation, alter approved test expectations to pass, declare production deployment or close the user's goal. Rework uses the existing task/attempt history and independent recheck.
