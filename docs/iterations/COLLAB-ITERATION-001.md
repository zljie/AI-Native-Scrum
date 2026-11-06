# 通用协作候选迭代｜范围、落地与剩余门禁

依据：用户上传 ANS-V14-P0-COLLAB-PRD-001 v1.0；本轮用户明确授权继续实施。
原 PRD 的 draft/仅编制文档状态保留为来源历史，不被冒充业务 Goal 批准。
补充决定：独立可选 Database Agent；通用五角色协作是目标，数据库只是样例。

版本纪律：保留 FRAMEWORK_VERSION=1.3。候选组件 collaboration-candidate/1。
只有全部 P0 和真实环境验收完成，才可提出发布 V1.4。本轮用户授权先合并候选代码
与Quick Start，随后由用户本地验证；合并不等于V1.4发布，不执行生产部署。

## 实施工作包

| WP | 本轮实现 | 验证/边界 |
|---|---|---|
| WP-01 现状清点 | 复用现有五角色、Skill、Evidence、观测与两文件升级 | 上游9e369347；实际源码快照可复核 |
| WP-02 统一协议 | TaskContext/角色能力/授权/交接/事件 JSON Schema；stdlib校验与追加式状态 | 正反向单测、schema验证 |
| WP-03 激活适配 | 可配置能力映射、跳过原因、原生Codex app-server线程适配；不可用/超时分支 | 协议运输测试为fixture，已登录宿主NOT_RUN |
| WP-04 交接调度 | 接收审查、返工版本、精确下游失效、协助请求、并发汇合及单写者 | 真值来自当前版本产物，不由completed推断 |
| WP-05 日志报告 | 因果事件、实例引用、脱敏Markdown追踪、V1.3可选桥接 | 文件哈希不等于身份认证；总成本未知 |
| WP-06 试点 | 数据模型样例真实SQLite RED/GREEN；UI/API/bug/ops非DB协议用例 | 8项域测试是真实执行；Agent是fixture |
| WP-07 升级迁移 | Bootstrap内嵌、原生Skill与DB专家入口、V1.3安全升级测试、保留本地定制 | 不开启采集，不改业务、不发布版本 |

## 验收追溯

| AT | 可执行测试/证据 | 能证明什么 |
|---|---|---|
| AT-001 | `check --release`；真实宿主仍NOT_RUN | Fixture必被拒；无真实启动不发布 |
| AT-002 | test_AT002_simple_no_unneeded_roles | 简单任务单Agent与跳过理由 |
| AT-003 | test_AT003_no_result_no_dependency_unlock | 缺交接/未接受不解锁 |
| AT-004 | test_AT004_AT009_rework_retains_revision_and_events | 退回、新revision、旧记录保留 |
| AT-005 | test_AT005_unavailable_is_not_started | 运行端缺失不伪造启动 |
| AT-006 | test_AT006_no_receipt_cannot_complete、运输超时测试 | 请求不等于启动或完成 |
| AT-007 | scope_denied、production_blocks、审批拒绝测试 | 控制器拒绝越界写/生产信号；宿主完整权限仍需实测 |
| AT-008 | drift_at_review、task_context_change、out_of_band_source | 产物/上下文变化阻断 |
| AT-009 | rework_retains、artifact_archive | 重交不覆盖旧内容与结论 |
| AT-010 | fake_role_words、fixture_cannot_enter_real、live_gate_never_passes_fixture | 文本/模拟回执不能成为真实参与 |
| AT-011 | duplicate_receipt、timeout_retry | 幂等/保留每次attempt |
| AT-012 | parallel_join、parallel_same_write_scope | 多依赖接受与写冲突阻断 |
| AT-013 | reopen_same_run、orphan_request_recovers | 追加日志恢复，不猜测中断结果 |
| AT-014 | secret_not_in_trace、hash_chain、symlink、missing_ref | 元数据内容最小化及缺口显式失败 |

各项仅在最终测试日志显示通过后计为协议/确定性证据。不得把全部单测绿灯等同于
AT-001在真实环境通过，不把UI/API路由用例冒充真实浏览器/API功能验收。

## 已明确未完成/不应隐去

1. 已登录、允许模型调用的真实Codex环境中，独立线程与交接端到端AT-001：NOT_RUN。
2. 父会话spawn_agent直接委派后端：本候选使用runtime_session，不声称实现该后端。
3. 原生Skill由宿主自动发现/实际引导效果：有入口和方法绑定，真实效果未验收。
4. review调用Token未汇总；报告只给assignment已知小计，整体成本未知。
5. Windows未适配fcntl文件锁；首个目标为macOS/Linux。
6. 上轮本地候选以源码/补丁交付；本轮已获用户授权更新Quick Start并提交合并。
   远程提交与CI结果以对应PR/Actions实际记录为准，不从本地报告推断。

## 发布前剩余步骤

按本轮授权在开发分支提交候选并通过CI后合并；在隔离项目以真实来源记录授权，使用已登录
Codex运行维护等级样例或真实小功能。核实线程回执、独立接收、原始RED/GREEN、
架构后置复核，输出真实run报告并运行--release。权限/MCP隔离、Skill激活和例外
处理均需实际验收。维护者确认所有P0与兼容结果后，再单独修改版本/发布记录。
