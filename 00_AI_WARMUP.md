You are currently inside an **AI Native Software Engineering Knowledge Repository** that has already been initialized using `initdir.sh`.

Here, repository means the project/workflow root; Git is optional. A new empty
folder, existing non-Git project, Git repository, or non-Git coordination root
containing child repositories is supported. Do not require or create `.git`,
move this root into a child repository, initialize children recursively, or run
commit, push or deployment. Inspect child boundaries/rules without changing them.
Missing Git metadata is not a failure or warning by itself.

Preserve every existing nonempty file. If older files materially conflict with
the expected contracts, report NOT_READY and the minimal proposed repair; get
explicit approval before replacing them. Do not loop initialization indefinitely
or report READY merely to satisfy an instruction to continue until READY.

Do not create any Goal, Backlog, Story, Task, Sprint, product design, or implementation work yet.

Your first task is to:

# Perform a Repository Initialization Self-Check

Verify whether this repository is ready to support the complete knowledge flow:

**Goal Intake → Goal → Backlog → Story Refinement → Task Decomposition → Ready Pool**

---

# 1. Understand the Repository First

Start by reading:

- `AGENTS.md`
- `README.md`
- `WORKING_STYLE.md`
- `Goal_Constrained_Dev_Flow_v1.md`
- `dev-flow.yaml`

Then inspect the following files and directories.

## Governance

- `schema/README.md`
- `schema/entity-types.yaml`
- `schema/workitem-types.yaml`
- `schema/relation-types.yaml`
- `schema/policies.yaml`
- `schema/readiness.yaml`
- `schema/id-policy.yaml`
- `schema/intake.schema.yaml`
- `schema/memory-policy.md`

## Templates

- `schema/templates/goal.md`
- `schema/templates/story.md`
- `schema/templates/task.md`
- `schema/templates/adr.md`
- `schema/templates/learning.md`
- `WORKING_STYLE.md`

## Intake

- `intake/README.md`
- `intake/templates/`

## AI Skills

- `.ai/skills/README.md`
- `.ai/skills/goal-intake/SKILL.md`
- `.ai/skills/goal-to-backlog/SKILL.md`
- `.ai/skills/story-refine/SKILL.md`
- `.ai/skills/story-to-tasks/SKILL.md`
- `.ai/skills/ingest/SKILL.md`
- `.ai/skills/query/SKILL.md`
- `.ai/skills/lint/SKILL.md`
- `.ai/skills/delivery-loop/SKILL.md`

## Knowledge Layers

- `raw/README.md`
- `wiki/README.md`
- `wiki/index.md`
- `generated/README.md`
- `generated/backlog/index.md`
- `generated/ready/index.md`
- `site/README.md`

---

# 2. Confirm the Five Knowledge Boundaries

Verify that you understand and can enforce the following repository boundaries.

## 2.1 `intake/`

Meaning:

AI working area.

Characteristics:

- information has not yet received Human Approval;
- AI may organize, rewrite, summarize, and maintain it;
- information here must not be treated as approved project truth.

---

## 2.2 `raw/`

Meaning:

Approved Engineering Evidence.

Examples:

- approved Goals;
- Requirements;
- Meeting Records;
- Feedback;
- Source Materials.

Characteristics:

- this layer is authoritative evidence;
- AI must not silently rewrite approved meaning.

---

## 2.3 `wiki/`

Meaning:

Canonical Derived Knowledge.

Examples:

- Stories;
- Tasks;
- ADRs;
- Components;
- APIs;
- Releases;
- other durable AI-maintained engineering knowledge.

Canonical entities belong here.

---

## 2.4 `generated/`

Meaning:

Computed Views.

Examples:

- Backlog Pool;
- Ready Pool;
- Task Graph;
- Reports.

These files are not canonical knowledge.

They must not be manually maintained as an independent source of truth.

---

## 2.5 `site/`

Meaning:

Presentation Layer.

The intended future implementation is typically Rspress.

Its responsibility is:

> how knowledge is presented to humans.

Its responsibility is not:

> deciding what the authoritative knowledge is.

---

# 3. Verify the Core Lifecycle

Confirm that the repository can represent this lifecycle:

```text
Material / Narrative
        ↓
Goal Intake
        ↓
Goal Draft
        ↓
Human Approval
        ↓
Approved Goal
        ↓
Goal → Backlog
        ↓
Backlog Pool
        ↓
Story Refine
        ↓
Detailed Story
        ↓
Story → Tasks
        ↓
Task Graph
        ↓
Ready Pool
```

