# 专业 Agent 基线：方法复用与项目实例化

状态：LEAD-004 候选，建立在前端/DBA 的 PR #27 之上。所有现有专业角色都绑定共同要求与对应专业方法；是否激活仍由当前任务影响、原 capability/policy 和授权决定。本页不代表用户宿主已经安装、专业能力已经提高或 V1.5 已可发布。

## 1. 基线覆盖

共同入口为 `.ai/skills/professional-baseline/SKILL.md`，统一项目绑定、来源版本、权限、证据、交接、失效和返工。下列方法部署在目标项目 `.ai/skills/<name>/SKILL.md`；仓库源文件位于 `collaboration/practices/<name>/SKILL.md`。

| 专业角色 | 角色基线 | 复用的方法与最低专业产物 |
|---|---|---|
| 导演 `director_agent` | `scenario-directing` | 复用 product-director/review-director；同版场景的主路径、关键分支、恢复和真实回验；每项 PASS/FAIL/NOT_RUN |
| 产品 `product_agent` | `product-engineering` | 复用 solution-pack；范围、规则、Story/AC、反例、未决事项，保留既有产品正本 |
| 架构 `architect_agent` | `architecture-engineering` | 复用 story-to-tasks、SDD/ADR；代码与调用事实、模块/API/数据影响、取舍、兼容性、验证和实现后核对 |
| UI/UX `uiux_agent` | `ux-engineering` | 复用 experience-director；信息层级、动作/状态/反馈、组件、响应式与可访问性合同 |
| 研发 `developer_agent` | `software-engineering` | 复用 delivery-loop；有边界的实现、后端/API 契约、根因定位、当前测试证据和独立交接 |
| DBA `database_agent` | 已有 `dba-engineering` | 实际方言/数据模型、审计与 ID 规则、种子/分配器、迁移与并发验证，沿用项目确认 |
| 测试 `test_agent` | `quality-engineering` | 复用 tdd-director/review-director；风险到测试映射、有效 RED、当前独立验证、可复现缺陷与重验 |
| 运维 `ops_agent` | `operations-engineering` | 复用 delivery-loop、已安装 V1.3 observability；环境/CI/制品事实、监测、恢复与待授权操作 |

研发的前端任务继续使用已有 `frontend-engineering` 与 `frontend-list-contract`。后端由通用研发基线覆盖，按实际项目再增加框架专项。没有新增前后端角色或第二个 DBA；不能从 profile 存在推断同角色多实例并发已得到支持。Lead 继续使用 `ans-lead`。

总计 10 份 practice Skill：1 份共同基线、8 个角色入口、1 份研发前端专项。本轮新增 8 份，复用并接入原前端/DBA 两份。

## 2. 三层实例化

| 层 | 内容 | 绑定位置 |
|---|---|---|
| 共同基线 | 真实状态、证据、授权、版本与交接要求 | 每个专业角色的 `skill_refs` |
| 专业方法 | 该角色的推理步骤、产物、质量判据 | 对应角色 Skill；继续引用已有流程 Skill |
| 项目规范 | 本项目 API、框架、SDD、数据、测试与运行要求 | 当前项目真实来源、Context Pack/任务输入和已复核 profile |

部署时为每个适用角色核对以下信息，写入已有项目初始化/Context Pack/工作单，不另建权威状态表：

- 实际项目根目录与 Goal/Story/Task；角色、能力、输入版本、允许读写范围和验证命令。
- API 契约/错误码/权限/幂等、前端框架与设计系统、SDD/ADR、数据库方言与迁移、测试入口、运行与观测规范的实际路径和版本。
- 适用 Skill 的真实路径与内容；规范中已确认、仍缺失或冲突的部分及受影响任务。
- 当前前置产物、接收审查者、结果与证据位置、失败回流和恢复入口。

通用方法不固定所有项目的框架、字段物理名称、数据库或目录。规范须通过现有上下文构建/replan 路径进入实际任务输入；聊天中的阅读声明不能替代哈希绑定。当前共享上下文漂移可能阻断整个 run；本轮没有引入更精细的失效算法，也未整合其他 PR 的 INIT-S2 准入实现。

