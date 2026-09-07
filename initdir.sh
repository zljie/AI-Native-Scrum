#!/usr/bin/env bash

set -euo pipefail

# ============================================================
# AI Native Software Engineering Knowledge Repository
#
# initdir.sh v0.3
#
# Development Knowledge Flow:
#
# Material / Narrative
#        ↓
# Goal Intake
#        ↓
# Approved Goal
#        ↓
# Goal → Backlog
#        ↓
# Backlog Pool
#        ↓
# Story Refinement
#        ↓
# Refined Story
#        ↓
# Story → Tasks
#        ↓
# Task Graph
#        ↓
# Ready Pool
#
# Sprint Planning intentionally NOT included in v0.3.
#
# Usage:
#
#   chmod +x initdir.sh
#   ./initdir.sh
#
# Existing non-empty files will NOT be overwritten.
# ============================================================


ROOT_DIR="$(pwd)"


# ============================================================
# Helpers
# ============================================================

create_dir() {
  local dir="$1"

  if [ -d "$dir" ]; then
    echo "  [exists] $dir/"
  else
    mkdir -p "$dir"
    echo "  [create] $dir/"
  fi
}


create_file_if_missing() {
  local file="$1"

  if [ -f "$file" ]; then
    echo "  [exists] $file"
    return
  fi

  mkdir -p "$(dirname "$file")"
  touch "$file"

  echo "  [create] $file"
}


echo ""
echo "============================================================"
echo " AI Native Engineering Knowledge Repository"
echo " Initializer v0.3"
echo "============================================================"
echo ""
echo "Root:"
echo "  $ROOT_DIR"
echo ""


# ============================================================
# 1. Governance / Schema
# ============================================================

echo ""
echo "[1/7] Governance & Schema"

create_dir "schema"
create_dir "schema/templates"

create_file_if_missing "schema/README.md"

create_file_if_missing "schema/entity-types.yaml"
create_file_if_missing "schema/workitem-types.yaml"
create_file_if_missing "schema/relation-types.yaml"
create_file_if_missing "schema/policies.yaml"

create_file_if_missing "schema/intake.schema.yaml"
create_file_if_missing "schema/readiness.yaml"
create_file_if_missing "schema/id-policy.yaml"

create_file_if_missing "schema/templates/goal.md"
create_file_if_missing "schema/templates/story.md"
create_file_if_missing "schema/templates/task.md"
create_file_if_missing "schema/templates/adr.md"


# ============================================================
# 2. Intake
# ============================================================

echo ""
echo "[2/7] AI Intake"

create_dir "intake"
create_dir "intake/active"
create_dir "intake/completed"
create_dir "intake/templates"

create_file_if_missing "intake/README.md"

create_file_if_missing "intake/templates/intake.yaml"
create_file_if_missing "intake/templates/extracted.md"
create_file_if_missing "intake/templates/clarification.md"
create_file_if_missing "intake/templates/goal-draft.md"
create_file_if_missing "intake/templates/decision-log.md"


# ============================================================
# 3. Raw Engineering Evidence
# ============================================================

echo ""
echo "[3/7] Raw Engineering Evidence"

create_dir "raw"

create_dir "raw/goals"
create_dir "raw/requirements"
create_dir "raw/meetings"
create_dir "raw/feedback"
create_dir "raw/attachments"

create_file_if_missing "raw/README.md"


# ============================================================
# 4. Canonical Knowledge
# ============================================================

echo ""
echo "[4/7] Canonical Engineering Knowledge"

create_dir "wiki"

create_dir "wiki/goals"
create_dir "wiki/workitems"
create_dir "wiki/decisions"

create_dir "wiki/architecture"
create_dir "wiki/architecture/components"
create_dir "wiki/architecture/apis"

create_dir "wiki/releases"
create_dir "wiki/logs"

create_file_if_missing "wiki/README.md"
create_file_if_missing "wiki/index.md"


# ============================================================
# 5. Generated Views
# ============================================================

echo ""
echo "[5/7] Generated Knowledge Views"

create_dir "generated"

create_dir "generated/backlog"
create_dir "generated/ready"
create_dir "generated/task-graphs"
create_dir "generated/reports"

create_file_if_missing "generated/README.md"

create_file_if_missing "generated/backlog/index.md"
create_file_if_missing "generated/ready/index.md"


# ============================================================
# 6. AI Skills
# ============================================================

echo ""
echo "[6/7] AI Skills"

create_dir ".ai"
create_dir ".ai/skills"

create_dir ".ai/skills/goal-intake"
create_dir ".ai/skills/goal-to-backlog"
create_dir ".ai/skills/story-refine"
create_dir ".ai/skills/story-to-tasks"

create_dir ".ai/skills/ingest"
create_dir ".ai/skills/query"
create_dir ".ai/skills/lint"

create_file_if_missing ".ai/skills/README.md"

create_file_if_missing ".ai/skills/goal-intake/SKILL.md"
create_file_if_missing ".ai/skills/goal-to-backlog/SKILL.md"
create_file_if_missing ".ai/skills/story-refine/SKILL.md"
create_file_if_missing ".ai/skills/story-to-tasks/SKILL.md"

create_file_if_missing ".ai/skills/ingest/SKILL.md"
create_file_if_missing ".ai/skills/query/SKILL.md"
create_file_if_missing ".ai/skills/lint/SKILL.md"


# ============================================================
# 7. Presentation / Root
# ============================================================

echo ""
echo "[7/7] Presentation & Root"

create_dir "site"

create_file_if_missing "site/README.md"

