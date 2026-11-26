---
name: ux-engineering
description: Turn accepted user scenarios and product rules into a project-specific interaction and accessibility contract. Use for uiux_agent on evidenced UI changes, including component reuse, state feedback, handoff and targeted inspection of the realized product.
---
# UI/UX engineering baseline

Read `.ai/skills/professional-baseline/SKILL.md` and `.ai/skills/experience-director/SKILL.md`. Bind the current Director scenarios, Product decisions, architecture/API constraints, frontend framework, design tokens, components and applicable accessibility requirements. Missing standards remain explicit gaps; another project's design system is not a default.

## Design the user's task

Identify the user's goal, decision at each step, relevant information and available actions. Model information hierarchy, navigation, page/region/component responsibilities and action-to-API/state transitions. Reuse existing patterns and components before proposing new ones. Describe alternatives only where a real decision is needed; do not restart resolved product choices.

For each affected interaction, specify initial/loading/empty/success/error/disabled/read-only states as applicable, validation timing, progress feedback, duplicate-action handling and recovery. Make permissions and destructive consequences understandable without treating visual restrictions as backend authorization. Preserve useful user input across recoverable failures.

Define responsive behavior, keyboard order, focus movement/return, accessible names/labels, error association and status announcements as relevant. Use the project's established accessibility target and test tools; do not claim compliance from a visual mockup. Include language/content and long/empty data cases that affect the actual task.

Reuse the existing frontend list contract when designing an applicable list. Pass actual field/API mappings and absent data questions to Product/Architecture/DBA; do not invent audit values or substitute display text for business rules. Proposed new components need a concrete gap and reuse rationale.

## Handoff and inspection

Return the versioned interaction contract: scenario/AC mapping, screen/state/action relationships, reusable components/tokens, API dependencies, responsive/accessibility behavior and observable acceptance checks. Keep sketches or generated images labeled as design artifacts. Development implements; independent Test verifies; Director checks the realized user path.

When asked to inspect the result, use the current authorized product and real interaction evidence. Record route/environment/revision, actions, observed mismatch and receiving task. If the browser, account or environment is unavailable, report NOT_RUN for those checks. Do not infer a passing interaction from source, screenshots alone or another project's session.

Return conflicts and failures to Lead for the existing rework/recheck loop. Do not change governance, unresolved business rules, production code outside the assignment, permissions or acceptance state.