## 3. 实际接入方式

默认 registry 保持六角色，Sprint registry 保持八角色。各角色的 `skill_refs` 包含共同基线、角色方法和原有流程引用，沿用 Engine 的存在/非空校验、SHA256 anchors、受保护写域、任务包和 freshness 检查。缺少 enabled 角色必需 Skill 会拒绝计划；计划后修改它会触发 `CONTEXT_DRIFT`。

任务包带当前 assignment 的 Skill 内容。其他专业方法不会仅因已注册而进入该角色的 Skill 列表；公共 inputs 仍可能包含跨专业资料。前端专项随 Developer 包提供，但仅在前端影响时适用，不要求每个实现任务做 UI 工作。

初始化器生成全部 10 份方法、本说明和默认六角色的路由。五个既有 Codex/Claude profile、DBA profile 以及 opt-in Sprint 导演/UIUX profile 都明确读取对应基线。**方法文件可用不等于 Sprint 角色/策略已安装**：Sprint 仍按原指南显式接入，未变成默认全员启动。

Skill 是执行指引。Engine 校验文件和协议，不自动证明模型完整遵循了方法。默认 `.ai/skills` 方法通过角色任务包/明确 profile 引用使用；不宣称所有宿主会将它们自动显示为用户级菜单。

## 4. 已核验的外部 Skill 候选

2026-11-26 核对以下一手仓库、固定提交的正文和许可证。此处记录**方法参考与适配判断**；本候选未复制第三方 Skill/脚本或安装第三方工作流。若以后原样分发，须按对应许可证保留署名与许可，并重新审查版本和执行边界。