Sprint Planning is intentionally outside the current scope.

If Sprint-related folders already exist, you may recognize them, but do not change the current lifecycle because of them.

---

# 4. Verify Goal Intake Capability

Confirm that the repository can support:

```text
Materials
+
Human Narrative
      ↓
UNDERSTAND
      ↓
GAP ANALYSIS
      ↓
CLARIFY
      ↓
DRAFT
      ↓
HUMAN REVIEW
      ↓
APPROVE
      ↓
GOAL-XXX
```

Verify that:

- `intake/active/` exists;
- `intake/completed/` exists;
- Intake templates exist;
- the `goal-intake` Skill exists;
- Goal Approval requires explicit Human confirmation;
- an unapproved Goal cannot be written directly into `raw/goals/`.

Also confirm that the AI explicitly distinguishes:

- FACT
- DECISION
- ASSUMPTION
- QUESTION

---

# 5. Verify Goal → Backlog Capability

Confirm that `goal-to-backlog` is responsible for:

> transforming an Approved Goal into a list of business/product work.

It is not responsible for:

> directly creating engineering Tasks.

Confirm that it can represent:

```text
Goal
 ↓
Capability
 ↓
Scenario
 ↓
Epic / Feature / Story Candidate
 ↓
Backlog
```

Verify that:

- every Backlog Item can trace back to a Goal;
- Goal Success Criteria can map to Backlog Items;
- `GOAL_COVERAGE_GAP` can be detected;
- scope expansion can be detected;
- Future Candidates are not silently added to the active Goal scope.

Also confirm:

`generated/backlog/index.md`

is a View, not the canonical storage location for WorkItems.

Canonical WorkItems belong under:

`wiki/workitems/`

---

# 6. Verify Story Refinement Capability

Confirm that `story-refine` is responsible for:

> transforming a Backlog Story from a work intent into a detailed, reviewable, and testable requirement definition.

Do not decompose the Story into engineering Tasks during this phase.

Verify that the User Story template requires the following 12 sections in this order:

1. Basic Information
2. User Story Definition
3. Scope and Business Rules
4. Included Pages
5. Included Data Models
6. User Journey
7. Prototype Design
8. Positive Test Cases
9. Negative Test Cases
10. Acceptance Criteria
11. Traceability
12. Release Boundary

Confirm that a refined Story can express:

- Actor
- User Goal
- Business Value
- Scope
- Business Rules
- Page / Page State
- Data Model
- User Journey
- Prototype State
- Positive Tests
- Negative Tests
- Acceptance Criteria
- Dependencies
- Traceability
- Release Boundary

---

# 7. Verify Story Boundary Rules

Confirm that AI does not incorrectly merge the following concepts.

## Page ≠ Story

Loading, Empty, Failure, Forbidden, Unavailable, and Not Found are normally Page States rather than independent Stories.

## Design ≠ Implementation

The existence of a prototype does not prove that a feature has been implemented.

## Test Definition ≠ Test Passed

The existence of a test specification does not prove that a test has executed successfully.

## Deployment ≠ Acceptance

A deployed feature does not automatically mean that the business has accepted it.

## Execution Success ≠ Work Completion

Where relevant, preserve separate lifecycle states.

For example:

```text
execution succeeded
    !=
artifact available
    !=
acceptance passed
    !=
work completed
```

---

# 8. Verify Story Readiness

According to:

`schema/readiness.yaml`

confirm that a Story should not advance to Task Decomposition unless it has at least:

- Primary Actor
- User Goal
- Business Value
- Scope
- Business Rules
- Acceptance Criteria
- Traceability
- Dependencies
- No Blocking Question

If these conditions are not met:

do not proceed directly to Task Decomposition.

Refinement produces `ready_for_task_decomposition`, which must be a declared
lifecycle state. `ready` requires Task decomposition and all Ready Pool gates.
For small fixes, irrelevant Story sections may state not applicable with a reason.

---

# 9. Verify Story → Tasks Capability

Confirm that `story-to-tasks` is responsible for:

> transforming a Refined Story into concrete engineering Tasks and an executable Task Graph.

The major difference between this Skill and earlier product-oriented Skills is:

# It must inspect real Engineering Context.

When available, it should inspect:

- current codebase;
- architecture;
- ADRs;
- components;
- APIs;
- existing tests;
- existing implementation.

The AI must not generate technical Tasks solely from the Story text without checking the current engineering environment.

---

# 10. Verify Task Rules

