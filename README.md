# AI-Native Software Engineering Knowledge Repository Bootstrap

A bootstrap repository for creating an **AI-native software engineering knowledge system** where human intent, project goals, backlog items, detailed user stories, engineering tasks, and execution-ready work are continuously transformed into durable, traceable knowledge.

The repository is designed around a simple idea:

> Software development should continuously produce structured knowledge that can be reused by both humans and AI agents.

Instead of treating documentation as a separate activity, this repository establishes a development knowledge lifecycle in which AI agents help capture, refine, structure, validate, and maintain project knowledge as the project evolves.

---

# What This Repository Contains

This bootstrap repository starts with two core files:

```text
.
├── initdir.sh
└── 00_AI_WARMUP.md
```

## `initdir.sh`

Initializes the standard repository structure, governance rules, schemas, templates, and AI Skills required by the knowledge system.

It creates the foundation for:

```text
Human Intent
    ↓
Goal Intake
    ↓
Approved Goal
    ↓
Backlog
    ↓
Refined User Story
    ↓
Engineering Tasks
    ↓
Task Graph
    ↓
Ready Pool
```

It does **not** initialize Sprint Planning, application architecture, or Rspress implementation yet.

The purpose of the script is to establish the knowledge system before project execution begins.

v0.4 adds a guided delivery and learning loop after Ready Pool. It requires
authorized work, actual verification and evidence-backed lessons; it does not
provide an autonomous execution service or automatically approve acceptance.

---

## `00_AI_WARMUP.md`

Contains the AI initialization and self-check prompt.

After running `initdir.sh`, provide this file to a repository-aware AI agent such as Codex, Claude Code, Cursor Agent, or another coding agent.

The agent uses the prompt to verify that the repository correctly supports:

```text
Goal Intake
    ↓
Goal Governance
    ↓
Goal → Backlog
    ↓
Story Refinement
    ↓
Story → Tasks
    ↓
Task Graph
    ↓
Ready Pool
```

The self-check validates not only directory existence, but also:

```text
Governance
Schema
AI permissions
Knowledge boundaries
Readiness gates
Stable IDs
Semantic relations
Incremental updates
Skill responsibilities
Canonical vs generated knowledge
```

A successful self-check should return:

```text
READY
```

before real project knowledge is introduced.

---

# Quick Start

Clone or create an empty Git repository and place the bootstrap files in the repository root.

Run:

```bash
chmod +x initdir.sh
./initdir.sh
```

The repository will be expanded into a structure similar to:

```text
.
├── AGENTS.md
├── README.md
│
├── schema/
│   ├── entity-types.yaml
│   ├── workitem-types.yaml
│   ├── relation-types.yaml
│   ├── policies.yaml
│   ├── readiness.yaml
│   ├── id-policy.yaml
│   ├── intake.schema.yaml
│   └── templates/
│       ├── goal.md
│       ├── story.md
│       ├── task.md
│       ├── adr.md
│       └── learning.md
│
├── intake/
│   ├── active/
│   ├── completed/
│   └── templates/
│
├── raw/
│   ├── goals/
│   ├── requirements/
│   ├── meetings/
│   ├── feedback/
│   └── attachments/
│
├── wiki/
│   ├── index.md
│   ├── goals/
│   ├── workitems/
│   ├── decisions/
│   ├── architecture/
│   ├── learning/
│   └── releases/
│
├── generated/
│   ├── backlog/
│   ├── ready/
│   ├── task-graphs/
│   └── reports/
│
├── .ai/
│   └── skills/
│       ├── goal-intake/
│       ├── goal-to-backlog/
│       ├── story-refine/
│       ├── story-to-tasks/
│       ├── ingest/
│       ├── query/
│       ├── lint/
│       └── delivery-loop/
│
├── WORKING_STYLE.md
│
└── site/
```

After initialization, ask your repository AI agent to read and execute:

