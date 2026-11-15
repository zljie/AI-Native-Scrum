# INIT-S2｜角色初始化材料、复核记录与既有 Engine 准入

状态：源码级研发候选。依赖 PR #23 / `cb6a110f7feea103e8159e049fc583af9ffaf742`；不合并 main，不修改已有项目，不发布 V1.5。总计划见 `PROJECT-AGENT-INITIALIZATION-PLAN.md`。本轮新 Draft PR #24。

## Sprint Planning

Sprint Goal：让已绑定项目规范的角色配置进入可检查的初始化复核流程，并将有效配置、任务 Context Pack 和既有授权一起绑定到现有执行 Journal。用户只授权研发候选开发；生产、权限扩展、发布和业务接受不在范围内。

| 工作包 | 本轮增量 | 交付边界 |
|---|---|---|
| A05 | 生成初始化任务与 pending 复核模板；校验独立命名复核记录、版本与证据 | 不自动批准；姓名不同不等于身份认证；真实专业 Agent 尚未运行 |
| A06 | 生成项目角色工作说明，将角色契约、API/前端/SDD 来源与版本接入实际任务包 | 不猜测项目规范、不杜撰测试命令；正文由现有 Engine 按显式源文件读取 |
| A07 | 源码准入入口编译受限角色注册表、任务上下文，复用 Engine.create、原始 Journal 和 freshness | 仅对经本入口创建的 run 生效；既有 legacy run 不冒充初始化完成 |

## 实际文件与复用

新增 `collaboration/project_agent_review.py`、`collaboration/project_agent_admission.py`、`collaboration/test_project_agent_admission.py` 和本文档。

复用 S1 `project_agents.py` 的配置版本/原始请求重建、`project_context.py` 的路径/哈希/漂移/不可覆盖输出，以及原有 `Engine` 的角色选择、授权、任务依赖、交接复核、TDD、恢复、观测和追加式 Journal。未修改通用执行引擎、宿主适配器、工作流、initdir.sh 或角色原始配置。

角色初始化任务是有界工作描述，不是新常驻 Agent。prepare 只生成材料，不启动模型。review 只检查已有记录，不把模板转成真实批准。plan 会写生成文件和执行 Journal，但不执行任务、不调用模型。

## A05：复核契约

`project-agent-initialization-review/v1` 绑定 project_id、manifest_ref/version、role_id、variant、profile_version、prepared_by、reviewed_by、带时区的 reviewed_at、decision、confirmation_ref、完整 input_hashes、非空 evidence_hashes 和 sample_kind。

仅 accepted 的记录可以进入准入检查。pending、rejected、changes_requested、自我复核（含大小写别名）、版本错配、输入哈希缺失、证据漂移、无确认引用、未知授权字段均拒绝。

接受记录只证明结构及当前文件绑定符合契约，不认证真人，不独立证明语义判断正确，不证明子 Agent 已启动。明确返回 identity_verification=not_performed、runtime_status=NOT_RUN、delegation_authorized=false。真实身份/运行证据留给 INIT-S3，不从本地 JSON 推断。

## A06：角色工作说明

工作说明包含初始化职责、事实与规范区别、项目引用及哈希、SDD/设计前置要求、任务范围及独立授权边界、验证与交接要求、版本变化后的停止条件。使用缩进 JSON 表达引用数据，不把文件名当成可执行指令。

每个已复核角色的说明进入该 run 生成注册表中的 skill_refs；规范正文与复核引用进入现有 Engine.packet 的 documents，接受现有大小限制。原始 `.codex/agents/*` 等宿主文件不改写。这不是已安装的 OMP 原生配置，也没有改变模型或工具权限。

## A07：真实接入路径

1. 检查 S1 配置当前且没有已声明缺项/冲突。
2. 检查任务 Context Pack 当前，且 Goal/Task 与已有任务上下文相同。
3. 使用原有 make_plan 验证原始授权、范围及专业角色选择。
4. 核对所有计划角色的版本化复核记录。辅助角色也须显式列入并复核；生成注册表禁用其他角色，避免通过 assist 临时激活未复核角色。
5. 拒绝覆盖初始化来源或其祖先目录的写授权。规范文件、接受记录、生成说明和注册表必须不可被本 run 自行改写。
6. 在原有 Engine.create 的锁内、第一条 Journal 快照出现前，再核对先前授权/基础来源、Context Pack 与当前任务计划，加入不可变 anchors 及 project_agent_initialization 元数据。
7. 后续标准 Engine/v15_controller 的 dispatch、review、结果应用及重开任务，仍使用同一份 Journal 和原有 freshness。没有新调度器，也无需每次重新使用准入入口。

计划完成不证明任务执行成功；工程结束不证明人工业务接受；app-server runtime_session 不等于原生 spawn_agent。

初始化规范变化会阻断该 run；不得通过改旧 Journal 或把旧记录重写为已通过恢复。任务代码的合法变更仍沿用 Engine 既有 source_hash 更新规则；被 profile 绑定为事实基线的文件更严格，需重新基线化。当前保守冻结整个所用 profile set 的依赖，不宣称已实现最小影响传播。

## 源码使用方式

必须在包含本 PR 的完整 ANS 源码中执行。`/authorized/project` 表示获准工作区，不是已完成接入的真实项目。

