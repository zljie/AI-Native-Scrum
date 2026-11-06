# AI-Native Software Engineering Knowledge Repository Bootstrap

A bootstrap repository for creating an **AI-native software engineering knowledge system** where human intent, project goals, backlog items, detailed user stories, engineering tasks, and execution-ready work are continuously transformed into durable, traceable knowledge.

The repository is designed around a simple idea:

> Software development should continuously produce structured knowledge that can be reused by both humans and AI agents.

Instead of treating documentation as a separate activity, this repository establishes a development knowledge lifecycle in which AI agents help capture, refine, structure, validate, and maintain project knowledge as the project evolves.

---

<!-- OBSERVABILITY QUICKSTART BEGIN -->
## V1.3: opt-in local observability

Fresh initialization and safe upgrades now include runtime telemetry, Token normalization,
health reports, paired experiment comparison and an experiment template. Nothing is collected
until `python3 .ai/tools/harness_observe.py enable` is explicitly run in the target project.
Use `status` before and after enabling. Native Hook collection additionally requires an
approved `install-hooks --provider codex --apply` (or claude), followed by host trust review.
Existing nonempty/customized files remain protected by the normal upgrade mechanism.

Read [the activation, privacy and experiment guide](docs/harness-observability.md).
Collector tests/CI are fixture evidence, not real model benchmarks or measured savings.
The generated Runner preserves its authorization checks and distinguishes cli_role from
runtime-observed native subagents. Actual production/real-model acceptance remains separate.
<!-- OBSERVABILITY QUICKSTART END -->

<!-- COLLABORATION CANDIDATE BEGIN -->
## Collaboration candidate (not V1.4 released)

General capability-based coordination now has candidate source, explicit handoff review,
immutable runtime evidence, scoped application and Codex app-server transport. The database
expert is optional and independent. Existing framework version remains 1.3 until all release
gates including a real authenticated multi-role run pass. Mock tests never qualify as live.
Read [candidate scope and activation](docs/agent-collaboration.md) and the iteration report
under docs/iterations/. No target project is upgraded or telemetry enabled by this commit.
<!-- COLLABORATION CANDIDATE END -->

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
same advisory Goal hook as Codex, and Tasks keep a Resume Point. v0.7 adds two
director Skills: `product-director` shows a business storyboard and settles one
key decision per round inside the solution pack, and `experience-director` walks
the user's task before coding, writes the Story's Experience Intent (`### 体验意图`)
and hands key experience items to Tasks. Both write into existing SOL, Story and
Task records; neither adds a new record type, status or Agent. v0.8 makes
authorized work continue: a Task records who authorized it, the `scope` and the
`until` point, and Agents keep going until a named stop condition instead of
ending at a check result or scope summary. v0.9 makes status changes and open
questions checkable: `schema/workitem-types.yaml` lists which role may move a
Task between which states (adding `blocked` and `cancelled`), each Task keeps a
Status History, the role that implemented work does not mark it done, questions
only a person can settle go to `wiki/decisions/HUMAN_DECISIONS.md`, and the
report-only `check_workflow.py` lists them with the Tasks they block. The
generated `AGENTS.md` now opens with a hard-constraint table naming the check
behind each rule; the explanatory sections moved to `schema/repository-guide.md`.
1.0 makes the record from Goal to acceptance trustworthy. A GREEN must repeat
the exact command of a valid RED that covers the same Story test cases, on
unchanged test files, after an implementation change; trivial or inline
commands and "no tests ran" are rejected, and evidence moves to `raw/evidence/`.
The Story's requirement contract is the only AC → test record, and the
report-only `check_acceptance.py` follows Goal → `GSC-*` → AC → case → current
evidence. Goals record who approved them, when and in which words; acceptance is
a person's row in the Goal's Acceptance Record. Changes after approval go
through change requests (`wiki/changes/CR-*.md`). Two director Skills join:
`tdd-director` runs one TDD round per Goal before Tasks, naming for every case
the wrong implementation it must reject, and `review-director` reviews a
delivered Goal against its purpose and writes the report a person accepts from.
A project's installed version is the `framework_version` line in
`.ai/framework-version`.