```text
00_AI_WARMUP.md
```

Do not start creating project Goals until the repository self-check reports that the repository is ready.

---

# Knowledge Architecture

The repository separates information into five different knowledge layers.

```text
                AI Skills
                    │
                    ▼
intake → raw → wiki → generated → site
```

Their responsibilities are intentionally different.

| Layer | Purpose | Authority |
|---|---|---|
| `intake/` | AI working memory before approval | Working |
| `raw/` | Human-approved project evidence | Source of Truth |
| `wiki/` | Canonical derived engineering knowledge | Canonical Knowledge |
| `generated/` | Computed views such as Backlog and Task Graphs | Derived View |
| `site/` | Human-facing presentation | Presentation |

The separation between these layers is one of the most important design principles of the repository.

---

# `intake/` — AI Working Memory

The project normally begins here.

Users should not be required to manually write structured Goal documents.

Instead, they may provide:

```text
Natural-language description
+
Documents
+
Existing requirements
+
Screenshots
+
Meeting notes
+
Product materials
```

The AI then runs a Goal Intake workflow:

```text
RECEIVE
   ↓
EXTRACT
   ↓
UNDERSTAND
   ↓
GAP ANALYSIS
   ↓
CLARIFY
   ↓
SYNTHESIZE
   ↓
DRAFT
   ↓
HUMAN REVIEW
   ↓
APPROVE
```

During Intake, AI distinguishes:

```text
FACT
DECISION
ASSUMPTION
QUESTION
```

Information under `intake/` is not yet authoritative project truth.

---

# `raw/` — Approved Evidence

Once a Goal has been explicitly approved by a human, it becomes approved project evidence.

For example:

```text
raw/goals/GOAL-001.md
```

This layer may also contain:

```text
Requirements
Meeting records
Customer feedback
Original reference materials
```

AI may read approved evidence but must not silently rewrite its meaning.

---

# `wiki/` — Canonical Engineering Knowledge

This is the durable AI-maintained knowledge layer.

Examples include:

```text
User Stories
Engineering Tasks
Architecture Decisions
Components
APIs
Release Knowledge
```

Canonical WorkItems are stored under:

```text
wiki/workitems/
```

A Story or Task should have one canonical representation.

The system follows:

> One Entity, One Canonical Source.

---

# `generated/` — Computed Views

Generated files are projections of canonical knowledge.

Examples:

```text
generated/backlog/
generated/ready/
generated/task-graphs/
generated/reports/
```

For example:

```text
wiki/workitems/STORY-004_借阅图书.md
```

is canonical knowledge.

While:

```text
generated/backlog/index.md
```

is only a Backlog view derived from current WorkItems.

Generated views should never become independent sources of truth.

---

# Development Knowledge Flow

The foundational knowledge pipeline reaches the **Ready Pool**. v0.4 then
provides a guided delivery, verification and learning workflow for authorized Tasks.

## Stage 1 — Goal Intake

Question:

> What are we actually trying to achieve?

Produces:

```text
GOAL-XXX
```

---

## Stage 2 — Goal to Backlog

Question:

> What business or product work must exist to achieve this Goal?

Produces coarse-grained work such as:

```text
Epic
Feature
Story Candidate
```

The Backlog represents:

> prioritized work intent.

It does not represent detailed engineering Tasks.

---

## Stage 3 — Story Refinement

Question:

> What exactly should this Story deliver?

A refined Story defines:

```text
Actor
User Goal
Business Value
Scope
Business Rules
Pages
Data Models
User Journeys
Prototype States
Positive Tests
Negative Tests
Acceptance Criteria
Dependencies
Traceability
Release Boundary
```

Story Refinement is intentionally performed **just in time**.

The repository should not unnecessarily refine the entire future Backlog.

---

## Stage 4 — Story to Tasks

Question:

> Given the current engineering system, what concrete work is required to implement this Story?

This is the first phase that must inspect real engineering context.