create_file_if_missing "AGENTS.md"
create_file_if_missing "README.md"
create_file_if_missing ".gitignore"


# ============================================================
# AGENTS.md
# ============================================================

if [ ! -s "AGENTS.md" ]; then

cat > AGENTS.md <<'EOF'
# AGENTS.md

# Repository Purpose

This repository is an AI Native Software Engineering Knowledge Repository.

It continuously converts:

    Human Intent
        ↓
    Approved Goals
        ↓
    Product Backlog
        ↓
    Refined User Stories
        ↓
    Engineering Tasks
        ↓
    Task Graph
        ↓
    Ready Work

into durable, traceable engineering knowledge.


# Core Development Flow

    Material / Narrative
            ↓
       GOAL INTAKE
            ↓
       Approved Goal
            ↓
     GOAL TO BACKLOG
            ↓
       Backlog Pool
            ↓
       STORY REFINE
            ↓
       Refined Story
            ↓
      STORY TO TASKS
            ↓
        Task Graph
            ↓
        Ready Pool


# Repository Layers


## schema/

Governance and machine-readable rules.

Contains:

- entity schemas
- WorkItem types
- relation types
- readiness policies
- ID policies
- document templates
- AI governance

AI may read this layer.

AI must not modify governance rules unless explicitly instructed.


## intake/

Temporary AI working memory before Goal approval.

AI may freely:

- create
- rewrite
- organize
- summarize

Information here is NOT authoritative project truth.


## raw/

Approved Engineering Evidence.

Examples:

- approved Goals
- Requirements
- Meeting Records
- Feedback
- Source Materials

This is authoritative evidence.

AI must not silently rewrite approved meaning.


## wiki/

Canonical derived engineering knowledge.

Examples:

- WorkItems
- Refined Stories
- Tasks
- ADRs
- Components
- APIs
- Releases

AI may maintain this layer according to governance rules.


## generated/

Computed knowledge views.

Examples:

- Backlog
- Ready Pool
- Task Graph
- Reports

Generated content is NOT canonical knowledge.

Do not manually use generated views as the source of truth.


## site/

Human presentation layer.

Typically implemented using Rspress.

It is not authoritative.


# Authority Order

When information conflicts:

1. Approved Raw Evidence
2. Current Engineering Evidence
3. Human-approved Decisions
4. Verified Canonical Knowledge
5. Inferred Canonical Knowledge
6. Generated Views
7. Intake Working Information


# One Entity, One Canonical Source

Never create duplicate canonical representations.

Example:

GOOD:

    wiki/workitems/STORY-004_登记图书借阅.md

BAD:

    backlog/STORY-004.md
    stories/STORY-004.md

representing the same Story.


# Backlog Principle

Backlog is a prioritized collection of work intent.

Backlog is NOT an engineering Task list.

The canonical entities are stored under:

    wiki/workitems/

The Backlog view is generated under:

    generated/backlog/


# Story Refinement Principle

A Backlog Story describes desired product value.

A Refined Story must clearly define:

- actor
- goal
- user value
- business rules
- scope
- journeys
- acceptance criteria
- dependencies
- traceability

Story refinement must NOT prematurely invent technical implementation.


# Task Principle

A Task describes concrete engineering work.

Tasks must be created only after the parent Story has sufficient readiness.

Task decomposition should consider:

- current codebase
- architecture
- ADRs
- existing components
- APIs
- existing tests
- engineering constraints

Do not generate generic architecture work without inspecting the existing system.


# Ready Pool Principle

AI planning systems may only select work from the Ready Pool.

A Story enters Ready only when:

- Story refinement is complete
- acceptance is testable
- no blocking product question remains
- Task decomposition is complete
- Task Graph exists
- major dependencies are known


# Human Governance

AI may propose.

Human approval is required for:

- Goal approval
- Goal boundary changes
- major Backlog scope changes
- architecture decisions
- acceptance decisions
- material product-rule conflicts


# Incremental Change

Prefer:

    Existing Knowledge
          +
      New Evidence
          ↓
      Knowledge Diff

over regenerating all existing work.

Stable IDs must be preserved.


# Semantic Relations

Prefer explicit relationships:

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


# Important Separation

Keep these concepts separate:

    Goal
    Backlog
    Story
    Task
    Sprint
    Execution
    Verification
    Acceptance
    Release

Do not use one lifecycle status as proof of another lifecycle.

Examples:

    Task completed != Story accepted
    Test passed != Release deployed
    Release deployed != Business acceptance

EOF

fi


# ============================================================
# Entity Types
# ============================================================

if [ ! -s "schema/entity-types.yaml" ]; then

cat > schema/entity-types.yaml <<'EOF'
version: "0.3"

entity_types:

  - id: goal
    description: Approved project or product Goal

  - id: requirement
    description: Approved product or engineering Requirement

  - id: work_item
    description: Generic executable or planned work entity

  - id: adr
    description: Architecture Decision Record

  - id: component
    description: Software or architecture component

  - id: api
    description: API or interface contract

  - id: pull_request
    description: Source code Pull Request

  - id: test
    description: Test definition or verification evidence

  - id: release
    description: Software release

EOF

fi


# ============================================================
# WorkItem Types
# ============================================================

if [ ! -s "schema/workitem-types.yaml" ]; then

cat > schema/workitem-types.yaml <<'EOF'
version: "0.3"

