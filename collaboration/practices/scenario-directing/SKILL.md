---
name: scenario-directing
description: Design observable user scenarios before implementation and verify their realized behavior after independent technical checks. Use for the ANS director_agent on evidenced user-flow or business-rule changes, including failure recovery and rework.
---
# Scenario directing baseline

Read `.ai/skills/professional-baseline/SKILL.md`, the current Goal, product rules and accepted upstream artifacts. Reuse `.ai/skills/product-director/SKILL.md` for scenario reasoning and `.ai/skills/review-director/SKILL.md` for the final purpose review. Follow the assigned Sprint scenario schema when present; do not invent another acceptance registry.

## Before development

Identify the actor, their situation, trigger, useful outcome and what they must decide. Walk the actual user task from entry to completion, identifying what the person sees, does, receives and can recover. Tie each required scenario to existing Story/AC references.

Cover the main path and relevant alternatives: absent data, invalid input, denied permission, delayed/failed service, duplicate action, interrupted work and recovery. Select cases from the real change; do not require unrelated branches. Separate product decisions from implementation guesses. Unknown business behavior goes to Product/Lead; do not select a framework, schema or policy on their behalf.

For each scenario, give preconditions, inputs/actions, expected visible result, important state changes and observable evidence needed. Identify which checks need the actual product, account, data or device. Pass the same versioned scenario contract to Product, Architecture, UI/UX and Test as applicable.

## After implementation

Read the accepted design and current independent technical evidence. Exercise the actual authorized product path using available tools and permitted data. Record environment/revision, inputs/actions, expected versus observed outcome and evidence references. Green unit tests, source inspection, mockups and screenshots of another version do not prove a user journey works.

Keep every required scenario in the returned inventory, including FAIL and NOT_RUN. If access, login, product or tool is missing, specify what could not be exercised. Do not label fixture observations or a different host as this project's acceptance.

For a failure, identify the affected scenario/AC, reproducible steps, observed behavior, responsible design or implementation task and the required recheck. Hand it to Lead; do not fix code, weaken the scenario or bypass independent Test. Reverify the affected current version after correction and retain the previous failed evidence.

## Return

Return a versioned scenario contract during design or a per-scenario PASS/FAIL/NOT_RUN report during verification, plus decisions/gaps and receiving-role references. Use actual packet identities and dependency hashes when the existing schema requires them. Report completion means the artifact was returned; it does not grant business acceptance or release.
