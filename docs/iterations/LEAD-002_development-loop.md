# LEAD-002：多角色研发闭环候选

日期：2026-11-24（北京时间）。状态：源码候选，真实用户宿主 / 原生委派 / 业务验收 NOT_RUN。

## 目标与基线

用户希望沿用本地主聊天中的通用 Lead，把每一个目标作为一轮 Scrum：导演推演，产品与架构规划，专业设计和研发，测试与导演分别验收，失败回责任任务修复，最后 Review / 复盘。专业要求在每个项目内初始化，不能写回全局 Skill 后串到其他项目。

本轮基于 PR #25 `51681fe5d817a1782e841b1fa9b84b71a50bf76a`，开发分支为 `feat/ans-closed-loop-sprint-20261124`，新增 PR 以 #25 的分支为 base。main 仍为 `78be107c2a6b271c48d37d7cb8a12c3655dc3f2b`。#12/#13 已合并成果继续复用；本轮没有合并 main，也没有操作生产数据库、部署、发布或扩大权限。

源资产核对包括 collaboration-candidate/1、V1.3 observability、V1.5 Context Pack / Activation / Task Graph / Evidence、PR #22 的 Sprint RFC、PR #23/#24 的项目初始化候选和 #25 的可分发 Lead。#22 是 RFC，不存在可直接使用的 Scrum CLI；#24 不在本分支依赖树中，没有把它的准入能力写成当前可执行能力。

## 实际实现

| 位置 | 本轮变更 |
|---|---|
| `skills/ans-lead/` | 默认规划、明确交付、恢复原轮三种意图；新增专业角色、项目初始化、执行入口、联合验收与返工合同 |
| `collaboration/sprint/` | 在既有六角色上增加导演 / UIUX，提供八专业角色、十三候选步骤的显式选用 registry / policy；按当前信号激活 |
| `collaboration/v15_controller.py` | `plan` 可显式传 `--registry` / `--policy`；默认值和执行权限检查不变 |
| `collaboration/agent_collaboration.py` | 配置写域冲突在 plan 阶段拒绝；任务包提供当前身份及传递前置产物清单，供实际 Agent 生成可绑定的结果 |
| `collaboration/sprint_flow.py` | 复用现有 make_plan 的只读预览，以及原 check / graph / metrics / history 的联合检查；不建立新 Journal、不执行返工、不关闭业务目标 |
| `initdir.sh` | 同步共享 Engine / controller 的嵌入版本；Sprint 配置和检查器仍为源码级选用资产，默认六角色初始化保持不变 |
| README 与 Lead 指南 | 安装一次、当前项目实例化、交付提示、显式配置接入、宿主限制、联合验收、返工、恢复及真实验收条件 |

场景合同 / 报告绑定当前 run、Task、sample_kind、实际 attempt、节点归属、合同与传递前置产物哈希、完整场景清单和证据哈希。实例信息从既有回执与 Journal 核对，作者不能猜测实例 ID。任务返回 completed 不代表场景 PASS；必验 FAIL / NOT_RUN 阻断联合通过。涉及 `ui_flow` / `business_rule` 的任务即使漏配导演也不能降格为不适用。

输入与规范漂移、前置交接接受、RED/GREEN、受限产物应用、重试次数、下游失效、未知副作用恢复和观测均复用原实现。自动 `drive` 仍顺序执行；没有新增自动并行调度器。检查给出的返工位置只是建议，由 Lead 核对实际证据后使用原有入口执行。

## 本轮实际协作与审查

当前会话实际调用并回收了独立的 `closed_loop_director`、`closed_loop_product` 和 `closed_loop_architecture`，产品与架构使用同版目标摘要与导演结果。另由 `closed_loop_asset_audit` 做资产 / 独立测试工作，`lead_quickstart_review` 做源码与文档审查。它们是本次云端研发协作证据，不是用户本地 Codexhost 角色发现、初始化或原生委派验收。

本轮真实发现并修复的问题：