work_item_types:

  epic:
    description: Large business outcome or capability group
    refinement_required: false
    task_decomposition_required: false

  feature:
    description: User-visible product capability
    refinement_required: true
    task_decomposition_required: true

  story:
    description: Independently observable user goal
    refinement_required: true
    task_decomposition_required: true

  task:
    description: Concrete engineering unit of work
    refinement_required: false
    task_decomposition_required: false

  bug:
    description: Incorrect implemented behavior
    refinement_required: true
    task_decomposition_required: true

  spike:
    description: Time-boxed investigation intended to reduce uncertainty
    refinement_required: false
    task_decomposition_required: false

  research:
    description: Research work
    refinement_required: false
    task_decomposition_required: false

  tech_debt:
    description: Engineering quality or maintainability work
    refinement_required: true
    task_decomposition_required: true

  refactor:
    description: Internal design improvement without intentional behavior change
    refinement_required: true
    task_decomposition_required: true

  migration:
    description: Data, platform or architecture migration
    refinement_required: true
    task_decomposition_required: true

  review:
    description: Explicit review or verification work
    refinement_required: false
    task_decomposition_required: false


lifecycle:

  - proposed
  - backlog
  - refining
  - ready
  - planned
  - in_progress
  - review
  - done
  - deprecated

EOF

fi


# ============================================================
# Relation Types
# ============================================================

if [ ! -s "schema/relation-types.yaml" ]; then

cat > schema/relation-types.yaml <<'EOF'
version: "0.3"

relation_types:

  - id: derived_from
    description: Derived from another entity or evidence

  - id: refines
    description: Refines another work definition

  - id: parent_of
    description: Structural decomposition relationship

  - id: depends_on
    description: Execution dependency

  - id: blocks
    description: Blocks progress of another entity

  - id: decided_by
    description: Governed by a decision or ADR

  - id: affects
    description: Impacts another entity

  - id: implemented_by
    description: Implemented by engineering work

  - id: verified_by
    description: Verified by test or evidence

  - id: released_in
    description: Delivered in a Release

  - id: supersedes
    description: Replaces an earlier entity

  - id: split_from
    description: Created by splitting an earlier entity

  - id: merged_from
    description: Created by merging earlier entities

EOF

fi


# ============================================================
# Readiness Schema
# ============================================================

if [ ! -s "schema/readiness.yaml" ]; then

cat > schema/readiness.yaml <<'EOF'
version: "0.3"


goal_ready:

  background:
    required: true

  objective:
    required: true

  success_criteria:
    required: true

  scope:
    required: true


story_ready:

  actor:
    required: true

  user_goal:
    required: true

  business_value:
    required: true

  scope:
    required: true

  business_rules:
    required: true

  acceptance_criteria:
    required: true

  traceability:
    required: true

  dependencies:
    required: true

  blocking_questions:
    max: 0


task_ready:

  parent_story:
    required: true

  task_goal:
    required: true

  acceptance:
    required: true

  dependency_analysis:
    required: true


ready_pool:

  story_ready:
    required: true

  task_graph:
    required: true

  blocking_questions:
    max: 0

EOF

fi


# ============================================================
# ID Policy
# ============================================================

if [ ! -s "schema/id-policy.yaml" ]; then

cat > schema/id-policy.yaml <<'EOF'
version: "0.3"

ids:

  intake:
    prefix: INTAKE
    format: INTAKE-YYYYMMDD-NNN

  goal:
    prefix: GOAL
    format: GOAL-NNN

  epic:
    prefix: EPIC
    format: EPIC-NNN

  feature:
    prefix: FEAT
    format: FEAT-NNN

  story:
    prefix: STORY
    format: STORY-NNN

  task:
    prefix: TASK
    format: TASK-NNN

  bug:
    prefix: BUG
    format: BUG-NNN

  spike:
    prefix: SPIKE
    format: SPIKE-NNN

  adr:
    prefix: ADR
    format: ADR-NNN

rules:

  stable_identity: true

  reuse_existing_id_on_title_change: true

  allocate_before_persist: true

  never_silently_reassign: true

EOF

fi


# ============================================================
# Policies
# ============================================================

if [ ! -s "schema/policies.yaml" ]; then

cat > schema/policies.yaml <<'EOF'
version: "0.3"

layers:

  schema:
    authority: governance
    ai_read: true
    ai_write: false

  intake:
    authority: working
    ai_read: true
    ai_write: true

  raw:
    authority: evidence
    ai_read: true
    ai_write: human_approval_required

  wiki:
    authority: canonical_derived_knowledge
    ai_read: true
    ai_write: true

  generated:
    authority: computed_view
    ai_read: true
    ai_write: generated_only

  site:
    authority: presentation
    ai_read: true
    ai_write: generated_only


principles:

  evidence_first: true

  human_governed: true

  one_entity_one_canonical_source: true

  incremental_update: true

  preserve_stable_ids: true

  preserve_knowledge_history: true

  semantic_relations_preferred: true

  backlog_is_view: true

  ready_pool_is_view: true

  task_graph_is_view: true

EOF

fi


# ============================================================
# Intake Schema
# ============================================================

if [ ! -s "schema/intake.schema.yaml" ]; then

cat > schema/intake.schema.yaml <<'EOF'
version: "0.3"

entity: goal_intake

statuses:

  - receiving
  - extracting
  - understanding
  - clarifying
  - drafting
  - reviewing
  - approved
  - completed
  - cancelled

knowledge_categories:

  - fact
  - decision
  - assumption
  - question

approval:

  human_required: true

EOF

fi


# ============================================================
# Goal Template
# ============================================================

if [ ! -s "schema/templates/goal.md" ]; then

cat > schema/templates/goal.md <<'EOF'
---
id: GOAL-XXX
type: goal
title:
status: approved
source_intake:
evidence: []
created_at:
updated_at:
---