The AI should examine, when available:

```text
Existing Code
Architecture
ADR
Components
APIs
Tests
Existing Implementations
```

It then creates canonical engineering Tasks.

Example:

```text
STORY-004
    │
    ├── TASK-041
    ├── TASK-042
    ├── TASK-043
    └── TASK-044
```

---

# Task Graph

Task dependencies are represented as an executable graph.

For example:

```text
TASK-041
Domain Model
    │
    ├──────────────┐
    ▼              ▼
TASK-042        TASK-043
Service         Validation
    │              │
    └──────┬───────┘
           ▼
        TASK-044
           API
           │
      ┌────┴────┐
      ▼         ▼
  TASK-045   TASK-046
  Frontend     Tests
```

Task Graphs are generated views:

```text
generated/task-graphs/
```

They must not contain dependency cycles.

---

# Ready Pool

The Ready Pool contains work that is sufficiently prepared for future execution planning.

```text
BACKLOG
    │
    │ story-refine
    ▼
REFINED STORY
    │
    │ story-to-tasks
    ▼
TASK GRAPH
    │
    │ readiness gate
    ▼
READY POOL
```

A Story should enter the Ready Pool only when:

```text
Story refinement is complete
+
Acceptance is testable
+
Task decomposition is complete
+
Task Graph exists
+
Dependencies are known
+
No blocking product question remains
```

The Ready Pool is intended to become the input for a future:

```text
AI Sprint Planner
```

---

# AI Skills

Repository workflows are implemented as explicit AI Skills.

```text
.ai/skills/
```

The primary development pipeline is:

```text
goal-intake
     ↓
goal-to-backlog
     ↓
story-refine
     ↓
story-to-tasks
```

Supporting Skills include:

```text
ingest
query
lint
delivery-loop
```

Each Skill has a deliberately narrow responsibility.

This prevents one large AI workflow from silently mixing product decisions, requirement interpretation, architecture design, and implementation planning.

---

# Human and AI Responsibilities

The repository follows:

> AI Maintained, Human Governed.

Humans remain responsible for important semantic decisions such as:

```text
Goal Approval
Goal Scope
Major Backlog Scope Changes
Product Rule Conflicts
Architecture Decisions
Business Acceptance
```

AI is expected to automate knowledge bookkeeping such as:

```text
Extraction
Structuring
Cross-linking
Traceability
Summarization
Dependency analysis
Coverage analysis
Knowledge linting
Generated views
Incremental updates
```

The goal is not to remove human judgment.

The goal is to remove unnecessary knowledge-maintenance work.

---

# Evidence First

AI must not invent project facts.

Important knowledge should remain traceable to evidence.

The intended chain is:

```text
Evidence
    ↓
Goal
    ↓
Story
    ↓
Task
    ↓
Implementation
    ↓
Test
    ↓
Release
```

As the repository evolves, engineering evidence such as Git commits, Pull Requests, CI results, tests, and releases can be integrated into the same knowledge system.

---

# Stable Identity

Entities use stable IDs such as:

```text
GOAL-001
EPIC-001
FEAT-001
STORY-001
TASK-001
BUG-001
ADR-001
```

Changing a title does not change identity.

Knowledge evolution should use semantic relations such as:

```text
supersedes
split_from
merged_from
```

rather than silently deleting or recreating entities.

---

# Semantic Relations

Relationships are intentionally explicit.

Examples:

```text
derived_from
refines
parent_of
depends_on
blocks
decided_by
affects
implemented_by
verified_by
released_in
supersedes
split_from
merged_from
```

This allows the repository to evolve from a Markdown Wiki into an **Engineering Knowledge Graph** without requiring a graph database during the early stages.

---

# Incremental Knowledge

The system prefers:

```text
Existing Knowledge
        +
New Evidence
        ↓
Incremental Diff
```

over:

```text
Delete
  ↓
Regenerate Everything
```