| 用途 | 固定版本来源 | 采用的思路 | ANS 适配边界 |
|---|---|---|---|
| 产品 | [GitHub prd](https://github.com/github/awesome-copilot/blob/93fc8b9ee3ef56b9b5e7261e6ce92d314cb2c1cf/skills/prd/SKILL.md) | 问题、范围、故事、验收、风险 | 保留 SOL/Story，不强制重问已确认信息或另建 PRD |
| 架构 | [GitHub create-architectural-decision-record](https://github.com/github/awesome-copilot/blob/93fc8b9ee3ef56b9b5e7261e6ce92d314cb2c1cf/skills/create-architectural-decision-record/SKILL.md) | 背景、备选、取舍、后果、验证 | 沿用项目 ADR/SDD 与批准状态；建议不自动变 Accepted |
| 后端/API 专项 | [GitHub api-breaking-change-detector](https://github.com/github/awesome-copilot/blob/93fc8b9ee3ef56b9b5e7261e6ce92d314cb2c1cf/skills/api-breaking-change-detector/SKILL.md) | 真实生产者与消费者、兼容性 | 原包针对 C# Web API 与 TS/JS 客户端，仅匹配项目时考虑；静态检查不代表运行验证 |
| 调试 | [Superpowers systematic-debugging](https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/skills/systematic-debugging/SKILL.md) | 复现、边界定位、单一假设、小步验证 | 问题回原 Lead/架构任务，不引入整套调度或未经测量的概率/效率说法 |
| 完成验证 | [Superpowers verification-before-completion](https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/skills/verification-before-completion/SKILL.md) | 声明对应可检查的真实结果 | 核对相同版本/环境的当前证据，因失效、缺口或必需 gate 重跑，不为每条消息重复全量测试 |
| 浏览器验证 | [Anthropic webapp-testing](https://github.com/anthropics/skills/blob/e4bb5d960d87126ff3b3a8af1a104b7db67560ba/skills/webapp-testing/SKILL.md) | 先观察渲染状态再操作、保留浏览器证据 | 优先已有测试资产，不强制 Python/Chromium/networkidle；登录宿主与目标项目仍须实测 |
| 运维 | [GitHub devops-rollout-plan](https://github.com/github/awesome-copilot/blob/93fc8b9ee3ef56b9b5e7261e6ce92d314cb2c1cf/skills/devops-rollout-plan/SKILL.md) | 变更前事实、验证信号、停止/恢复及再验证 | 未知阈值/时间/联系人不硬填；方案不授予部署、生产操作或消息发送权限 |
| 主控对照 | [BytePioneer lead-delegation](https://github.com/BytePioneer-AI/agent-skills/blob/bf3e5622b7ad8a605598302a3cabf2924d9ee142/skills/lead-delegation/SKILL.md) | 保留目标、工作单、实际回收、原会话续接 | 继续 ans-lead/Journal，不引入个人模型分工、另一 ledger 或集成合并授权 |

许可证来源：[GitHub awesome-copilot MIT](https://github.com/github/awesome-copilot/blob/93fc8b9ee3ef56b9b5e7261e6ce92d314cb2c1cf/LICENSE)、[Superpowers MIT](https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/LICENSE)、[webapp-testing 单包 Apache-2.0](https://github.com/anthropics/skills/blob/e4bb5d960d87126ff3b3a8af1a104b7db67560ba/skills/webapp-testing/LICENSE.txt)、[BytePioneer MIT](https://github.com/BytePioneer-AI/agent-skills/blob/bf3e5622b7ad8a605598302a3cabf2924d9ee142/LICENSE)。某个单包的许可证不能概括为整个集合相同。

导演/UIUX 优先复用项目已有 product-director、experience-director、review-director 和场景合同；这些方法已经贴合当前链路，不额外安装同类主控。

## 5. 获取、升级与使用

从已审阅候选 `feat/ans-professional-agent-baselines-20261126` 获取源码，记录实际 SHA 和该提交 CI；main 合并状态单独核对。通用 Lead 安装见源码仓库 `docs/lead-quickstart.md`。仅复制全局 ans-lead 不会给已有业务项目补齐专业方法。

对于已获准接入的项目，复用初始化器现有生成/比较流程；先在隔离目录生成候选，比较 Skill、registry、profile、规则和文档。已有非空文件默认保留，重跑初始化不表示旧项目已升级。保留定制，按现有授权逐项合并必要差异，再核对引用、上下文和准入；不在任务运行时静默替换 Skill/规范。Sprint 额外配置仍按源码仓库 `docs/lead-development-loop.md` 接入。

在已具备项目资产的主聊天可使用：

```text
$ans-lead
围绕当前目标推进已授权迭代。先核对本项目的专业基线、API/前端/SDD/数据/测试/运行规范及版本。
只按实际影响派发专业角色，把共同基线与对应专业方法纳入各自工作单和当前上下文。
回收专业产物、实际证据、未决事项及下一接收者；失败回责任任务修复并独立重验。
分别报告文件绑定、实际方法使用、技术验证、导演场景和用户接受；无法访问的真实宿主检查标 NOT_RUN。
```

提示不补造授权或兼容 adapter。当前 Codexhost → Engine 接缝仍未完成；app-server 独立 runtime_session 不是原生 spawn_agent。没有真实登录宿主时可完善资产与计划，不能由 fixture 宣称真实交付闭环已验收。

## 6. 验收层次

| 层次 | 可观察通过条件 | 证据边界 |
|---|---|---|
| 文件/生成 | 10 份 Skill 格式有效、生成文件与源一致、两套 registry/native profile 路由正确、升级保留定制 | 实际工程结果见 LEAD-004 记录 |
| 协议 | 各专业包包含正确文本/哈希，缺 Skill 拒绝、变更阻断、按原影响规则选择角色 | 隔离测试，不是用户项目 Agent |
| 方法使用 | 真实角色使用当前方法与项目规范，返回本专业实际产物 | 需要对应宿主/项目证据，仅 packet 存在不够 |
| 独立验收 | 当前版本的技术/场景检查、缺陷回流重验；必验 NOT_RUN 不汇总为全通过 | 用户真实宿主/项目未执行，NOT_RUN |
| 能力收益 | 在可比较任务上记录遗漏、返工、投入和维护成本，与原基线比较 | 未测量，不宣称提升幅度 |

未获新授权前不合并 main、不做生产数据库/部署/扩大权限/发布。真实项目宿主验收完成后，再评估 V1.5 发布门槛。
