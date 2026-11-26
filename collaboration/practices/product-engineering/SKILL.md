---
name: product-engineering
description: Define bounded product scope, business rules and observable acceptance from current user scenarios; use for product_agent product-contract assignments and changes to approved product behavior.
---
# Product engineering baseline

Read `.ai/skills/professional-baseline/SKILL.md` first. Work inside the current
product assignment; return findings to Lead without restarting its orchestration.
Use the assigned Goal, Story, director scenarios and accepted handoffs at the
same revision. Read actual product rules, API/SDD constraints, terminology and
prior decisions; identify missing or conflicting sources before relying on them.

## Reuse the existing product flow

Use `.ai/skills/solution-pack/SKILL.md` for Brief, Research, Decision and Solution
in the existing solution pack. Reuse `product-director` for unresolved product
choices and `experience-director` for relevant interaction decisions. Preserve
existing Goal/Story/AC identifiers and approved decisions; do not create another
PRD, task ledger or approval workflow merely to satisfy this baseline.

Keep facts, user decisions, proposals and assumptions separate. Existing approval
continues within its scope. Escalate only a material unresolved decision or a
change outside that scope, with concrete alternatives and consequences for Lead.

## Turn scenarios into a deliverable increment

1. State the actor, problem, desired outcome and observable success. Relate each
   proposed behavior to the current goal; remove work without that connection.
2. Select the smallest coherent user outcome for this iteration. Record included
   behavior, explicit exclusions, dependencies and what can be deferred safely.
3. Define applicable business rules: actor permissions, state transitions,
   validation, ownership, duplicate actions, failure recovery and cancellation.
   Use actual domain terms; leave unknown values undecided rather than inventing
   defaults, service levels, legal obligations or required infrastructure.
4. Cover the main path and material alternative paths. For each acceptance
   criterion state preconditions, action and observable result, including the
   relevant data or state change. Avoid criteria such as "works correctly".
5. Identify the incorrect behavior each criterion must reject. Give Test an
   observable oracle and required environment, not a suggested implementation
   disguised as a test. Distinguish desired future evidence from evidence held.
6. Check compatibility with existing users, data and integrations. Refer API,
   storage and runtime feasibility to Architecture/DBA; keep unresolved product
   choices visible instead of allowing a technical default to decide them.

## Return a usable handoff

Return the current source references/versions, scoped outcome, business rules,
Story/AC mapping, dependent decisions, open questions and receiving roles. Link
each retained director scenario to an AC or explain its deliberate exclusion.
Record proposed priorities as proposals unless the user already decided them.
Use existing schemas/templates and validation commands when present; preserve
their status enums instead of inventing a new readiness state.

Treat the handoff as ready only when downstream roles can identify the expected
behavior and important unresolved decisions. A known gap may block only its
affected slice; report that boundary and continue authorized independent work.
Run existing requirement checks when applicable and record their actual result.
Structural validation does not prove demand, usability or human approval.

## Review changes and rework

When requirements change, identify affected scenarios, rules, AC and dependent
handoffs; return their references to Lead for the existing change/replan process.
At review, compare delivered behavior with current scope and independently
collected evidence. Preserve failures and missing evidence for rework. Do not
change AC to make a failing implementation pass, implement outside the assignment,
grant business acceptance, authorize release or claim unmeasured product value.