# Goal

## 背景

## Goal / Objective

## Why Now

## 成功标准

## Scope

## Non-Goals

## Constraints

## Stakeholders

## Evidence

## Assumptions

## Open Questions

## Knowledge Evolution

EOF

fi


# ============================================================
# Story Template
# ============================================================

if [ ! -s "schema/templates/story.md" ]; then

cat > schema/templates/story.md <<'EOF'
---
id: STORY-XXX
type: work_item
work_type: story

title:
functional_domain:
actor:

priority:
iteration:

status: refining

derived_from: []
depends_on: []

source_pages: []
source_function_ids: []

knowledge_status: inferred

created_at:
updated_at:
---

# 基本信息

- ID：
- 标题：
- 功能域：
- Actor：
- 适用范围：
- Priority：
- Iteration：
- Status：
- Dependencies：
- Source Pages：
- Source Function IDs：

---

# User Story 定义

作为……

我希望……

从而……

## 用户问题

## 用户价值

## 完成定义

## 前置条件

## 触发条件

---

# 范围与业务规则

## In Scope

## Out of Scope

## Business Rules

### BR-01

### BR-02

---

# 包含的页面

仅描述逻辑产品页面。

页面状态不是独立产品页面。

## PG-01

名称：

用途：

相关状态：

- loading
- normal
- empty
- failure
- unavailable
- not_found
- forbidden

仅保留与当前 Story 有关的状态。

---

# 包含的数据模型

## DM-01

名称：

变更类型：

- 新增
- 修改
- 只读引用

Ownership：

Permission：

Isolation：

Status：

Fields：

Relations：

No-write Constraint：

未确认的物理字段或权限契约必须标记：

待确认

---

# 用户旅程

## UJ-01 主流程

1.
2.
3.

## Alternate / Failure Journey

---

# 原型设计

## UI-01

对应页面：

对应状态：

对应业务规则：

对应测试：

对应验收标准：

---

# 正向测试用例

## TC-P-01

前置条件：

操作：

预期结果：

禁止出现的错误结果：

---

# 逆向测试用例

## TC-N-01

覆盖：

- authorization
- ownership
- missing data
- invalid state
- dependency failure

前置条件：

操作：

预期结果：

禁止出现的错误结果：

---

# 验收标准

## AC-01

Given

When

Then

---

# 追踪关系

| Story | Rule | Page | Model | Journey | Prototype | Test | Acceptance |
|---|---|---|---|---|---|---|---|
| STORY-XXX | BR-01 | PG-01 | DM-01 | UJ-01 | UI-01 | TC-P-01 | AC-01 |

---

# 发布边界

## Dependencies

## Migration Impact

## Permission Impact

## Rollback Relevance

## Unresolved Decisions

## Implementation Evidence

当前 Story 文档本身不证明功能已经实现。

## Test Evidence

当前 Story 文档本身不证明测试已经执行成功。

## Deployment Evidence

当前 Story 文档本身不证明功能已经部署。

## Business Acceptance

当前 Story 文档本身不证明业务已经验收通过。

---

# Knowledge Evolution

EOF

fi


# ============================================================
# Task Template
# ============================================================

if [ ! -s "schema/templates/task.md" ]; then

cat > schema/templates/task.md <<'EOF'
---
id: TASK-XXX

type: work_item
work_type: task

title:

parent_story:

status: proposed

depends_on: []

affected_components: []

execution:
  preferred_actor:
    - agent
    - human

estimated_complexity:

knowledge_status: inferred

created_at:
updated_at:
---

# Task

## Goal

这个 Task 具体要完成什么工程工作？

## Parent Story

## Engineering Context

涉及：

- Existing Code
- Component
- API
- ADR
- Test

## Scope

## Files / Components Potentially Affected

仅在已经检查代码仓库后填写。

不得凭空创造文件路径。

## Dependencies

## Implementation Constraints

## Acceptance

## Verification

## Risks

## Open Questions

## Traceability

EOF

fi


# ============================================================
# ADR Template
# ============================================================

if [ ! -s "schema/templates/adr.md" ]; then

cat > schema/templates/adr.md <<'EOF'
---
id: ADR-XXX
type: adr
title:
status: proposed
created_at:
updated_at:
---

# Context

# Decision

# Alternatives

# Consequences

# Related WorkItems

# Evidence

EOF

fi


# ============================================================
# Intake README / Templates
# ============================================================

if [ ! -s "intake/README.md" ]; then

cat > intake/README.md <<'EOF'
# AI Goal Intake

Goal Intake converts:

    Materials + Human Narrative

into:

    Approved Goal

through:

    Understand
        ↓
    Clarify
        ↓
    Draft
        ↓
    Human Review
        ↓
    Approve

Working Intake data is not authoritative evidence.

Approved Goals are written to:

    raw/goals/

EOF

fi


if [ ! -s "intake/templates/intake.yaml" ]; then

cat > intake/templates/intake.yaml <<'EOF'
id: INTAKE-YYYYMMDD-001

type: goal_intake

status: receiving

created_at:

target:
  entity_type: goal

inputs: []

readiness:

  background: missing
  objective: missing
  success_criteria: missing
  scope: missing

confidence:

EOF

fi


if [ ! -s "intake/templates/extracted.md" ]; then

cat > intake/templates/extracted.md <<'EOF'
# Intake Extraction

## Current Understanding

## FACT

## DECISION

## ASSUMPTION

## QUESTION

## Risks / Conflicts

EOF

fi


if [ ! -s "intake/templates/clarification.md" ]; then