v1.1 adds five reusable specialist role contracts (`product_agent`,
`architect_agent`, `developer_agent`, `test_agent`, `ops_agent`) with project-level
Codex/Claude Code adapters. `GoalExecutive` remains the primary coordinator,
not an automatically spawned sixth Agent. Test independently verifies GREEN;
Ops checks release/operations readiness after verification, with deployment
still separately authorized. `schema/agent-roles.yaml` is a portable role
contract, not an executable scheduler or a permission sandbox. Single-Agent
sequential operation remains supported.

v1.2 adds an append-only, project-local Agent handoff record format:
`schema/agent-handoff.schema.json` and `.ai/tools/agent_handoff.py`.
It validates role identities, goal/work item links, project-relative artifacts,
source revision, evidence, and a reference to recorded authorization. The tool
cannot establish the authenticity of human consent, make a gate PASS or launch
other agents. Execution and acceptance still require their own checks.
The opt-in `.ai/tools/check_gates.py --review PATH` validates structured
`gate-review/v1` input against the current RED/GREEN evidence and Ops readiness
artifacts, returning nonzero for missing/stale/inconsistent evidence. It is a
check, not an automatic deployment or acceptance authority.
The local opt-in `.ai/tools/local_agent_runner.py` plans P0 routes, or invokes
one explicitly authorized Codex/Claude Code CLI role at a time. `run` defaults
to a dry-run; `--execute` is required even for read-only access, and workspace
edits additionally require `--allow-write --write-authorization-ref ...`.
The append-only `wiki/runs/RUN-*.json` WorkRun stores exit status, revision and
output hashes without storing potentially sensitive model output. Provider
permission modes are not a substitute for an OS sandbox or real approvals.
`schema/work-graph.schema.json` and `.ai/tools/work_graph.py` derive a computed
Goal → Story/Task → WorkRun → Artifact → Evidence/Gate → human Acceptance Record
view from canonical project data. The default is read-only JSON output; DOT and
explicit `--output generated/...` exports are available. Missing links remain
visible as findings, and neither the graph nor its checks infer human approval.

For a runnable, isolated P0 reference scenario, see
[`examples/report_subscription/`](examples/report_subscription/README.md):
report subscriptions and report requests, a bugfix regression, and a proposed
change that correctly remains blocked pending human approval. These examples
are not copied into initialized projects or represented as approved Goals.

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

