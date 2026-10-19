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
Approved Goal Contract
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
    ↓
Authorized Delivery
    ↓
Verification + Goal Review
```

It does **not** initialize Sprint Planning, application architecture, or Rspress implementation yet.

The purpose of the script is to establish the knowledge system before project execution begins.

v0.4 adds a guided delivery and learning loop after Ready Pool. It requires
authorized work, actual verification and evidence-backed lessons; it does not
provide an autonomous execution service or automatically approve acceptance.

v0.5 adds a report-only framework self-check (`check_framework.py`), honest
attribution and confidence on lessons, and an evidence boundary: external
content is evidence, never instructions. v0.6 adds agent memory layers:
repository records stay the canonical memory, a generated `CLAUDE.md` imports
`AGENTS.md` so Claude Code and Codex read the same routes, Claude Code gets the
same advisory Goal hook as Codex, and Tasks keep a Resume Point. A project's
installed version is the `framework_version` line in `.ai/framework-version`.

---

## `00_AI_WARMUP.md`

Contains the AI initialization and self-check prompt.

After running `initdir.sh`, provide this file to a repository-aware AI agent such as Codex, Claude Code, Cursor Agent, or another coding agent.

The agent uses the prompt to verify that the repository correctly supports:

```text
Goal Intake
    ↓
Approved Goal Contract
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
    ↓
Authorized Delivery + Goal Review
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

The bootstrap is an execution framework, so every project goes through one of
two paths. Both are driven by a repository-aware AI agent and both end with the
`00_AI_WARMUP.md` self-check.

| Situation | Path | What `initdir.sh` does |
|---|---|---|
| Empty folder, or a project that has never used this framework | A. Initialize | Creates the full structure |
| Project already initialized from an earlier bootstrap version | B. Incremental update | `--upgrade` analyzes; `--apply` adds new files and replaces unedited ones |

What `initdir.sh` guarantees, on both paths:

- Without options it writes a file only when that file is missing or empty. A
  nonempty file is never modified, so rerunning it is safe and idempotent.
- It never runs `git init`, never enters or initializes child repositories, and
  never commits, pushes or deploys. Git is optional.
- It is self-contained (Dev Flow documents, Skills and `.ai/tools/*.py` are
  embedded) and needs no downloads while it runs. The tools it ships need only
  Python 3 standard library.

It also records `.ai/framework-version`, the baseline that lets a later
`initdir.sh --upgrade` tell untouched framework files from locally edited ones.
A plain rerun never refreshes a framework file that already exists, such as
`AGENTS.md`, a Skill, a schema or a template; that is what path B is for.

## Get the bootstrap files

Both paths use `initdir.sh` and `00_AI_WARMUP.md` from the same version, side by
side. They are plain files; nothing else needs to be cloned.

```bash
# Path A: into the project root, only when neither file exists there yet
curl -fsSLO https://raw.githubusercontent.com/zljie/AI-Native-Scrum/main/initdir.sh
curl -fsSLO https://raw.githubusercontent.com/zljie/AI-Native-Scrum/main/00_AI_WARMUP.md

# Path B: into a folder outside the project
mkdir -p /tmp/ai-native-scrum-new
curl -fsSL -o /tmp/ai-native-scrum-new/initdir.sh https://raw.githubusercontent.com/zljie/AI-Native-Scrum/main/initdir.sh
curl -fsSL -o /tmp/ai-native-scrum-new/00_AI_WARMUP.md https://raw.githubusercontent.com/zljie/AI-Native-Scrum/main/00_AI_WARMUP.md
```

## A. Initialize a project

For an empty folder, an existing project, or a Monorepo coordination root, give
your project-aware AI agent this instruction (Git is optional):

