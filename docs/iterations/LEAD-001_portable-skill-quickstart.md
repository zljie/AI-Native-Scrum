# LEAD-001：可跨项目安装的 Lead 与 Quickstart

日期：2026-11-24（北京时间）。状态：候选已实现，真实用户宿主验收 NOT_RUN。

## 问题与本轮范围

用户需要在本地 Codexhost 安装一次、在多个已有业务项目中复用 Lead。前一轮个人 Skill 的安装与当前聊天中的协作测试，没有把源码提交到 ANS 仓库，也不能证明用户本地宿主可用。

本轮从 `main@78be107c2a6b271c48d37d7cb8a12c3655dc3f2b` 开发，交付 `skills/ans-lead/` 与可执行的安装说明。V1.5 PR #12/#13 已合并；本次 Lead 是后续独立候选。未合并 main，未部署、发布或改变权限，未操作生产数据库。

## 实际变更

- 复用现有 `ans-lead` 的导演 → Lead 回收 → 产品/架构 → Lead 计划流程，新增明确的业务项目/父线程绑定、规范版本与失效规则、跨项目和恢复约束。
- 分发目录只有通用 Skill、UI 元数据、交接模板与 Codexhost 接入约束，不包含项目路径、业务规范、登录信息或运行结果。
- README Quick Start 保留 A/B/C 并新增 D；[独立指南](../lead-quickstart.md) 说明候选提交获取、用户级安装、已有目标保护、调用、更新/回退及真实两项目验收。
- 复用 Codexhost 已有 `codexhost-delegation` 与实际 CLI 帮助，不添加运行器、调度器、数据库或自动执行功能。不会调用 ANS 初始化器来修改用户全局配置。
- 固定引用上游 `a03b8826` 的源代码，明确其独立 Codex Thread 的 `never` / `danger-full-access` 行为；权限未核实或超授权时不启动。Host 父子线程与原生 `spawn_agent` 证据分开。

## 验证与实际证据

本地检查见 [执行记录](../../generated/reports/2026-11-24-lead-quickstart.txt)：

| 检查 | 结果及含义 |
|---|---|
| Skill frontmatter/命名校验 | PASS；只证明包的基础格式 |
| 现有 Quickstart 回归 | 6/6 PASS；保留初始化/升级提示及已安装命令契约 |
| 嵌入一致性 | PASS，`changed: []`；未改 `initdir.sh` 或嵌入资产 |
| 文档中 3 个 shell 命令块 | Bash 语法 PASS；没有执行远程 clone 或宿主命令来冒充本机验证 |
| 临时目录运行原文安装示例 | 5 个场景 PASS：含空格路径、重复安装保留定制、符号链接冲突、普通文件冲突、不完整源 |
| 本地引用 | 5 条链接可解析；固定上游源码另行只读核验 |
| 用户真实 Codexhost | NOT_RUN，无用户本机连接/登录证据 |
| 发布 | 未评估为可发布，未关闭 V1.5 门禁 |

远程 CI 以本 PR 的实际 head、工作流运行与 job 结果为准；主分支历史绿色结果不代替候选 CI。仓库现有 CI 是回归证据，不证明本次 Skill 已在用户宿主执行。

## 未完成与后续验收

使用用户实际登录的 Codexhost，在授权允许的有效权限下，完成指南的用户级发现、导演先行、产品/架构同版输入、真实产物回收、两个业务项目隔离、规范变更失效、恢复和更新/回退验收。缺登录/能力/权限证据保留 NOT_RUN；执行后条件不满足记 FAIL。

本最小版本止于计划。完整 Scrum 运行和原生 `spawn_agent` 是独立门槛；[V1.5 发布门禁](V1.5-RELEASE-GATES.md) 保持有效。合并 main 与发布仍需新授权。

## 复用记录

复用了现有 Lead Skill、`collaboration/test_quickstart.py` 与 `collaboration/embed.py`。适配成本为项目绑定、宿主差异、全局分发说明和复制保护检查；没有可比较的投入/结果测量，不声明提效收益。按 [LRN-005](../../wiki/learning/LRN-005_检查配置入口而不只检查脚本.md) 验证真实文档入口，按 [LRN-008](../../wiki/learning/LRN-008_协作回执与交接门禁.md) 分开记录启动、回收与业务/发布验收。

本会话没有可调用的 Tolaria MyWIKI `get_note` 能力，`Intake/202611.md` 外部记录未写入；本文件保存本轮可复核记录。
