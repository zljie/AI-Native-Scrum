# 通用多 Agent 协作候选实现

**状态：供本地验证的研发候选；不是 V1.4 正式版本。** 框架版本继续保留 1.3。
实现依据为 ANS-V14-P0-COLLAB-PRD-001，包含激活委派、交接和事件三个 P0。
用户后续明确决定：Database Agent 为独立、按需的可选专家；这覆盖原草案
DEC-003“默认放在架构/研发能力内”的建议，但不改变通用协作目标。

## 1. 边界

复用现有 Goal/Story/Task、原始 RED/GREEN 证据、V1.3 观测、原生角色声明和
安全增量升级。不新建业务需求正本、不自动批准 Goal、不更改工作项 status。
通用内核不包含数据库专用调度分支；角色、能力和任务依赖由 JSON 配置决定。
5 个基础角色保持；独立 database_agent 默认只在数据库能力命中时参与。
项目可禁用它并配置其它符合能力的角色，不改变内核代码。

本版调用 **Codex app-server 的独立原生线程/turn**，标识为 `runtime_session`。
它不是普通 `codex exec` 的角色文本，但也不是父线程 `spawn_agent` 子线程。
在没有真实、已登录、获准执行的运行环境时，AT-001 为 NOT_RUN，不能发布 V1.4。
测试的 fixtureTransport 只能证明协议，不计为真实 Agent，也不能通过 --release。
没有安装真实执行端时会记录 unavailable，绝不自动伪装或降级。

原生 Agent 的身份/工具权限仍由宿主控制。控制器的账号和确认引用是可定位记录，
不是外部身份认证；本地可写文件、哈希链和模拟测试都不构成抗恶意篡改保证。

## 2. 从需求到真实项目

使用者在实际项目根目录读取 AGENTS.md 和 agent-collaboration Skill。主协调者先
检查源码、模型、接口、迁移和测试入口，再给任务附上有源文件依据的能力信号。
该步骤是主协调 Agent 的分析职责，**不是已经训练或验证过的自动语义分类器**。
不把关键词或同一对话中的角色称呼当原生参与证据。

规则覆盖 copy_only、ui_flow、business_rule、api_contract、database_schema、bugfix、
runtime_change、cross_module 等。纯文案只安排研发，其余角色记跳过原因。
普通业务变更可触发产品、架构、研发、测试；运行影响触发运维；数据库变更触发
可选专家。架构前置分析和后置事实复核为两个有区分的委派。

将已确认任务与授权整理为 `task-context/v1` 和 `collaboration-authorization/v1`，
字段见 `schema/collaboration/*.schema.json`。不复制旧 Goal 的 approved 状态。
授权文档必须定位真实确认来源；授权包含允许文件、批准的测试 argv 和明确的
attempt/parallel 上限。1–20/1–8 是实现校验上限，不是已批准的项目运行预算。
敏感权限、生产或破坏性信号默认 blocked；本候选不提供自动批准/豁免命令。

已有项目应在隔离分支按 `initdir.sh --upgrade` 预览，再按原规则批准应用；
MERGE/REVIEW 不强制覆盖。候选组件由两文件 Bootstrap 内嵌生成，不需要在线下载
Python 包。升级不会开启 V1.3 采集或信任 Hooks。版本仍为 1.3，不伪称发布完成。

## 3. 最小操作

以下为**目标项目**命令。不要在未经批准的业务任务上照抄示例授权。

```bash
python3 .ai/tools/agent_collaboration.py --run-id RUN-001 plan --context intake/collaboration-context.json
python3 .ai/tools/agent_collaboration.py --run-id RUN-001 ready
python3 .ai/tools/agent_collaboration.py --run-id RUN-001 drive --execute
python3 .ai/tools/agent_collaboration.py --run-id RUN-001 check
python3 .ai/tools/agent_collaboration.py --run-id RUN-001 report
```

`plan` 只保存计划，不启动模型。`drive --execute` 使用已有范围授权，按依赖派发、
建立交接、让指定接收角色独立审查。默认串行推进；显式并行调用也检查单写者、
范围冲突和共同依赖，非必要不扩大并发。主协调只在范围/规则变化时找人确认。
高风险信号、缺运行时、缺原始测试证据或拒收会停止推进，保留准确原因。

真实行为变更的 TaskContext 必须有 `verification`：tests、inputs、covers、command。
command 必须是授权内的 argv。内核在实现前复用原有 `evidence.py` 记录/核验有效
RED；实现后复用相同命令、未变测试和实际源版本生成 GREEN。实现角色不可写测试。
无需自动 TDD 的纯文案仍需批准的检查。没有证据工具/有效 RED 时不能因为新协议而
绕过旧规则。原始 recorder 的测试日志仍在 raw/evidence，其原有留存/脱敏责任不变。

```bash
python3 .ai/tools/agent_collaboration.py --run-id RUN-001 evidence --phase red
python3 .ai/tools/agent_collaboration.py --run-id RUN-001 evidence --phase green
python3 .ai/tools/agent_collaboration.py --run-id RUN-001 validate -- python3 -m unittest discover -s tests -v
python3 .ai/tools/agent_collaboration.py --run-id RUN-001 finish
```

validate 的命令必须与授权记录完全匹配；退出 0 是该命令的执行结果，不是业务接受。
finish 只说明可检查的工程约束满足；正式发布还需要真实宿主、旧回归与维护者接受。

## 4. 专业协助、交接和恢复

