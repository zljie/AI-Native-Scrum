#!/usr/bin/env bash

set -euo pipefail

# ============================================================
# AI Native Software Engineering Knowledge Repository
#
# initdir.sh v0.4
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
# Sprint Planning intentionally NOT included in v0.4.
#
# Usage:
#
#   chmod +x initdir.sh
#   ./initdir.sh
#
# Existing non-empty files will NOT be overwritten.
# Run in the intended project/coordination root; Git is not required.
# No git init, child-repository initialization, commit, push or deployment.
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
echo " Initializer v0.4"
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
create_file_if_missing "schema/templates/solution.md"


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
create_dir "wiki/solutions"

create_dir "wiki/architecture"
create_dir "wiki/architecture/components"
create_dir "wiki/architecture/apis"

create_dir "wiki/releases"
create_dir "wiki/logs"
create_dir "wiki/learning"

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
create_dir ".ai/skills/delivery-loop"
create_dir ".ai/skills/solution-pack"

create_file_if_missing ".ai/skills/README.md"

create_file_if_missing ".ai/skills/goal-intake/SKILL.md"
create_file_if_missing ".ai/skills/goal-to-backlog/SKILL.md"
create_file_if_missing ".ai/skills/story-refine/SKILL.md"
create_file_if_missing ".ai/skills/story-to-tasks/SKILL.md"

create_file_if_missing ".ai/skills/ingest/SKILL.md"
create_file_if_missing ".ai/skills/query/SKILL.md"
create_file_if_missing ".ai/skills/lint/SKILL.md"
create_file_if_missing ".ai/skills/delivery-loop/SKILL.md"
create_file_if_missing ".ai/skills/solution-pack/SKILL.md"

create_dir ".ai/tools"

create_file_if_missing ".ai/tools/check_requirements.py"

create_dir ".codex"
create_dir ".codex/hooks"

create_file_if_missing ".codex/hooks.json"
create_file_if_missing ".codex/hooks/goal_flow.py"


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

# Skill Entry Points

Read `WORKING_STYLE.md` before starting work. Search `wiki/learning/` for
relevant patterns and pitfalls; read only matching records and verify their
conditions against the current code and environment.

These repository-local Skills are explicit entry points, not proof of native
Agent installation. Read the selected file before following its workflow.

The workflow root may be an empty folder, a non-Git project, a Git repository,
or a non-Git coordination root containing multiple repositories. Do not require
or create a root `.git`, relocate this root to a child repository, or initialize
children recursively. Preserve existing nonempty files and child-repository rules.
Record repository ownership, dependencies and cross-repository acceptance for
multi-repository work. Initialization never authorizes commit, push or deployment.

Read `Goal_Constrained_Dev_Flow_v1.md` and `dev-flow.yaml` for the stage contracts:
Goal Baseline → PM → Tech → Test RED → Dev GREEN → Goal Acceptance.
These are Agent-reviewed contracts, not an installed automatic gate engine.
Use `raw/goals/` as the only Goal Contract source and the existing schema lifecycle.
Declare artifact applicability and existing paths before execution; approve any
exemption explicitly. Never mark a stage passed without its actual evidence.

| Request | Skill |
|---|---|
| Clarify a new goal | `.ai/skills/goal-intake/SKILL.md` |
| Build approved goal backlog | `.ai/skills/goal-to-backlog/SKILL.md` |
| Brief, research, decide and shape a solution | `.ai/skills/solution-pack/SKILL.md` |
| Refine one story | `.ai/skills/story-refine/SKILL.md` |
| Decompose a refined story | `.ai/skills/story-to-tasks/SKILL.md` |
| Implement, verify, or resume an authorized task | `.ai/skills/delivery-loop/SKILL.md` |
| Import evidence | `.ai/skills/ingest/SKILL.md` |
| Answer knowledge questions | `.ai/skills/query/SKILL.md` |
| Inspect knowledge consistency | `.ai/skills/lint/SKILL.md` |
| Check six-view requirement contracts (report only) | `python3 .ai/tools/check_requirements.py` |

After substantive delivery work, use the learning steps in `delivery-loop`
to capture reusable evidence. Do not treat learned advice as authorization.

Repository-local Codex Hooks under `.codex/` provide advisory Goal context and
evidence reminders. They never approve scope, block tools or prove acceptance.
Codex must trust the project hook definition before it runs.

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
        ↓
    Authorized Delivery → Verification → Human Acceptance
        ↓
    Evidence-backed Learning → Relevant Future Work

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

Approved Goal files under `raw/goals/` are the Goal Contract. Preserve their
revision, stable `GSC-*` success-criterion IDs and Protected Constraints.
Changing Objective, a success criterion or a protected constraint requires
explicit Goal Owner approval and a recorded revision.

Apply the stage handoffs in `Goal_Constrained_Dev_Flow_v1.md` and `dev-flow.yaml`
through the existing Skills. PM owns Story/AC; Tech owns design/interfaces;
Test owns behavior RED and expectation review; Dev owns GREEN and regression.
One Agent can perform these roles sequentially. Additional Agents require
explicit authorization. Final acceptance remains a separate human decision.


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

# Personal Learning Boundaries

`WORKING_STYLE.md` holds human-confirmed collaboration preferences.
`wiki/learning/LRN-*.md` holds canonical evidence-backed patterns and pitfalls.
Use `schema/templates/learning.md`; preserve IDs and update an existing record
for the same lesson instead of duplicating it.

Record a reusable solution, a demonstrated failure, or explicit user feedback.
Include evidence, applicability, limits and verification status. Exclude
credentials, sensitive data, routine success logs and speculative advice.

New lessons start as `candidate`. Promote to `validated` after demonstrated
successful reuse with evidence, or explicit human confirmation. Counterevidence
narrows the conditions or deprecates the lesson; preserve the history.
Human confirmation records approval of a method; productivity benefits require
separate reuse measurements. Keep `reuse_benefit_status: unmeasured` without them.
Promoting a lesson never changes approval or access permissions.

AI may maintain lesson records. Changes to `WORKING_STYLE.md`, governance,
architecture or product rules require explicit user authorization. Propose a
small diff and its evidence; do not silently rewrite Skills after every run.

EOF

fi


# ============================================================
# Entity Types
# ============================================================

if [ ! -s "schema/entity-types.yaml" ]; then

cat > schema/entity-types.yaml <<'EOF'
version: "0.4"

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

  - id: learning
    description: Evidence-backed reusable engineering pattern or pitfall

EOF

fi


# ============================================================
# WorkItem Types
# ============================================================

if [ ! -s "schema/workitem-types.yaml" ]; then

cat > schema/workitem-types.yaml <<'EOF'
version: "0.4"

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
  - ready_for_task_decomposition
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
version: "0.4"

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
version: "0.4"


goal_ready:

  background:
    required: true

  objective:
    required: true

  success_criteria:
    required: true

  success_criteria_ids:
    required: true

  protected_constraints:
    required: true

  change_control:
    required: true

  scope:
    required: true


story_ready:

  goal_success_criteria:
    required: true

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

  # requirement-contract/v1 Stories only; Stories without the block are legacy
  # and are reported, not forcibly migrated. Checked by the report-only
  # .ai/tools/check_requirements.py; business meaning still needs review.
  requirement_contract:
    applies_to: stories_with_requirement_contract_block
    checker: .ai/tools/check_requirements.py
    views: [architecture, acceptance, user_story, description, prototype, business_logic]
    not_applicable_requires_reason: true
    acceptance_requires_test: true
    goal_criteria_covered: true
    dependencies_acyclic: true
    goal_approved: true

  # Stories that reference a solution pack (frontmatter solution / decisions).
  solution_pack:
    applies_to: stories_referencing_a_solution_pack
    brief_confirmed: true
    decisions_decided_by_human: true
    superseded_decisions_need_review: true
    answered_research_needs_non_inference_evidence: true


task_ready:

  parent_story:
    required: true

  goal_success_criteria:
    required: true

  task_goal:
    required: true

  acceptance:
    required: true

  dependency_analysis:
    required: true

  verification:
    required: true


ready_pool:

  story_ready:
    required: true

  task_graph:
    required: true

  task_graph_acyclic:
    required: true

  acceptance_coverage:
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
version: "0.4"

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

  learning:
    prefix: LRN
    format: LRN-NNN

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
version: "0.4"

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

learning:
  statuses: [candidate, validated, deprecated]
  categories: [pattern, pitfall]
  evidence_required: true
  applicability_required: true
  validation_requires_reuse_or_human_confirmation: true
  reuse_benefit_statuses: [unmeasured, measured]
  benefit_claim_requires_comparable_measurements: true
  automatic_governance_changes: false

goal_contract:
  canonical_path: raw/goals
  success_criteria_ids_required: true
  protected_constraint_changes_require_human_approval: true
  automatic_enforcement: false
  hooks_advisory_only: true

EOF

fi


# ============================================================
# Intake Schema
# ============================================================

if [ ! -s "schema/intake.schema.yaml" ]; then

cat > schema/intake.schema.yaml <<'EOF'
version: "0.4"

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
revision: 1
goal_owner:
source_intake:
evidence: []
protected_constraints: []
change_approval_required: true
created_at:
updated_at:
---

# Goal

## 背景

## Goal / Objective

## Why Now

## 成功标准

### GSC-01

可观察结果：

验收证据：

## 使用效果回看（适用时）

当成功标准依赖实际使用时，记录观察方式、责任人及回看触发条件；
用实际效果调整后续优先级。没有使用数据时标记未验证。
局部工程任务可在自身验收通过后完成，后续效果观察作为明确的跟进事项。

## Scope

## Non-Goals

## Constraints

## Protected Constraints

列出未经 Goal Owner 明确批准不得修改的边界；如无，明确写“无”。

## Stakeholders

## Evidence

## Assumptions

## Open Questions

## Change Control

任何 Objective、GSC-* 或 Protected Constraints 的语义变更都必须记录新 revision、
变更原因和 Goal Owner 的明确批准；Hooks 只提醒，不自动批准或阻断。

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
goal_success_criteria: []
depends_on: []
solution:

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
- 研发类型（change_type）：
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

# 系统架构位置

说明需求属于哪里、影响哪里。

## ARCH-01

系统 / 模块 / 组件：

边界：

上游：

下游：

影响范围：

---

# 范围与业务规则

## In Scope

## Out of Scope

## Business Rules

### BR-01

### BR-02

## 权限与状态转换

---

# 研发描述

说明具体需要实现什么。

## DEV-01

功能：

输入：

输出：

接口 / 数据：

约束：

异常处理：

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

无 UI 时在需求契约中把 prototype 声明为不适用并写明理由，不虚构页面。

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

下面的需求契约块是本 Story 六维视图之间引用关系的机读正本；条目内容只写在上方
各节，契约块只登记 ID 和引用，不重复正文。Goal 引用、依赖和方案包以 frontmatter 的
`goal_success_criteria`、`depends_on`、`solution` 为准；`decisions` 列出本 Story
依据的人工决策（如 `SOL-001#DEC-01`），无方案包时留空。检查：
`python3 .ai/tools/check_requirements.py`（只出报告，不修改状态）。

