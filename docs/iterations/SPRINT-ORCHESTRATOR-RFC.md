# AI-Native-Scrum｜内置 Sprint Orchestrator RFC（候选设计）

> 状态：RFC / 未实现 / 未验收；目标为未来迭代能力，不改变 V1.5 既定发布门禁，不自动增加运行权限。
> 设计日期：2026-11-15。基于当前 main 的 collaboration-candidate/1、V1.3 observability、V1.5 Project Context Pack / Activation / Task Graph / Journal / Recovery / Invalidation 候选。
> 一句话目标：**一次 `scrum start` 绑定一个 Sprint Goal，主 Agent 在既定授权范围内组织子 Agent 完成一轮规划、执行、检查、评审和复盘，交付一个可验证的产品增量或者带证据的未完成结论。**

## 1. 背景与范围

当前 `README.md` 明确写明初始化尚不包含 Sprint Planning；`dev-flow.yaml` 是供 Agent 阅读的 DSL 而不是可执行引擎；`v15_controller.py` 已有 `plan/drive/graph/metrics/recover/check` 等候选接口。新功能应为现有引擎**增加 Sprint 控制层**，而非建设第二套 Task 状态、授权系统、Agent Runner 或观测存储。

**本 RFC 要解决：**
- 用户给出 Sprint Goal 后，系统生成可确认的 Sprint Plan（范围、Story、AC、预算、依赖、角色、Definition of Done）。
- 主 Agent 作为 Scrum Orchestrator，基于项目事实与专业能力匹配，将 Task 委派给已允许的子 Agent；Task 可并行，但依赖门禁与写入范围不可冲突。
- 每次任务完成、失败、阻断、审查或变更时执行事件驱动的 Inspect & Adapt，有限重试/返工，并保持证据与状态可追溯。
- 一轮 Scrum 最终生成 Increment、Sprint Review 和 Retrospective，未完成内容回流 Product Backlog，不能伪造业务验收。
- Sprint 可以跨多次 Agent 回合/会话运行和安全恢复；“一次目标是一轮 Scrum”不是要求一次模型回复完成所有工作。

**非目标：** 不在此 RFC 中声明 V1.5 发布；不自行合并 main、部署生产、访问生产数据、扩大模型/工具权限；不实现虚构的 Codex JSON-RPC spawn API；不把 runtime_session 视为 `spawn_agent`；不自动审批 Goal/Scope/Acceptance；不将 Sprint 规划当作可执行授权。

## 2. 运行模型：主 Agent 与专业子 Agent

主 Agent（Scrum Orchestrator / Goal Executive）持有 Sprint Goal 与计划、选择 Ready Story、建立受控依赖图、调用已有 Activation Planner、依据证据提出专业 Agent 激活、派发已获授权任务、处理变更与阻断、收集独立审核、组织 Review/Retro，并报告真实结果。

保留现有五种角色契约：Product、Architect、Developer、Test、Ops；Database 等专业角色属于按需激活而非常驻角色。角色数量由任务影响证据决定，不允许靠“需求提到数据库”之类关键词推断需改表。若只需一个 Agent，应允许跳过不必要的角色，并记录跳过理由；不伪造其他 Agent 参与。

`scrum_orchestrator` **不是自动新增第六个开发 Agent**；主 Agent 同时承担 Scrum Master 式的协调职责，Product Owner 的最终业务优先级/验收权仍由有授权的人保留。

### 子 Agent Task Assignment 最小契约

| 字段 | 语义 |
|---|---|
| `sprint_id, goal_ref, story_ref, task_ref` | 与已有 Goal/Story/Task 正本关联 |
| `owner_role, capability, activation_evidence_refs` | 专业角色及证据驱动激活原因 |
| `input_context_hash, code_revision` | 与 Project Context Pack / 当前版本绑定 |
| `depends_on, acceptance_criteria` | 依赖及可验证的完成条件 |
| `allowed_read_scopes, allowed_write_scopes, authorization_ref` | 最小权限范围与授权引用 |
| `outputs, evidence_requirements, review_role` | 交接产物、测试证据、独立审核 |
| `attempt_limit, timeout_policy, rollback_or_recovery_policy` | 有限预算、检查点和故障规则 |

所有输出仍写入现有交接和 Journal；未经过独立 Review 的已完成任务不得自动释放下游依赖。若共享写入范围冲突，应串行化或阻断，而不是“并行后选胜者”。

## 3. 每轮 Sprint 的可执行闭环