This preserves identity, decisions, traceability, and engineering history.

---

# What Is Not Included Yet

The bootstrap generates knowledge and delivery workflow instructions. Execution
tools, environments, CI and native Agent Skill installation still require actual
integration and verification.

Future layers may include:

```text
AI Sprint Planning
Execution Batch Planning
Human / Agent Assignment
Automated Engineering Execution
Git / PR Synchronization
CI / Test Synchronization
Release Knowledge
Impact Analysis
Knowledge Drift Detection
Rspress Knowledge Portal
Hybrid Retrieval / RAG
Engineering Context Packs
```

These capabilities should be introduced only after the foundational lifecycle works reliably.

---

# Recommended First Project

After repository initialization and a successful Self-Check, begin with a small real project.

For example:

```text
Start a new Goal Intake.

I want to build a library lending system.

The first version should allow administrators to add books
and register borrowing activity.

Please follow the repository Goal Intake workflow.

Do not create the Goal immediately.
First understand the intent, identify assumptions,
and clarify the Goal with me.
```

The expected lifecycle is:

```text
Idea
 ↓
Goal Intake
 ↓
GOAL-001
 ↓
Backlog
 ↓
Refined Story
 ↓
Task Graph
 ↓
Ready Pool
```

Running one small project through the entire lifecycle is recommended before expanding the repository model.

---

# Design Philosophy

This repository is based on several fundamental principles:

**Evidence First**

AI derives knowledge from evidence rather than inventing facts.

**One Entity, One Canonical Source**

Canonical knowledge must not be duplicated across multiple files.

**AI Maintained, Human Governed**

AI handles knowledge bookkeeping; humans retain semantic authority.

**Knowledge as Graph**

Engineering knowledge should have explicit relationships rather than isolated documents.

**Incremental Evolution**

Knowledge should evolve through diffs rather than full regeneration.

**Just-in-Time Refinement**

Only work that is approaching execution should be deeply refined.

**Generated Views Are Not Truth**

Backlog, Ready Pool, Task Graphs, and future Sprint views are computed projections of canonical knowledge.

---

# Long-Term Vision

The long-term objective is to create a **Continuous Engineering Memory**.

A system where:

```text
Software Engineering
        ↓
Produces Evidence
        ↓
AI Compiles Knowledge
        ↓
Knowledge Helps Humans & Agents
        ↓
New Engineering Work
        ↓
Produces New Evidence
        ↺
```

Ultimately, the repository should make it possible for an AI Agent to answer questions such as:

```text
Why does this feature exist?

Which Goal does it support?

Which decision defined its behavior?

Which Tasks implement it?

Which code changed?

Which tests verify it?

Has it been released?

What will be affected if this requirement changes?
```

The repository is therefore not simply a documentation system.

It is intended to become an **AI-native engineering context and memory layer** for the entire software development lifecycle.

---

# Bootstrap

Start with:

```bash
chmod +x initdir.sh
./initdir.sh
```

Then run the repository self-check using:

```text
00_AI_WARMUP.md
```

When the result is:

```text
READY
```

start your first Goal Intake.

---

**Software evolves. Engineering knowledge should compound with it.**

---

# Personal Delivery and Learning in v0.4

Use one observable loop:

```text
Relevant preferences and lessons
  → Authorized Task + executable acceptance
  → Small change → Actual verification → Acceptance
  → Evidence-backed retrospective → Scoped learning
  → Smallest reusable asset when justified
  → Apply on a later task → Verify reuse and costs → Keep, narrow or deprecate
```

Read `.ai/skills/delivery-loop/SKILL.md` in an initialized project. Repository
AGENTS.md provides explicit routes for all eight Skills; `.ai/skills/` is not
automatically installed into every Agent. Start from current code, the Task and
its parent Story. Record actual checks and failures under the same Task. A local
test pass does not prove deployment or human business acceptance.