cat > intake/templates/clarification.md <<'EOF'
# Goal Clarification

## Round 1

### Questions

### Answers

### Resolved

### Remaining

EOF

fi


if [ ! -s "intake/templates/goal-draft.md" ]; then

cp "schema/templates/goal.md" "intake/templates/goal-draft.md"

fi


if [ ! -s "intake/templates/decision-log.md" ]; then

cat > intake/templates/decision-log.md <<'EOF'
# Intake Decision Log

## DECISION-001

Date:

Decision:

Reason:

Alternatives:

Impact:

Confirmed By:

EOF

fi


# ============================================================
# Goal Intake Skill
# ============================================================

if [ ! -s ".ai/skills/goal-intake/SKILL.md" ]; then

cat > .ai/skills/goal-intake/SKILL.md <<'EOF'
# GOAL INTAKE

## Purpose

Transform project materials and human narrative into a clear,
approved and traceable Goal.

## Workflow

1. RECEIVE
2. EXTRACT
3. UNDERSTAND
4. GAP ANALYSIS
5. CLARIFY
6. SYNTHESIZE
7. DRAFT
8. REVIEW
9. APPROVE
10. COMPLETE

Before approval:

work only under:

    intake/active/

After explicit Human Approval:

create:

    raw/goals/GOAL-XXX.md

Then archive Intake under:

    intake/completed/

Do NOT automatically create:

- Backlog
- Stories
- Tasks
- ADR
- Sprint

EOF

fi


# ============================================================
# Goal → Backlog Skill
# ============================================================

if [ ! -s ".ai/skills/goal-to-backlog/SKILL.md" ]; then

cat > .ai/skills/goal-to-backlog/SKILL.md <<'EOF'
# GOAL TO BACKLOG

## Purpose

Transform an approved Goal into a prioritized Backlog of business/product work.

The Backlog represents work intent.

It is NOT an engineering Task list.

## Preconditions

The Goal must:

- exist under raw/goals/
- have an official ID
- be approved
- contain Objective
- contain Success Criteria
- contain Scope

## Workflow

1. LOAD
2. UNDERSTAND
3. BOUNDARY
4. CAPABILITY MAP
5. SCENARIO MODEL
6. DECOMPOSE
7. COVERAGE CHECK
8. DEPENDENCY ANALYSIS
9. HUMAN REVIEW
10. PERSIST

## Scope Analysis

Classify possible work:

    IN_SCOPE
    OUT_OF_SCOPE
    UNCERTAIN

Never silently add OUT_OF_SCOPE work.

## Decomposition

Preferred hierarchy:

    Goal
      ↓
    Epic / Feature
      ↓
    Story Candidate

Do NOT create engineering Tasks here.

## Coverage

Every Goal Success Criterion must map to one or more Backlog Items.

Flag missing coverage as:

    GOAL_COVERAGE_GAP

## Gold-plating

Useful but non-required work should be classified:

    FUTURE_CANDIDATE

Do not add it to active Backlog without approval.

## Persistence

Canonical WorkItems:

    wiki/workitems/

Generated Backlog View:

    generated/backlog/index.md

The generated Backlog is never the canonical source.

## Approval

Before approval:

    status: proposed

After explicit human approval:

    status: backlog

Do not automatically refine all Backlog Stories.

EOF

fi


# ============================================================
# Story Refine Skill
# ============================================================

if [ ! -s ".ai/skills/story-refine/SKILL.md" ]; then

cat > .ai/skills/story-refine/SKILL.md <<'EOF'
---
name: story-refine
description: Refine one approved Backlog WorkItem into a detailed, reviewable and independently testable User Story with scope, business rules, pages, data models, journeys, prototypes, tests, acceptance criteria, dependencies and complete traceability. Do not treat Story documentation as evidence that implementation, testing, deployment or business acceptance has occurred.
---

# STORY REFINE

## Purpose

Transform one approved Backlog Story into a sufficiently detailed,
independently testable User Story.

This is Just-in-Time Refinement.

Do NOT refine the whole Backlog unless explicitly requested.


# Source of Truth

Before writing:

1. Locate the requested Story ID in:

       wiki/workitems/

2. Use:

       generated/backlog/index.md

   only as a Backlog view.

3. Preserve the canonical Story's:

   - ID
   - title
   - functional domain
   - priority
   - iteration if present
   - dependencies
   - status
   - source Goal
   - source Requirements
   - boundary notes

4. Read only relevant authoritative evidence:

   - Goal
   - Requirements
   - PRD
   - domain model
   - design input
   - referenced prototype material

5. Treat prototype prompts, mock data and simulation outputs as design inputs,
   not proof of implementation.

6. If authoritative sources conflict:

   preserve the conflict under:

       待确认事项

   Do not silently invent a product rule.

7. If the requested scenario materially exceeds the approved Backlog boundary:

   STOP.

   Request a Backlog decision.


# Story Boundary

One Story should have:

- one primary actor
- one primary user goal
- one independently observable result
- one acceptance boundary

A Page is NOT automatically a Story.

Examples such as:

- loading
- empty
- failure
- unavailable
- forbidden
- not found

are normally Page States.

Split a Story only when one of these becomes independently manageable:

- responsibility
- lifecycle
- authorization
- dependency
- acceptance


# Important Lifecycle Separation

Do not collapse separate lifecycle facts.

When relevant preserve:

    execution succeeded
        !=
    artifact available
        !=
    acceptance passed
        !=
    work completed

Likewise:

    prototype exists
        !=
    implementation exists

    test specification exists
        !=
    test passed

    release document exists
        !=
    production deployed


# Workspace-specific Invariants