```json requirement-contract
{
  "contract": "requirement-contract/v1",
  "revision": 1,
  "change_type": "feature",
  "views": {
    "architecture": {"applicable": true, "items": ["ARCH-01"]},
    "acceptance": {"applicable": true, "items": ["AC-01"]},
    "user_story": {"applicable": true, "items": ["UJ-01"]},
    "description": {"applicable": true, "items": ["DEV-01", "DM-01"]},
    "prototype": {"applicable": true, "items": ["PG-01", "UI-01"]},
    "business_logic": {"applicable": true, "items": ["BR-01"]}
  },
  "links": {
    "AC-01": {"goal": ["GOAL-XXX#GSC-01"], "rules": ["BR-01"], "tests": ["TC-P-01", "TC-N-01"], "verification": "automated"},
    "UI-01": {"rules": ["BR-01"], "acceptance": ["AC-01"]}
  },
  "decisions": [],
  "open_questions": []
}
```

不适用的视图写成 `{"applicable": false, "reason": "..."}`；acceptance 必须适用。
阻塞问题写成 `{"id": "Q-01", "blocking": true, "text": "..."}`，存在时不能 Ready。

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

goal_success_criteria: []

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

Before execution, map each Acceptance Criterion to a command or actual
operation, prerequisite environment/data and expected result. Declare any
required permission or unavailable dependency; do not invent a successful run.

| Acceptance | Command / Operation | Prerequisites | Expected Result |
|---|---|---|---|

## Execution Evidence

Append attempts under this Task. Record time, code revision or changed files,
environment, actual command/operation, result and evidence path. Keep failed
attempts and distinguish NOT_RUN, BLOCKED, FAIL and PASS.
When feedback delay is a repeated problem, record time from the change to an
actionable result and the main wait (environment, test, review or acceptance).
Do not introduce timing bookkeeping for every trivial operation.

## Completion Boundary

List which checks passed and whether deployment or human business acceptance
is required. A passing local check does not establish either of those facts.
When operation is in scope, specify follow-up owner, problem signals and rollback
conditions. For scripts or prototypes, state the smaller agreed boundary instead
of silently requiring production deployment or indefinite monitoring.

## Risks

## Open Questions

## Traceability

| Goal Criterion | Story Acceptance | Task Acceptance | Evidence |
|---|---|---|---|
| GOAL-XXX#GSC-01 | AC-01 | Acceptance item | NOT_RUN |

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

sed 's/^status: approved$/status: draft/' "schema/templates/goal.md" > "intake/templates/goal-draft.md"

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
---
name: goal-intake
description: Clarify new project intent into a goal draft and persist approved goal evidence only after explicit human approval.
---

Read `Goal_Constrained_Dev_Flow_v1.md` and `dev-flow.yaml` for GOAL_BASELINE.
The approved contract remains under `raw/goals/`; do not create `.goal/`.

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

The approved Goal is the Goal Contract. Before persisting it:

- assign stable `GSC-*` IDs to every success criterion;
- name the Goal Owner;
- list Protected Constraints, or explicitly state none;
- start at `revision: 1` and require explicit Goal Owner approval for later
  Objective, `GSC-*` or Protected Constraint changes.

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
---
name: goal-to-backlog
description: Decompose an approved goal into traceable product backlog items without prematurely creating engineering tasks.
---

Read `Goal_Constrained_Dev_Flow_v1.md` and `dev-flow.yaml` for PM handoff.
Story records remain canonical in `wiki/workitems/`; a story map links to them.

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
- give every Success Criterion a stable `GSC-*` ID
- declare Protected Constraints and change control
- contain Scope

When a problem needs a choice before Stories, use `.ai/skills/solution-pack/SKILL.md`
(Brief → Research → Decision → Solution) and link Stories to that pack.

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

Every `GSC-*` Goal Success Criterion must map to one or more Backlog Items.

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

Read `Goal_Constrained_Dev_Flow_v1.md` and `dev-flow.yaml` for PM_GATE.
Before PM handoff, confirm Story/AC/Goal coverage and applicable menu, module and
function relationships. Record approved applicability and actual artifact paths;
do not create irrelevant UI/database artifacts for scripts or document projects.

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
   - mapped Goal Success Criteria
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
3. 系统架构位置
4. 范围与业务规则
5. 研发描述
6. 包含的页面
7. 包含的数据模型
8. 用户旅程
9. 原型设计
10. 正向测试用例
11. 逆向测试用例
12. 验收标准
13. 追踪关系
14. 发布边界

For a small fix or internal script, mark irrelevant sections (such as pages,
prototype or data models) as not applicable with a short reason. Do not invent
content to fill them; retain scope, acceptance, verification and risk boundaries.

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


# Solution Pack Link

If the Story follows a solution pack (`.ai/skills/solution-pack/SKILL.md`), set
frontmatter `solution: SOL-XXX` and list relied-on decisions in the contract
`decisions` field. Do not copy the Solution into the Story; reference it.
A Story relying on a proposed, unresolved or superseded decision, or on an
unconfirmed Brief, is not Ready.


# Six-view Requirement Contract

The six views are linked views of one requirement, not separate documents:

    architecture    ARCH-*         where it belongs and what it affects
    acceptance      AC-*           change_type and observable acceptance
    user_story      UJ-*           actor, scenario, journey
    description     DEV-* / DM-*   behavior, I/O, interfaces, data, exceptions
    prototype       PG-* / UI-*    pages, interactions, states
    business_logic  BR-*           rules, permissions, state transitions

Write content only in the Story sections. Under 追踪关系 keep one
`json requirement-contract` block (see `schema/templates/story.md`) that lists
item IDs, links and open questions. Do not repeat section content in JSON; Goal
criteria and dependencies stay in frontmatter. Mark an irrelevant view
`applicable: false` with a reason instead of inventing content; acceptance is
always applicable. Each AC links Goal criteria, rules, TC-* tests and a
verification method; each UI-* links rules and acceptance.

Run `python3 .ai/tools/check_requirements.py` before PM handoff. It reports
structure, references, coverage, dependency cycles, unapproved Goals and blocking
questions. It never edits status or approves scope, and it cannot judge business
meaning: still review cross-view semantic conflicts and value. Existing Stories
without the block are legacy; add a block only when refining them again.


# Traceability

The requirement-contract block is the Story's traceability record. Link:

    Goal Success Criterion
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

    ready_for_task_decomposition

verify:

- all 14 required sections exist
- `python3 .ai/tools/check_requirements.py` reports this Story READY
  (legacy Stories without a contract block use the manual checks below)
- Story boundary matches Backlog
- source Goal exists
- every `goal_success_criteria` reference exists in the source Goal
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
---
name: story-to-tasks
description: Inspect current engineering context and decompose a refined story into verifiable tasks and an acyclic dependency graph before Ready Pool promotion.
---
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

Read `Goal_Constrained_Dev_Flow_v1.md` and `dev-flow.yaml` for TECH_GATE.
Inspect the relevant design, interface and data contracts; record applicable
artifacts, paths and unresolved decisions. Decompose design, verification,
implementation and integration work without bypassing stage dependencies.
Test handoff requires a passed TECH_GATE, even when the Ready Pool is populated.
In multi-repository projects, identify each Task's repository, owner, dependencies,
verification command and cross-repository acceptance. Keep existing child rules.

Map every Story Acceptance Criterion to implementation and/or verification Tasks.
Preserve the Story's `GOAL-XXX#GSC-XX` references on the Tasks that contribute
to those criteria; do not copy or reinterpret the Goal Contract.

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
- executable verification entry, prerequisites and expected results

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
- every Task Goal Success Criterion reference resolves through its parent Story


# Output

Canonical:

    wiki/workitems/TASK-XXX_*.md

Generated:

    generated/task-graphs/STORY-XXX.md
    generated/ready/index.md

Only after all Ready Pool gates pass, set the canonical Story to `status: ready`.
Refinement alone leaves it `ready_for_task_decomposition`.

Do NOT plan Sprint here.

EOF

fi


# ============================================================
# Generic Ingest Skill
# ============================================================

if [ ! -s ".ai/skills/ingest/SKILL.md" ]; then

cat > .ai/skills/ingest/SKILL.md <<'EOF'
---
name: ingest
description: Import external engineering evidence while preserving source meaning and approval boundaries; use dedicated skills for goals and work decomposition.
---
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
---
name: query
description: Answer project questions from canonical knowledge and source evidence, retrieving only relevant engineering lessons and verifying drift-prone facts.
---
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

For work methods and known pitfalls, also read `WORKING_STYLE.md` and search
`wiki/learning/`. Check evidence, status and applicability before reusing advice.
Learnings cannot override current source evidence, user instructions or approvals.

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
---
name: lint
description: Inspect knowledge lifecycle, references, readiness and learning evidence; report semantic conflicts instead of silently changing governance.
---
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
- GOAL_CONSTRAINT_VIOLATION
- GOAL_CHANGE_WITHOUT_APPROVAL
- GOAL_TRACEABILITY_GAP
- GOAL_EVIDENCE_GAP


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
- TASK_WITHOUT_VERIFICATION
- BROKEN_TASK_DEPENDENCY
- TASK_GRAPH_CYCLE
- STORY_TASK_COVERAGE_GAP


# Ready Pool Checks

- READY_WITHOUT_REFINED_STORY
- READY_WITHOUT_TASK_GRAPH
- READY_WITH_BLOCKING_QUESTION
- READY_WITH_TASK_GRAPH_CYCLE

# Learning Checks

- LEARNING_WITHOUT_EVIDENCE
- LEARNING_WITHOUT_APPLICABILITY
- DUPLICATE_LEARNING
- VALIDATED_LEARNING_WITHOUT_REUSE_OR_CONFIRMATION
- LEARNING_CONTRADICTS_CURRENT_EVIDENCE

# Requirement Contract Checks

For Stories with a `json requirement-contract` block, run:

    python3 .ai/tools/check_requirements.py
    python3 .ai/tools/check_requirements.py --require-goal-coverage   # Ready Pool review

It reports MISSING_VIEW, NOT_APPLICABLE_WITHOUT_REASON, UNDEFINED_ITEM,
BROKEN_REFERENCE, DUPLICATE_ID, AC_WITHOUT_TEST, GSC_NOT_COVERED,
DEPENDENCY_CYCLE, GOAL_NOT_APPROVED, BLOCKING_QUESTION,
READY_STATUS_WITHOUT_READINESS and GOAL_COVERAGE_GAP with file:line.
Exit code 1 means a contract error or a Story claiming readiness with blockers.
Separate these automatic results from your semantic review in the report.

This Skill is an Agent inspection workflow. The requirement checker is
report-only and covers declared structure and references, not business meaning.
`scripts/check_bootstrap.py` in the bootstrap repository checks initialization
and template contracts only; neither proves business readiness.

# Goal Executive Review

Read `Goal_Constrained_Dev_Flow_v1.md` and `dev-flow.yaml` for stage reviews.
Report missing applicable PM/Tech artifacts, AC-to-test gaps, invalid behavior
RED, unapproved test weakening and stale/missing cross-repository evidence.
Stage results belong in Execution Evidence, not the schema lifecycle `status`.
Only explicit human final acceptance may produce an ACCEPTED outcome.

When reviewing one Goal, report:

- `Goal Status: ON_TRACK | AT_RISK | BLOCKED`
- satisfied `GSC-*` criteria and their evidence
- unmet or unverified `GSC-*` criteria
- new scope or Protected Constraint drift
- smallest corrective action
- what still requires Goal Owner or business acceptance

This is an evidence-backed assessment, not an automatic gate. Do not replace a
failed hard constraint with a weighted score.


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

if [ ! -s ".ai/skills/delivery-loop/SKILL.md" ]; then