Keep human-confirmed habits in `WORKING_STYLE.md`; this bootstrap repository
already records the user's preference for minimum approved scope, acceptance
before implementation and evidence that separates completion stages. New target
projects get a neutral file to personalize explicitly; existing preferences are
never overwritten. They are not implicitly copied to unrelated projects.

Store reusable work methods and demonstrated pitfalls canonically under
`wiki/learning/LRN-*.md`, using `schema/templates/learning.md` in initialized
projects. Each record needs its source/evidence, applicability, limits, method or
root cause, prevention/check and reuse history. New records are `candidate`;
successful reuse or explicit human confirmation can promote them to `validated`.
Validation is scoped to the recorded conditions, not a guarantee of productivity.
Human confirmation approves a method or preference; measured reuse benefits are
recorded separately. New or legacy records without measurements mean
`reuse_benefit_status: unmeasured`, even when the lesson itself is validated.
Contrary evidence narrows or deprecates a record without deleting its history.

At task start, search for only relevant records and verify their conditions
against current facts. At task end, update the existing lesson for the same cause,
or record a genuinely new reusable lesson. Skip ordinary logs, secrets and
speculative advice. Propose changes to personal preferences, Skills or governance
with evidence and a small diff; do not silently rewrite rules from one run.
Daily, select one main delivery outcome, get useful feedback during work, then
decide whether an existing asset should be reused or improved. No new daily
document, lesson or Skill quota is required. Weekly, inspect known human effort,
rework, first-pass acceptance and the slowest feedback loop; improve one repeated
friction. Missing measurements remain unknown.

## Reusable capability and outcome checks

Choose the smallest asset justified by observed repetition:

| Repeated problem | Prefer |
|---|---|
| Incorrect behavior that can recur | Regression check |
| Repeated operation | Existing or small script |
| Stable repeated implementation | Component or template |
| Judgment and tool coordination | Skill |

Keep assets at their existing canonical paths. A lesson references their actual
entry point, prerequisites, expected result and limits rather than copying them.
Do not create a whole package when a check or command is enough. Repetition is
a reason to evaluate automation, not a mandatory count-based trigger.

On a later real task, record steps reused, necessary adaptation, actual
verification, known human effort/rework and asset maintenance cost. Set
`reuse_benefit_status: measured` only with comparable baseline/reuse observations;
otherwise retain unmeasured. Successful invocation can validate reuse of a method
without proving minutes saved or a productivity multiplier. See this repository's
`wiki/learning/LRN-001_验收前置与隔离回归.md` for a scoped bootstrap example.

Connect Task acceptance to Goal success criteria. When success depends on actual
usage, agree on an observation method, owner and follow-up trigger and use results
to revisit priorities. Missing usage evidence remains unverified; later outcome
review does not keep an otherwise accepted local engineering task open forever.

Prefer independently verifiable behavior slices with explicit inputs, outputs
and dependencies. Design for foreseeable modification without speculative
abstractions. For operation that is in scope, identify the owner, failure signals
and rollback conditions; scripts, prototypes and production changes have different
completion boundaries. Include review, confirmation and maintenance costs in
process evaluation; simplify assets or procedures that cost more than their
observed value.

## Bootstrap verification and upgrades

In this source repository run:

```bash
python3 scripts/check_bootstrap.py
```

This standard-library check initializes isolated temporary projects, validates
template contracts, checks file-hash preservation on rerun, rejects deliberately
invalid cases and checks legacy-file preservation. It does not execute business
acceptance or implement full knowledge-graph lint. The Skill `lint` remains an
Agent inspection workflow.

Running `initdir.sh` retains every existing nonempty file. To upgrade a v0.3
project, initialize v0.4 in a separate temporary directory, compare the affected
schema/templates/Skills/AGENTS.md, then apply an approved minimal diff. Preserve
canonical work and user preferences; rerunning alone does not migrate them.
