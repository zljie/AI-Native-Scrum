---
id: LRN-007
type: learning
title: Codex 原生发现入口与列表契约的可验证边界
category: pattern
status: candidate
derived_from: []
evidence: [scripts/check_ui_contracts.py, examples/codex-list-contract/tests/list.spec.cjs]
applies_when: 在 Codex 中把已批准的 UI 规范应用到明确登记的列表页面
do_not_apply_when: 页面尚未登记或真实浏览器检查未通过，不能宣称业务验收完成
created_at: 2026-11-03
last_verified_at: 2026-11-03
reuse_evidence: []
human_confirmation:
assets: [initdir.sh, scripts/check_ui_contracts.py, scripts/check_ui_example_evidence.py]
reuse_benefit_status: unmeasured
supersedes: []
---
# Codex 列表契约与证据边界

原生 `.agents/skills` 入口与根 AGENTS.md 路由让约束可发现；它们不是强制安全边界。批准规则以版本化 schema 为正本，项目登记真实路由、字段映射、组件/样式/测试文件；布局与行为需要实际浏览器测试，不能用 grep 或手写成功报告替代。

本轮新增四种结构违例的浏览器负例及空登记、过期证据、缺测试、跳过测试的失败检查。初始化/证据检查在隔离目录通过；本机浏览器因 socket 权限无法启动，因此浏览器断言结果未确认。CI 已配置，但未执行、未启用 required checks。

该模式只证明已登记对象，不能发现故意遗漏页面；源依赖登记须审查。证据哈希防过期误用，不防故意伪造报告。新经验保持 candidate，无收益测量。