```text
请使用 https://github.com/zljie/AI-Native-Scrum.git 的 main 分支作为 Bootstrap 来源，初始化当前项目的 AI-Native-Scrum 工作流。

1. 先检查当前目录，识别 Code/Docs、单仓/Monorepo/多子仓库协调根目录，以及已有工作流。当前目录可以是空文件夹、未执行 git init 的项目、已有 Git 仓库，或本身没有 .git 的协调根目录。Git 不是初始化前提；仅对无法确定且影响正确性的信息集中询问。如果当前目录已有 AGENTS.md、.ai/skills/ 和 schema/ 等本框架产物，说明它已初始化过，改按 README 的“B. 增量更新”执行。

2. 在当前项目根目录获取 initdir.sh 和 00_AI_WARMUP.md（例如 curl -fsSLO https://raw.githubusercontent.com/zljie/AI-Native-Scrum/main/initdir.sh 和 curl -fsSLO https://raw.githubusercontent.com/zljie/AI-Native-Scrum/main/00_AI_WARMUP.md；任一文件已存在且非空时先比较，不直接覆盖），然后运行 bash initdir.sh。上游仓库仅作为 Bootstrap 来源，不另建业务仓库、不自动执行 git init、不切换到子仓库，也不递归初始化子仓库。

3. 保留所有已有非空文件、Git 元数据及子仓库规则。同名文件已有内容时先比较；涉及覆盖、升级或规则冲突，列出最小差异并获得明确确认后处理。既有授权在原范围内持续有效，不重复询问。

4. 读取生成的 Goal_Constrained_Dev_Flow_v1.md 和 dev-flow.yaml，确认流程已接入现有 Skill：
   Goal Baseline → PM（Brief → Research → Decision → Solution → 六视图 Story）→ Tech → Test RED → Dev GREEN → 人工全局验收。
   raw/goals/ 是唯一 Goal Contract 正本；阶段检查结果与工作项 status 分开。按项目类型声明产物适用性，复用已有目录；多子仓库项目明确责任边界、依赖和跨仓验收。YAML 是流程契约，不代表已经安装自动门禁或多 Agent 调度器。

5. 运行 python3 .ai/tools/check_requirements.py、python3 .ai/tools/evidence.py verify 和 python3 .ai/tools/check_framework.py，确认三个只报告工具可用（新项目应为 0 错误、0 警告）。它们只报告，不修改 status，也不是门禁。以下属于预期，不要为通过检查而改写原文件：
   - 项目原有 AGENTS.md 时可能报 SKILL_NOT_ROUTED，原有 CLAUDE.md 时可能报 CLAUDE_MD_SHIM。列出需要补的路由行或 @AGENTS.md 导入行，经我确认后再加。
   - 项目原有 .claude/settings.json 或 .codex/hooks.json 时会保留原文件，不会写入本框架的 Goal Hook。需要时给出最小合并差异，经我确认后再合并。

6. 按 00_AI_WARMUP.md 执行初始化自检。仅修复意图明确的低风险缺项，并重新检查；全部满足后报告 READY。遇到实质冲突或需要额外授权时，报告 NOT_READY、阻塞项及最小修复建议，不覆盖原文件、不无限重跑，也不强行报告通过。

7. 最后汇报项目识别结果、实际根目录、创建/保留的文件、执行过的检查、真实状态及待办。READY 仅代表初始化就绪，不代表业务验收完成。

本次仅初始化和自检：不创建业务 Goal、Backlog、Story 或 Task，不开发业务功能，不启动额外 Agent，不自动提交、推送或部署。
```

Place `initdir.sh` and `00_AI_WARMUP.md` from the bootstrap source in the intended
project root. Fetch missing/empty files only; if either file is already nonempty,
compare with the source and obtain approval before replacing it. Source retrieval
can use a temporary directory; do not clone a new business repository or change
the target's Git topology.

Keep the current root when it coordinates child repositories, even if it has no
`.git`. Do not descend into or initialize children recursively. Preserve their
files, Git metadata and local rules.

Run:

```bash
chmod +x initdir.sh
./initdir.sh
python3 .ai/tools/check_requirements.py   # report only
python3 .ai/tools/evidence.py verify      # report only
python3 .ai/tools/check_framework.py      # report only
```

The repository will be expanded into a structure similar to:

```text
.
├── AGENTS.md
├── CLAUDE.md                 # Claude Code entry point; imports AGENTS.md
├── README.md
├── WORKING_STYLE.md
├── Goal_Constrained_Dev_Flow_v1.md
├── dev-flow.yaml
│
├── schema/
│   ├── entity-types.yaml
│   ├── workitem-types.yaml
│   ├── relation-types.yaml
│   ├── policies.yaml
│   ├── readiness.yaml
│   ├── id-policy.yaml
│   ├── intake.schema.yaml
│   ├── memory-policy.md      # memory layers, precedence, tool-memory boundary
│   └── templates/
│       ├── goal.md
│       ├── story.md          # six-view requirement contract
│       ├── task.md           # includes a Resume Point
│       ├── adr.md
│       ├── solution.md       # Brief / Research / Decision / Solution
│       └── learning.md
│
├── intake/   active/ completed/ templates/
├── raw/      goals/ requirements/ meetings/ feedback/ attachments/
├── wiki/     index.md goals/ workitems/ decisions/ architecture/ learning/ releases/
├── generated/ backlog/ ready/ task-graphs/ reports/ (evidence/ when recorded)
│
├── .ai/
│   ├── framework-version     # baseline hashes for --upgrade
│   ├── skills/
│   │   ├── goal-intake/       ├── ingest/
│   │   ├── goal-to-backlog/   ├── query/
│   │   ├── solution-pack/     ├── lint/
│   │   ├── story-refine/      └── delivery-loop/
│   │   └── story-to-tasks/
│   └── tools/
│       ├── check_requirements.py
│       ├── check_framework.py
│       └── evidence.py
│
├── .codex/
│   ├── hooks.json
│   └── hooks/goal_flow.py
├── .claude/
│   └── settings.json         # Claude Code SessionStart hook, same goal_flow.py
│
└── site/
```

After initialization, ask your repository AI agent to read and execute
`00_AI_WARMUP.md`. Do not start creating project Goals until the self-check
reports `READY`.

Both agents get the project rules from the same file: Codex reads `AGENTS.md`,
and Claude Code reads it through the generated `CLAUDE.md` (`@AGENTS.md`). If the
project already had a `CLAUDE.md`, it is kept as is; add an `@AGENTS.md` line to
it, or `check_framework.py` keeps reporting `CLAUDE_MD_SHIM`.

The optional Goal Hooks run one script, `.codex/hooks/goal_flow.py`:

| Agent | Definition | What it adds |
|---|---|---|
| Codex | `.codex/hooks.json` | Goal context at session start; evidence reminder at Stop |
| Claude Code | `.claude/settings.json` | Goal context at session start and after compaction |

Review each with `/hooks` in that agent and trust the project-local definition.
An existing `.claude/settings.json` or `.codex/hooks.json` is kept, so its owner
merges the hook by hand. Skipping or disabling the Hooks does not disable the
repository workflow; it only removes the session context and reminder.

## B. Incremental update of an initialized project

Use this when a project was initialized from an earlier bootstrap and you want the
current framework without losing project knowledge. Upgrading an unedited 0.5
project to 0.6, for example, reports `.claude/settings.json` and
`schema/memory-policy.md` as `NEW`, and `AGENTS.md`, the Task template, the
`delivery-loop` and `lint` Skills, the Skills and schema READMEs, `goal_flow.py`
and `check_framework.py` as `UPDATE`. `--apply` also creates `CLAUDE.md`, which
is project-owned and therefore not listed in the analysis.

Initialization writes `.ai/framework-version` (since v0.4). It records the
sha256 of every framework file as the framework wrote it, which is the baseline
that lets an upgrade tell an untouched stale file from a locally edited one. It is
the only file `initdir.sh` rewrites, and only when an entry changes.