| 阶段 | 主 Agent 动作 | 进入/退出门禁与产物 |
|---|---|---|
| S0 Goal Intake | 读取获批 Goal 与项目事实，识别约束；缺事实先请求澄清 | Goal/Story/Task 来源、授权与版本可查 |
| S1 Sprint Planning | 选择少量 Ready Story，编制 Sprint Goal、DoD、投入预算和依赖图 | 用户确认范围及必要授权，`sprint-plan/v1` |
| S2 Agent Activation | 分析业务影响，激活适用专业能力，提出并行/串行计划 | 复用 Context Pack、Activation Planner、独立影响复核 |
| S3 Sprint Execution | 分派任务，推动 Tech→Test RED→Dev GREEN→独立 Test Verify→Ops Ready（按适用性） | 复用 `Engine`、Task Graph、TDD、Handoff Review 与 Journal；失败有限返工 |
| S4 Inspect & Adapt | 每个事件检查进度、依赖、漂移、预算和风险，必要时重规划或阻断 | 追加事件；不静默覆盖旧证据；超范围需新批准 |
| S5 Sprint Review | 对照 AC 与 Sprint Goal 展示真实 Increment、测试/CI 及未完成 | 通过质量门禁 ≠ 人工业务接受；保留明确 `NOT_RUN` |
| S6 Retrospective & Close | 统计返工与阻塞根因，将改进项录入下轮 Backlog，关闭本轮 | 产出 `sprint-review`、`sprint-retro`、未完成清单；保留历史 |

**事件驱动式 Daily Scrum：** 在 AI 微迭代中，每次任务状态变化即可做 progress/check，不需要伪造每天都召开过的会议；长周期 Sprint 才按实际日历补充人工同步。Sprint timebox、并发、Token 与返工上限必须可配置，耗尽时停止/汇报而非无限续跑。

## 4. Sprint 数据契约、状态与存储边界

建议唯一的新业务正本是 Sprint Goal/Plan（如 `wiki/sprints/SPRINT-001.md` 或经审核等价记录），内容包括目标、绑定 Goal/Story、范围、时限/预算、DoD、批准信息与冻结的版本。实际 Task 状态继续以现有 Work Item/Engine Journal 为准。

建议 `sprint-plan/v1` 字段：

```yaml
schema: sprint-plan/v1
sprint_id: SPRINT-001
goal_ref: raw/goals/GOAL-001.md
sprint_goal: "为设备台账增加可选检修等级，并完成编辑及筛选的可验证增量"
story_refs: ["wiki/workitems/STORY-001.md"]
context_pack_ref: intake/context-pack.json
authorization_ref: intake/authorization.json
definition_of_done:
  - "所有范围内 AC 有当前代码版本的验证证据"
  - "独立 Test Verify 通过；无未批准的范围扩展"
  - "Sprint Review 记录 Increment 与未完成项"
limits:
  max_parallel_roles: 3
  max_rework_rounds: 2
  execute_requires_explicit_authorization: true
  production_operations_allowed: false
```

字段只作接口方向示例；样例路径、角色与授权**不是**业务项目已获批准的事实。

Sprint 生命周期建议 `DRAFT → READY → ACTIVE → REVIEW → CLOSED`；可从 ACTIVE/REVIEW 进入 `BLOCKED`，以及经有权主体决定进入 `CANCELLED`。这里的 Sprint 阶段是从既有事件与门禁得出的**只读视图**，不单独写一套 Task 状态。CLOSED 仅表示一轮时间盒已结算，必须另设 `outcome: ACCEPTED | PARTIAL | REJECTED | NOT_EVALUATED`；不能由 CLOSED 推断 Goal 被人工接受。

上下文或契约变更时保留旧 Sprint 及旧 run 的原始版本，必须形成新授权下的重规划记录和因果链接；未知中断副作用必须继续 BLOCKED，不允许自动重放。

## 5. 原生多 Agent 运行边界

使用现有 `v15_controller.py`、`codex_adapter.py` 和唯一 Engine Journal。主 Agent 发起任务前，先核验宿主可用性、所需权限、任务作用域与项目授权；执行请求本身不等于启动回执。

- `runtime_session`：Codex app-server 独立会话执行，**不是**父 Agent 原生 `spawn_agent`。
- `native_subagent`：必须在真实登录宿主观察到与同一次 parent turn 绑定的子 Agent 启动、等待/完成或失败事件，并核对真实回执；不支持或事件不完整时 fail closed。
- `fixture`：仅供协议与确定性自动化测试；不得作为真实 Agent 履职、真实多 Agent 效果、Token 总量或发布验收证据。