1. 首次未执行场景时，原 Engine 的 `result_refs: []` 被当成非法结果，导致显示 INVALID。现在仅将这个明确的初始空值作为无结果，正确保留 NOT_RUN，其他非法类型仍拒绝。
2. registry / profile 等配置引用中的 `./`、重复分隔符与授权写域可能指向同一文件。冲突比较现在使用经既有安全路径解析后的实际路径，覆盖文件及祖先目录。
3. 场景合同需要的 Task / sample_kind 和传递前置哈希原先只在测试侧读取 Engine 状态取得。实际任务包现在提供这些上下文；测试作者不再依赖这条侧通道。
4. 无导演节点时原先可以直接判场景不适用。现在先核对受版本约束的当前影响信号；必需场景缺角色保持 NOT_RUN 并阻断。

这些是源码 / 协议层的实际修复，不是实际业务项目中的缺陷回放；没有编造真实项目成功返工案例。

## 验证记录

本地命令、最终结果与变更文件哈希见 [执行记录](../../generated/reports/2026-11-24-lead-development-loop.txt)。远程 CI 以本轮 PR 的实际 head 和各 workflow / job 为准，最终运行链接记录在 PR 描述中，避免把历史 main 或 #25 的绿色结果当作本候选结果。

| 检查 | 实际结果 |
|---|---|
| 最终 Sprint 回归 | 27/27 PASS，166.540 秒，退出码 0；含当前任务包、场景缺失/失败、漂移、返工、路径保护与只读检查 |
| 旧 Engine 定向回归 | 4/4 PASS；依赖汇合、交接、返工历史及合法源文件变更 |
| 既有 Quickstart 回归 | 6/6 PASS |
| 隔离 bootstrap / upgrade | PASS；最终共享 Engine / controller 嵌入版本已检查 |
| 嵌入一致性、Shell 与 Skill 格式 | PASS；两个 embed 检查均 `changed: []` |
| 安装说明原文验证 | 3 个 shell 块语法 PASS；临时目录内 5 个复制/拒绝覆盖场景 PASS |
| 独立源码与文档复核 | 三个明确接缝已修复，最终静态审查无新增提交阻塞 |

确定性回归使用真实 Engine、临时项目文件、实际本地验证命令与明确 synthetic 的 Agent 回执 / 场景观察。它验证协议结构、失败阻断和版本失效，不能验证真实角色的推理质量或真实用户路径。隔离初始化只在临时目录运行；文档复制检查没有修改用户级 Skill 安装。

## 剩余门槛与下一轮

| 待办 | 完成条件 | 当前状态 |
|---|---|---|
| Codexhost → Engine 实际适配 | 真实接口与有效权限明确；启动、结果、交接、失败及恢复回执能被同一 Engine 接收，不绕过 `UNTRUSTED_ADAPTER` | BLOCKED / 未实现 |
| 项目角色初始化接入 | 复用实际可用 INIT-S2 准入；API / 前端 / SDD / 数据 / 测试规范按项目绑定，规范变更使受影响结果失效 | 本分支未集成 #24，真实验收 NOT_RUN |
| 单个真实项目完整纵向切片 | 导演 → 设计 → 实现 → 独立技术验证 → 真实场景回放 → Review；若实际失败，按责任任务修复并重验 | NOT_RUN |
| 两项目隔离、漂移与恢复 | 两个获准真实项目分别使用自己的规范和线程；中断不重复派发，未知副作用先核实 | NOT_RUN |
| 原生 `spawn_agent` | 指定真实宿主的工具调用及父子生命周期证据，不能由 app-server runtime_session 或 Codexhost Thread 替代 | NOT_RUN |
| 用户业务接受与 V1.5 发布 | 独立真实决定及全部原发布门槛满足；main 合并和发布获得新授权 | NOT_EVALUATED / 未授权 |

真实纵向切片优先沿用实际存在且获准的 V15-AT-001 设备台账项目。当前没有用户本机登录宿主和项目连接，不能用临时演示或本会话协作代替。后续按 [研发闭环指南](../lead-development-loop.md) 和 [V1.5 发布门禁](V1.5-RELEASE-GATES.md) 执行。

## 复用记录

本轮没有增加 Task 数据库或第二套运行台账。适配成本包括两角色合同、可绑定的场景协议、任务包字段、路径保护、旧初始化兼容、独立回归和文档维护；收益未测量，不声明提效比例。沿用 [LRN-008](../../wiki/learning/LRN-008_协作回执与交接门禁.md) 的证据分层，追加同因复用记录，继续保持 candidate。

本会话未发现可调用的 Tolaria MyWIKI `get_note` 能力，`Intake/202611.md` 外部记录未写入；本文件保留本轮可复核记录。