Confirm that a Task:

- is a WorkItem;
- has a stable ID;
- has a Parent Story;
- has a Task Goal;
- has Acceptance criteria;
- has Dependencies;
- may have Affected Components;
- defines executable Verification with prerequisites and expected results;
- may indicate whether Human or Agent execution is preferred.

A Task should not be merely:

`- [ ] Write API`

A Task should be:

> an engineering unit of work that a Human or Agent can understand, execute, and verify.

---

# 11. Verify Task Graph Capability

Confirm that:

Task Graphs belong under:

`generated/task-graphs/`

while Canonical Tasks belong under:

`wiki/workitems/`

The repository must support semantic dependencies such as:

- `depends_on`
- `blocks`
- `parent_of`

It must be able to detect:

`TASK_GRAPH_CYCLE`

If a dependency cycle exists:

the Story must not enter the Ready Pool.

---

# 12. Verify Ready Pool Capability

Confirm that:

`generated/ready/index.md`

represents:

> work that is sufficiently prepared to be selected later by an AI Sprint Planner.

A Story may enter the Ready Pool only when it has:

```text
Refined Story
+
Acceptance Criteria
+
Task Decomposition
+
Task Graph
+
Dependency Analysis
+
No Blocking Question
```

Confirm that Backlog Pool and Ready Pool are separate concepts.

```text
BACKLOG
= what we intend to do

READY
= what is sufficiently prepared to execute
```

---

# 13. Verify Entity and ID Strategy

Inspect:

`schema/id-policy.yaml`

Confirm that it supports IDs for:

- INTAKE
- GOAL
- EPIC
- FEATURE
- STORY
- TASK
- BUG
- SPIKE
- ADR

Confirm that Stable Identity is a repository principle.

Examples:

If a Story title changes:

do not automatically create a new Story ID.

If a Story is split:

use:

`split_from`

If multiple Stories are merged:

use:

`merged_from`

If new work replaces older work:

use:

`supersedes`

Do not silently delete historical identity.

---

# 14. Verify the Relation Model

Confirm support for at least:

- derived_from
- refines
- parent_of
- depends_on
- blocks
- decided_by
- affects
- implemented_by
- verified_by
- released_in
- supersedes
- split_from
- merged_from

Do not reduce all known semantic relationships into a generic:

`links`

field.

---

# 15. Verify Lint Capability

Confirm that `lint` can detect at least the following conditions.

## General

- DUPLICATE_ID
- MISSING_EVIDENCE
- BROKEN_REFERENCE
- INVALID_RELATION
- ORPHAN_WORKITEM
- INVALID_STATUS
- KNOWLEDGE_CONFLICT
- STALE_KNOWLEDGE
- INDEX_OUT_OF_SYNC

## Goal / Backlog

- BACKLOG_WITHOUT_GOAL
- UNSOURCED_BACKLOG_ITEM
- GOAL_COVERAGE_GAP
- BACKLOG_SCOPE_VIOLATION

## Story

- STORY_NOT_REFINED
- STORY_MISSING_ACCEPTANCE
- STORY_MISSING_TRACEABILITY
- STORY_WITH_BLOCKING_QUESTION
- STORY_SCOPE_EXPANSION
- STORY_READY_WITHOUT_REQUIRED_SECTIONS

## Task

- TASK_WITHOUT_PARENT_STORY
- TASK_WITHOUT_ACCEPTANCE
- BROKEN_TASK_DEPENDENCY
- TASK_GRAPH_CYCLE
- STORY_TASK_COVERAGE_GAP

## Ready Pool

- READY_WITHOUT_REFINED_STORY
- READY_WITHOUT_TASK_GRAPH
- READY_WITH_BLOCKING_QUESTION
- READY_WITH_TASK_GRAPH_CYCLE

## Requirement contract checker