专业角色可返回 needs_assistance，附能力、实际证据引用和允许的产物范围。协调者
用同一注册表加入有界任务，要求交接接受后恢复原任务；不让专家自行递归启动。
也可显式调用 assist。相同证据请求幂等，未知/禁用能力不会被伪造为已启动。

上游 completed 不解锁下游。submit 创建不可覆盖的 handoff revision；review 由
指定接收角色的独立线程判断 accepted / changes_requested / rejected。接收必须
引用当前 artifact hash，不能用发送方自己“通过”的文本替代。
review 命令与 dispatch 都需要 --execute。独立性指独立执行实例，不等于独立人。
角色质疑、方案分歧写入授权产物；未经确定的业务规则不能由技术 Agent自选。

```bash
python3 .ai/tools/agent_collaboration.py --run-id RUN-001 submit --sender architecture_pre --receiver implementation
python3 .ai/tools/agent_collaboration.py --run-id RUN-001 review --handoff HO-architecture_pre-implementation-1 --execute
python3 .ai/tools/agent_collaboration.py --run-id RUN-001 retry --delegation architecture_pre
python3 .ai/tools/agent_collaboration.py --run-id RUN-001 recover
```

retry 追加 attempt，并使传递依赖/旧交接失效；旧产物按内容哈希留存，不删除失败。
recover 只将中断请求标为 blocked，不猜测模型是否成功，也不贸然重复执行。
外部代码或业务契约漂移会阻断。应审查变更、建立新基线/run，而不是修改旧历史
使检查通过。已经合法落地的控制器写入更新预期输入哈希，避免自身变化被误判。

本地文件批量提交不是数据库事务：每个文件原子替换，写入中断有 applying 记录，
恢复后必须人工核对部分写入。本候选不声称能自动补偿未授权的生产副作用。

## 5. 运行端与权限

适配器执行 initialize → thread/start → turn/start，核验线程/turn 响应，随后记录
AGENT_STARTED；失败、超时、请求被拒、只有角色文字都不能补造 started。
每个工作和交接复核是新会话；同一次回执重复到达不增加参与数。

真实子进程仅获得经批准的任务上下文快照，文件系统使用 readOnly/restricted。
它输出有 base_sha256 的改动建议；控制器先检查完整改动批次的路径/权限/旧哈希，
再应用到项目。未经批准的生产操作、secret 路径和治理规则写入被拒绝。
运行时额外 MCP、网络/工具配置及账号权限仍需要宿主隔离和项目审查；仅有 profile
和 JSON sandbox 参数不能替代对实际运行环境的验证。任何运行时审批请求都拒绝
并中止，由用户在正确入口处理，不使用绕过审批的 flag。

## 6. 日志与报告

执行控制正本 `.ai/collaboration/runs/<run>/NNNNNN.json` 是追加式事件+状态快照，
flock + 原子落盘保证本机并发一致性，可重载/检查哈希链。目录权限收紧，默认 Git
忽略，0600 文件。不存 prompt、模型原始回复、工具参数、原始运行时 ID 或错误详情。
`.ai/collaboration/artifacts/<hash>` 保存任务明确授权的交付物版本，以支持返工审计；
它们不是聊天日志，仍可能含项目代码/业务内容，只保存在本地批准范围，不自动上传。

复用 V1.3 开关：启用后发出 collaboration_transition 的白名单事件关联 run/角色。
关闭观测不关闭控制正本。可读 report 展示计划/实际实例、跳过、交接与审查、失败和
时间线。Token 目前展示可证实的 assignment 小计；review 用量尚未汇总，完整总成本
保持 unknown，不能用于宣布节省或跑分收益。fixture 默认不进入真实观测统计。

V1.3 原始 WorkRun/Handoff 格式不重写；新协议是该工作项一次协作的运行记录，
引用原 Goal/Story/Task/Evidence，不创建第二套业务生命周期。旧 CLI runner 保持兼容，
但它的 cli_role 不能被本候选升级成原生线程证据。

## 7. 验收与使用状态

在源码仓库运行：
```bash
python3 observability/embed.py
python3 collaboration/embed.py
python3 -m unittest discover -s collaboration -p 'test_*.py' -v
python3 collaboration/demo.py --output /tmp/ans-collaboration-demo
python3 scripts/check_bootstrap.py
```

设备台账检修等级是隔离样例，不是 jlcase 的已批准需求。demo 的 SQLite 操作和
测试是真实执行，专业 Agent 是确定性 fixture，不消耗模型、不算 AT-001。
其 report 必须显示 fixture；`check --release` 必须失败。原生协议运输测试也用
模拟 server，不代替实际账号和模型。

至少在一个经授权的真实 Codex 环境跑通架构/研发/测试独立线程与交接，再运行
`check --release`，且通过其余验收后才可讨论版本发布。它仍不是业务批准入口。
本候选不承诺自动把所有未来角色/宿主适配好，也没有常驻事件总线或图形控制台。

## 8. 初始化、热更新与本地验证入口

框架源码README的Quick Start A/B分别是初始化和安全增量更新提示词，C为单独授权的
本地验证。升级必须固定来源SHA并保留本地规则；相同framework_version也检查候选
组件/文件哈希。热更新不是运行中无停机替换：requested/running/applying工作先安全
完成或暂停，不能替换旧进程正在使用的工具。旧run/产物/观测记录保留，漂移用新run
处理，不修改历史基线。代码合并不发布V1.4，AT-001由真实获授权运行关闭。