**可直接复制：** [A 初始化提示词](#a-initialize-a-project) ·
[B 热更新提示词](#b-incremental-update-of-an-initialized-project) · [C 本地验证](#c-本地激活与真实协作验证初始化热更新之后)。
先安装或安全更新，再按范围授权验证；不得把候选组件当成已发布V1.4。

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

**当前安装基线：`framework_version: 1.3`；通用协作组件：`collaboration-candidate/1`。**
代码可合并供本地验证，但真实宿主验收 AT-001 完成前不发布或标记 V1.4。
相同的框架版本号也可能包含新的候选组件；升级以**固定提交 SHA、文件哈希和
`--upgrade` 差异**为准，不能因为版本仍为 1.3 就跳过。

“热更新”在本文指**保留业务资产的增量更新**，不是运行中的 Agent 或 Python 进程
无停机替换。先让现有任务完成或安全暂停，确认没有 requested/running/applying
工作，再更新工具；不要在旧进程执行时替换它的脚本、配置或输入。

两条路径均先把 Bootstrap 放到项目外的独立临时目录，避免覆盖项目中的旧文件。
在 Bash 中解析并固定 main 的实际提交；执行前检查该提交的 CI、候选说明与脚本。
下面只下载文件，不初始化项目，不启动 Agent：

```bash
set -euo pipefail
SOURCE_SHA="$(git ls-remote https://github.com/zljie/AI-Native-Scrum.git refs/heads/main | awk 'NR==1 {print $1}')"
[[ "$SOURCE_SHA" =~ ^[0-9a-f]{40}$ ]] || { echo 'Cannot resolve source commit' >&2; exit 1; }
BOOTSTRAP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/ans-bootstrap.XXXXXX")"
for FILE in initdir.sh 00_AI_WARMUP.md; do
  curl --fail --silent --show-error --location \
    "https://raw.githubusercontent.com/zljie/AI-Native-Scrum/$SOURCE_SHA/$FILE" \
    --output "$BOOTSTRAP_DIR/$FILE"
done
printf '%s\n' "$SOURCE_SHA" > "$BOOTSTRAP_DIR/SOURCE_SHA"
printf 'Source commit: %s\nBootstrap folder: %s\n' "$SOURCE_SHA" "$BOOTSTRAP_DIR"
```

保留输出中的实际目录；换终端后需要重新设置 `BOOTSTRAP_DIR`。Git 在这里仅用于
获取远程引用，**目标项目不需要 `.git`，禁止为此自动执行 `git init`**。
没有 Git 时可通过 GitHub 连接解析同一提交并下载；不能退回分别下载移动中的 main。
普通初始化/升级只需要这两个同版本文件，不需要克隆一个新的业务仓库。

## A. Initialize a project

For an empty folder, an existing project, or a Monorepo coordination root, give
your project-aware AI agent this instruction (Git is optional):

```text
请为当前项目安全初始化 AI-Native-Scrum。上游是
https://github.com/zljie/AI-Native-Scrum 的 main；本轮只安装框架、自检和准备本地验证，
不直接开发业务功能、不启动付费模型执行、不提交、推送或部署。

1. 识别项目和现状
确认实际项目/协调根目录，区分空目录、已有代码、Monorepo和多子仓库。
读取当前AGENTS.md、CLAUDE.md、WORKING_STYLE.md、已有Skills/MCP/Hooks与子目录规则，
记录Git状态（若有）和未提交工作。AGENTS.md单独存在不等于安装过本框架；结合
.ai/framework-version、.ai/tools和schema核验。已经安装则转入B增量更新，不重复初始化。
不创建/移动.git，不递归初始化子仓库，不清理、重置或stash用户改动。

2. 固定来源并安装
解析main的真实提交SHA并检查该提交的CI、版本与候选状态。将initdir.sh及
00_AI_WARMUP.md从同一SHA下载到项目外的独立临时目录，记录来源与文件哈希，
阅读相关脚本后，在目标根目录运行 bash <临时目录>/initdir.sh。
仅创建缺失/空文件，保留已有非空文件。项目根的旧Bootstrap不直接覆盖；需要复制时先比较。
本轮授权范围内的低风险安装和自检连续完成，不在每次检查后重复询问。
本地规则与新入口发生语义冲突或有覆盖风险时，集中提出最小差异供我决定。

3. 检查真实能力，而不是固定数量
核对Goal/Story/Task、五个基础角色、导演Skills、原生发现入口、证据与授权边界。
若本次来源包含通用协作候选，额外核验：
- .ai/tools/agent_collaboration.py、.ai/tools/codex_adapter.py；
- schema/collaboration/的注册表、策略和版本化契约；
- .ai/skills、.agents/skills、.claude/skills中的agent-collaboration入口；
- 独立可选database_agent的专业契约和声明。
数据库专家按需参与，不嵌进研发角色，也不强制每个任务启动所有角色。
依据实际注册表统计，不把“恰好13个Skill/5个文件”作为固定验收条件。
候选当前采用Codex app-server独立runtime_session，不等于父会话spawn_agent子线程；
Claude入口存在也不表示已经实现Claude协作执行适配器。

4. 绑定项目并保留约束
定位真实模块、接口、数据模型/迁移、测试命令和架构记录，优先复用现有索引。
不能访问运行数据库时，仅说明核验了代码/迁移文件；不伪造表结构或连接权限。
保留业务规则、列表规范、人工审批、TDD及既有项目Skill/MCP，不另建需求正本。
有界专业委派、交接接收、返工和架构回写须使用当前版本的协作Skill与契约，
不是在初始化时临时构建调度器。未来真实工作授权范围内可连续交接，不每步重复审批。

5. 执行自检
读取本次固定版本的00_AI_WARMUP.md，在目标根运行：
python3 .ai/tools/check_requirements.py
python3 .ai/tools/evidence.py verify
python3 .ai/tools/check_workflow.py
python3 .ai/tools/check_acceptance.py
python3 .ai/tools/check_framework.py
python3 .ai/tools/harness_observe.py status
python3 .ai/tools/harness_observe.py report
python3 .ai/tools/agent_collaboration.py --help
最后一项仅在候选存在时运行；缺失则报告能力不具备，不编造命令。
已有业务历史缺证据或原规则缺路由时如实报告，不改任务状态、不补造批准或测试。
新项目无运行数据时应显示disabled/no_data/unknown，不以零成本或全部通过替代。

6. 分开报告安装、激活与验收
报告实际根目录、来源SHA、框架/组件标识、文件变更、保留规则、命令和结果。
分别列出：文件安装、自检、宿主发现、Hook实际事件、runtime_session真实执行、
交接/测试验收、V1.4发布条件。未执行项标NOT_RUN，不能用一个READY覆盖所有状态。
当前候选保持framework_version 1.3；不要手动改成1.4，不创建发布标签。

本次不创建业务Goal/Story/Task或虚假批准；观测默认关闭，不自动信任Hooks。
要验证真实协作，按README的C节准备单独的隔离验证与范围授权；
本次初始化限制不是项目今后永久禁止子Agent委派的规则。
```

Use the reviewed `BOOTSTRAP_DIR` from the download step. Run from the intended
project/coordination root, not from the source repository or a child repository:

```bash
bash "$BOOTSTRAP_DIR/initdir.sh"
python3 .ai/tools/check_requirements.py
python3 .ai/tools/evidence.py verify
python3 .ai/tools/check_workflow.py
python3 .ai/tools/check_acceptance.py
python3 .ai/tools/check_framework.py
python3 .ai/tools/harness_observe.py status
python3 .ai/tools/harness_observe.py report
python3 .ai/tools/agent_collaboration.py --help   # discovery only; no model invocation
```

`local_agent_runner.py route --kind feature` remains a plan-only compatibility
entry. The collaboration candidate uses its separate context, authorization and
execution interface described in [the collaboration guide](docs/agent-collaboration.md).
Do not create a fake Goal merely to run `work_graph.py`; use a real existing Goal.

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
│   ├── agent-roles.yaml      # five portable role contracts and handoff boundaries
│   ├── agent-handoff.schema.json
│   ├── gate-review.schema.json
│   ├── work-run.schema.json
│   ├── work-graph.schema.json
│   ├── repository-guide.md   # flow, layers, authority order, principles
│   └── templates/
│       ├── goal.md
│       ├── story.md          # six-view requirement contract
│       ├── task.md           # Status History and a Resume Point
│       ├── adr.md
│       ├── solution.md       # Brief / Research / Decision / Solution
│       └── learning.md
│
├── intake/   active/ completed/ templates/
├── raw/      goals/ requirements/ meetings/ feedback/ attachments/ evidence/
├── wiki/     index.md goals/ workitems/ decisions/ changes/ reviews/ handoffs/ gates/ runs/ architecture/ learning/ releases/
├── generated/ backlog/ ready/ task-graphs/ reports/
│
├── .ai/
│   ├── framework-version     # baseline hashes for --upgrade
│   ├── skills/
│   │   ├── goal-intake/       ├── ingest/
│   │   ├── goal-to-backlog/   ├── query/
│   │   ├── solution-pack/     ├── lint/
│   │   ├── story-refine/      ├── delivery-loop/
│   │   ├── story-to-tasks/    ├── product-director/
│   │   ├── tdd-director/      ├── experience-director/
│   │   │                      └── review-director/
│   └── tools/
│       ├── check_requirements.py
│       ├── check_framework.py
│       ├── check_workflow.py
│       ├── check_acceptance.py
│       ├── evidence.py
│       ├── agent_handoff.py
│       ├── check_gates.py
│       ├── local_agent_runner.py
│       └── work_graph.py
│
├── .codex/
│   ├── hooks.json
│   ├── hooks/goal_flow.py
│   └── agents/               # five native Codex TOML Agent profiles
├── .claude/
│   ├── settings.json         # Claude Code SessionStart hook, same goal_flow.py
│   └── agents/               # five native Claude Code Markdown profiles
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
current framework without losing project knowledge. Upgrading an unedited 0.9
project to 1.0, for example, reports the `tdd-director` and `review-director`
Skills, `.ai/tools/check_acceptance.py` and the change-request and review
templates as `NEW`, and `AGENTS.md`, `.ai/tools/evidence.py`,
`.ai/tools/check_workflow.py`, the Goal, Story and Task templates, the
`goal-intake`, `story-to-tasks` and `delivery-loop` Skills, the Skills README,
`dev-flow.yaml` and `Goal_Constrained_Dev_Flow_v1.md` as `UPDATE`. A template or
Skill you edited locally shows as `MERGE` instead.

Initialization writes `.ai/framework-version` (since v0.4). It records the
sha256 of every framework file as the framework wrote it, which is the baseline
that lets an upgrade tell an untouched stale file from a locally edited one. It is
the only file `initdir.sh` rewrites, and only when an entry changes.

Put the new `initdir.sh` and `00_AI_WARMUP.md` together in a folder outside the
project (see [Get the bootstrap files](#get-the-bootstrap-files)), then run from
the project root (Python 3 is required for `--upgrade`):

```bash
grep framework_version .ai/framework-version                     # installed version
bash "$BOOTSTRAP_DIR/initdir.sh" --upgrade               # analysis only, changes nothing
bash "$BOOTSTRAP_DIR/initdir.sh" --upgrade --apply       # apply the safe part
bash "$BOOTSTRAP_DIR/initdir.sh" --upgrade --mark-merged schema/templates/story.md
bash "$BOOTSTRAP_DIR/initdir.sh" --upgrade --base /path/to/old/initdir.sh   # no version file yet
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
请对当前项目执行AI-Native-Scrum安全增量更新（热更新），并准备本地协作验证。
上游：https://github.com/zljie/AI-Native-Scrum 的main。
本轮允许安全更新框架、保留语义的最小入口合并、自检和交付验证指引；不实施业务需求，
不改数据库、不提交/推送/部署，不自动启动真实模型运行或开启远程遥测。

1. 记录现状与暂停执行
确认项目/协调根目录，读取已有规则、.ai/framework-version、组件标识、Git状态，
记录未提交文件及框架/业务关键文件哈希。检查协作运行记录及实际宿主是否仍在执行。
“热更新”不是运行中无停机替换：有requested/running/applying任务或未解决的部分写入时，
先报告阻塞和恢复点，等待任务完成或经授权安全暂停；不杀进程、不删日志、不自动recover。
不git init、不reset/clean/stash、不进入子仓库批量升级。

2. 固定同一上游提交
检查main实际SHA及对应CI，记录本次来源。把initdir.sh和00_AI_WARMUP.md从同一SHA
下载到项目外的唯一临时目录，先审阅脚本。不要用移动的main混下两个文件，不直接覆盖旧脚本。
版本仍为1.3不代表无更新：结合候选组件标识、文件哈希与升级差异判定。
只使用已合并主线或我明确指定的来源；不自动拿未合并分支冒充新版本。

3. 先分析再安全应用
从项目根运行 bash <临时目录>/initdir.sh --upgrade，查看生成报告与差异。
缺可靠基线时，仅在找到真实旧Bootstrap后使用--base；不得编造旧版本。
按NEW/UPDATE/CURRENT/LOCAL/MERGE/REVIEW/OBSOLETE分类。
本提示词授权：核对无语义冲突后，连续应用NEW和未被本地改动的UPDATE，保留备份；
运行 bash <临时目录>/initdir.sh --upgrade --apply，不需要对同一授权反复确认。
LOCAL保留；MERGE/REVIEW先逐项比较，仅合并保持本地规则不变的必要入口。
涉及规则含义、权限、业务或架构变化时集中征求决定；OBSOLETE不自动删除。
真实合并完成的文件才用--mark-merged <路径>登记，不能为消除警告伪造基线。

4. 保护项目和进行中工作
保留Goal/Story/Task、ADR、learning、审批原话、RED/GREEN和旧WorkRun/Handoff，
以及.ai/collaboration运行记录、产物归档、观测配置、未提交代码和子仓库约定。
不补造批准/审查/测试，不改旧status，不将历史证据直接当当前GREEN。
已有规则如列表布局、末三列顺序、创建人显示名称、项目Skills/MCP和CI不得被通用模板覆盖。
对AGENTS.md/CLAUDE.md/Hook采用最小差异；热更新过程不扩大宿主信任或执行权限。

5. 核验通用协作候选与实际接口
读取当前docs/agent-collaboration.md、agent-collaboration Skill、注册表及策略。
核验五个基础角色与独立可选数据库专家通过同一契约协作，而非数据库专用流程。
核验TaskContext、范围授权、真实执行回执、下游显式接收、返工与恢复的入口。
保留原local_agent_runner.py兼容路径；cli_role不能冒充runtime_session，
runtime_session也不能冒充父会话spawn_agent子线程。该候选执行器当前仅支持Codex app-server。
缺工具/登录/合法授权时标blocked或NOT_RUN，不使用夹具宣称真实Agent参与。
输入/注册表变动可能使旧协作run失效：保留旧历史，核对后创建新run，不修改旧哈希骗过检查。

6. 检查与就绪报告
按新版00_AI_WARMUP.md运行以下实际存在的入口：
python3 .ai/tools/check_requirements.py
python3 .ai/tools/evidence.py verify
python3 .ai/tools/check_workflow.py
python3 .ai/tools/check_acceptance.py
python3 .ai/tools/check_framework.py
python3 .ai/tools/harness_observe.py status
python3 .ai/tools/harness_observe.py report
python3 .ai/tools/agent_collaboration.py --help
执行适用的安全回归，比较受保护文件升级前后哈希；环境缺失项明确NOT_RUN。
保留原有观测开关状态；需要enable或新增Hook时先按C节取得本地验证授权，
预览合并差异，保留其他Hook，由我在宿主审核信任，不绕过。

7. 交付给我本地验证
报告来源SHA、升级前后框架/组件版本、分类统计、实际变更和未合并差异，
分别给出文件升级、自检、宿主发现、Hook事件、真实协作、业务验收的状态。
提供当前版本确实支持的plan/ready/drive/check/report命令、测试需求路径与日志位置；
说明真实执行可能消耗模型额度，需要独立范围授权并在隔离分支/副本进行。
不要自动执行drive --execute，不复制fixture批准到真实任务，不擅自回填AT-001。
V1.4仍待真实运行和发布门禁；代码合并不等于发布，禁止修改版本号或打标签。

上述是本次热更新范围，不是永久禁止项目后续自主协作。
后续经我批准的功能任务应允许主协调者在既定范围内连续委派和交接。
```

Existing Stories may stay legacy until they are refined again; nothing in the
upgrade rewrites canonical work in `raw/` or `wiki/`.

---

## C. 本地激活与真实协作验证（初始化/热更新之后）

本节是**单独的验证动作**。安装/热更新不自动授权模型调用、代码修改或数据库操作。
jlcase等已有项目先用B，保存未提交工作；在专用测试分支或隔离副本验证，不直接操作生产。
读 [迭代与未关闭门禁](docs/iterations/COLLAB-ITERATION-001.md)、
[隔离验收需求](docs/iterations/COLLAB-TEST-001_maintenance-grade.md) 和
[运行协议](docs/agent-collaboration.md)。这些样例不是jlcase已有的业务批准。

### C1. 本地观测（需项目负责人同意）

```bash
python3 .ai/tools/harness_observe.py status
python3 .ai/tools/harness_observe.py enable
python3 .ai/tools/harness_observe.py install-hooks --provider codex
python3 .ai/tools/harness_observe.py install-hooks --provider codex --apply
```

仅在预览后执行 `--apply`，保留原Hook/插件设置。按宿主实际能力用 `/hooks` 审核信任，
必要时开启新会话；未收到真实事件不能称已激活。参考
[Codex Hook信任说明](https://learn.chatgpt.com/docs/hooks)。
协作控制记录保存在 `.ai/collaboration/`，它不依赖观测开关；V1.3观测桥仅在开启后采集。
候选当前只实现 [Codex app-server](https://learn.chatgpt.com/docs/app-server) 运行适配，
不是Claude运行器，也不是仅靠Hook自动执行所有后续用户需求。

### C2. 准备真实任务，先计划再执行

先确认 `codex --version`、`codex app-server --help` 和本人登录状态，勿在日志中打印凭据。
用户本人在正常宿主完成登录；不把密码/token放到任务、提示词或授权文件里。
主协调者根据真实项目证据填写 `schema/collaboration/task-context.schema.json` 与
`authorization.schema.json`，关联已有Goal/Story/Task、验收、输入、文件范围、测试argv
及用户实际确认来源。**不直接把fixture JSON改为real，不用示例批准冒充本人同意。**
需要额外预算、文件范围或外部操作时重新取得相应授权。

下列占位值必须替换为项目实际的新run ID及上下文文件；先 `--help` 核对接口。
`plan` 会保存本地计划，不调用模型；检查 `ready` 后，只有明确授权才运行 `drive`。

```bash
RUN_ID="RUN-<项目内未使用的数字ID>"
CONTEXT="intake/<已核实的上下文文件>.json"
python3 .ai/tools/agent_collaboration.py --run-id "$RUN_ID" plan --context "$CONTEXT"
python3 .ai/tools/agent_collaboration.py --run-id "$RUN_ID" ready
# 只有批准本次范围/模型消耗/隔离验证后，才执行下一条：
python3 .ai/tools/agent_collaboration.py --run-id "$RUN_ID" drive --execute
python3 .ai/tools/agent_collaboration.py --run-id "$RUN_ID" check
python3 .ai/tools/agent_collaboration.py --run-id "$RUN_ID" report
python3 .ai/tools/harness_observe.py report
```

缺有效RED/GREEN、授权、运行回执、当前产物或交接接受时，停止推进并报告具体原因。
读取 `status`；按指南处理明确返工或中断，不无限重试、不删旧记录重新伪造通过。
真实协作完成后，用 `check --release` 检查AT-001相关条件，失败不得豁免为成功；
即使该检查通过，仍要完成其它发布条件和维护者确认，工具不会自动发布V1.4。

### C3. 不消耗模型的框架验证（与真实Agent验收分开）

以下在**完整框架源码仓库**中运行，不是只有两文件初始化的业务项目：

```bash
python3 collaboration/embed.py
python3 -m unittest discover -s collaboration -p 'test_*.py' -v
python3 collaboration/demo.py --output /tmp/ans-collaboration-demo
```

源代码测试需要CI指定的jsonschema测试依赖；目标项目运行工具本身仍只依赖Python标准库。
demo真实执行SQLite和测试，但Agent回执为fixture：AT-001为NOT_RUN，发布检查应拒绝。
正式记录应分别报告：框架自检、隔离业务测试、独立runtime_session协作、
人工业务验收及V1.4发布状态。Token未覆盖交接复核等全部执行时，总成本仍为unknown。

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

`python3 .ai/tools/evidence.py run --task TASK-XXX --phase red|green --tests <test files> --covers STORY-XXX#TC-* --inputs <story> <code> -- <command>`
runs a verification command and keeps its output, exit code, code revision and
the sha256 of every declared input under `raw/evidence/<TASK>/`; failed attempts
stay. An import, syntax, setup or "no tests ran" failure is rejected as RED, and
trivial (`true`, `false`) or inline (`python -c`) commands are rejected. A GREEN
is rejected unless it repeats the exact command of a valid RED covering the same
cases, on unchanged test files, after an implementation input changed.
`python3 .ai/tools/check_acceptance.py` follows each Goal criterion through the
Story ACs and cases to current evidence and checks the approval, acceptance and
change-request records. `python3 .ai/tools/evidence.py verify` reports each
Task's latest GREEN as CURRENT, STALE (an input changed), FAIL or NONE, and exits
1 when a Task in `review` or `done` lacks CURRENT evidence. It is engineering
evidence only: it never edits status and never records business acceptance.

### Status changes and human decisions

Each Task records every status change as a row in its Status History (time,
from, to, role, actor, ref). `schema/workitem-types.yaml` `transitions` says which
role may make which move: `dev` moves work to `review`, a verifying role (`test`,
`tech` or a person) moves it to `done`, only a person cancels, and a `blocked`
Task names what it waits on (`blocked_by`) and where it resumes
(`resume_state`). Questions only a person can settle are `Q-NNN` entries in
`wiki/decisions/HUMAN_DECISIONS.md`; Agents block only the dependent Tasks and
keep working on the rest, and never write an answer they were not given.
`python3 .ai/tools/check_workflow.py` reports moves outside the table, the same
actor implementing and verifying (SELF_VERIFIED), incomplete answers, open
questions with the Tasks they block, and Tasks with three or more failed GREEN
attempts. It is report-only and cannot prove who really acted.

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

`Goal Baseline → PM → Tech → Test RED → Dev GREEN → Test Verify → Ops Ready → human Goal Acceptance`.

Goal Intake establishes the approved baseline; Backlog/Story Refinement handles
PM; Task Decomposition checks Tech contracts and assigns design/test/dev work;
Delivery Loop performs behavior RED before implementation, GREEN and regression;
Test then independently verifies current evidence; Ops records operational
applicability, rollout/rollback and monitoring readiness before human acceptance.
Lint and Delivery Loop review global Goal coverage before human acceptance.
Record each stage's PASS / FAIL / BLOCKED / NOT_RUN and evidence in the canonical
work items. Keep stage results separate from `schema/workitem-types.yaml` statuses.

The YAML is a custom, Agent-reviewed workflow contract. This bootstrap does not
install an automatic gate engine, CI checks, or Agent scheduling. Hooks remain
advisory. The five role profiles are discoverable Codex/Claude Code adapters,
not five running services, and their textual write scopes are not sandbox rules.
One Agent may perform the roles in sequence; additional Agents require explicit
authorization. Ops readiness does not grant deploy, rollback or secret access;
ACCEPTED records only explicit human final acceptance.

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
AGENTS.md provides explicit routes for all thirteen Skills; `.ai/skills/` is not
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

## Codex list-page contract

[Codex 列表页规范及真实验收接入](docs-codex-list-contract.md) defines the approved search/table/pagination layout and final three audit/action columns. Native discovery and evidence binding are provided; business-page CI and required branch checks remain explicit project integrations.
