# Codexhost 委派约束

在 Codexhost 主聊天或用户明确选择 Codexhost 时读取。本文件约束 Lead 如何使用已有桥接能力，不实现新运行器，不安装或修改宿主。

## 先核对实际安装

1. 读取当前可用的 `codexhost-delegation` Skill。用环境提供的 `CODEXHOST_CLI_PATH` 执行 CLI；未设置时才尝试 `codexhost`。POSIX shell 使用 `"$CODEXHOST_CLI_PATH"`，PowerShell 使用 `& $env:CODEXHOST_CLI_PATH`。路径必须按当前 shell 正确引用，不使用 `eval`。
2. 读取 CLI 总帮助、`delegate --help`、具体子命令帮助；记录可验证的实际安装版本/构建来源。帮助和本机返回值优先于本文示例。命令不存在、连接失败或未登录时，相关委派为 NOT_RUN。
3. 由用户在正常宿主完成登录。不读取、复制或打印凭据文件、token，也不为探测能力创建 client、调整环境白名单或权限配置。
4. 核实本次独立委派的有效审批和沙箱策略是否符合已有授权。无法核实时不启动；不能把“只读分析”的提示词当作沙箱，也不能假定继承父会话权限。

以下是已核验的上游源码事实，**不代表用户已安装的版本**：

- `BytePioneer-AI/codex-host@a03b8826f7a6bde8a54a9707e3e330dd077bb4a7` 的 [Skill 目录发现](https://github.com/BytePioneer-AI/codex-host/blob/a03b8826f7a6bde8a54a9707e3e330dd077bb4a7/packages/skill-library/src/directories.ts) 包含用户级 `~/.agents/skills`。发现目录不等于当前会话已加载。
- 同提交的 [官方桥接 Skill](https://github.com/BytePioneer-AI/codex-host/blob/a03b8826f7a6bde8a54a9707e3e330dd077bb4a7/packages/host-runtime/src/delegation-skill.ts) 要求读取帮助、创建独立任务会话、收到通知后读取 Thread。
- 同提交的 [Codex adapter](https://github.com/BytePioneer-AI/codex-host/blob/a03b8826f7a6bde8a54a9707e3e330dd077bb4a7/packages/host-runtime/src/app-server-host.ts) 在独立委派路径调用 `thread/start` 与 `turn/start`，传入 `approvalPolicy: "never"`、`sandbox: "danger-full-access"`。**该路径不能被描述成继承父会话的受限权限。** 如果实际安装仍采用该策略且超出当前授权，不运行此路径，返回具体阻塞；不自行扩大授权或修改宿主来放行。

## 绑定、派发与回收

能力与权限核实通过后，按已读帮助使用实际支持的接口：

- 新委派显式设置业务项目的绝对 `cwd` 和已核实的父 Thread；若本机帮助支持 `--cwd` / `--parent-thread`，在 `delegate start` 使用它们。不依赖 Host 默认工作目录，不猜测父 Thread。
- 先给导演发送完整 B1；读取并核对结果后形成 D1，再将同一版 B1 + D1 分别交给产品、架构。三份工作单均只读分析，禁止专业子会话递归委派。沿用宿主默认模型/思考配置，除非已有明确选择。
- 保存真实返回的任务链接、Thread、父 Thread、cwd 与输入版本；项目/父 Thread 不符或 `PARENT_THREAD_AMBIGUOUS` 时停止后续派发，报告绑定问题。
- `watch` 通知仅表示状态。核对实际 `watch.state`：`watching` 才是已登记，`alreadyTerminal` / `alreadyNeedsInput` 不会再另发通知，`notRegistered` 也不表示委派未启动。用实际 `thread read` 或已完成且包含产物的 `thread wait` 读取结果，不能以 started/completed 字样代替回收审查。结果/消息视图不包含完整工具 Trace，不用它证明全部工具行为。
- 等待使用有界超时；超时表示仍未完成。保留已读结果和运行引用，继续其他独立工作或报告进展，不无限轮询。
- 小修回到原 Thread。先读其状态再发送；遇到 `THREAD_BUSY` 不默认使用 `--steer` 或取消重启。未授权时不创建 worktree、不修改项目文件、不自动开下一轮。

## 恢复与跨项目

- 恢复前按本机 `thread list` / `thread read` 帮助查找并核对已有任务、项目、父 Thread、B/D 与规范版本；列表须跟随 `nextCursor` 直到结束，不能把首页未找到当作实例不存在。没有查询能力时保留 NOT_RUN/未完成状态，不猜测结果或重复启动。
- 如果使用帮助支持的 `--request-id`，只对完全相同的项目、父 Thread、职责与输入重试复用该值。输入改变则使用新的请求标识；不得把不同项目或不同版本复用为同一请求。
- 同一停止通知可能重复。按真实实例及其已接受输入版本去重，不能因重复通知再次派发产品/架构。切换项目时重新绑定，旧 Thread 仅保留为原项目证据。

命令参数与上述状态语义来源：[固定版本 CLI 帮助](https://github.com/BytePioneer-AI/codex-host/blob/a03b8826f7a6bde8a54a9707e3e330dd077bb4a7/packages/host-runtime/src/delegation-cli-help.ts)。实际执行前仍以本机帮助为准。

## 对外证据名称

| 实际发生的调用 | 可报告的事实 | 不能据此报告 |
|---|---|---|
| Codexhost 创建独立 Thread，并保存 Host 父子关系 | Codexhost 独立会话委派与回收 | Codex 原生 `spawn_agent` 已验收 |
| 直接通过 Codex app-server 创建独立 Thread | app-server `runtime_session` | 原生子 Agent |
| 真实 `spawn_agent` 调用及可核验的父子生命周期 | 对应宿主的原生子 Agent 证据 | 其他项目/宿主也已通过 |

Skill 被发现、静态检查、通知、fixture、另一个云端聊天的协作均不能关闭用户本地 Codexhost 的真实验收。需要宿主证据而当前无法访问时，明确记录 NOT_RUN。