cat > .ai/skills/delivery-loop/SKILL.md <<'EOF'
---
name: delivery-loop
description: Execute an authorized engineering task in small verifiable steps, retain actual acceptance evidence and turn demonstrated solutions or failures into scoped reusable lessons.
---
# Delivery and Learning Loop

## Before execution

Read `Goal_Constrained_Dev_Flow_v1.md` and `dev-flow.yaml`. Apply the relevant
PM_GATE and TECH_GATE before Test/Dev handoff. Record PASS, FAIL, BLOCKED or
NOT_RUN with evidence in the Task's Execution Evidence; these are Agent reviews,
not automatic tool/CI enforcement. Declare applicability and actual paths;
any exemption needs a reason, alternative verification and explicit approval.

Read the canonical Task, parent Story, relevant current code and tests,
`WORKING_STYLE.md`, and only matching records in `wiki/learning/`.
Record the lesson IDs actually used. Current evidence and user instructions
take precedence over remembered advice.
Connect the Task to its Goal's success criteria. Where success depends on actual
use, agree how and by whom effects will be observed; do not treat test pass as
proof of user value. Keep later observation separate from local Task completion.
Resolve every `GOAL-XXX#GSC-XX` reference through the approved Goal Contract and
report any missing or changed reference before implementation.

Confirm that the Task is authorized, dependencies are satisfied and scope is
clear. Existing approval remains valid within its scope; do not repeatedly ask.
For a scope conflict, missing required permission or unavailable prerequisite,
report BLOCKED before dependent work. Learning never grants authorization.

Use the Task's Verification table to map acceptance to concrete operations,
prerequisite data/environment and expected results. If a required check is not
executable, report that gap before implementation. For a bug, preserve a minimal
reproduction; for non-trivial new behavior, add a check that rejects wrong behavior.

## Implement and verify

For applicable behavior changes, perform Test before Dev: run an executable
behavior assertion that fails because the behavior is unimplemented or wrong
(RED), retain its output, implement the minimum fix (GREEN), then refactor and
run affected regression. Import, syntax, dependency and configuration errors
are not valid RED. A Test role may be performed by the same Agent before Dev;
do not launch another Agent without authorization. An approved non-code/manual
verification exception must be recorded rather than inventing a RED result.
Do not delete or weaken tests or acceptance criteria to obtain GREEN. If an
expectation is wrong, retain the failure and obtain PM/Tech role review before
changing it; Goal/constraint changes still require explicit human approval.

Work on one delivery item at a time. Reuse existing code and checks; implement
one observable acceptance slice, then run its relevant verification. Inspect
callers and change impact rather than judging only the edited lines.
Prefer behavior slices with explicit inputs, outputs, dependencies and checks,
rather than tiny technical fragments that can only be verified after integration.
Parallel execution requires suitable boundaries and authorization; decomposition
alone does not require additional Agents. Design for foreseeable change without
adding speculative abstractions or configuration.

Verify from acceptance criteria with a fresh review pass. Use a separate reviewer
when useful and available; it is not required for every small change. Actual
test execution and evidence are still required when the Task specifies them.
For UI or external integration criteria, a local build alone is insufficient.

Append attempts to the same Task's Execution Evidence: time, revision or changed
files, environment/data, actual operation, result and evidence path. Use
NOT_RUN, BLOCKED, FAIL or PASS; preserve failures. Never invent a command result.
Do not retry an uncertain external write until its persisted state is checked.

On failure, keep the Task open, identify the failing acceptance criterion, retain
the reproduction and fix the cause. Rerun that check and the affected regression.

Only claim engineering completion when every required criterion has matching
passing evidence and required approvals are satisfied. Otherwise leave the Task
in `review` or `in_progress` with the gap. Record implementation, test, deployment
and human business acceptance separately; use not applicable with a reason when
outside the approved Task boundary. Never mark a Story accepted from Task tests.
If operation is in scope, agree on the observation owner, failure signals and
rollback conditions. Scripts, prototypes and production features have different
completion boundaries. Where actual usage can change priorities, record its
evidence against the Goal or an explicit follow-up when it becomes available.
Before the final report, summarize Goal Status as `ON_TRACK`, `AT_RISK` or
`BLOCKED`, with unmet criteria and evidence gaps. Repository Hooks may remind the
Agent about this review, but never block tools, approve changes or keep a turn open.

Review DEV_GREEN_GATE and GOAL_ACCEPTANCE against all critical Stories and hard
constraints. For multiple repositories, include interface/integration and core
journey results plus each repository's revision (or non-Git file hashes).
Local GREEN cannot substitute for global acceptance. Only explicit human final
approval records ACCEPTED; keep work item statuses within the schema lifecycle.
Release readiness never authorizes commit, push or deployment.

## Learn from the result

After substantive work, inspect evidence for a reusable work method, demonstrated
pitfall, or explicit user correction. Skip routine logs and speculative rules.
Search existing lessons first; update the same lesson for the same root cause.
Create new records from `schema/templates/learning.md` under `wiki/learning/`
using the next unused LRN ID. Record source Task/evidence, conditions and limits,
recipe or root cause, prevention and a check that would detect the problem.
Exclude credentials and sensitive customer/account data.

Choose the smallest reusable asset only when justified by observed repetition:
- recurring wrong behavior: a regression check;
- recurring operations: an existing or small script;
- stable repeated implementation: a component or template;
- judgment and tool coordination: a Skill.
Reuse the project's existing assets before creating one. Record an actual path,
entry point, prerequisites, expected result and limits. A lesson may reference an
asset without duplicating it. Do not require a new asset or lesson every day.

New records start as `candidate`. On a later relevant task, apply the lesson only
within its conditions and append the actual reuse outcome. Promote to `validated`
after successful reuse evidence or explicit human confirmation. A passing test
of the original fix alone is not evidence of successful future reuse.
Human confirmation accepts a preference or method, not a measured productivity
gain. Record asset reuse separately: later task/evidence, steps reused, adaptation,
verification, known human effort/rework and maintenance cost. Use comparable
baseline and reuse observations before setting `reuse_benefit_status: measured`.
Otherwise leave it `unmeasured`; do not infer minutes or percentage saved.
On contrary evidence, narrow or deprecate the record without erasing history.

For changes to personal preferences, Skills, schema, architecture or product
rules, propose the smallest diff with its evidence and obtain explicit approval
unless that exact change is already authorized. A lesson cannot silently rewrite
governance. Keep the record as advice until the approved change is implemented.

Daily, select one main delivery outcome, seek useful feedback during work and
finish by checking whether an existing asset should be reused or improved. This
is a lightweight habit, not a mandatory new document or scoring checklist.
In a weekly review, use known human effort, rework, first-pass acceptance and
useful feedback delay to find the slowest loop (environment, test, review or
business confirmation). Leave missing measurements unknown. Improve one repeated
friction; include asset maintenance and review costs before claiming a benefit.
Simplify a process or asset when its observed cost exceeds its value. Do not use
code volume, document count or Agent activity as measured productivity.
EOF

fi

if [ ! -s ".codex/hooks.json" ]; then

cat > .codex/hooks.json <<'EOF'
{
  "description": "Advisory Goal context and evidence reminders; never blocks tools or completion.",
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume|clear|compact|fork",
        "hooks": [
          {
            "type": "command",
            "command": "root=\"$PWD\"; while [ ! -f \"$root/.codex/hooks/goal_flow.py\" ]; do [ \"$root\" != / ] || exit 0; root=$(dirname \"$root\"); done; python3 \"$root/.codex/hooks/goal_flow.py\"",
            "timeout": 5,
            "statusMessage": "Loading Goal Contract context",
            "additionalContextLimit": 1200
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "root=\"$PWD\"; while [ ! -f \"$root/.codex/hooks/goal_flow.py\" ]; do [ \"$root\" != / ] || exit 0; root=$(dirname \"$root\"); done; python3 \"$root/.codex/hooks/goal_flow.py\"",
            "timeout": 5,
            "statusMessage": "Reviewing Goal evidence"
          }
        ]
      }
    ]
  }
}
EOF

fi

if [ ! -s ".codex/hooks/goal_flow.py" ]; then

cat > .codex/hooks/goal_flow.py <<'EOF'
#!/usr/bin/env python3
"""Provide advisory Goal context without blocking Codex operations."""

import json
from pathlib import Path
import re
import sys


def field(text, key):
    match = re.search(rf"^{re.escape(key)}:[ \t]*(.+?)?[ \t]*$", text, re.MULTILINE)
    return (match.group(1) or "").strip() if match else ""


def approved_goals(root):
    goals = []
    for path in sorted((root / "raw/goals").glob("GOAL-*.md")):
        text = path.read_text(errors="replace")
        if field(text, "status") == "approved":
            goals.append((field(text, "id") or path.stem, field(text, "title") or "untitled"))
    return goals


def session_start(root):
    goals = approved_goals(root)
    listed = ", ".join(f"{goal_id} {title}" for goal_id, title in goals[:5])
    if len(goals) > 5:
        listed += f", +{len(goals) - 5} more"
    goal_context = listed or "none; use Goal Intake for product scope or explicit authorization for maintenance"
    context = (
        "AI-Native-Scrum Goal flow is advisory and never grants authorization or blocks tools. "
        f"Approved Goals: {goal_context}. Before editing, identify the relevant Goal Contract, "
        "GSC-* criteria and Protected Constraints. Before claiming completion, report Goal Status "
        "(ON_TRACK, AT_RISK or BLOCKED), acceptance evidence and remaining gaps."
    )
    return {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        }
    }


def stop(payload):
    message = (payload.get("last_assistant_message") or "").lower()
    completion_claims = ("已完成", "完成了", "已修复", "done", "implemented", "fixed", "passed")
    evidence_terms = ("验证", "测试", "证据", "验收", "未验证", "未测试", "evidence", "test", "risk", "风险")
    result = {"continue": True}
    if any(term in message for term in completion_claims) and not any(term in message for term in evidence_terms):
        result["systemMessage"] = (
            "Goal flow advisory: this looks like a completion claim without verification evidence. "
            "Confirm Goal Status, acceptance evidence and remaining gaps; this reminder does not block the turn."
        )
    return result


