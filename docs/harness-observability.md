# V1.3｜驾驭工程运行数据与架构迭代

## 本次交付的边界

V1.3 在既有 V1.2 角色、授权、Runner、Gate、Evidence 和 Work Graph 上增加**默认关闭、本地优先**的观测层，不是新的调度器。初始化仍只需要同版 `initdir.sh` 与 `00_AI_WARMUP.md`，生成器已内嵌观测工具；升级继续使用 `--upgrade` / `--apply` / `--mark-merged`，保留本地定制，不重写业务正本。

运行成功、测试通过、独立工程评估、人工业务验收是四个不同结果。本组件不会代人批准，不会新增模型调用，不会放宽沙箱/写入/发布授权。CI 使用确定性夹具；不把测试数据当作真实模型跑分。

## 第一次启用：在目标项目根目录执行

```bash
python3 .ai/tools/harness_observe.py status
python3 .ai/tools/harness_observe.py enable
# 先预览，再显式合并；已有 Hook 和其他设置保持不变。
python3 .ai/tools/harness_observe.py install-hooks --provider codex
python3 .ai/tools/harness_observe.py install-hooks --provider codex --apply
# Claude 用户使用 --provider claude；不必安装两个宿主。
```

在 Codex 中用 `/hooks` 审核并信任本次变更后的定义；不要绕过信任。修改配置可能需要新开会话。`configured` 只表示配置存在；必须运行一个真实请求后，`status` 的 `host_events_observed` 才能说明收到了宿主事件。无记录表示“未观测”，不表示“从未使用”。旧宿主若不支持新增事件，保持采集关闭或仅使用 Runner，记录版本兼容性缺口。

日常仍使用原有 `local_agent_runner.py` 命令。启用后，它在原授权校验后对**实际的 provider 子进程边界**采集运行、耗时与 Token。`route` 仍只规划，不启动 Agent；dry-run 仍不执行。任何未通过授权校验的任务不会因开启日志而执行。原有 WorkRun 不改变格式，通过 `run_id` 与私有 Trace 关联。

```bash
# 需要同时关联多个角色/门禁时设置一个非敏感、稳定的实验 Trace ID。
export AI_NATIVE_TRACE_ID=TRACE-EXP-001-A-01
python3 .ai/tools/local_agent_runner.py route --kind feature
# 原有 run 命令、--execute 和授权引用要求保持不变。
python3 .ai/tools/harness_observe.py report
python3 .ai/tools/harness_report.py --trace TRACE-EXP-001-A-01
python3 .ai/tools/harness_report.py --output generated/reports/harness-001.html
python3 .ai/tools/harness_observe.py disable
```

**不要把只读角色运行误当作原生子 Agent。** `codex exec` / `claude -p` 在 Runner 里一律标为 `cli_role`。只有收到含实例 ID 的 `SubagentStart` 宿主事件才记录 `native_subagent_started`。每个实例与父会话做散列关联；恢复同一实例不重复计为新实例。当地文件不是防篡改或身份认证系统，任何有同等文件权限的人都可能伪造日志。

## 采集范围与缺口

| 边界 | 当前可记录 | 不能据此认定 |
|---|---|---|
| Runner | 请求、实际进程启动、退出、耗时、失败/超时、provider 用量 | 功能正确、人工验收、原生委派 |
| Codex Hook | Session/Prompt/Tool/Subagent/Stop；PostModelRequest 的可用用量 | 所有工具路径均覆盖；无 Hook 等于无活动 |
| Claude Hook | Session/Prompt/Tool/Subagent/Stop；Skill 工具成功调用 | 调用 Skill 就正确执行了导演方法 |
| Gate checker | 两种 Gate 的真实结构/证据检查结果 | 生产发布授权、身份真实性、业务验收 |
| 实验人工/测试评估 | 适用性、指导效果、首轮通过、返工、人工时间与证据引用 | 自动认证评审者；自动证明因果提效 |

Codex 通过读取 `.ai/skills/.../SKILL.md` 执行的方法不能从普通文件读取自动确认为 Skill 调用。本版不会把 `cat SKILL.md` 算成导演已执行。对于这种路径，导演**有效性**需要独立场景验收；“无原生调用事件”不是“不可能执行”的证明。Router 当前仅有显式 `route` 规划，日志不会伪造一个不存在的自动分类器。

Codex/Claude CLI 输出协议未知、终止事件缺失、失败或超时，用量保留 `null`/不完整。Codex `input_tokens` 已含缓存读取；Claude 输入总量为 `input_tokens + cache_read_input_tokens + cache_creation_input_tokens`。推理 Token 不额外叠加到已含它的输出总量。每个 run 有总量时不再加同 run 的逐请求 Hook 用量；不同 run 仍计入，包括失败和返工。缺任一 run 用量或存在中断时，完整总量为 `null`，仅显示可核实的小计。跨子 Agent 的账户计费覆盖仍以 provider 输出范围为准；Token 不是订阅账单金额。

## 隐私、存储、成本与保留

事件为 `.ai/observability/events/<event-id>.json`，每条原子创建，不覆盖既有事件；私有配置与事件默认被目录内 `.gitignore` 排除，文件权限 0600。保存白名单元数据、哈希、用量和结果枚举，**不保存用户提示词、模型正文、工具参数/输出、环境变量、原始会话 ID、transcript 路径或原始错误消息**。不读取宿主历史 transcript，不发送到外部服务。Git HEAD、dirty 标志及框架/采集器指纹用于定位版本，HEAD 不覆盖未提交/未跟踪文件内容；精确验收仍需已有 Evidence 输入哈希。