Put the new `initdir.sh` and `00_AI_WARMUP.md` together in a folder outside the
project (see [Get the bootstrap files](#get-the-bootstrap-files)), then run from
the project root (Python 3 is required for `--upgrade`):

```bash
grep framework_version .ai/framework-version                     # installed version
bash /tmp/ai-native-scrum-new/initdir.sh --upgrade               # analysis only, changes nothing
bash /tmp/ai-native-scrum-new/initdir.sh --upgrade --apply       # apply the safe part
bash /tmp/ai-native-scrum-new/initdir.sh --upgrade --mark-merged schema/templates/story.md
bash /tmp/ai-native-scrum-new/initdir.sh --upgrade --base /path/to/old/initdir.sh   # no version file yet
```

The analysis initializes the new version in a temporary folder and compares every
framework file (`AGENTS.md`, `.ai/skills/`, `.ai/tools/`, `schema/`,
`intake/templates/`, `.codex/`, `.claude/settings.json`, `dev-flow.yaml`, `Goal_Constrained_Dev_Flow_v1.md`,
the folder READMEs, `initdir.sh`, `00_AI_WARMUP.md`). It prints one status per file
and writes a report with diffs to a temporary folder:

| Status | Meaning | `--apply` |
|---|---|---|
| `NEW` | Missing in the project | Creates it |
| `UPDATE` | Unchanged since the framework wrote it | Replaces it, keeping a backup |
| `MERGE` | Edited locally and changed upstream | Leaves it; merge by hand |
| `REVIEW` | Differs, and no baseline is recorded | Leaves it; compare by hand |
| `LOCAL` | Edited locally, unchanged upstream | Nothing to do |
| `OBSOLETE` | No longer shipped by the framework | Leaves it; remove by hand if unused |
| `CURRENT` | Already matches | Nothing to do |

After merging a `MERGE` or `REVIEW` file by hand, record it with
`--mark-merged PATH` so the next upgrade uses the new version as its baseline.

Projects initialized before the version file have no baseline, so every changed
file shows as `REVIEW`. If you still have the `initdir.sh` the project was
initialized from, pass it with `--base /path/to/old/initdir.sh`. The analysis then
classifies files as `UPDATE`, `MERGE` or `LOCAL`, and `--apply` stores that
baseline in `.ai/framework-version` so later upgrades no longer need `--base`.

Project-owned files are never compared or changed: `README.md`, `CLAUDE.md`,
`WORKING_STYLE.md`, `.gitignore`, `wiki/index.md`, everything else in `raw/`,
`wiki/`, `intake/active/`, `intake/completed/` and `generated/`.

To have your AI agent drive the upgrade, give it this instruction:

```text
请使用 https://github.com/zljie/AI-Native-Scrum.git 的 main 分支，把当前已初始化的 AI-Native-Scrum 项目增量升级到最新框架。

1. 确认当前目录是已初始化的项目根目录（存在 AGENTS.md、.ai/skills/、schema/）。有 Git 时先记录 git status。

2. 把新版 initdir.sh 和 00_AI_WARMUP.md 下载到项目外的同一个临时目录（例如 /tmp/ai-native-scrum-new，来源 https://raw.githubusercontent.com/zljie/AI-Native-Scrum/main/），不要覆盖项目里的同名文件。先用 grep framework_version .ai/framework-version 记录当前版本，再在项目根目录运行 bash <临时目录>/initdir.sh --upgrade。如果项目没有 .ai/framework-version 且能找到当初使用的 Bootstrap 版本，加上 --base <旧 initdir.sh>。

3. 向我汇报分析结果：各状态的文件清单，以及 MERGE / REVIEW 文件的关键差异（来自报告）。

4. 获得我确认后运行 --upgrade --apply：它只新建 NEW 文件、替换 UPDATE 文件并保留备份。

5. 对 MERGE / REVIEW 文件，在保留本地修改的前提下给出最小合并差异，经我确认后修改，再用 --mark-merged <路径> 逐个登记。不确定的文件保持原样并列为待办。

6. 运行 python3 .ai/tools/check_requirements.py、python3 .ai/tools/evidence.py verify 和 python3 .ai/tools/check_framework.py，并按新版 00_AI_WARMUP.md 自检。以下属于预期结果，不要为通过检查而修改：
   - 没有 requirement-contract 块的旧 Story 报告为 legacy，等下次 Story Refine 时再按新模板补齐；
   - 已是 review/done、但没有记录 RED/GREEN 证据的旧 Task 会报 DONE_WITHOUT_CURRENT_GREEN；不要改它们的 status，也不要补造证据；需要时重新执行验证并用 evidence.py run 记录。
   - 保留了自有 AGENTS.md 的项目，check_framework.py 可能报 SKILL_NOT_ROUTED 警告；列出缺少的路由行请我确认，不要直接改写 AGENTS.md。
   - 保留了自有 CLAUDE.md 的项目会报 CLAUDE_MD_SHIM；建议在其中加一行 @AGENTS.md，经我确认后再改。原有的 .claude/settings.json 会显示为 REVIEW，按第 5 步合并 SessionStart Hook。
   - 旧 Task 没有 Resume Point 不算问题，下次暂停该 Task 时再补。
   - 旧 LRN 记录没有 attribution 字段时视为未填写，不要补造归因。

7. 最后汇报：新建、替换、合并、保留未动的文件，检查结果，READY 或 NOT_READY 及待办。

本次只升级框架：不改写已有 Goal、Backlog、Story、Task、ADR 或 learning 记录，不批量迁移旧 Story，不启动额外 Agent，不自动提交、推送或部署。
```

Existing Stories may stay legacy until they are refined again; nothing in the
upgrade rewrites canonical work in `raw/` or `wiki/`.

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

The knowledge pipeline reaches the **Ready Pool**, then v0.4 guides authorized
delivery, actual verification, Goal review and evidence-backed learning.

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

## Stage 2b — Brief, Research, Decision, Solution

The working main line is:

```text
Goal → Brief → Research → Decision → Solution → Story → Task
```

When a problem needs a choice before Stories, the `solution-pack` Skill keeps
one pack per problem round in `wiki/solutions/SOL-XXX_<name>.md`:

| Step | Who | Result |
|---|---|---|
| Brief | AI drafts, a person reviews and confirms | problem, scenarios, roles, scope, constraints, questions to research |
| Research | AI searches and browses on its own within public, authorized scope | questions with sources, access dates, evidence nature, applicability and effect on the choice |
| Decision | AI recommends, a person chooses | alternatives, recommendation, the actual choice, reason, conditions and revisit triggers |
| Solution | AI organizes the decided direction | flow, architecture position, key logic, interfaces, failure and recovery |

Research covers comparable products, similar problems elsewhere,
implementation basis and applicability conditions. Evidence is marked as
official claim, page observation, hands-on verification, internal material or
AI inference; reading a vendor page is not using the product. Login, payment,
registration or submitting business data goes to the person; unreachable
content is recorded as a gap. Any browser tool the Agent already has (for
example Playwright MCP) is just a tool of the same workflow.

An AI recommendation stays `proposed` until a person decides. A Story that
relies on a proposed, unresolved or superseded decision, or on an unconfirmed
Brief, is reported `NOT_READY` by `.ai/tools/check_requirements.py`. The checker
can show that a confirmation record exists, not that the person truly took part.
Small changes may use a short pack or none; seven steps are not seven files.

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

### Six-view requirement contract

Each refined Story describes one requirement through six linked views:

| View | Question | Story IDs |
|---|---|---|
| Architecture position | Where does it belong and what does it affect? | `ARCH-*` |
| Change type and acceptance | What kind of change, and how is completion proven? | `change_type`, `AC-*` |
| User story | Who solves which problem in which scenario? | `UJ-*` |
| Implementation description | What exactly must be built? | `DEV-*`, `DM-*` |
| Prototype | How do users act and which states do they see? | `PG-*`, `UI-*` |
| Business logic | Which rules decide behaviour? | `BR-*` |

The Story Markdown remains the only canonical source. Its 追踪关系 section holds
one `json requirement-contract` block that lists item IDs, cross-view links and
open questions without repeating section content; Goal criteria and
dependencies stay in frontmatter. A view that does not apply (for example a
prototype for a background job) is declared not applicable with a reason.

Check it in a target project with:

```bash
python3 .ai/tools/check_requirements.py                          # every Story
python3 .ai/tools/check_requirements.py --require-goal-coverage  # Ready Pool review
python3 .ai/tools/check_requirements.py --json                   # machine report
```

The checker uses only the Python standard library. It reports missing views,
unexplained non-applicability, undefined items, broken references, acceptance
criteria without tests, uncovered Goal criteria, dependency cycles, unapproved
Goals and blocking questions, each with `file:line`, and gives every Story a
`READY` or `NOT_READY` verdict. It exits 1 on contract errors or when a Story's
status claims readiness while blockers remain. It never edits files or status,
is not wired into Hooks, and cannot judge business meaning or value; those stay
in Agent/human review. Stories without a contract block are listed as legacy
and are not forcibly migrated.

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

## Stage 5 — Authorized Delivery and Goal Review

### Version-bound evidence

`python3 .ai/tools/evidence.py run --task TASK-XXX --phase red|green --inputs <story> <tests> <code> -- <command>`
runs a verification command and keeps its output, exit code and the sha256 of
every declared input under `generated/evidence/<TASK>/`; failed attempts stay.
An import, syntax or setup failure is rejected as RED, and GREEN without a valid
behavior RED is rejected. `python3 .ai/tools/evidence.py verify` reports each
Task's latest GREEN as CURRENT, STALE (an input changed), FAIL or NONE, and exits
1 when a Task in `review` or `done` lacks CURRENT evidence. It is engineering
evidence only: it never edits status and never records business acceptance.

Question:

> Did the approved work produce verified evidence for the Goal without drifting
> from its Protected Constraints?

The `delivery-loop` Skill starts only from authorized Tasks with executable
acceptance. It records actual checks and failures, maps evidence back to stable
`GOAL-XXX#GSC-XX` criteria, and reports Goal status as `ON_TRACK`, `AT_RISK`, or
`BLOCKED`. Human approval still controls Goal changes and business acceptance.

The optional Codex Hooks only surface Goal context and missing-verification
reminders. They do not block tools, approve changes, continue work automatically,
or replace repository evidence.

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
     ↓
delivery-loop
```

Supporting Skills include:

```text
ingest
query
lint
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

# Goal Contract and Advisory Hooks

The approved Goal under `raw/goals/` is the Goal Contract. Do not create a
second `.goal/` source of truth. Each contract gives success criteria stable
`GSC-*` IDs, names Protected Constraints and records revisions approved by the
Goal Owner. Stories and Tasks retain `GOAL-XXX#GSC-XX` traceability through
acceptance and evidence.

## Goal-constrained stage handoffs

[`Goal_Constrained_Dev_Flow_v1.md`](Goal_Constrained_Dev_Flow_v1.md) and
[`dev-flow.yaml`](dev-flow.yaml) extend the existing Skills with:

`Goal Baseline → PM → Tech → Test RED → Dev GREEN → human Goal Acceptance`.

Goal Intake establishes the approved baseline; Backlog/Story Refinement handles
PM; Task Decomposition checks Tech contracts and assigns design/test/dev work;
Delivery Loop performs behavior RED before implementation, GREEN and regression;
Lint and Delivery Loop review global Goal coverage before human acceptance.
Record each stage's PASS / FAIL / BLOCKED / NOT_RUN and evidence in the canonical
work items. Keep stage results separate from `schema/workitem-types.yaml` statuses.

The YAML is a custom, Agent-reviewed workflow contract. This bootstrap does not
install an automatic gate engine, CI checks, or Agent scheduling. Hooks remain
advisory. One Agent may perform the roles in sequence; additional Agents require
explicit authorization. ACCEPTED records only explicit human final acceptance.

Declare applicable artifacts, approved exemptions and actual paths per Story.
Reuse existing project layouts; UI, API and database artifacts are required only
when applicable. Product maps reference canonical work items without duplicating
their truth. In a multi-repository workspace, record repository owners, Task
locations, interface dependencies and cross-repository acceptance; evidence uses
each child's revision or non-Git content hashes. Local GREEN alone does not
establish global acceptance or authorize commit, push or deployment.

The generated `.codex/hooks.json` keeps this flow visible without enforcing it:

- `SessionStart` adds concise Goal context for the Agent;
- `Stop` warns only when a completion claim appears to omit verification evidence;
- neither hook blocks tools, continues a turn, approves scope or proves acceptance.

[Project-local Codex Hooks](https://learn.chatgpt.com/docs/hooks) require trust
before Codex runs them and can be disabled by the user or administrator. They
are a convenience layer, not a security or governance boundary. The durable
contract remains in the repository.

Goal review uses explicit results rather than a weighted score:

```text
Goal Status: ON_TRACK | AT_RISK | BLOCKED
+ satisfied GSC-* criteria and evidence
+ unmet or unverified criteria
+ scope or Protected Constraint drift
+ smallest corrective action
+ outstanding human or business acceptance
```

---

# Agent Memory

Claude Code and Codex load memory; the repository holds it. The tools handle
loading instruction files, compaction, session resume and each user's private
notes (Claude Code auto memory, Codex Memories). Those notes are per user and per
machine, unversioned and unreviewed, so the framework keeps everything a project,
another person or another tool must rely on in repository records:

| Need | Record |
|---|---|
| Always-on routes and rules | `AGENTS.md`, imported by `CLAUDE.md` |
| Project working preferences | `WORKING_STYLE.md` |
| Goals, decisions, solutions | `raw/goals/`, `wiki/` |
| Lessons with attribution and confidence | `wiki/learning/LRN-*.md` |
| Where paused work stands | the Task's Resume Point |

`schema/memory-policy.md` gives the precedence order (current instruction and
evidence first, tool memory near the end) and how a fact found in tool memory
moves into the repository during the `delivery-loop` learning step. `CLAUDE.md`
exists because Claude Code stops reading `AGENTS.md` once any `CLAUDE.md` or
`CLAUDE.local.md` is present. `check_framework.py` warns with `CLAUDE_MD_SHIM`
when the import is missing and reports the always-on size for each tool. The
framework builds no memory store of its own and never touches `~/.claude/` or
`~/.codex/`.

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
Automated Knowledge Drift Enforcement
Rspress Knowledge Portal
Hybrid Retrieval / RAG
Engineering Context Packs
```

These capabilities should be introduced only after the foundational lifecycle works reliably.
This repository intentionally does not provide an automatic Goal enforcement
gate; its Goal review and Hooks are advisory.

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
Approved GOAL-001 Contract
 ↓
Backlog
 ↓
Refined Story
 ↓
Task Graph
 ↓
Ready Pool
 ↓
Authorized Delivery
 ↓
Verification + Goal Review
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

start your first Goal Intake. In Codex, use `/hooks` to review and optionally
trust the generated project Hooks; the core workflow remains usable without them.

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
AGENTS.md provides explicit routes for all nine Skills; `.ai/skills/` is not
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

It also exercises non-Git folders, existing Git repositories, and non-Git roots
with child repositories, runs the actual configured Hook commands from nested
paths, and checks embedded Dev Flow documents against their source files. It
does not execute the real project's PM/Tech/Test/Dev gates or Codex's trusted
Hook runtime. `READY` is a Warmup assessment, not this check's automatic output.

The same run initializes a requirements fixture and checks that a filled Story
template passes, an explicitly not-applicable prototype passes, and each invalid
contract (missing view, unexplained applicability, undefined item, broken
prototype rule, untested AC, uncovered Goal criterion, unknown dependency,
invalid JSON, dependency cycle, unapproved Goal, blocking question) is rejected.

Rerunning `initdir.sh` retains every existing nonempty file and creates only
missing or empty ones, so it never brings an existing framework file up to date.
Use `initdir.sh --upgrade` (Quick Start path B) for that: it compares with a fresh
reference initialization, uses `.ai/framework-version` to separate untouched
files from local edits, and with `--apply` changes only files nobody edited. Old
Stories may stay legacy until they are refined again; canonical work and user
preferences are never migrated automatically.

The bootstrap check also covers upgrades: it verifies that every written file is
in the upgrade file lists, that initialization records correct hashes, that the
analysis classifies new, stale, local, merge and unknown-baseline files without
writing, that `--apply` changes only unedited files, and that `--mark-merged` and
`--base` record baselines.