def main():
    try:
        payload = json.load(sys.stdin)
        event = payload.get("hook_event_name")
        root = Path(__file__).resolve().parents[2]
        result = session_start(root) if event == "SessionStart" else stop(payload)
    except (OSError, ValueError, TypeError):
        result = {"continue": True}
    json.dump(result, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()
EOF

chmod +x .codex/hooks/goal_flow.py

fi

if [ ! -s "schema/templates/solution.md" ]; then

cat > schema/templates/solution.md <<'SOLUTION_TEMPLATE'
---
id: SOL-XXX
type: solution
title:
goal_success_criteria: []
created_at:
updated_at:
---

# Brief

AI 根据 Goal 和讨论起草，人审阅后在契约块中把 brief 标为 confirmed，
并填写实际的确认人、日期和出处。未确认前可以调研，但下游 Story 不能 Ready。

## 问题

## 背景与场景

## 角色

## 范围

## 约束

## 需要调研的问题

---

# Research

AI 围绕 Brief 自主检索、浏览原站、查看竞品和类似场景，整理证据。
覆盖适用的方向：同类竞品、类似问题的处理方式、实现依据、适用条件。
区分官方宣称、页面观察、亲自操作验证、内部材料和 AI 推断；
看过官网不等于体验过，看到功能介绍不等于验证了实现。
无法访问或需要登录、付费、注册、提交业务数据的内容记为证据缺口，交给人处理。

## RQ-01

问题：

发现（引用 EV-xx）：

适用条件与局限：

对方案选择的影响：

仍未知：

---

# Decision

AI 给出候选、推荐、依据、代价和不确定性，以及需要人回答的具体问题。
人可以选择、调整、要求补充调研、推迟或否决。只记录实际发生的选择；
AI 推荐在人选择前保持 proposed，不能写成已决定。

## DEC-01

需要决定的问题：

候选与依据：

AI 推荐及理由：

人的实际选择 / 调整：

理由与尚存条件：

关联 Goal revision：

影响范围：

需要重新审视的触发条件：

---

# Solution

把已决定的方向组织成完整方案；引用已有架构、原型和接口资料，不复制第二套设计正本。
Story 通过 frontmatter `solution` 和契约块 `decisions` 引用本方案包。

## SOLN-01

总体流程：

架构定位：

关键逻辑 / 状态：

交互与接口方向：

失败与恢复：

---

# 方案契约

只登记 ID、状态、证据元数据与引用，正文写在上方各节。检查：
`python3 .ai/tools/check_requirements.py`（只出报告）。
research.status: open / answered / gap；evidence.nature: official_claim /
page_observation / hands_on_verified / internal_material / ai_inference；
decision.status: proposed / needs_research / decided / rejected / deferred / superseded。

```json solution-contract
{
  "contract": "solution-contract/v1",
  "revision": 1,
  "brief": {"status": "draft", "confirmed_by": "", "confirmed_at": "", "confirmation_ref": ""},
  "research": [
    {"id": "RQ-01", "status": "open", "evidence": []}
  ],
  "decisions": [
    {"id": "DEC-01", "status": "proposed", "research": ["RQ-01"], "recommended": "", "chosen": "", "decided_by": "", "decided_at": "", "confirmation_ref": ""}
  ],
  "solution": {"items": ["SOLN-01"]}
}
```
SOLUTION_TEMPLATE

fi

if [ ! -s ".ai/skills/solution-pack/SKILL.md" ]; then

cat > .ai/skills/solution-pack/SKILL.md <<'SOLUTION_SKILL'
---
name: solution-pack
description: Turn an approved Goal into a reviewed Brief, evidence-backed Research, human Decisions and a Solution in one solution pack before Stories are refined; the AI recommends, a person decides.
---

# SOLUTION PACK

Read `Goal_Constrained_Dev_Flow_v1.md` and `dev-flow.yaml`. The main line is:

    Goal → Brief → Research → Decision → Solution → Story → Task

Brief, Research, Decision and Solution live in one pack per problem round:
`wiki/solutions/SOL-XXX_<name>.md`, from `schema/templates/solution.md`.
Scale the depth to the work; a small change may need a short Brief and one
Decision. Do not create seven files or seven Agents. PM, Tech, Test and Dev are
responsibilities one Agent may perform in sequence.

## Brief

Draft the Brief from the approved Goal and the discussion: problem, background,
scenarios, roles, scope, constraints and questions to research. Ask the person to
review it. Mark `brief.status: confirmed` only with the actual reviewer, date and
where it was confirmed. Research may start on a draft; Stories may not be Ready.

## Research

Work through this loop without asking before every public page:

    read the Brief → list questions that affect the choice → search candidate
    sources → open original sites, read material, look at real flows → record
    evidence and uncertainty → search again for gaps → compare and recommend

Cover the applicable directions: comparable products (who they serve, core
journey, organization, limits); similar problems in other domains (approval,
failure recovery, permissions, duplicate submission); implementation basis
(official docs, open source, interface specs, research, public cases); and
applicability (what the solution depends on, whether we have it, what cannot be
copied). Investigate the underlying question, not only feature lists.

Use the available search and browser tools (for example Playwright MCP for
exploratory browsing). Do not install tools without authorization. Login,
payment, registration or submitting business data beyond existing authorization
goes to the person; unreachable content is an evidence gap, never a guess.

For each important finding keep: source link or material location, access date,
screenshot/material location when useful, the specific finding, evidence nature,
applicability and limits, and its effect on the choice. Evidence nature is one of
`official_claim`, `page_observation`, `hands_on_verified`, `internal_material`,
`ai_inference`. Seeing a vendor site is not using the product; a feature page is
not a verified implementation. An answered question needs evidence beyond AI
inference. Stop when the evidence supports the key choices of this round.

## Decision

For each choice give: the question, real alternatives (or why none exist), the
recommendation, relation to Goal and constraints, benefit/cost/risk, evidence and
uncertainty, and exactly what the person must decide. Keep it `proposed`.

The person may choose, adjust, ask for more research (`needs_research`), defer
or reject. Record only what actually happened: the choice, reason, conditions,
Goal revision, impact, revisit triggers, who decided, when and where. Never mark
an AI recommendation as decided, and do not treat a bare "OK" without concrete
options as a full decision record. When key evidence or premises change, mark
the decision `superseded` (keep its history) so dependent Stories surface for
review; the person decides whether to choose again.

Routine work inside existing authorization does not need a new Decision. Goal,
Protected Constraint and critical scope/architecture changes follow Goal change
control. A Decision is not Goal approval and not final business acceptance.
Architecture decisions may also be recorded as ADRs in `wiki/decisions/`.

## Solution

Organize the decided direction: overall flow, architecture position, key logic
and states, interaction and interface direction, failure and recovery. Reference
existing architecture, prototype and interface material instead of copying it.

## Handoff to Stories

Stories set frontmatter `solution: SOL-XXX` and list relied-on decisions in their
requirement contract (`"decisions": ["SOL-XXX#DEC-01"]`). Then use `story-refine`.
Run `python3 .ai/tools/check_requirements.py`; it reports pack structure, evidence
fields, unconfirmed Briefs, pending or superseded decisions and broken references.
It cannot prove a person really took part or chose well; say so in reports.

## Learning

When the person decides, the pack keeps their actual choice next to the AI
recommendation; later results can be compared in the delivery-loop learning step.
Thinking before reading the recommendation is an optional practice the person
may adopt, not a gate.
SOLUTION_SKILL

fi

if [ ! -s ".ai/tools/check_requirements.py" ]; then

cat > .ai/tools/check_requirements.py <<'CHECK_REQUIREMENTS_PY'
#!/usr/bin/env python3
"""Report-only checks for Story requirement contracts and solution packs.

Checks requirement-contract/v1 blocks in wiki/workitems/ Stories and
solution-contract/v1 blocks in wiki/solutions/ packs (Brief, Research,
Decision, Solution). Proves structure, references, declared coverage,
dependencies, recorded human decisions and readiness inputs. It cannot judge
business meaning or prove that a person really chose; it approves nothing and
never edits files or status. Stories without a contract block are legacy and
are not migrated; Stories without a solution pack are still checked.
"""

import argparse
import json
from pathlib import Path
import re
import sys


CONTRACT = "requirement-contract/v1"
FENCE = re.compile(r"^```json requirement-contract[ \t]*\n(.*?)^```[ \t]*$", re.MULTILINE | re.DOTALL)
PACK_FENCE = re.compile(r"^```json solution-contract[ \t]*\n(.*?)^```[ \t]*$", re.MULTILINE | re.DOTALL)
PACK_CONTRACT = "solution-contract/v1"
DECISION_REF = re.compile(r"^(SOL-[A-Za-z0-9-]+)#(DEC-[0-9]+)$")
DATE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
RESEARCH_STATUSES = ("open", "answered", "gap")
EVIDENCE_NATURES = ("official_claim", "page_observation", "hands_on_verified", "internal_material", "ai_inference")
DECISION_STATUSES = ("proposed", "needs_research", "decided", "rejected", "deferred", "superseded")
CONFIRMATION = ("chosen", "decided_by", "decided_at", "confirmation_ref")
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---(?:\n|$)", re.DOTALL)
HEADING = re.compile(r"^#{2,4}[ \t]+([A-Z]+(?:-[A-Z]+)*-[0-9]+)\b", re.MULTILINE)
GSC_REF = re.compile(r"^(GOAL-[A-Za-z0-9-]+)#(GSC-[0-9]+)$")
VIEWS = {
    "architecture": ("ARCH",),
    "acceptance": ("AC",),
    "user_story": ("UJ",),
    "description": ("DEV", "DM"),
    "prototype": ("UI", "PG"),
    "business_logic": ("BR",),
}
ALWAYS_APPLICABLE = ("acceptance",)
CHANGE_TYPES = (
    "feature", "enhancement", "bugfix", "refactor", "integration",
    "data_migration", "configuration", "documentation",
)
VERIFICATION = ("automated", "manual", "inspection")
LINK_TARGETS = {"goal", "rules", "acceptance", "tests", "verification"}
CLAIMS_READY = ("ready_for_task_decomposition", "ready", "planned", "in_progress", "review", "done")


def frontmatter(text):
    match = FRONTMATTER.match(text)
    return match.group(1) if match else ""


def field(header, key):
    match = re.search(rf"^{re.escape(key)}:[ \t]*(.*?)[ \t]*$", header, re.MULTILINE)
    return match.group(1).strip().strip("'\"") if match else ""


def list_field(header, key):
    # shortcut: reads flow `[a, b]` or block `- a` lists only; use a YAML parser for full YAML.
    match = re.search(rf"^{re.escape(key)}:[ \t]*(.*?)[ \t]*$", header, re.MULTILINE)
    if not match:
        return []
    value = match.group(1)
    if value.startswith("["):
        return [item.strip().strip("'\"") for item in value.strip("[]").split(",") if item.strip()]
    items = []
    for line in header[match.end():].splitlines()[1:]:
        item = re.match(r"^[ \t]+-[ \t]+(.+?)[ \t]*$", line)
        if not item:
            break
        items.append(item.group(1).strip("'\""))
    return items


def prefix(item_id):
    return item_id.rsplit("-", 1)[0]


class Report:
    def __init__(self, root):
        self.root = root
        self.findings = []

    def add(self, severity, code, path, line, subject, message):
        location = f"{path.relative_to(self.root)}:{line}" if path else "-"
        self.findings.append({
            "severity": severity, "code": code, "location": location,
            "subject": subject, "message": message,
        })


class Story:
    def __init__(self, path, text, fence=FENCE):
        self.path = path
        self.text = text
        header = frontmatter(text)
        self.id = field(header, "id") or path.stem
        self.status = field(header, "status")
        self.solution = field(header, "solution")
        self.goal_criteria = list_field(header, "goal_success_criteria")
        self.depends_on = list_field(header, "depends_on")
        self.blocks = list(fence.finditer(text))
        self.contract = None
        self.errors = 0
        self.blockers = 0

    def line(self, needle=None):
        start = self.blocks[0].start(1) if self.blocks else 0
        position = self.text.find(needle, start) if needle else -1
        if position < 0:
            position = self.text.find(needle) if needle else -1
        return self.text.count("\n", 0, max(position, start)) + 1


def load_goals(root):
    goals = {}
    for path in sorted((root / "raw/goals").glob("GOAL-*.md")):
        text = path.read_text(errors="replace")
        header = frontmatter(text)
        goal_id = field(header, "id") or path.stem
        goals[goal_id] = {
            "path": path,
            "status": field(header, "status"),
            "criteria": {match for match in HEADING.findall(text) if match.startswith("GSC-")},
        }
    return goals


def load_stories(root):
    stories = []
    for path in sorted((root / "wiki/workitems").rglob("*.md")):
        text = path.read_text(errors="replace")
        if field(frontmatter(text), "id").startswith("STORY-") or path.name.startswith("STORY-"):
            stories.append(Story(path, text))
    return stories


def load_packs(root):
    packs = []
    for path in sorted((root / "wiki/solutions").rglob("SOL-*.md")):
        packs.append(Story(path, path.read_text(errors="replace"), PACK_FENCE))
    return packs


def check_pack(pack, goals, report):
    """Return {decision_id: status} and count errors on the pack."""
    def error(code, subject, message, needle=None):
        pack.errors += 1
        report.add("ERROR", code, pack.path, pack.line(needle or subject), subject, message)

    if len(pack.blocks) != 1:
        error("CONTRACT_FIELD_INVALID", pack.id, "a solution pack needs exactly one solution-contract block")
        return {}, "missing"
    try:
        contract = json.loads(pack.blocks[0].group(1))
    except json.JSONDecodeError as problem:
        pack.errors += 1
        line = pack.text.count("\n", 0, pack.blocks[0].start(1)) + problem.lineno
        report.add("ERROR", "CONTRACT_INVALID_JSON", pack.path, line, pack.id, problem.msg)
        return {}, "missing"
    if not isinstance(contract, dict) or contract.get("contract") != PACK_CONTRACT:
        error("CONTRACT_VERSION_UNSUPPORTED", pack.id, f"expected contract: {PACK_CONTRACT}", "contract")
        return {}, "missing"
    for reference in pack.goal_criteria:
        match = GSC_REF.match(reference)
        goal = goals.get(match.group(1)) if match else None
        if not goal or match.group(2) not in goal["criteria"]:
            error("BROKEN_REFERENCE", reference, "Goal success criterion not found in raw/goals/")

    brief = contract.get("brief") if isinstance(contract.get("brief"), dict) else {}
    brief_status = brief.get("status")
    if brief_status not in ("draft", "confirmed"):
        error("CONTRACT_FIELD_INVALID", "brief", "brief status must be draft or confirmed")
    elif brief_status == "confirmed" and not all(brief.get(key) for key in ("confirmed_by", "confirmed_at", "confirmation_ref")):
        error("BRIEF_WITHOUT_CONFIRMATION", "brief", "confirmed Brief needs confirmed_by, confirmed_at and confirmation_ref")

    body = PACK_FENCE.sub("", pack.text)
    defined = set(HEADING.findall(body))
    seen = set()

    def declare(item, wanted):
        if not isinstance(item, str) or prefix(item) != wanted:
            error("CONTRACT_FIELD_INVALID", str(item), f"use {wanted}-NN IDs")
            return False
        if item in seen:
            error("DUPLICATE_ID", item, "ID is declared more than once")
            return False
        seen.add(item)
        return True

    research_ids = set()
    research = contract.get("research") if isinstance(contract.get("research"), list) else []
    for question in research:
        question = question if isinstance(question, dict) else {}
        item = question.get("id")
        if not declare(item, "RQ"):
            continue
        research_ids.add(item)
        if item not in defined:
            error("UNDEFINED_ITEM", item, "research question has no matching section heading")
        if question.get("status") not in RESEARCH_STATUSES:
            error("CONTRACT_FIELD_INVALID", item, f"status must be one of {', '.join(RESEARCH_STATUSES)}")
        evidence = question.get("evidence") if isinstance(question.get("evidence"), list) else []
        usable = 0
        for record in evidence:
            record = record if isinstance(record, dict) else {}
            evidence_id = record.get("id")
            if not declare(evidence_id, "EV"):
                continue
            if (not record.get("source") or not DATE.match(str(record.get("accessed_at", "")))
                    or record.get("nature") not in EVIDENCE_NATURES):
                error("EVIDENCE_FIELD_INVALID", evidence_id,
                      f"evidence needs source, accessed_at (YYYY-MM-DD) and nature in {', '.join(EVIDENCE_NATURES)}")
            elif record["nature"] != "ai_inference":
                usable += 1
        if question.get("status") == "answered" and not usable:
            error("RESEARCH_WITHOUT_EVIDENCE", item, "answered question needs evidence beyond AI inference")

    decisions = {}
    for decision in contract.get("decisions") if isinstance(contract.get("decisions"), list) else []:
        decision = decision if isinstance(decision, dict) else {}
        item = decision.get("id")
        if not declare(item, "DEC"):
            continue
        status = decision.get("status")
        decisions[item] = status
        if item not in defined:
            error("UNDEFINED_ITEM", item, "decision has no matching section heading")
        if status not in DECISION_STATUSES:
            error("CONTRACT_FIELD_INVALID", item, f"status must be one of {', '.join(DECISION_STATUSES)}")
        if status in ("decided", "superseded") and not decision.get("recommended"):
            error("DECISION_WITHOUT_RECOMMENDATION", item, "record the AI recommendation (or why there is no alternative)")
        references = decision.get("research") if isinstance(decision.get("research"), list) else []
        for reference in references:
            if reference not in research_ids:
                error("BROKEN_REFERENCE", reference, f"{item} research reference is not a declared RQ", f'"{reference}"')
        if status in ("decided", "superseded") and not all(decision.get(key) for key in CONFIRMATION):
            error("DECISION_WITHOUT_CONFIRMATION", item,
                  "a human decision needs chosen, decided_by, decided_at and confirmation_ref from the actual record")
        if status == "decided" and not references:
            error("DECISION_WITHOUT_RESEARCH", item, "decided choice cites no research question")

    solution = contract.get("solution") if isinstance(contract.get("solution"), dict) else {}
    items = solution.get("items")
    if not isinstance(items, list):
        error("CONTRACT_FIELD_INVALID", "solution", "solution.items must list SOLN-NN IDs")
        items = []
    for item in items:
        if declare(item, "SOLN") and item not in defined:
            error("UNDEFINED_ITEM", item, "solution item has no matching section heading")
    return decisions, brief_status


def check_structure(story, report):
    def error(code, subject, message, needle=None):
        story.errors += 1
        report.add("ERROR", code, story.path, story.line(needle or subject), subject, message)

    if len(story.blocks) > 1:
        error("DUPLICATE_CONTRACT", story.id, "only one requirement-contract block is allowed")
    try:
        contract = json.loads(story.blocks[0].group(1))
    except json.JSONDecodeError as problem:
        story.errors += 1
        line = story.text.count("\n", 0, story.blocks[0].start(1)) + problem.lineno
        report.add("ERROR", "CONTRACT_INVALID_JSON", story.path, line, story.id, problem.msg)
        return None, {}
    if not isinstance(contract, dict):
        error("CONTRACT_FIELD_INVALID", story.id, "contract must be a JSON object")
        return None, {}
    if contract.get("contract") != CONTRACT:
        error("CONTRACT_VERSION_UNSUPPORTED", story.id, f"expected contract: {CONTRACT}", "contract")
        return None, {}
    if not story.id.startswith("STORY-"):
        error("CONTRACT_FIELD_INVALID", story.id, "frontmatter id must be a STORY-* ID")
    revision = contract.get("revision")
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
        error("CONTRACT_FIELD_INVALID", "revision", "revision must be an integer >= 1")
    if contract.get("change_type") not in CHANGE_TYPES:
        error("CONTRACT_FIELD_INVALID", "change_type", f"change_type must be one of {', '.join(CHANGE_TYPES)}")
    if not story.goal_criteria:
        error("CONTRACT_FIELD_INVALID", "goal_success_criteria", "frontmatter must list GOAL-XXX#GSC-XX criteria")

    views = contract.get("views") if isinstance(contract.get("views"), dict) else {}
    declared = {}
    for name, prefixes in VIEWS.items():
        view = views.get(name)
        if not isinstance(view, dict):
            error("MISSING_VIEW", name, "six-view contract requires this view", "views")
            continue
        if view.get("applicable") is True:
            items = view.get("items")
            if not isinstance(items, list) or not items:
                error("VIEW_WITHOUT_ITEMS", name, "applicable view must list item IDs")
                continue
            for item in items:
                if not isinstance(item, str) or prefix(item) not in prefixes:
                    error("CONTRACT_FIELD_INVALID", str(item), f"{name} items must use {'/'.join(prefixes)}-NN IDs", name)
                elif item in declared:
                    error("DUPLICATE_ID", item, f"declared in both {declared[item]} and {name}")
                else:
                    declared[item] = name
        elif view.get("applicable") is False:
            if name in ALWAYS_APPLICABLE:
                error("REQUIRED_VIEW_NOT_APPLICABLE", name, "acceptance view cannot be not applicable")
            elif not isinstance(view.get("reason"), str) or not view["reason"].strip():
                error("NOT_APPLICABLE_WITHOUT_REASON", name, "not-applicable view needs a reason")
        else:
            error("CONTRACT_FIELD_INVALID", name, "applicable must be true or false")
    return contract, declared


def check_solution_links(story, contract, packs, report):
    def error(code, subject, message):
        story.errors += 1
        report.add("ERROR", code, story.path, story.line(f'"{subject}"' if subject in story.text else subject), subject, message)

    def blocker(code, subject, message):
        story.blockers += 1
        report.add("BLOCKER", code, story.path, story.line(subject), subject, message)

    if story.solution and story.solution not in packs:
        error("BROKEN_REFERENCE", story.solution, "solution pack not found in wiki/solutions/")
    references = contract.get("decisions", [])
    if not isinstance(references, list):
        error("CONTRACT_FIELD_INVALID", "decisions", "decisions must list SOL-XXX#DEC-NN references")
        references = []
    used = {story.solution} if story.solution in packs else set()
    for reference in references:
        match = DECISION_REF.match(str(reference))
        pack = packs.get(match.group(1)) if match else None
        if not pack or match.group(2) not in pack["decisions"]:
            error("BROKEN_REFERENCE", str(reference), "decision not found in its solution pack")
            continue
        used.add(match.group(1))
        status = pack["decisions"][match.group(2)]
        if status == "superseded":
            blocker("DECISION_NEEDS_REVIEW", reference,
                    f"{story.id} relies on a superseded decision; a person decides whether to choose again")
        elif status != "decided":
            blocker("DECISION_NOT_CONFIRMED", reference,
                    f"decision is {status}; an AI recommendation is not a human decision")
    for pack_id in sorted(used):
        pack = packs[pack_id]
        if pack["errors"]:
            blocker("SOLUTION_PACK_INVALID", pack_id, "referenced solution pack has contract errors")
        if pack["brief"] != "confirmed":
            blocker("BRIEF_NOT_CONFIRMED", pack_id, "the AI-drafted Brief has not been reviewed and confirmed")


def check_references(story, contract, declared, goals, story_ids, report):
    def error(code, subject, message, needle=None):
        story.errors += 1
        report.add("ERROR", code, story.path, story.line(needle or subject), subject, message)

    body = FENCE.sub("", story.text)
    headings = HEADING.findall(body)
    defined = set(headings)
    for item in sorted({item for item in headings if headings.count(item) > 1}):
        error("DUPLICATE_ID", item, "item heading is defined more than once")
    for item in declared:
        if item not in defined:
            error("UNDEFINED_ITEM", item, "declared item has no matching section heading in the Story")

    for reference in story.goal_criteria:
        match = GSC_REF.match(reference)
        goal = goals.get(match.group(1)) if match else None
        if not match:
            error("CONTRACT_FIELD_INVALID", reference, "use GOAL-XXX#GSC-XX")
        elif not goal or match.group(2) not in goal["criteria"]:
            error("BROKEN_REFERENCE", reference, "Goal success criterion not found in raw/goals/")
        elif goal["status"] != "approved":
            story.blockers += 1
            report.add("BLOCKER", "GOAL_NOT_APPROVED", story.path, story.line(reference), reference,
                       f"Goal status is {goal['status'] or 'missing'}, not approved")

    for dependency in story.depends_on:
        if dependency not in story_ids:
            error("BROKEN_REFERENCE", dependency, "depends_on target Story not found in wiki/workitems/")

    links = contract.get("links") if isinstance(contract.get("links"), dict) else {}
    for source, link in links.items():
        if source not in declared:
            error("BROKEN_REFERENCE", source, "link source is not a declared view item")
            continue
        if not isinstance(link, dict) or not set(link) <= LINK_TARGETS:
            error("CONTRACT_FIELD_INVALID", source, f"link may only use {', '.join(sorted(LINK_TARGETS))}")
            continue
        for key, wanted in (("rules", "business_logic"), ("acceptance", "acceptance")):
            for target in link.get(key, []):
                if declared.get(target) != wanted:
                    error("BROKEN_REFERENCE", target, f"{source} {key} target is not a declared {wanted} item", f'"{target}"')
        for target in link.get("tests", []):
            if not target.startswith("TC-") or target not in defined:
                error("BROKEN_REFERENCE", target, f"{source} test has no matching TC-* section heading", f'"{target}"')
        for target in link.get("goal", []):
            if target not in story.goal_criteria:
                error("BROKEN_REFERENCE", target, f"{source} goal is not in this Story's goal_success_criteria", f'"{target}"')

    covered = set()
    for item, view in declared.items():
        link = links.get(item) if isinstance(links.get(item), dict) else {}
        if view == "acceptance":
            if not link.get("tests"):
                error("AC_WITHOUT_TEST", item, "acceptance criterion has no linked executable test")
            if link.get("verification") not in VERIFICATION:
                error("AC_WITHOUT_VERIFICATION", item, f"verification must be one of {', '.join(VERIFICATION)}")
            if not link.get("goal"):
                error("AC_WITHOUT_GOAL", item, "acceptance criterion does not trace a Goal success criterion")
            covered.update(link.get("goal", []))
        elif view == "prototype" and item.startswith("UI-") and not link.get("acceptance"):
            error("PROTOTYPE_WITHOUT_ACCEPTANCE", item, "prototype must link at least one acceptance criterion")
    for reference in story.goal_criteria:
        if reference not in covered:
            error("GSC_NOT_COVERED", reference, "no acceptance criterion in this Story covers the criterion")

    questions = contract.get("open_questions", [])
    if not isinstance(questions, list):
        error("CONTRACT_FIELD_INVALID", "open_questions", "open_questions must be a list")
        questions = []
    for question in questions:
        if isinstance(question, dict) and question.get("blocking") is True:
            story.blockers += 1
            subject = str(question.get("id") or "question")
            report.add("BLOCKER", "BLOCKING_QUESTION", story.path, story.line(subject), subject,
                       str(question.get("text") or "blocking question is open"))
    return covered


def check_cycles(stories, report):
    graph = {story.id: story.depends_on for story in stories}
    by_id = {story.id: story for story in stories}
    seen, active, reported = set(), [], set()

    def visit(node):
        if node in active:
            cycle = active[active.index(node):] + [node]
            key = frozenset(cycle)
            if key not in reported:
                reported.add(key)
                for member in set(cycle):
                    if member in by_id:
                        by_id[member].errors += 1
                story = by_id[cycle[0]]
                report.add("ERROR", "DEPENDENCY_CYCLE", story.path, story.line(cycle[1]), " -> ".join(cycle),
                           "Story dependencies must be acyclic")
            return
        if node in seen or node not in graph:
            return
        active.append(node)
        for dependency in graph[node]:
            visit(dependency)
        active.pop()
        seen.add(node)

    for node in sorted(graph):
        visit(node)


def run(root, require_goal_coverage):
    report = Report(root)
    goals = load_goals(root)
    stories = load_stories(root)
    story_ids = {story.id for story in stories}
    packs = {}
    for pack in load_packs(root):
        decisions, brief = check_pack(pack, goals, report)
        packs[pack.id] = {"decisions": decisions, "brief": brief, "errors": pack.errors}
    checked, covered = [], set()
    for story in stories:
        if not story.blocks:
            report.add("INFO", "LEGACY_STORY_NOT_CHECKED", story.path, 1, story.id,
                       "no requirement-contract block; not migrated or checked")
            continue
        checked.append(story)
        contract, declared = check_structure(story, report)
        if contract is not None:
            covered |= check_references(story, contract, declared, goals, story_ids, report)
            check_solution_links(story, contract, packs, report)
    check_cycles(checked, report)

    for story in checked:
        if story.blockers and story.status in CLAIMS_READY:
            story.errors += 1
            report.add("ERROR", "READY_STATUS_WITHOUT_READINESS", story.path, 1, story.id,
                       f"status {story.status} claims readiness while blockers remain")
    gaps = []
    for goal_id, goal in sorted(goals.items()):
        if goal["status"] != "approved":
            continue
        for criterion in sorted(goal["criteria"]):
            reference = f"{goal_id}#{criterion}"
            if reference not in covered:
                gaps.append(reference)
                if require_goal_coverage:
                    report.add("ERROR", "GOAL_COVERAGE_GAP", goal["path"], 1, reference,
                               "approved Goal criterion is not covered by any checked Story acceptance")
    verdicts = {story.id: "NOT_READY" if story.errors or story.blockers else "READY" for story in checked}
    pack_verdicts = {pack_id: "INVALID" if pack["errors"] else "VALID" for pack_id, pack in packs.items()}
    errors = sum(1 for finding in report.findings if finding["severity"] == "ERROR")
    return report, verdicts, pack_verdicts, gaps, len(stories) - len(checked), errors


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=".", help="workflow root containing raw/ and wiki/")
    parser.add_argument("--require-goal-coverage", action="store_true",
                        help="fail when an approved Goal criterion has no covering Story acceptance")
    parser.add_argument("--json", action="store_true", help="print a JSON report")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    report, verdicts, pack_verdicts, gaps, legacy, errors = run(root, args.require_goal_coverage)
    summary = {
        "checked": len(verdicts), "legacy": legacy, "solution_packs": len(pack_verdicts),
        "ready": sum(1 for verdict in verdicts.values() if verdict == "READY"),
        "errors": errors,
        "blockers": sum(1 for finding in report.findings if finding["severity"] == "BLOCKER"),
        "gaps": len(gaps),
    }
    if args.json:
        json.dump({"findings": report.findings, "stories": verdicts, "solution_packs": pack_verdicts,
                   "goal_gaps": gaps, "summary": summary},
                  sys.stdout, ensure_ascii=False, indent=2)
        print()
    else:
        for finding in report.findings:
            print(f"{finding['severity']} {finding['code']} {finding['location']} {finding['subject']} {finding['message']}")
        for pack_id, verdict in sorted(pack_verdicts.items()):
            print(f"{pack_id} {verdict}")
        for story_id, verdict in sorted(verdicts.items()):
            print(f"{story_id} {verdict}")
        for gap in gaps:
            print(f"GAP {gap} not covered by any checked Story acceptance")
        print("SUMMARY " + " ".join(f"{key}={value}" for key, value in summary.items()))
        print("Report only: business meaning, value, whether a person really decided, and acceptance")
        print("still need human/Agent review.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
CHECK_REQUIREMENTS_PY

chmod +x .ai/tools/check_requirements.py

fi

if [ ! -s "schema/templates/learning.md" ]; then

cat > schema/templates/learning.md <<'EOF'
---
id: LRN-XXX
type: learning
title:
category: pitfall
status: candidate
derived_from: []
evidence: []
applies_when:
do_not_apply_when:
created_at:
last_verified_at:
reuse_evidence: []
human_confirmation:
assets: []
reuse_benefit_status: unmeasured
supersedes: []
---
# Learning

## Observation and Evidence

What happened? Link the source Task and actual result, not only a test definition.

## Root Cause / Reusable Method

## Prevention and Verification

## Reusable Asset (if justified)

Reference an existing check, script, component, template or Skill with its entry
point, prerequisites, expected result and limits. Do not duplicate the asset or
create one just to fill this section; ordinary lessons may have no asset.

## Reuse History

| Date | Later Task / Evidence | Asset / Reused Steps | Adaptation | Verification | Effort / Rework / Maintenance | Change to Lesson |
|---|---|---|---|---|---|---|

Status: candidate, validated or deprecated. Category: pattern or pitfall.
Validated requires successful reuse evidence or explicit human confirmation.
Human confirmation is not a measured gain. Reuse benefit is unmeasured unless
comparable baseline and reuse measurements include known costs and evidence.
Missing measurements and legacy records without a benefit field mean unmeasured.
EOF

fi

if [ ! -s "WORKING_STYLE.md" ]; then

cat > WORKING_STYLE.md <<'EOF'
# Working Style

Human-confirmed collaboration preferences live here. Read before work.
Current user instructions take precedence; change this file only when authorized.
Fill in preferences explicitly with the user, rather than inferring them from a
single task. Reusable solutions and pitfalls belong in `wiki/learning/`.
EOF

fi

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

## delivery-loop

Authorized Task → Small Change → Actual Verification → Acceptance → Learning

Read `WORKING_STYLE.md` before work; retrieve matching `wiki/learning/` records.
Invocation is explicit through the repository AGENTS.md routes; native Agent
installation is a separate environment-specific step.


Not implemented in v0.4:

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

## Reusable Methods and Pitfalls

Read `WORKING_STYLE.md`; search canonical `wiki/learning/LRN-*.md` by the
current problem, conditions and affected components. New lessons are candidates,
not universal rules. Verify applicability and append evidence when reused.

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
    templates/learning.md

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


# Stage contracts are embedded to keep script-only bootstrap self-contained.
# Keep in sync with the two source documents; check_bootstrap.py verifies equality.

if [ ! -s "dev-flow.yaml" ]; then
cat > "dev-flow.yaml" <<'DEV_FLOW_YAML'
# Agent-reviewed workflow contract; no automatic Harness/CI gate engine is installed.
# Custom DSL, not a native Codex configuration format. See Goal_Constrained_Dev_Flow_v1.md.
apiVersion: harness.example/v1alpha1
kind: DevFlow
metadata:
  name: goal-constrained-dev-flow
  version: 1.0.0
spec:
  goalContract: raw/goals/GOAL-*.md
  integration:
    workItems: wiki/workitems/
    decisions: wiki/decisions/
    goalCriteria: GOAL-XXX#GSC-XX
    workItemLifecycle: schema/workitem-types.yaml
    gateExecution: agent_review_with_recorded_evidence
    automaticEnforcement: false
    applicability: declare_per_story_before_execution
    exemptionRequiresApproval: true
    paths: reuse_existing_project_paths_and_record_mapping
    multiRepo: record_repo_owner_dependencies_and_cross_repo_acceptance
    requirementContract: requirement-contract/v1 block in wiki/workitems/ Stories
    requirementCheck: .ai/tools/check_requirements.py  # report only; never changes status
    solutionPacks: wiki/solutions/SOL-*.md  # Brief, Research, Decision, Solution
    humanDecisionRequired: true  # AI recommends; a person decides
  executive:
    role: GoalExecutive
    modes: [goal_alignment, drift_review, acceptance_review]
    statuses: [ON_TRACK, AT_RISK, BLOCKED]
    requireApprovalFor:
      - goal_change
      - hard_constraint_change
      - critical_scope_change

  traceability:
    mainLine: [goal, brief, research, decision, solution, story, task]
    chain: [goal, brief, research, decision, solution, story, acceptanceCriterion, function, design, test, implementation, evidence]
    enforceUniqueIds: true
    requireStoryToGoalLink: true
    requireAcceptanceCriteriaToTests: true

  stages:
    - id: PM
      owner: ProductManagerAgent
      dependsOn: [GOAL_BASELINE]
      outputs:
        - docs/product/user-story-map.md
        - docs/product/menu-design.yaml
        - docs/product/modules.yaml
        - docs/product/functions.yaml
      gate:
        id: PM_GATE
        checks:
          - files_exist
          - every_story_has_goal_ref
          - every_story_has_acceptance_criteria
          - menu_module_function_consistency
          - no_unapproved_goal_changes

    - id: TECH
      owner: TechArchitectAgent
      dependsOn: [PM_GATE]
      outputs:
        - docs/architecture/platform.mmd
        - docs/architecture/features.mmd
        - prototypes/app-shell.html
        - prototypes/pages/*.html
        - docs/architecture/database.md
        - db/schema.sql
        - contracts/openapi.yaml
      gate:
        id: TECH_GATE
        checks:
          - files_exist
          - mermaid_syntax_valid
          - required_functions_have_design
          - api_contract_valid
          - database_contract_consistent
          - prototype_covers_core_journeys
          - no_unapproved_goal_changes

    - id: TEST
      owner: TestAgent
      dependsOn: [TECH_GATE]
      outputs:
        - tests/unit/**
        - docs/testing/traceability.yaml
        - docs/testing/red-baseline.md
      optionalOutputs:
        - tests/component/**
        - tests/contract/**
        - tests/e2e/**
      gate:
        id: TEST_RED_GATE
        checks:
          - all_critical_acceptance_criteria_have_tests
          - tests_executable
          - red_due_to_unimplemented_behavior
          - no_placeholder_assertions

    - id: DEV
      owner: DeveloperAgent
      dependsOn: [TEST_RED_GATE]
      outputs:
        - src/**
        - docs/development/implementation-map.yaml
        - reports/test-results/**
        - reports/acceptance-evidence.md
      gate:
        id: DEV_GREEN_GATE
        checks:
          - unit_tests_pass
          - contract_tests_pass_if_applicable
          - integration_and_e2e_pass_for_core_journeys
          - migrations_valid_if_applicable
          - no_unapproved_test_weakening
          - evidence_matches_current_revision

  finalGate:
    id: GOAL_ACCEPTANCE
    owner: GoalExecutive
    require: [DEV_GREEN_GATE, all_hard_constraints_satisfied, all_critical_stories_accepted]
    humanApprovalRequired: true
    acceptedOutcome: ACCEPTED

  policies:
    devMayEditTestExpectations: false
    testExpectationChangeRequiresReview: [ProductManagerAgent, TechArchitectAgent]
    missingEvidenceBlocksAcceptance: true
    storyLevelParallelism: requires_explicit_authorization
    integrationGateRequiredBeforeRelease: true
DEV_FLOW_YAML
fi

if [ ! -s "Goal_Constrained_Dev_Flow_v1.md" ]; then
cat > "Goal_Constrained_Dev_Flow_v1.md" <<'DEV_FLOW_GUIDE'
# Dev Flow v1.0 — 目标约束、测试先行的 Agent 研发流程

> 适用对象：以软件产品/应用为交付目标的单 Agent 或多 Agent 研发项目。
> 核心原则：Goal Contract 不因任务拆分而失效；上游交付有契约，下游实现有证据；Test 在 Dev 之前，执行 RED → GREEN → REFACTOR。

## 1. 目标与边界

本流程服务于一个全局目标（Goal）。Goal Executive 负责解释和维护目标，PM、Tech、Test、Dev 负责各阶段交付。同一个 Agent 可以顺序承担这些职责，不自动启动其他 Agent。

本轮接入的是流程契约和 Agent 审查指引：各 Gate 由 Agent 根据实际检查结果记录 PASS / FAIL / BLOCKED / NOT_RUN；没有安装自动 Harness、CI 强制门禁或多 Agent 调度器。Hooks 仍只提醒，不阻断工具、不批准变更。缺失必需证据时不得宣称阶段通过。

### 与 AI-Native-Scrum 的衔接

| 阶段 | 现有入口 / 正本 | 交接要求 |
|---|---|---|
| Goal Baseline | `.ai/skills/goal-intake/SKILL.md`；`raw/goals/GOAL-*.md` | 明确人工批准、revision、GSC-*、Protected Constraints |
| Brief → Research → Decision → Solution | `.ai/skills/solution-pack/SKILL.md`；`wiki/solutions/SOL-*.md` | AI 起草 Brief 并经人确认；Research 证据可回查并标明性质；AI 给出推荐，人做选择并留确认记录；Solution 承接已决定的方向 |
| PM | `.ai/skills/goal-to-backlog/SKILL.md`、`.ai/skills/story-refine/SKILL.md`；`wiki/workitems/` | Story、AC、Goal 关联及适用的菜单/模块/功能映射；六维需求契约经 `.ai/tools/check_requirements.py` 报告 READY（仅结构与引用） |
| Tech | `.ai/skills/story-to-tasks/SKILL.md` | 检查已确认的设计与接口契约，分配设计、测试、实现和跨仓集成任务；未通过 Tech Gate 不进入正式测试交接 |
| Test → Dev | `.ai/skills/delivery-loop/SKILL.md` | 可执行的行为 RED → 最小实现 GREEN → 重构及回归；保留原始失败证据 |
| Goal Acceptance | `.ai/skills/lint/SKILL.md`、`delivery-loop` | 汇总原始目标、硬约束及跨 Story/跨仓证据，交人工最终验收 |

Goal Contract 唯一正本是 `raw/goals/GOAL-*.md`，不另建 `.goal/contract.yaml`。Story/Task 沿用 `schema/id-policy.yaml` 的标识和 `GOAL-XXX#GSC-XX` 关联；决策与获批变更记录在 `wiki/decisions/` 并引用 Goal revision。目标变更先在 `intake/` 待审，批准后才更新正本。

以下产物清单是完整软件应用的基线。实施前按 Story 声明 Web、数据库、API、自动化测试等适用性和实际路径；复用现有目录，不搬迁已有代码。脚本、文档、无 UI 或无数据库项目，可以用已有产物/人工验证替代不适用项，但须记录理由、验证方式并获得明确批准；不得默默跳过关键 AC 或以空文件通过。初始化只安装流程资料，不创建产品设计、测试占位或业务代码。

多子仓库项目可在没有 `.git` 的协调根目录使用本流程。根目录记录全局目标与跨仓追溯，每项设计、Task 和证据标明所属子仓库、责任人、依赖及验收命令。Git 证据按子仓库记录各自 revision；非 Git 文件记录路径与内容哈希。子仓库规则仍适用，不递归初始化、改写或自动提交子仓库。局部测试通过后，仍须验证跨仓接口及全局核心旅程。

主线：Goal → Brief → Research → Decision → Solution → Story → Task。PM / Tech / Test / Dev 是贯穿这条主线的职责，不是另一套并行流程；Decision 不代替 Goal 批准或最终验收。

核心不变量：

1. 原始目标、关键范围、不可妥协约束只可通过受控的 Goal Change Request 变更。
2. 每个 User Story 都有稳定 ID、验收条件和 Goal 关联。
3. 每个技术设计对象均能追溯到模块/功能/故事；必要的基础设施例外必须说明理由。
4. 每个可测试的验收条件都有对应测试（Unit/Component/Contract/Integration/E2E 中一种或多种）。
5. 测试不能为使开发通过而被单方面删除、弱化或篡改。
6. 局部完成不代表整体交付；最终验收必须回到全局目标。

## 2. 总体流程

```mermaid
flowchart LR
    G[Goal Contract\n目标基线] --> P[PM\n需求设计]
    P --> GP{Gate P\n需求基线}
    GP -- PASS --> T[Tech\n技术方案与契约]
    GP -- FAIL --> P
    T --> GT{Gate T\n技术可实现}
    GT -- PASS --> Q[Test\nTDD 测试先行]
    GT -- FAIL --> T
    Q --> GQ{Gate Q\nRED 验证}
    GQ -- PASS --> D[Dev\nGREEN / REFACTOR]
    GQ -- FAIL --> Q
    D --> GD{Gate D\n测试与证据}
    GD -- FAIL --> D
    GD -- PASS --> A{Goal Executive\n全局验收}
    A -- PASS --> R[Release Ready]
    A -- FAIL --> P
```

注意：图表示逻辑依赖，不意味着同一时刻只能有一个角色工作。需求与接口基线确认后，各 User Story 可以按纵向切片推进；并行 Agent 工作另需明确授权，发布时统一验证全局目标。

## 3. 各角色交付契约

### 3.1 PM — 产品需求设计

**强制交付**

| 交付物 | 建议路径 | 最少应包括 |
|---|---|---|
| 用户故事地图 | `docs/product/user-story-map.md` | Persona、用户活动、旅程、Story ID、优先级、版本切片、验收条件 |
| 菜单设计 | `docs/product/menu-design.yaml` | 导航层级、菜单 ID、页面 ID、角色权限、对应功能 ID |
| 模块设计 | `docs/product/modules.yaml` | Module ID、责任边界、依赖、业务对象、功能清单 |
| 功能设计 | `docs/product/functions.yaml` | Function ID、触发条件、输入、输出、业务规则、异常状态、关联 Story ID |

**Gate P：** 所有 in-scope Story 有验收条件和 Goal 映射；菜单—页面—模块—功能关系不冲突；业务术语明确；待确认事项可见而未被默认当作事实；范围变更获得批准。

### 3.2 Tech — 架构与设计

**强制交付**

| 交付物 | 建议路径 | 最少应包括 |
|---|---|---|
| 技术基座架构（Mermaid） | `docs/architecture/platform.mmd` | 技术栈、客户端、服务端、存储、集成、鉴权、观测与边界 |
| 应用功能架构（Mindmap） | `docs/architecture/features.mmd` | 模块、页面、功能分层，以及 PM Function ID |
| App Shell（HTML） | `prototypes/app-shell.html` | 全局布局、导航、权限入口、状态区、响应式约束 |
| 页面示例（HTML） | `prototypes/pages/*.html` | 至少覆盖关键页面类型与主要交互状态 |
| 后端数据库设计 | `docs/architecture/database.md` + `db/schema.sql` | 数据实体、主外键、约束、索引、迁移策略、数据字典 |
| **API / Interface Contract（补充）** | `contracts/openapi.yaml` 或 `contracts/interfaces.*` | 请求/响应、错误码、DTO、领域接口、版本约束 |

**Gate T：** Story / Function 能定位到对应技术实现边界；界面原型覆盖主要用户路径；测试团队有稳定可依赖的接口契约；数据库设计支撑业务规则；架构决策未违背 Goal Contract。对于非 Web 应用，HTML 交付的豁免应显式说明并经批准。

### 3.3 Test — 测试先行（TDD）

**强制交付**

- `tests/unit/**`：由用户故事及其验收条件推导的单元测试。
- `tests/component/**`：必要的 UI/组件行为测试。
- `tests/contract/**`：必要的接口契约测试。
- `tests/e2e/**`：覆盖核心用户旅程的端到端测试（可在对应代码具备后运行）。
- `docs/testing/traceability.yaml`：Story → AC → Test 的可机器检查映射。
- `docs/testing/red-baseline.md`：测试先于实现的 RED 证据和失败原因。

**TDD 细则：**

1. 按 Story 验收条件拆分测试，不直接把高层故事机械翻译为单个 Unit Test。
2. 先确认 Tech 的 API/Interface Contract；由 Tech 提供可加载但未实现业务行为的接口骨架（仅在必要时）。
3. RED 应由行为尚未实现导致的断言失败产生；语法错误、配置错误、缺少依赖和无法导入模块不算合格 RED。
4. 固化预期行为与测试证据；Dev 不得擅自修改/删除测试以换取 GREEN。
5. 发现用户故事或接口契约冲突时，提出澄清/变更请求，而不是悄悄调整期望。

**Gate Q：** 关键 AC 有测试且 Traceability 完整；测试套件可运行；RED 失败原因正确；测试断言不是空断言或恒真断言。

### 3.4 Dev — 基于测试与设计开发

**强制交付**

- `src/**`：按 Tech 契约实现的产品代码。
- `db/migrations/**`：数据库变更与兼容处理（若适用）。
- `docs/development/implementation-map.yaml`：Function/Test → 实现位置的追溯映射。
- `reports/test-results/**`：自动化测试结果。
- `reports/acceptance-evidence.md`：构建、单测、接口、E2E、核心演示与已知限制证据。

**TDD 循环：** RED（由 Test 交付）→ GREEN（最小满足断言的实现）→ REFACTOR（在测试保护下改善设计）→ Regression（回归测试）。

**Gate D：** 必须的单测/契约测试通过；回归测试通过；数据库迁移可验证；没有未审批的目标变更；证据与目标覆盖矩阵完整。对于尚无法自动化的条件，记录人工验证步骤和责任人。

## 4. Goal Executive 跨阶段职责

Goal Executive 并不是第五个开发角色。它持续检查：

- `goal_alignment`：当前设计、测试、代码是否仍满足原始 Goal；
- `scope_integrity`：有无未审批地删除、弱化或新增范围；
- `traceability`：Goal → Story → Function → Design → Test → Code → Evidence 能否贯通；
- `unresolved_risks`：未解决的问题是否会影响最终目标；
- `acceptance`：是否有足够证据可以宣称目标完成。

目标评估状态：`ON_TRACK` / `AT_RISK` / `BLOCKED`。`ACCEPTED` 仅记录人工最终验收结果，不是 Agent 自评状态，也不是工作项的 `status`。语义偏离由 Goal Executive 做解释性判断；未来自动门禁需要另行实现和验证，当前以实际执行证据及人工授权为准。

## 5. 阶段门禁

| 门禁 | 触发时机 | 强制校验 | 失败处理 |
|---|---|---|---|
| G0 Goal Baseline | 正式规划前 | Goal Contract、范围与不可变约束已明确 | 请求澄清，禁止下游进入正式实施 |
| G1 PM Gate | PM 交付后 | Story—AC—Goal 完整；菜单/模块/功能映射 | 退回 PM |
| G2 Tech Gate | Tech 交付后 | 所有强制技术交付物存在；接口及数据契约可测试 | 退回 Tech |
| G3 Test RED Gate | Test 交付后 | 测试覆盖 AC、测试可运行、行为 RED 有效 | 退回 Test/Tech |
| G4 Dev GREEN Gate | Dev 交付后 | 单测/契约/集成/必要 E2E 全通过，证据齐全 | 退回 Dev，必要时发起设计变更 |
| G5 Goal Acceptance | 版本交付前 | 原始目标约束满足；审查所有风险/变更 | 未通过则不得标记 Release Ready |

**不要把测试数量或通过率单独当作目标完成的替代指标。** 核心硬约束必须逐项通过。

## 6. 追溯模型与样例

沿用 `schema/id-policy.yaml` 的稳定标识：Goal 使用 `GOAL-*`、Story 使用 `STORY-*`、Task 使用 `TASK-*`；Story 内的 AC 使用带 Story 上下文的引用。模块、功能、测试 ID 是产物内部标识，不自行扩展实体类型。

```text
GOAL-001  完整的双人五子棋游戏
  └─ STORY-003  玩家连续五子时判定胜利（goal_success_criteria: [GOAL-001#GSC-01]）
      ├─ AC-003-01  横向、纵向及双对角线均可判定
      ├─ FUNC-012  evaluateWinner(board, lastMove)
      ├─ TC-021  test_horizontal_five_wins
      ├─ TC-022  test_diagonal_five_wins
      └─ CODE     src/domain/win-rules.ts
```

门禁检查不应只验证 ID 存在，更应验证 Test 覆盖了 AC 的行为、Dev 实现与接口契约一致、Evidence 能对应具体代码版本。

## 7. 工作项流转与返工机制

阶段审查顺序为 `GOAL_BASELINE → PM_GATE → TECH_GATE → TEST_RED_GATE → DEV_GREEN_GATE → GOAL_ACCEPTANCE`，阶段结论记录于工作项的 Execution Evidence，并关联证据路径。

工作项 `status` 继续遵守 `schema/workitem-types.yaml`：`proposed → backlog → refining → ready_for_task_decomposition → ready → in_progress → review → done`（`planned` 等其他合法状态按既有规则使用）。精炼完成不等于 Ready Pool、GREEN 不等于业务验收；不得把阶段 ID 或 `RED_VERIFIED`、`ACCEPTED` 写入 `status`。目标通过后也不自动修改 Goal 的 `approved` 状态。

如果发现问题：

- **目标变化**：必须创建 `GoalChangeRequest`，批准后更新 Goal Contract 版本，并标记所有相关交付物需要重审。
- **需求缺漏**：回到 PM 更新 Story/AC，显式记录受影响的 Tech/Test/Dev 工作项需复核，保留历史证据；没有自动失效引擎。
- **接口变化**：回到 Tech 更新 Contract，Test 必须确认旧断言是否仍成立。
- **代码缺陷**：Dev 修复，不能擅改测试来掩盖问题。
- **测试预期错误**：Test 修改测试，但要记录原因，并由 PM/Tech 审核行为是否符合原目标。

获得授权后允许以 Story 为单位并行推进，不能绕开相应 Story 的 Gate。合并与发布时必须进行跨 Story 的全局回归；Release Ready 不授权提交、推送或部署。

## 8. 仓库推荐目录

```text
project/
├─ AGENTS.md
├─ dev-flow.yaml
├─ Goal_Constrained_Dev_Flow_v1.md
├─ raw/goals/          # 批准的 Goal Contract
├─ intake/             # 待审批变更
├─ wiki/
│  ├─ workitems/        # Story / Task 正本
│  └─ decisions/        # 决策与获批变更
├─ docs/
│  ├─ product/
│  │  ├─ user-story-map.md
│  │  ├─ menu-design.yaml
│  │  ├─ modules.yaml
│  │  └─ functions.yaml
│  ├─ architecture/
│  │  ├─ platform.mmd
│  │  ├─ features.mmd
│  │  └─ database.md
│  ├─ testing/
│  │  ├─ traceability.yaml
│  │  └─ red-baseline.md
│  └─ development/
│     └─ implementation-map.yaml
├─ contracts/
│  └─ openapi.yaml
├─ prototypes/
│  ├─ app-shell.html
│  └─ pages/
├─ db/
│  ├─ schema.sql
│  └─ migrations/
├─ src/
├─ tests/
│  ├─ unit/
│  ├─ component/
│  ├─ contract/
│  └─ e2e/
└─ reports/
   ├─ test-results/
   └─ acceptance-evidence.md
```

## 9. 当前落地边界与后续建议

1. 本轮已接入 AI-Native-Scrum 的 Skill、正本边界和工作项状态；`dev-flow.yaml` 是供 Agent 阅读的自定义 DSL，不是原生可执行配置。
2. 在获批的实际 Story 上先用人工/Agent 审查执行阶段交接；五子棋仅为示例，不是初始化后的默认任务。
3. Bootstrap 自检只验证生成与有限流程合同，不验证真实项目的全部门禁。自动验证器、CI Required Check、多 Agent 调度及 MCP 服务均需另行批准、实现和验证。
4. 不把本轮流程接入当作自动门禁、真实产品验收或发布成功。

## 10. 实际项目的阶段审查准则（需执行并记录证据）

- 无关联 Goal 的正式 Work Item 被 Gate 拒绝。
- 删除一个必需的 PM/Tech 交付物，阶段 Gate 明确失败。
- 关键 AC 没有测试，Test Gate 明确失败。
- Dev 试图删除测试或未经批准改变 AC，触发审查。
- 某个 Story 本地通过，但跨模块 E2E 或终局规则失败时，Goal Acceptance 拒绝发布。
- 所有强制条件满足、测试结果可复现且变更记录完整时，可以进入人工最终验收。
DEV_FLOW_GUIDE
fi

# ============================================================
# Root README
# ============================================================

if [ ! -s "README.md" ]; then

cat > README.md <<'EOF'
# AI Native Software Engineering Knowledge Repository

This repository manages knowledge from project intent to engineering-ready
Tasks, then supports authorized delivery, verification and evidence-backed learning.

The workflow root does not need Git. Empty folders, existing non-Git/Git projects
and non-Git coordination roots with child repositories are supported. Run the
initializer in this intended root; it does not run git init or initialize children.
Existing nonempty files are preserved; incompatible old files need an approved
comparison and update rather than repeated initialization or a forced READY.

## Goal-constrained delivery

Read `Goal_Constrained_Dev_Flow_v1.md` and `dev-flow.yaml`:
Goal Baseline → PM → Tech → Test RED → Dev GREEN → human Goal Acceptance.
Use the existing Skills and schema lifecycle, and `raw/goals/` as the only Goal
Contract source. Declare artifact applicability and reuse project paths; no
business scaffolding is created by initialization. Record repository ownership,
dependencies and cross-repository evidence when coordinating multiple repos.
The YAML is an Agent-reviewed custom DSL; no automatic Harness or CI gate
engine is installed. READY describes bootstrap readiness, not product acceptance.

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
            ↓
     Authorized Delivery
            ↓
    Verification / Acceptance
            ↓
    Reusable Methods / Pitfalls

## Layers

    schema/       Governance
    intake/       Pre-approval working memory
    raw/          Approved Evidence
    wiki/         Canonical Knowledge
    generated/    Computed Views
    .ai/skills/   Knowledge Workflows
    .codex/        Advisory Goal context Hooks
    site/         Presentation
    WORKING_STYLE.md  Human-confirmed collaboration preferences

Read `.ai/skills/delivery-loop/SKILL.md` for execution and learning.
Canonical lessons live in `wiki/learning/`; use `schema/templates/learning.md`.
These workflows guide Agents; file generation does not prove actual delivery.
`.codex/hooks.json` adds non-blocking Goal context and evidence reminders. Hooks
do not approve scope, enforce policy or prove acceptance.

Sprint Planning is intentionally excluded from v0.4.

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
echo "Delivery and learning entry: .ai/skills/delivery-loop/SKILL.md"
echo "Existing non-empty files were retained. For upgrades, compare with a fresh temporary initialization before applying an approved diff."

echo ""
