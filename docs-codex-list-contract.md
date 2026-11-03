# Codex 列表页规范：第一条可验证闭环

本轮聚焦 Codex，不扩展其他宿主。既有多平台文件保持兼容，不删除、不声称已统一强制执行。

## 已确认规范

搜索区在表格上方；分页区在表格下方；末三列严格为 **创建人 → 最后更新时间 → 操作**。
`createdBy`、`updatedAt`、`actions` 是语义槽名，不是强制 API 字段名。具体字段由项目映射；缺失数据需解决真实数据契约，不能编造。

初始化生成：
- `schema/ui/list-page.json`：版本化规范正本。
- `.agents/skills/frontend-list-contract/SKILL.md`：Codex 原生发现入口，不依赖临时聊天记忆。
- 根 `AGENTS.md`：列表页任务路由与执行边界。
- `schema/ui/pages.json`：项目自有页面登记，初始为空，空登记不能获得验收通过。
- `.ai/tools/check_ui_contracts.py`：验证登记与证据新鲜度，不假装执行浏览器测试。

已有项目使用现有 `--upgrade` 比较/批准流程，不能直接覆盖已修改的规则或 AGENTS.md。规则变更需用户授权；不得为通过验收删除登记、删除测试或放宽列序。

## 在真实项目接入

1. 登记适用路由、源文件、测试文件和真实字段映射。登记应在 review 中与路由清单比较，工具不能发现刻意遗漏的页面。
2. 使用现有组件库封装合规布局；参考 `examples/codex-list-contract` 的真实页面与浏览器测试，不把示例当成业务验收。
3. CI 先运行浏览器测试。报告 `pageIds` 必须覆盖全部登记页面。报告格式包含 `exitCode`、`testsPassed`、`testsSkipped`、`browser`、`viewport`、`command`、`checks`；checks 必含 layout、tail-columns、search-behavior、pagination-behavior。报告必须由测试运行器生成。
4. 测试成功后运行 `python3 .ai/tools/check_ui_contracts.py snapshot --report generated/ui-report.json --evidence generated/ui-evidence.json`。
5. 交付前用同样参数执行 `verify`。代码、测试、规则或报告变化使旧证据失效。

## 保障与边界

AGENTS.md/Skills 提供模型上下文，不等于保证模型永不违约。证据哈希只防过期误用，不防故意伪造测试报告；CI 必须实际运行测试，并通过审查确保页面登记完整。源文件登记还应包含影响布局的组件、样式和依赖锁。

本仓库 CI 验证框架生成行为及独立浏览器示例。目标业务项目必须接入自己的测试；只有维护者启用 required checks/分支保护后才有合并阻断效果。本轮不修改仓库权限和分支保护，不声称已部署业务页面。加载、空数据、错误恢复和窄屏需要项目特定验收，不能被四个结构反例替代。
