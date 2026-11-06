# Changelog

## Unreleased — 通用协作候选与 Quick Start

新增角色无关协作候选（collaboration-candidate/1）、独立可选数据库专家、交接与返工、
Codex app-server runtime_session适配、事件追踪与跨场景测试。更新README的初始化及
热更新提示词，固定来源SHA、保护本地规则、暂停活动运行后再更新，并独立安排本地
观测与真实协作验证。代码合并供本地验证，不改变framework_version 1.3；真实AT-001、
其它发布门禁与维护者确认未完成前，不发布V1.4。

## 1.3 — Observability P0（已合并，PR #9）

新增默认关闭、本地优先的事件采集、Runner 与 Gate 边界观测、原生 Hook 的可选增量接入、Token 标准化与去重、健康报告与配对实验比较。新增 ADR/EXP 记录与实验模板；初始化仍为双文件自包含，升级保留本地定制。

真实/fixture 数据隔离；未知用量不补零；CLI 角色与原生子 Agent 分开；Skill 调用与指导效果分开；工程评估与人工业务验收分开。没有开启自动多 Agent 调度、生产部署、远程日志上传或新权限。

## 1.2 — 已有基线

PR #2–#7：CI、P0 示例、交接、证据门禁、本地 Runner 与 Work Graph。PR #8：Codex 原生列表页契约与浏览器验收示例。上述是功能历史，不是效益测量。