Sprint Report 应分别列示 `planned_assignments`、`verified_runtime_session_starts`、`verified_native_subagent_starts`、`independent_review_count`、`unknown_usage_count`、`end_to_end_token_total`。未知数据保持 null/unknown。

## 6. 预期 CLI/API（**未实现**）

```text
scrum plan   --goal GOAL-001 --scope STORY-001 --out intake/sprint-plan.json
scrum start  --plan intake/sprint-plan.json           # 初始化状态与 Journal；默认不执行
scrum run    --sprint SPRINT-001 --execute --native-subagent  # 严格授权和真实宿主门禁
scrum status --sprint SPRINT-001
scrum review --sprint SPRINT-001
scrum retro  --sprint SPRINT-001
scrum close  --sprint SPRINT-001                      # 结算而非批准发布
```

建议提供一个 `sprint-orchestrator` Skill 作为主 Agent 的流程入口；真正的运行控制、权限校验与事件落库应在可测试的确定性代码中实现，不依赖提示词自述“完成”。

## 7. 建议实施工作包

| 工作包 | 优先级 | 交付 | 验收条件 |
|---|---|---|---|
| SCRUM-01 Contract | P0 | Sprint Goal/Plan schema、版本与范围规则，流程 Skill | 无真实授权时只能 dry-run；计划不更改 Task 正本 |
| SCRUM-02 Planner | P0 | Ready Story 选择、Task Graph/角色激活映射、DoD 核验 | 缺证据/依赖时 fail closed；支持简单单 Agent 路径 |
| SCRUM-03 Orchestrator | P0 | 复用 Engine 的派工、事件检查点、有限返工、恢复 | 依赖未 Review 不解锁；写冲突阻断；中断不盲重试 |
| SCRUM-04 Review & Retro | P0 | Increment/AC 覆盖、独立 Review、Retrospective 与 Backlog 回流 | 不自批、失败不算完成；所有结论可追溯到最新 revision |
| SCRUM-05 Observability | P0 | Sprint Trace、真实角色激活、耗时/Token/返工统计 | fixture、session 和 native child 严格区分；未知保留 null |
| SCRUM-06 Live AT | 发布门禁 | 已登录原生多 Agent 宿主与真实业务试点 | 真实父子回执、独立验收、漂移/恢复/回滚；不可用则 NOT_RUN |
| SCRUM-07 Bootstrap/UX | P1 | 初始化/升级保护、Sprint 状态板与简报 | 旧项目文件不被覆盖；完整回归通过 |

实施顺序：先做 SCRUM-01 的**无副作用规划与校验**，再把 SCRUM-02/03 接入当前 Engine，随后完成 SCRUM-04/05；最后才做 SCRUM-06 真实宿主与业务黄金路径。SCRUM-07 可独立推进 UI，但 UI 不可替代验收。

## 8. 验收场景（建议复用 V15-AT-001 设备台账）

- 正向：一轮 Sprint 完成“新增可选检修等级、编辑、筛选”，主 Agent 基于真实代码事实激活架构/DB/研发/测试，生成当轮 AC 证据和独立 Review；若不需要改表则不激活 DB 专家。
- 返工：Test Verify 失败，Sprint 保持 ACTIVE/AT_RISK，返工回责任任务；旧 revision 和失败证据保留，不能直接通过 Review。
- 并行：两个无共享写作用域的任务可并行；共享作用域冲突必定序列化或 BLOCKED。
- 漂移：接口/迁移或需求变更，旧 Context Pack 失效、下游旧验收不得重复使用，必须新授权下重规划。
- 恢复：宿主中断、副作用未知时保持 BLOCKED，不重复写入/重放迁移，不猜测 Agent 已完成。
- 宿主：没有真实 `spawn_agent` 时完整 Sprint 的原生委派验收为 NOT_RUN；不得以 `runtime_session`、fixture 或模型文本替代。
- 权限：未经新授权不合并主分支、不部署、不开生产数据库、不扩大工具权限；Sprint 结束不能改变这些约束。

## 9. 与 V1.5 关系及合并纪律

这是新能力提案，不纳入 V1.5 的“已完成”清单，不冲掉当前真实宿主、AT-001、升级回滚及 Trace/Token 发布阻塞。推荐单独特性分支 Draft PR 设计评审；只有设计接受后才分工作包实施。实现可以逐步构建，但 V1.5 是否可发布仍按原 `V1.5-RELEASE-GATES.md` 判定；任何代码 CI PASS 不自动证明真实 Sprint、多 Agent 或业务验收通过。