Only apply these when the Story concerns a Workspace-style domain:

- one WorkItem has one owning Workspace
- ParentChild means decomposition
- depends_on means execution dependency
- Session means continuous interaction
- WorkRun means one execution attempt
- Workspace does not copy external-system business facts
- Workspace does not silently expand permissions

Do not apply product-specific rules to unrelated domains.


# Required Story Structure

Every refined Story must contain these sections in this order:

1. 基本信息
2. User Story 定义
3. 范围与业务规则
4. 包含的页面
5. 包含的数据模型
6. 用户旅程
7. 原型设计
8. 正向测试用例
9. 逆向测试用例
10. 验收标准
11. 追踪关系
12. 发布边界

Use:

    schema/templates/story.md


# User Story Definition

Use:

    作为...
    我希望...
    从而...

Document:

- user problem
- user value
- completion definition
- preconditions
- trigger
- in-scope behavior
- exclusions
- business rules


# Scope Protection

Do not expand a read-only Story into:

- create
- update
- external write
- execution
- artifact generation
- business approval

unless explicitly approved by the Backlog boundary.


# Pages & Prototype

Separate logical product pages from page states.

For each relevant state map:

    Page State
        ↓
    Test Case
        ↓
    Acceptance Criterion

Do not create unnecessary page-state documentation.


# Data Models

Every model must be marked:

- 新增
- 修改
- 只读引用

Include only fields and relationships required by the Story.

Use stable internal IDs for relationships.

Never use display names as canonical keys.

Document where relevant:

- ownership
- permissions
- isolation
- lifecycle state
- no-write constraints

Unresolved physical fields or permission contracts must be:

    待确认


# Journey

Document:

- main journey
- relevant alternate journey
- relevant failure journey


# Tests

Positive tests cover:

- main path
- legitimate boundary states

Negative tests cover when relevant:

- authorization
- ownership
- missing data
- invalid lifecycle state
- dependency failure
- service failure

Every test must have observable expected results.


# Acceptance

Use Given / When / Then.

Every Acceptance Criterion must be traceable.


# Traceability

End the Story with a table linking:

    Story
    Business Rule
    Page
    Data Model
    Journey
    Prototype
    Test
    Acceptance


# Release Boundary

Always state:

- dependencies
- migration impact
- permission impact
- rollback relevance
- unresolved decisions

Explicitly distinguish whether evidence exists for:

- implementation
- tests
- deployment
- business acceptance

Story documentation alone proves NONE of these.


# Story Readiness Gate

Before changing Story status to:

    ready

verify:

- all 12 required sections exist
- Story boundary matches Backlog
- source Goal exists
- Acceptance Criteria are testable
- major dependencies are known
- no blocking product question remains
- traceability covers all Acceptance Criteria
- no unresolved placeholder remains except explicit actionable 待确认
- no page state is represented as an independent product page
- no design artifact is described as implemented production behavior


# Output

Update the canonical Story under:

    wiki/workitems/

Do not create a duplicate Story copy.

After refinement:

    status: ready_for_task_decomposition

Do NOT automatically generate Tasks unless requested by the next Skill.

EOF

fi


# ============================================================
# Story → Tasks Skill
# ============================================================

if [ ! -s ".ai/skills/story-to-tasks/SKILL.md" ]; then

cat > .ai/skills/story-to-tasks/SKILL.md <<'EOF'
# STORY TO TASKS

## Purpose

Transform one refined User Story into concrete engineering Tasks
and an executable dependency graph.

This is the transition from Product Knowledge to Engineering Execution Knowledge.


# Preconditions

The Story must:

- exist under wiki/workitems/
- be refined
- contain testable Acceptance Criteria
- contain known dependencies
- contain no blocking product question


# Required Context

Before generating Tasks read:

1. Refined Story
2. Parent Goal
3. Related Requirements
4. Existing architecture
5. Relevant ADRs
6. Current codebase
7. Existing components
8. Existing APIs
9. Existing tests

Do NOT create generic Tasks without inspecting the current engineering context.


# Workflow

1. LOAD STORY
2. LOAD ENGINEERING CONTEXT
3. IDENTIFY CHANGE SURFACE
4. DECOMPOSE
5. DEPENDENCY ANALYSIS
6. TASK READINESS
7. BUILD TASK GRAPH
8. VALIDATE STORY COVERAGE
9. PERSIST
10. UPDATE READY POOL


# Engineering Context

Determine whether required behavior should:

- reuse existing code
- extend existing code
- introduce new code
- modify API
- modify data model
- modify UI
- modify tests
- require migration
- require architecture decision

Do not assume every Story needs:

- a new service
- a new database table
- a new API
- a new frontend page


# Task Design

Each Task should represent independently observable engineering work.

A Task must answer:

- what changes
- why this change is needed
- what engineering context is involved
- what it depends on
- how completion is verified


# Example

Story:

    STORY-004 登记图书借阅

Possible Tasks:

    TASK-041
    扩展 BorrowRecord 领域模型

    TASK-042
    实现借阅领域服务

    TASK-043
    实现创建借阅 API

    TASK-044
    实现馆藏可借状态校验

    TASK-045
    实现借阅操作界面

    TASK-046
    编写借阅单元测试

    TASK-047
    编写借阅端到端测试

This is only valid if consistent with the current codebase.


# Dependencies

Use semantic dependencies:

    depends_on
    blocks
    parent_of

Do not create fake dependencies for convenience.


# Task Graph

Generate:

    generated/task-graphs/<STORY-ID>.md

Task Graph is a generated view.