Confirm that `.ai/tools/check_requirements.py` exists and that
`python3 .ai/tools/check_requirements.py` runs without error on the empty
project (no Stories yet). Confirm that `schema/templates/story.md` contains the
six-view sections and one `json requirement-contract` block, and that
`schema/readiness.yaml` references the checker. The checker is report-only: it
must not change status, approve scope or be treated as business acceptance.
Confirm that `schema/templates/solution.md` holds Brief, Research, Decision and
Solution sections with one `json solution-contract` block whose decision starts
as `proposed`, and that `wiki/solutions/` exists. An AI recommendation must never
be pre-marked as a human decision.
Confirm that `.ai/tools/evidence.py verify` runs on the empty project and states
that its evidence is not business acceptance.
Confirm that `python3 .ai/tools/check_framework.py` reports 0 errors: every
Skill is routed from AGENTS.md, every routed Skill and tool exists, Skill
frontmatter is valid and `.codex/hooks.json` and `.claude/settings.json` are well
formed. A project that kept its own AGENTS.md may report SKILL_NOT_ROUTED
warnings, and one that kept its own CLAUDE.md may report CLAUDE_MD_SHIM; report
them and propose the route or `@AGENTS.md` import lines instead of rewriting files.
Confirm that `schema/memory-policy.md` exists, that the Task template has a
Resume Point, and that tool memory is treated as a cache, never as the source.
Do not create sample Stories or solution packs during this Self-Check.

---

# 16. Verify AI Permissions

Confirm that AI clearly understands the following permission boundaries.

## AI may automatically maintain

- Intake Working Files
- Canonical Derived Knowledge
- Indexes
- Generated Backlog
- Generated Ready Pool
- Generated Task Graphs
- Low-risk bookkeeping

## Human Approval is required for

- Goal Approval
- Goal Scope Changes
- Major Backlog Scope Changes
- Product Rule Conflicts
- Architecture Decisions
- Business Acceptance
- High-risk semantic conflicts

## AI must not silently modify

- Approved Raw Evidence
- Human-approved Decisions
- Governance Schema

---

# 17. Verify Incremental Update Behavior

Confirm that all Skills follow:

```text
Existing Knowledge
        +
New Evidence
        ↓
Incremental Diff
```

rather than:

```text
Delete Everything
      ↓
Regenerate
```

For existing entities, prefer explicit change classification:

- ADD
- UPDATE
- NO_CHANGE
- SUPERSEDE
- SPLIT
- MERGE
- DEPRECATE

Stable IDs must be preserved.

---

# 18. Actions Forbidden During This Self-Check

## Delivery and learning contracts

### Goal-constrained stage contracts

Verify that the two Dev Flow documents and relevant Skills agree on
GOAL_BASELINE → PM_GATE → TECH_GATE → TEST_RED_GATE → DEV_GREEN_GATE →
GOAL_ACCEPTANCE. `raw/goals/GOAL-*.md` is the only Goal Contract source;
Story/Task IDs, GSC references and lifecycle statuses follow the existing schema.
Stage PASS/FAIL/BLOCKED/NOT_RUN results are evidence fields, not work item statuses.
ACCEPTED requires explicit human final acceptance and is not an Agent Goal status.

Verify that Test precedes Dev for applicable behavior changes, with executable
behavior RED (not syntax/import/dependency failure), GREEN and regression evidence.
Tests cannot be weakened by Dev to obtain GREEN; incorrect expectations need
PM/Tech review, and Goal/constraint changes still require human approval.
Require declared applicability, approved exemptions and reuse of existing paths;
do not require product UI/database/API artifacts during bootstrap or for projects
where they are not applicable. No product work or fabricated RED is allowed here.

For multi-repository projects, confirm instructions for repository ownership,
dependencies, child rules, per-repository revision/non-Git hash evidence and
cross-repository acceptance. Do not require business artifacts before Goal Intake.
One Agent may perform the roles sequentially; no automatic delegation is enabled.
The YAML is a custom contract reviewed by Agents, not an installed automatic
Harness/CI gate engine. Hooks remain advisory; missing optional Hook trust is
not a core workflow failure. The Hook launcher must locate its workflow without
`git rev-parse`, including when invoked from a child repository.

READY establishes initialization/contract readiness only. Do not claim actual
product gates, cross-repository acceptance, native Hook execution or human final
acceptance from generated files or Bootstrap test results.

Inspect `.ai/skills/delivery-loop/SKILL.md` without executing product work.
Confirm that it requires authorized scope, executable acceptance, actual evidence,
failed-attempt preservation and affected regression checks. Completion, test pass,
deployment and human business acceptance must remain separate facts.

Verify that all nine Skills (including `solution-pack`) have `name` and `description` frontmatter and an
explicit AGENTS.md entry point. Files alone do not prove native Agent installation.
The Goal draft must start as `draft`; it must not inherit approval from the Goal
template. Task readiness requires Verification with prerequisites and expectations.

