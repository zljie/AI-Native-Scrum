# Lead Quickstart：本地安装一次，多个项目复用

`ans-lead` 是主聊天的协作入口。默认使用规划模式：你在本地 Codexhost 打开一个已有项目、提出目标，Lead 组织导演、产品和技术架构的真实独立会话，回收后交付首轮计划。明确要求推进研发时，按已有授权进入交付合同；继续原迭代时先核对并恢复原任务。

**交付状态：规划与研发闭环候选。** 源码在本仓库 `skills/ans-lead/`；本指南同时提供未合并候选的获取方式。合并状态以 GitHub PR 为准，目录存在于候选分支不表示已经进入 main。真实本地宿主验收见最后一节。

完整研发链路的源码接入见 [研发闭环指南](lead-development-loop.md)。当前 Codexhost 独立线程尚未接入 ANS Engine 的真实执行入口，选择交付模式时会明确保留这个阻塞；安装 Skill 不能消除适配、权限与真实验收缺口。

## 目录

- [1. 分清安装位置与项目位置](#1-分清安装位置与项目位置)
- [2. 获取并安装候选](#2-获取并安装候选)
- [3. 核对 Codexhost 的实际能力与权限](#3-核对-codexhost-的实际能力与权限)
- [4. 在项目主聊天使用](#4-在项目主聊天使用)
- [5. 更新、恢复与切换项目](#5-更新恢复与切换项目)
- [6. 真实宿主验收](#6-真实宿主验收)

## 1. 分清安装位置与项目位置

| 位置 | 放什么 | 生命周期 |
|---|---|---|
| ANS 源码 checkout | 可审查的 Skill 源码与本文 | 获取/更新版本时使用 |
| 用户级 `~/.agents/skills/ans-lead/` | 通用 Lead 流程、交接模板、Codexhost 接入约束 | 同一台机器安装一次，多个项目复用 |
| 当前业务项目 | 该项目的 AGENTS.md、API/前端/SDD/测试规范、既有 Goal/方案/任务记录 | 每次调用按当前项目重新读取和绑定 |
| Codexhost 当前主聊天与独立委派线程 | 本轮目标、任务与返回结果 | 保留实际线程引用，恢复时核对项目和版本 |

本 Skill 可用于尚未初始化 ANS 的已有项目；不要求复制整个 ANS 仓库到业务项目，也不要求运行 `initdir.sh`。已有 ANS 项目继续复用原有 Goal/SOL/Task/Journal 与准入规则，不建立第二套权威台账。当前 Skill 不代替专业 Agent 初始化/评审模块。

## 2. 获取并安装候选

### 2.1 在业务项目外获取源码

需要 Git；下列命令在 macOS/Linux shell 或 PowerShell 中均可获取源码。请选择业务项目以外的目录，目标 `AI-Native-Scrum-lead` 必须尚不存在：

```sh
git clone --branch feat/ans-closed-loop-sprint-20261124 --single-branch --depth 1 https://github.com/zljie/AI-Native-Scrum.git AI-Native-Scrum-lead
git -C AI-Native-Scrum-lead rev-parse HEAD
git -C AI-Native-Scrum-lead status --short
```

记录输出的实际提交 SHA，检查该提交的 PR 差异与 CI。后续安装只读取这份已固定的本地 checkout，不再次混合下载移动分支中的单个文件。若候选分支已删除，先在 GitHub 找到已审阅且包含 `skills/ans-lead/SKILL.md` 的提交并检出；不要直接假定旧 main 已包含它。

审阅 `skills/ans-lead/SKILL.md` 与 `references/`。若已有本仓库 checkout，可使用其中已核实的候选提交，不必再次 clone。不要在此步骤运行初始化器或安装宿主。

### 2.2 安装通用 Skill

将完整 `skills/ans-lead/` 目录复制为用户主目录下的 `.agents/skills/ans-lead/`。安装位置应直接包含 `SKILL.md`、`agents/openai.yaml`、`references/handoff.md`、`references/codexhost.md`、`references/delivery-loop.md`，不能多套一层目录。已存在同名目录时先比较，保留已有定制。

下面的 Bash 示例需要 Python 3，在上一步 clone 所在的父目录运行；路径中的空格受支持。它拒绝覆盖已有目录、文件或符号链接，只复制 Skill，不修改业务项目或宿主配置：

```bash
export ANS_LEAD_SOURCE_DIR="${ANS_LEAD_SOURCE_DIR:-$PWD/AI-Native-Scrum-lead/skills/ans-lead}"
export ANS_LEAD_INSTALL_DIR="${ANS_LEAD_INSTALL_DIR:-$HOME/.agents/skills/ans-lead}"
python3 - <<'PY'
import os
import shutil
from pathlib import Path

source = Path(os.environ['ANS_LEAD_SOURCE_DIR']).expanduser().resolve(strict=True)
target = Path(os.environ['ANS_LEAD_INSTALL_DIR']).expanduser().absolute()
required = ('SKILL.md', 'agents/openai.yaml', 'references/handoff.md', 'references/codexhost.md', 'references/delivery-loop.md')
if not all((source / item).is_file() for item in required):
    raise SystemExit('Source is incomplete; no installation performed')
if target.exists() or target.is_symlink():
    raise SystemExit(f'Existing target preserved; compare before updating: {target}')
target.parent.mkdir(parents=True, exist_ok=True)
shutil.copytree(source, target)
for item in required:
    if (source / item).read_bytes() != (target / item).read_bytes():
        raise SystemExit(f'Copy verification failed: {item}')
print(f'Copied and verified Skill files: {target}')
print('Host discovery and real delegation: NOT_RUN')
PY
```

Windows 用户可用文件管理器将同一完整目录复制到 `%USERPROFILE%\.agents\skills\ans-lead`；存在目标时取消覆盖并先比较。此文只提供通用目录复制，不声称已经验证每个操作系统的宿主发现行为。

在 Codexhost 中刷新 Skill 列表或重新打开该列表，确认能找到 `ans-lead`，并核对显示的实际来源路径。若当前聊天看不到它，按实际宿主提供的加载方式在项目新聊天中检查；不要仅凭磁盘目录存在声称已激活。用户级目录的上游依据见 [接入约束](../skills/ans-lead/references/codexhost.md)。

## 3. 核对 Codexhost 的实际能力与权限

确认 Codexhost 已运行、当前项目/聊天绑定正确，并由用户本人在正常宿主完成登录。读取本机的 `codexhost-delegation` Skill 和 CLI 帮助，不输出登录凭据。

POSIX shell 的只读帮助检查：

```bash
ANS_HOST_CLI="${CODEXHOST_CLI_PATH:-codexhost}"
"$ANS_HOST_CLI" --help
"$ANS_HOST_CLI" delegate --help
"$ANS_HOST_CLI" thread --help
```

PowerShell 优先用 `& $env:CODEXHOST_CLI_PATH ...`；未设置该变量时才使用 `codexhost ...`。实际版本可从宿主版本信息或其帮助支持的版本命令核实，不假设所有版本支持同一标志。

派发前确认以下事实：

- 支持创建独立任务线程，以及查询、等待和读取实际返回；通知不能代替读取。
- 能显式绑定本次业务项目绝对路径与正确父线程，并核对实际回执。工作目录不是文件访问沙箱。
- 本次委派的有效审批/沙箱权限符合已有授权，模型与思考设置沿用宿主默认或用户已选择值。

**已知版本限制：** 已核验上游提交 `a03b8826` 的 Codex 委派路径用 `thread/start` / `turn/start` 创建独立 Thread，参数为 `approvalPolicy: "never"`、`sandbox: "danger-full-access"`。它不能被当作继承主聊天的受限权限，也不能据此证明原生 `spawn_agent`。详见带固定源码链接的 [Codexhost 接入约束](../skills/ans-lead/references/codexhost.md)。这是该提交的事实，实际安装版本需要另行核实。

若权限行为未知，或该路径超出当前授权，本轮真实委派为 **NOT_RUN**。Lead 可整理 Brief 和待派发工作单，明确能力缺口；不能自行放宽权限、修改环境白名单、创建凭据或改用云端测试宣称本机验收通过。

## 4. 在项目主聊天使用

在 Codexhost 选择实际业务项目并打开主聊天。使用如下提示；项目路径可以由 Lead 根据真实宿主绑定核对，用户无需提供内部线程 ID：

```text
$ans-lead
我当前业务项目的目标是：<业务目标>。
成功表现是：<可观察的结果>。
本轮范围与已有约束：<已知范围；未知则注明>。
先核对当前项目目录，读取该项目 AGENTS.md、API、前端、SDD 与测试规范，记录来源版本。
在当前 Codexhost 能力与权限确认符合已有授权后，委派导演推演；你实际读完结果后，
再把同一版目标和导演结果交给产品与技术架构，回收、对齐并制定最小实施计划。
这轮止于计划。缺失能力、登录、权限或规范请如实列出；没有运行的委派标 NOT_RUN。
```

预期交付包括：目标和首轮范围、导演场景摘要、产品/架构结论、带依赖及验收条件的工作包、待决事项，以及真实会话/输入版本/回收证据摘要。产品或架构只有职责提示但未创建真实独立会话时，不能报告“专业 Agent 已参与”。

B 表示本轮目标摘要 Brief 的版本，D 表示导演结果的版本；恢复和汇总时核对二者及项目规范版本。

Lead 每轮读取项目实际规范，作为专业角色工作单的要求；规范缺失则保留为待核实项。已有初始化产物与准入规则时按其当前版本使用，不把别的项目规范自动复制过来，也不把“读过规范”写成“专业 Agent 初始化已验收”。

要明确请求完整迭代，可以在同一主聊天使用：

```text
$ans-lead
围绕当前项目的这个目标开展一轮研发迭代，按我已有的研发范围授权推进。
先复用/核对计划，再按实际影响组织导演、产品、架构、数据库、UI/UX、研发、测试和运维。
使用项目现有准入、任务图、交接与证据机制；验收失败回责任任务修复并独立重验。
最终分别报告工程交付、技术验证、导演场景、用户接受与发布状态，给出未完成项和复盘。
宿主/适配不可用时保留已完成材料并指出阻塞；不把其他宿主、fixture 或角色文字当作本机验收。
```

这段提示表达用户意图，不是新 CLI 或自动授权。当前候选的 Codexhost → Engine 接缝未完成，不能凭此提示声称已进入真实研发执行；现有生产/合并/部署/权限边界持续有效。

## 5. 更新、恢复与切换项目

**更新 Skill：** 等本轮规划完成或安全暂停，获取新提交并记录 SHA；比较全局安装目录与新 `skills/ans-lead/` 的差异。保留定制，将旧安装目录移动到 Skill 发现目录之外并保留为备份，确认原安装目标已不存在，再复制获准的新版本。不要在多个被扫描目录同时保留同名有效 Skill，避免来源歧义。安装示例遇到已有目标会停止，不会自动升级。

**回退 Skill：** 将当前安装目录移动到 Skill 发现目录之外保留为备份，确认原目标已不存在，再将已核实的原版本恢复到该位置，重新核对宿主显示的来源。版本回退不删除已有规划记录，也不使旧结果自动适用于新规范；宿主重新发现及回退后的真实委派仍需实际验证。

**恢复同一轮：** Lead 先查询真实已有线程，核对项目、父聊天、B/D 输入与规范版本，再继续原线程的等待/读取或聚焦追问。超时不代表完成，重复通知不重复派发。不能从旧通知猜测结果，不能悄悄开一批新线程冒充恢复。

**切换项目：** 在 Codexhost 切换至另一个业务项目，建议开该项目的主聊天，使用同一个 `ans-lead`。重新建立项目绑定和输入快照。不得复用上一项目的线程、API 规范或结论；全局 Skill 中也不写回这些内容。

**规范变更：** 记录新版本与受影响的角色分析，保留旧结果并标记已被替代，只重做受影响部分。Lead 汇总前再次核对来源版本；不同版本结果不能直接拼成已完成计划。

## 6. 真实宿主验收

本候选的文件/安装示例检查与用户真实宿主验收分别记录。当前交付未接入用户本地的登录 Codexhost，以下验收均为 **NOT_RUN**；表格是后续执行要求，不是已完成测试。

| 验收项 | 通过条件 | 当前状态 |
|---|---|---|
| 用户级发现 | 真实宿主显示 `ans-lead` 及正确用户级来源；业务项目无需各复制一份 | NOT_RUN |
| 有效权限 | 记录实际版本与本次委派的审批/沙箱行为，符合已有授权；不靠提示词假装限制 | NOT_RUN |
| 导演先行 | 主聊天创建真实独立导演会话，读取结果后才派发产品/架构 | NOT_RUN |
| 同版下游输入 | 产品和架构是两个独立会话，收到同一版 B/D 与该项目规范 | NOT_RUN |
| 回收可查 | 保存真实会话引用、父子关系、cwd、输入版本及已读取的产物；Lead 检查冲突 | NOT_RUN |
| 两个真实项目 | 项目 A、B 分别使用自身已存在且不同的规范；全局 Skill 无业务内容，回执/结果不串项目 | NOT_RUN |
| 变更失效与恢复 | 真实运行中规范变化/中断后核对旧实例与版本，受影响结果失效，恢复不重复派发 | NOT_RUN |
| 更新/回退 | 用户真实宿主对所选新旧版本重新发现正确来源，定制和历史证据保留 | NOT_RUN |
| 模式边界 | 默认规划止于计划；明确交付要求只在既有授权、项目准入和真实执行入口均满足时继续 | NOT_RUN |

两项目验收应使用获准的真实业务项目和真实规范，不用示例 fixture 替代。宿主不支持、无登录或权限无法核实时保留 NOT_RUN 并记录具体原因；实际执行且证据违背条件时记录 FAIL，不能也写成未运行。

此处通过仅能证明对应已验证的本地 Lead 路径。完整交付还需 [研发闭环指南](lead-development-loop.md) 的真实执行、联合验收和返工证据。ANS 原生 `spawn_agent`、业务接受与 V1.5 发布仍各自遵循 [V1.5 发布门禁](iterations/V1.5-RELEASE-GATES.md) 和已有授权。