Canonical Tasks live under:

    wiki/workitems/


# Cycle Detection

Task Graph MUST NOT contain a dependency cycle.

If detected report:

    TASK_GRAPH_CYCLE

and STOP readiness promotion.


# Story Coverage

Map every Story Acceptance Criterion to implementation and/or verification Tasks.

Example:

    AC-01
       ↓
    TASK-042
    TASK-043
    TASK-046

Missing coverage:

    STORY_TASK_COVERAGE_GAP


# Task Quality Gate

Each Task must have:

- stable ID
- parent Story
- engineering Goal
- acceptance
- dependencies
- traceability

Do not invent file paths if the codebase has not verified them.


# Ready Pool

A Story may enter:

    generated/ready/

only after:

- Story refinement passes
- Task decomposition passes
- Task Graph exists
- Task Graph has no cycle
- no blocking questions remain
- Acceptance coverage is complete


# Output

Canonical:

    wiki/workitems/TASK-XXX_*.md

Generated:

    generated/task-graphs/STORY-XXX.md
    generated/ready/index.md

Do NOT plan Sprint here.

EOF

fi


# ============================================================
# Generic Ingest Skill
# ============================================================

if [ ! -s ".ai/skills/ingest/SKILL.md" ]; then

cat > .ai/skills/ingest/SKILL.md <<'EOF'
# ENGINEERING INGEST

## Purpose

Ingest external engineering evidence into the knowledge repository.

Examples:

- Requirement
- Meeting
- Feedback
- Pull Request
- Commit
- Test Result
- Build
- Release
- Incident

This Skill does NOT perform:

- Goal Intake
- Goal → Backlog
- Story Refinement
- Story → Tasks

Those have dedicated Skills.

Never silently modify authoritative Raw Evidence.

EOF

fi


# ============================================================
# Query Skill
# ============================================================

if [ ! -s ".ai/skills/query/SKILL.md" ]; then

cat > .ai/skills/query/SKILL.md <<'EOF'
# KNOWLEDGE QUERY

## Purpose

Answer project and engineering questions using durable repository knowledge.

Preferred retrieval order:

1. wiki/index.md
2. canonical entities under wiki/
3. semantic relations
4. generated views
5. approved Raw Evidence
6. codebase when engineering verification is required

Generated views are navigation aids.

They are not canonical truth.

If a conversation creates durable knowledge:

determine whether it belongs to:

- intake
- raw
- wiki
- generated

before persisting it.

EOF

fi


# ============================================================
# Lint Skill
# ============================================================

if [ ! -s ".ai/skills/lint/SKILL.md" ]; then

cat > .ai/skills/lint/SKILL.md <<'EOF'
# KNOWLEDGE LINT

## Purpose

Continuously inspect knowledge quality and lifecycle consistency.


# General Checks

- DUPLICATE_ID
- MISSING_EVIDENCE
- BROKEN_REFERENCE
- INVALID_RELATION
- ORPHAN_WORKITEM
- INVALID_STATUS
- KNOWLEDGE_CONFLICT
- STALE_KNOWLEDGE
- INDEX_OUT_OF_SYNC


# Goal / Backlog Checks

- BACKLOG_WITHOUT_GOAL
- UNSOURCED_BACKLOG_ITEM
- GOAL_COVERAGE_GAP
- BACKLOG_SCOPE_VIOLATION


# Story Checks

- STORY_NOT_REFINED
- STORY_MISSING_ACCEPTANCE
- STORY_MISSING_TRACEABILITY
- STORY_WITH_BLOCKING_QUESTION
- STORY_SCOPE_EXPANSION
- STORY_READY_WITHOUT_REQUIRED_SECTIONS


# Task Checks

- TASK_WITHOUT_PARENT_STORY
- TASK_WITHOUT_ACCEPTANCE
- BROKEN_TASK_DEPENDENCY
- TASK_GRAPH_CYCLE
- STORY_TASK_COVERAGE_GAP


# Ready Pool Checks

- READY_WITHOUT_REFINED_STORY
- READY_WITHOUT_TASK_GRAPH
- READY_WITH_BLOCKING_QUESTION
- READY_WITH_TASK_GRAPH_CYCLE


# Repair Policy

Automatically repair only low-risk bookkeeping issues.

Never automatically resolve:

- product scope conflicts
- business-rule conflicts
- architecture decisions
- permission conflicts
- acceptance decisions

EOF

fi


# ============================================================
# Skills README
# ============================================================

if [ ! -s ".ai/skills/README.md" ]; then

cat > .ai/skills/README.md <<'EOF'
# AI Skills

Current development knowledge pipeline:

## 01 goal-intake

    Material / Narrative
        ↓
    Approved Goal


## 02 goal-to-backlog

    Approved Goal
        ↓
    Backlog WorkItems


## 03 story-refine

    Backlog Story
        ↓
    Detailed User Story


## 04 story-to-tasks

    Refined Story
        ↓
    Engineering Tasks
        ↓
    Task Graph
        ↓
    Ready Pool


Supporting Skills:

## ingest

External Engineering Evidence → Repository

## query

Repository Knowledge → Contextual Answer

## lint

Repository Knowledge → Quality / Consistency Report


Not implemented in v0.3:

    AI Sprint Planning
    Sprint Execution
    Engineering Sync
    Impact Analysis

EOF

fi


# ============================================================
# Raw README
# ============================================================

if [ ! -s "raw/README.md" ]; then

cat > raw/README.md <<'EOF'
# Raw Engineering Evidence

Authoritative approved project evidence.

Directories:

    goals/
    requirements/
    meetings/
    feedback/
    attachments/