```bash
# 生成待执行的角色初始化材料，不生成 accepted 决定。
python3 collaboration/project_agent_admission.py --root /authorized/project prepare \
  --manifest generated/project-agents/profiles.json --project-id project-a \
  --role developer_agent --variant frontend --sample-kind real \
  --output-dir generated/project-agents/init-dev-001

# 独立复核完成后，检查其真实记录；不可照抄测试中的 fixture 批准。
python3 collaboration/project_agent_admission.py --root /authorized/project review \
  --manifest generated/project-agents/profiles.json --project-id project-a \
  --role developer_agent --variant frontend --sample-kind real \
  --record intake/developer-initialization-review.json

# 生成受控 run；不启动模型。
python3 collaboration/project_agent_admission.py --root /authorized/project plan \
  --request intake/agent-admission.json \
  --output-dir generated/project-agents/run-001

# 查询同一个既有执行引擎的任务视图。
python3 collaboration/v15_controller.py --root /authorized/project --run-id RUN-001 graph
```

准入请求示例（仅示意，不是授权）：

```json
{
  "schema": "project-agent-admission/v1",
  "project_id": "project-a",
  "manifest_ref": "generated/project-agents/profiles.json",
  "context_ref": "intake/task-context.json",
  "context_pack_ref": "generated/reports/context-pack.json",
  "policy_ref": "schema/collaboration/policy.json",
  "profiles": [
    {"role_id": "developer_agent", "variant": "frontend", "review_ref": "intake/developer-initialization-review.json"}
  ]
}
```

profiles 必须覆盖实际计划选择的所有角色；示例中的单研发角色只适用于原有规则确实只选择该角色的任务。复杂任务缺架构/测试配置会被拒绝，不因示例而降低门禁。后续实际 drive 仍需原有 --execute、合法任务授权与真实宿主；本 PR 不代替这些条件。

输出只新增于 generated/project-agents，拒绝覆盖。多文件准备不是文件系统事务；遇到并发变化或失败时可能保留未使用的生成材料，但第一条 Journal 不会在准入失败时生成。保留材料排查，使用新的输出目录重试，不自动清理/覆盖旧材料或执行副作用。

## Review：确实发现的两项缺陷

初始测试提交 `a20ef17e72607c86f8025304ad513855ac5d78f7` 的 Collaboration CI（run `43750308797`，job `132922577307`）运行 **180 项：178 通过、2 失败、0 跳过**。

失败测试为 `test_authorization_race_before_first_journal_is_rejected` 与 `test_pack_source_race_before_first_journal_is_rejected`。实际错误均为期望拒绝异常却未抛出：第一次预检后、Engine 创建前，授权或 Context Pack 源文件变化可能被第二次计划静默接纳。

修复在首次写入 Journal 前复查原始授权值与原有 anchors，再校验 Context Pack 当前性及 Engine 当前快照。保留原测试不降低断言。修复提交的结果须以其自己的最终 CI 记录为准，不能借用 S1 或旧绿色结果。该失败不是生产事故，也不是对抗恶意文件系统的完整安全证明。

## 验收与剩余门禁

新增 33 项确定性测试复用真实 Engine、已有 FixtureAdapter 与完整源代码，覆盖记录绑定、待审/拒绝、自审、fixture/real 区分、缺项、来源失效、包错配、权限边界、实际 packet、标准 Engine 重开、运行中漂移、交接审核、辅助角色、完整 fixture 链路、并发检查及 CLI 脱敏。fixture 不代表真实专业 Agent。

```bash
python3 -m unittest discover -s collaboration -p 'test_project_agent_admission.py' -v
python3 -m unittest discover -s collaboration -p 'test_*.py' -v
python3 -m unittest discover -s observability -p 'test_*.py' -v
python3 -m unittest discover -s examples/report_subscription/tests -v
python3 observability/embed.py
python3 collaboration/embed.py
python3 scripts/check_bootstrap.py
```

本会话本地 git ls-remote 因 DNS 失败，未取得完整本地检出；不声称本地全量测试。完整回归使用既有 GitHub Actions。确切最终提交、测试合并 ref、tree、工作流及测试数保存在 PR #24 说明/评论。

仍未完成：真实子 Agent 执行初始化、外部身份/权限验证、规范语义独立复核、OMP 原生适配、自动 Skill 路由、Bootstrap 安全安装/升级/回滚、完整真实 Sprint 与 AT-001。全部按相应 NOT_RUN/未实现状态报告。FRAMEWORK_VERSION 保持 1.3。

## Retrospective

本轮由单个执行 Agent 开发与自查，不能说已完成真实多 Agent Scrum。工程证据必须区分初始化材料、复核记录、运行实例与业务接受。新增经验为 candidate：前置检查与 Journal 首次写入之间必须比较原始观察，而不只验证第二份新快照；接受文件不能授权执行；将初始化来源接入现有不可变 anchors，可复用其恢复后版本检查。无 Token/时间收益测量。

下一步按 INIT-S3 核查真实宿主能力及角色初始化回执，补独立评审；INIT-S4 再做安全分发和真实项目闭环。缺宿主时维持 NOT_RUN，不用 fixture 补成通过，不扩大权限获取验收结果。