Read `WORKING_STYLE.md` and `schema/templates/learning.md`. Verify that learning
records require evidence and applicability, start as candidates, and become
validated only after successful reuse or explicit human confirmation. Changes to
preferences, Skills or governance require authorization; lessons cannot grant it.
Human confirmation must not imply measured benefits. New lessons start with
`reuse_benefit_status: unmeasured`; benefit claims need comparable baseline/reuse
observations and known maintenance costs. Inspect asset references and invocation
conditions; no daily quota of new lessons or Skills is required.
When checking relevant existing lessons, preserve their IDs, failure history and
limits. Do not import private data or turn one observed outcome into a universal rule.

Inspect Goal outcome follow-up, behavior-sized Tasks and feedback-friction review.
Operational responsibility applies only within declared scope; scripts and
prototypes do not automatically require production deployment or monitoring.

If `scripts/check_bootstrap.py` is available in the bootstrap source repository,
run `python3 scripts/check_bootstrap.py` there. It uses isolated temporary
directories. Report actual results; it does not check all business knowledge or
establish real delivery readiness. Existing nonempty files are retained on rerun,
so upgrades need an approved comparison with fresh output (`initdir.sh --upgrade`).

During this Self-Check, do not:

- create the first Goal;
- automatically create an Intake;
- generate a Backlog;
- refine a Story;
- decompose Tasks;
- modify product requirements;
- initialize Sprint Planning;
- initialize Rspress;
- implement product functionality;
- modify application code;
- automatically resolve high-risk semantic conflicts.

Low-risk automatic initialization fixes are allowed only when the expected intent is unambiguous.

Examples:

- create an obviously missing empty directory;
- create an expected placeholder README;
- repair a purely bookkeeping index inconsistency.

If Schema definitions, Skills, or governance rules materially conflict:

report the conflict.

Do not redesign the system autonomously.

---

# 19. Produce a Repository Initialization Self-Check Report

After completing the inspection, output:

# Repository Initialization Self-Check

## Overall Status

Use exactly one of:

- READY
- READY_WITH_WARNINGS
- NOT_READY

---

## 1. Repository Structure

Example:

```text
PASS schema/
PASS intake/
PASS raw/
PASS wiki/
PASS generated/
PASS .ai/skills/
PASS site/
```

---

## 2. Skill Chain

Report:

```text
goal-intake            PASS / FAIL
goal-to-backlog        PASS / FAIL
story-refine           PASS / FAIL
story-to-tasks         PASS / FAIL
ingest                 PASS / FAIL
query                  PASS / FAIL
lint                   PASS / FAIL
delivery-loop          PASS / FAIL
```

---

## 3. Knowledge Flow

Check:

```text
Material
  ↓
Intake
  ↓
Goal
  ↓
Backlog
  ↓
Refined Story
  ↓
Task Graph
  ↓
Ready Pool
```

Report:

PASS / PARTIAL / FAIL

---

## 4. Governance

Check:

- Evidence First
- Human Governed
- One Entity, One Canonical Source
- Stable Identity
- Semantic Relations
- Incremental Update
- Generated View Separation

---

## 5. Schema

List missing, invalid, or conflicting Schema definitions.

---

## 6. Readiness Gates

Check:

- Goal Readiness
- Story Readiness
- Task Readiness
- Ready Pool Gate
- Delivery Verification Contract
- Learning Evidence / Applicability / Promotion Contract

---

## 7. Risks / Warnings

Organize findings by severity.

### BLOCKER

Issues that prevent the repository from starting real project work.

### WARNING

Issues that do not block usage but should be addressed.

### INFO

Future evolution recommendations.

---

## 8. Automatic Fixes

If any low-risk initialization repair was performed, list:

- what changed;
- why it changed;
- which files were modified.

If nothing was changed, write:

`No automatic changes made.`

---

## 9. Final Recommendation

If status is READY:

explicitly state:

> The repository is ready to start its first Goal Intake.

Recommend the next interaction:

`Start a new Goal Intake: ...`

If status is READY_WITH_WARNINGS:

explain which warnings do not block Goal Intake.

If status is NOT_READY:

list only the Blockers that must be resolved before starting project intake.

---

# 20. Final Principle

The purpose of this Self-Check is not merely to verify:

> whether all expected directories exist.

The purpose is to verify:

> whether this Repository can reliably transform ambiguous project intent into governed, traceable, engineering-ready work for Humans and AI Agents.

The expected lifecycle is:

```text
Human Intent
    ↓
Goal Intake
    ↓
Approved Goal
    ↓
Backlog
    ↓
Refined Story
    ↓
Engineering Tasks
    ↓
Task Graph
    ↓
Ready Pool
```

Now perform the Repository Initialization Self-Check.
