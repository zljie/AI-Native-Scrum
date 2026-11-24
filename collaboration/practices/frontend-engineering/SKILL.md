---
name: frontend-engineering
description: Apply reusable frontend engineering methods inside the Developer Agent for evidenced UI changes; preserve the project's approved stack, design system, interaction contract and quality evidence.
---
# Frontend engineering practice

Apply only for frontend or interaction work; for unrelated tasks report NOT_APPLICABLE. Read actual project frontend standards, UI/UX handoff, API/SDD, component inventory, tokens, routes and tests. Bind current source paths and versions. Unknown or conflicting standards are gaps for Lead, not permission to invent them.

## Model before implementation
Translate the accepted user scenario into Page → Layout → Region → Component → Action → API → State/Feedback. Select the project-supported list, detail, form, workflow, dashboard, workspace or configuration pattern based on actor, goal, domain data and permissions. Separate action intent from triggers (button, shortcut, menu); map input, validation, permission, API, state change and feedback. Reuse the project's DSL when present; a lightweight mapping is sufficient otherwise. Do not create a competing DSL.

## Reuse before creation
Inspect feature code, shared components, patterns, icons and the approved resource registry first. Prefer reuse, composition, variants/slots/adapters before new primitives. For a compatible React/TypeScript/shadcn project, official shadcn/ui, approved free ReUI/Kibo UI and approved icon sets such as Lucide are possible candidates, not globally approved dependencies. Other stacks keep their own component ecosystem. Do not introduce or upgrade frameworks merely for a task.

Verify original source, license, version, maintenance, stack fit, dependencies and accessibility for each external resource. No paid/preview-only or unclear-license copy. Record source URL, version, license, adaptation and dependency/lockfile diff. Before creating an unreusable component/icon record COMPONENT_GAP or ICON_GAP, what was searched, rejected alternatives and the reuse plan. Do not invent approvals or silently overwrite customized components.

## Design and behavior
Use project design tokens for semantic color, typography, spacing, radius, theme and responsiveness. No ad-hoc visual language, arbitrary hard-coded values or emoji as product icons. Use an approved semantic icon family, accessible names, keyboard/focus and responsive behavior. Implement relevant loading/empty/success/error/disabled/readonly states and recovery. Handle permission denial, validation, duplicate submission and API failure as applicable; never fabricate real data or authorization.

For applicable lists, reuse .agents/skills/frontend-list-contract/SKILL.md and schema/ui/list-page.json: search above table, pagination below, final headers 创建人 / 最后更新时间 / 操作. Map to actual API semantics; missing audit data is a blocker/decision. Register routes and tests using the existing contract. Follow the existing browser evidence procedure; no new checker or relaxed rule. If local rules conflict, obtain a recorded Lead decision; do not silently override.

## Deliver and verify
Follow approved RED/GREEN and test handoff. Run authorized type check, lint, targeted component/interaction tests, browser flows and visual/keyboard checks as applicable. Record exact commands, exit codes, source/test revision, observations or NOT_RUN with reasons. For lists use existing UI contract snapshot/verify with actual browser reports. Screenshots/mockups and self-review are not independent acceptance.

Return changed paths, pattern/action mapping, reused components, gap/provenance records, state/permission/API mapping, evidence and risks. Do not weaken tests, self-approve or modify other roles' records. Propose reusable lessons after verification through existing LRN/ADR; do not rewrite the global Skill from one project without review.
