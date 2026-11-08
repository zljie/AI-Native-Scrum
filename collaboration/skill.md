---
name: agent-collaboration
description: Coordinate project-aware professional agents for UI, API, bug, database or operations changes using bounded activation, verified runtime receipts, explicit handoffs and evidence; keep simple work single-agent.
---
# General professional collaboration (candidate, not a V1.4 release)

Read AGENTS.md and docs/agent-collaboration.md. Reuse the current Goal/Story/Task,
project rules, Skills, evidence tools and authorized scope. Do not create competing
business truth. First inspect actual code and constraints; map observed impacts to
capability tags with source references. The policy does NOT infer impacts from raw
user text by itself. Create the small TaskContext and reuse confirmed authorization.
Do not re-ask for approval at every professional handoff within that scope.

For V1.5 evidence-bound activation, read `docs/v1.5-collaboration.md` and first
build a `project-context-pack/v1` from actual project files with
`.ai/tools/project_context.py`. Only then use `.ai/tools/v15_activation.py`
and `.ai/tools/v15_controller.py plan` to verify signal evidence and select
necessary professional capabilities. A database file is not proof that a
schema change is needed. Do not bypass these checks by inventing signals.

Use `.ai/tools/agent_collaboration.py` to plan, inspect ready assignments, and
explicitly drive the available execution adapter. The five base roles use the same
protocol; database_agent is a separate optional expert, not embedded in Developer.
Read .ai/skills/product-director/SKILL.md or experience-director for relevant product
choices; tdd-director before implementation and review-director before acceptance.
The selected role must actually use the relevant method; file discovery is not proof.

Single-agent copy edits record skips. Real behavior changes require the existing
RED/GREEN evidence binding. Only execution-side receipts can count as started.
A plan, cat SKILL.md, role prose or fixture JSON is not native participation.
The current adapter uses independent Codex app-server threads (runtime_session),
NOT parent spawn_agent child threads. Missing runtime/auth => blocked; never silently
switch to role simulation. Fixture mode is for tests only and cannot pass release.

A completed producer only unlocks consumers after directed handoff review accepts
its current artifacts. Reject missing constraints; retain failures and revisions.
Request professional assistance through the coordinator; never spawn recursively.
On a contract change invalidate affected dependents and replan under the approved
change process. Architecture performs pre-impact and post-verification reconciliation
when applicable. Suggestions for larger redesign become ADR proposals, not scope creep.

Show stage, role, actual runtime mode, blockers and next actions. Run check and
produce a trace report. Report engineering checks, live integration, production
execution and human acceptance separately. Do not mark/release V1.4 before AT-001
and all other release gates are supported by real evidence.