AI may read Raw Evidence.

AI must not silently rewrite approved meaning.

EOF

fi


# ============================================================
# Wiki README
# ============================================================

if [ ! -s "wiki/README.md" ]; then

cat > wiki/README.md <<'EOF'
# Canonical Engineering Knowledge

This directory contains durable derived engineering knowledge.

Examples:

    goals/
    workitems/
    decisions/
    architecture/
    releases/

Important:

Backlog, Ready Pool and Task Graph are generated views.

They do NOT belong here as canonical copies.

Canonical Stories and Tasks belong under:

    wiki/workitems/

EOF

fi


# ============================================================
# Wiki Index
# ============================================================

if [ ! -s "wiki/index.md" ]; then

cat > wiki/index.md <<'EOF'
# Engineering Knowledge Index

## Goals

_No Goals ingested._

## Backlog

See:

    generated/backlog/index.md

## Ready Work

See:

    generated/ready/index.md

## Decisions

_No Decisions._

## Architecture

_No Architecture Knowledge._

## Releases

_No Releases._

## Knowledge Health

| Metric | Value |
|---|---:|
| Goals | 0 |
| Backlog Items | 0 |
| Refined Stories | 0 |
| Ready Stories | 0 |
| Tasks | 0 |
| ADRs | 0 |
| Knowledge Conflicts | 0 |

EOF

fi


# ============================================================
# Generated README
# ============================================================

if [ ! -s "generated/README.md" ]; then

cat > generated/README.md <<'EOF'
# Generated Knowledge Views

Everything in this directory is derived.

Do not treat these files as canonical project truth.

## backlog/

Prioritized Work Intent.

Generated from canonical WorkItems whose lifecycle belongs to Backlog.

## ready/

Stories whose refinement and Task decomposition are complete.

Future AI Sprint Planning should select work only from this pool.

## task-graphs/

Dependency graphs generated from canonical Tasks.

## reports/

Lint, coverage and other generated reports.

EOF

fi


# ============================================================
# Backlog View
# ============================================================

if [ ! -s "generated/backlog/index.md" ]; then

cat > generated/backlog/index.md <<'EOF'
# Backlog Pool

> Generated View. Do not edit as canonical knowledge.

## Proposed

_None._

## Backlog

_None._

## Refining

_None._

## Future Candidates

_None._

EOF

fi


# ============================================================
# Ready Pool
# ============================================================

if [ ! -s "generated/ready/index.md" ]; then

cat > generated/ready/index.md <<'EOF'
# Ready Pool

> Generated View.

Only work satisfying Story Readiness and Task Graph quality gates
may appear here.

## Ready Stories

_None._

EOF

fi


# ============================================================
# Schema README
# ============================================================

if [ ! -s "schema/README.md" ]; then

cat > schema/README.md <<'EOF'
# Knowledge Governance & Schema

Defines repository rules.

Files:

    entity-types.yaml
    workitem-types.yaml
    relation-types.yaml
    policies.yaml
    intake.schema.yaml
    readiness.yaml
    id-policy.yaml

Templates:

    templates/goal.md
    templates/story.md
    templates/task.md
    templates/adr.md

Schema changes should normally require human review.

EOF

fi


# ============================================================
# Site
# ============================================================

if [ ! -s "site/README.md" ]; then

cat > site/README.md <<'EOF'
# Presentation Layer

Reserved for Rspress.

Do not initialize the presentation layer until the knowledge lifecycle works:

    Goal Intake
        ↓
    Goal
        ↓
    Backlog
        ↓
    Story Refinement
        ↓
    Task Graph
        ↓
    Ready Pool

Rspress should render knowledge.

Rspress should not become the canonical knowledge source.

EOF

fi


# ============================================================
# Root README
# ============================================================

if [ ! -s "README.md" ]; then

cat > README.md <<'EOF'
# AI Native Software Engineering Knowledge Repository

This repository manages the complete knowledge lifecycle from project intent
to engineering-ready Tasks.

## Current Pipeline

    Material / Narrative
            ↓
       Goal Intake
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

## Layers

    schema/       Governance
    intake/       Pre-approval working memory
    raw/          Approved Evidence
    wiki/         Canonical Knowledge
    generated/    Computed Views
    .ai/skills/   Knowledge Workflows
    site/         Presentation

Sprint Planning is intentionally excluded from v0.3.

EOF

fi


# ============================================================
# Git Ignore
# ============================================================

if [ ! -s ".gitignore" ]; then

cat > .gitignore <<'EOF'
.DS_Store

node_modules/

npm-debug.log*
yarn-debug.log*
pnpm-debug.log*

site/doc_build/
site/.rspress/
site/node_modules/

dist/
build/

.idea/
.vscode/

.tmp/
.cache/

EOF

fi


# ============================================================
# Final Output
# ============================================================

echo ""
echo "============================================================"
echo " Initialization Complete"
echo "============================================================"
echo ""

if command -v tree >/dev/null 2>&1; then

  tree -a -I '.git|node_modules'

else

  find . \
    -not -path './.git*' \
    -not -path './node_modules*' \
    | sort

fi


echo ""
echo "============================================================"
echo " DEVELOPMENT FLOW"
echo "============================================================"
echo ""

echo "  01 Goal Intake"
echo "       ↓"
echo "  02 Goal → Backlog"
echo "       ↓"
echo "  03 Story Refine"
echo "       ↓"
echo "  04 Story → Tasks"
echo "       ↓"
echo "  Ready Pool"
echo ""

echo "AI Sprint Planning is intentionally NOT initialized yet."

echo ""
