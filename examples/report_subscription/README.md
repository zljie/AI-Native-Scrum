# P0 Golden Path：报告订阅与报告需求（仅演示）

这是独立于框架内核的 **可运行示例**，用于验证三条 P0 路径：新功能、缺陷修复、需求变更。
它不是已批准业务项目，也没有真实的人工 Goal 验收或生产发布；不得将本目录中的
示例描述复制为 `raw/goals/` 下的已批准正本。

## 目标与能力

- `GOAL-DEMO-001`：用户可以订阅公开的日报/月报，并可以提交新的报告需求。
- `STORY-DEMO-001`：订阅支持跨 CLI 调用持久化；重复订阅幂等。
- `STORY-DEMO-002`：提出报告需求后记录为 `submitted`，而不是自动批准或生成报告。
- P0 Bugfix：大小写与空白造成的重复订阅必须有回归测试。
- P0 Change：新增周报种类需经过 Goal/AC 影响分析和**真实人类批准**才可实现；示例保持 BLOCKED。

## 执行

在仓库根目录运行：

```bash
python3 -m unittest discover -s examples/report_subscription/tests -v
python3 -m examples.report_subscription.cli --db /tmp/report-demo.sqlite subscribe --user demo-1 --report monthly-operations
python3 -m examples.report_subscription.cli --db /tmp/report-demo.sqlite list --user demo-1
python3 -m examples.report_subscription.cli --db /tmp/report-demo.sqlite request --user demo-1 --description "Create a new compressor health report"
```

命令会向提供的 SQLite 文件写入演示数据；请使用隔离的临时数据库，不要指向正式业务数据。

## 五角色的最小交接契约

| Gate | 演示中的角色/产物 | 当前真实状态 |
|---|---|---|
| PM_GATE | Product：两个 Story 与可观察 AC | 设计示例，未获真人批准 |
| TECH_GATE | Architect：SQLite 唯一键、ID/报告种类约束 | 实现可检查，但没有人工架构批准 |
| TEST_RED_GATE | Test：行为测试（可复现） | 通过测试不等于保留了当时真实 RED 证据 |
| DEV_GREEN_GATE | Dev：`service.py`、`cli.py`、单元/CLI 测试 | 本地测试可运行 |
| TEST_VERIFY_GATE | Test：独立复核代码 revision、命令与回归 | 需与本次实现者不同的执行者真实核查 |
| OPS_READY_GATE | Ops：仅本地 CLI，不部署；记录 N/A 原因 | 未宣称生产运行就绪 |
| GOAL_ACCEPTANCE | GoalExecutive 汇总证据交由人最终验收 | NOT_RUN，**不能由样例自动通过** |

## P0 场景

1. [`feature.json`](scenarios/feature.json)：完整 Goal 交付，角色覆盖最全。
2. [`bugfix.json`](scenarios/bugfix.json)：从失败回归用例开始，避免不必要的 Product/Tech 环节；修改 AC 时返回上游。
3. [`change_request.json`](scenarios/change_request.json)：变更申请必须阻塞在人的批准前，不能因为 Agent 建议正确就默认同意。

严格状态契约仍来自项目初始化后的 `schema/workitem-types.yaml` 与 `dev-flow.yaml`。
这些 JSON 是示例输入与测试夹具，不是新的生产级流程引擎。更进一步的交接、门禁、运行与追溯由后续独立分支补齐。