健康报告同时提供真实执行的耗时中位数与运行耗时和；并行运行的耗时和不等于墙钟时间或人工工时。`--trace` 展示指定 Trace 的安全元数据时间线，不读取原始聊天。统计默认排除 `fixture` 数据。`--include-fixtures` 仅用于诊断。报告只导出汇总/显式评估数据到新 `generated/` 文件，不覆盖已存在报告；导出仍须审查后才提交 Git。事件不自动加入 Work Graph 正本，WorkRun 仍是原运行记录。开启 Hook 有本地进程/文件 I/O 成本，应在真实试跑测量，不能宣称零开销。

```bash
python3 .ai/tools/harness_observe.py prune --older-than-days 30         # 只预览
python3 .ai/tools/harness_observe.py prune --older-than-days 30 --apply # 显式删除过期事件
```

采集错误只输出固定诊断码，不打印敏感异常。观测层失败不改变 Runner 授权、返回码或 Hook 决策；数据缺口必须通过 `status`、报告和 stderr 排查，不把观测失败当业务失败，也不默默当成功。

## 数据驱动架构迭代

复用 `wiki/decisions/ADR-*.md` 保存架构决策，`wiki/learning/LRN-*.md` 保存经验证经验，新增 `schema/templates/experiment.md` 供按需创建 `wiki/experiments/EXP-*.md`。不在初始化中自动填写业务批准、实验数据或收益。

每轮形成：问题/基线 → 一个可证伪假设 → 一个主变量改动 → 固定用例与验收 → 新旧对照 → ADR 的采用/缩小/回滚决策 → 后续真实任务复核。PR、CI 说明实现是否回归通过，不能替代用户体验或效益数据。

### 配对实验数据契约

`harness_report.py --manifest wiki/experiments/EXP-001.json` 读取 `harness-experiment/v1`，顶层仅 `schema`、`experiment_id`、`cases`。每个 case 必含：

- `case_id`、正整数 `repeat`、`variant`（baseline/candidate）、`framework_revision`、唯一 `trace_ids`。
- 四个 64 位小写 SHA-256：`task_sha256`、`acceptance_sha256`、`model_config_sha256`、`environment_sha256`；同配对必须一致。模型版本、推理强度、runtime 版本、预算与工具权限应计入对应指纹。框架版本为实验变量，单独记录。
- `observation_complete`、`expected_director`（已知 Skill 名或 null）、`native_agent_applicable`。
- 独立评估：`director_guidance_passed`、`engineering_passed`、`first_pass`（bool/null）；`rework_count`、`human_active_seconds`（非负整数/null）。不是看到退出 0 就填写通过。
- `evidence_refs`（至少一个项目内实际非空文件）、`reviewer_source`（human/independent_test_runner）、`reviewer_id`。报告保存引用证据的内容哈希，但不认证作者身份。

缺失变体、重复 case、跨组重复 Trace、模型/任务/验收/环境指纹不同、缺证据、越界路径、被排除的模拟 Trace 均拒绝比较。未知值不补零。失败和返工 Trace 必须全部登记，否则成本仍有选择偏差。人工等待与主动操作时间不能互相替代。

当只有 CLI 角色日志而没有宿主采集覆盖时，子 Agent 参与率和 Skill 调用率为未知，不以零冒充未发生；导演指导效果单独依赖独立评估，不能因为 Codex 文件读取不可观测就判为无效。

六项指标：导演调用/独立有效性；原生子 Agent 参与；首次工程验收率；平均返工次数；每个通过用例的总 Token 成本（含失败）；人工主动操作秒数。每项同时列 known/missing；比例仅对已观测/已标注分母计算。建议先跑 10–20 个配对场景、多次重复、随机/交错 A/B 顺序，固定验收者/测试标准；本工具输出描述性比较，不宣称显著性或因果关系。

```bash
python3 .ai/tools/harness_report.py --manifest wiki/experiments/EXP-001.json \
  --output generated/reports/EXP-001-comparison.json
```

## 升级与验收清单

1. 保留现有规则，通过原有安全升级流程生成工具、Schema、模板与文档；`MERGE/REVIEW` 的 Runner/AGENTS 文件要人工审查，不强行覆盖。
2. 新项目默认采集关闭，`status`/空报告必须明确无数据；不得因无业务数据把初始化判失败。
3. 启用、合并目标宿主 Hooks、信任后，用真实会话核验事件；故意让一条安全命令失败，确认日志区分失败且不含内容。
4. 用有权限的只读 CLI 角色任务核验 Token；无可用登录环境则标 NOT_RUN，不以模拟结果替代。
5. 执行 `python3 -m unittest discover -s observability -p 'test_*.py' -v`（源码仓库）、Bootstrap 回归与 UI 既有检查。

协议参考（核对日期 2026-11-05）：OpenAI Codex [非交互 JSON](https://learn.chatgpt.com/docs/non-interactive-mode)、[Hooks](https://learn.chatgpt.com/docs/hooks)；Anthropic [Hooks](https://code.claude.com/docs/en/hooks)、[CLI](https://code.claude.com/docs/en/headless)、[缓存口径](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)。具体安装版本可能不同，协议未匹配时用量/覆盖保持未知。
