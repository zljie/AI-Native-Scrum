# ANS 项目级专业 Agent 初始化｜迭代计划与 S1 增量

状态：研发候选；不是 V1.5 发布、真实 Agent 验收或项目部署完成。

## 1. 目标与基线

用户已确认：ANS 只定义通用 Scrum 流程、角色职责与治理契约；接入具体项目后，绑定该项目的接口、前端框架、SDD 等规范，生成可追溯、可校验、可更新的专业角色配置。实际任务再绑定当前工作范围，不把项目专属规则硬编码到通用模板。

基线检查：
- main：`78be107c2a6b271c48d37d7cb8a12c3655dc3f2b`；PR #12/#13 已合并。
- 代码依赖：PR #21 的 `011cb829079019039b357c75a7067239c65138e1`，复用其输入类型加固，不复制修改。
- Scrum 设计参考：PR #22 / `7522a637b8bece5cf61c91a78e0917b325d9d034`。该 RFC 仍为设计，不宣称 Sprint 控制器已实现。
- 本增量采用独立 stacked Draft PR，base 为 PR #21 开发分支；不修改 main、#21 或并行 V2.0 分支。
- 既有角色注册表、Project Context 路径/哈希/不可覆盖写入工具保持复用；后续使用已有 Activation、Engine Journal、Task Graph 与 V1.3 Observability。

## 2. 不变量

1. 框架角色、项目规范、任务上下文分层；项目或任务不能自行扩大授权。
2. 事实文件与声明的规范分开；发现代码现状不等于批准新规范。
3. 规范有来源、确认记录引用和版本；文件存在/哈希匹配不认证确认者身份，不证明语义正确。
4. 配置候选、配置接受、真实实例启动、工程验收、业务接受分别记录。
5. `runtime_session` 不等于父 Agent 的原生子 Agent；fixture 不代替真实宿主。
6. 任务状态继续以既有 Engine/工作项为正本；配置清单不是第二套任务数据库。
7. 不合并 main、不部署、不访问生产数据库、不扩大权限、不自动启用遥测或 Hooks。

## 3. 四轮迭代与完成定义

按依赖推进，不承诺未经确认的日期或人力。每轮均包含 Planning、实施、Review 和 Retro；时间盒关闭不等于所有任务验收通过。

| Sprint | 目标与工作包 | 角色职责（计划，不代表已启动） | 完成证据 |
|---|---|---|---|
| INIT-S1 | A01 冻结请求/清单契约；A02 只读规范与事实绑定；A03 角色配置候选及漂移检查；A04 正反向测试 | 主 Agent 协调；架构定义契约；研发实现；测试独立复核 | 两项目同角色不同规范；缺项/冲突 BLOCKED；漂移 STALE；不可伪造授权；确切 HEAD CI |
| INIT-S2 | A05 各角色初始化任务与确认流程；A06 生成可读工作说明；A07 任务绑定与派工前门禁 | 产品/架构确认规范来源；专业角色提出初始化结果；测试验证门禁 | 独立接受记录绑定 profile version；任务绑定 profile+Context+授权；失效配置不能派工；保留单 Agent 明示降级 |
| INIT-S3 | A08 OMP 宿主能力核查与适配；A09 真实专业子 Agent 初始化/执行/交接；A10 Trace | 主 Agent 调度；OMP 原生角色实例；测试独立验证 | 真实父子回执、项目/角色/attempt/版本绑定；失败/中断不伪造完成；不支持时 NOT_RUN，绝不放宽权限 |
| INIT-S4 | A11 Bootstrap/安全升级与回滚；A12 规范更新与任务失效传播；A13 完整 Sprint/AT-001 | 架构影响复核；研发集成；测试回归；运维仅交付就绪 | 不覆盖项目定制；升级回滚；规范变更影响范围；真实项目 Review/Retro；再评估发布门禁 |

复用原则：初始化流程属于现有角色协作的任务类型；不另建永久常驻初始化 Agent，不把五角色无条件全部启动。原生实例身份和权限由宿主验证，提示词自述不作证据。

## 4. S1 本轮实现范围

新增源码 `collaboration/project_agents.py` 与测试 `collaboration/test_project_agents.py`。

- `build`：读取显式 `project-agent-init-request/v1` 和已有 `agent-capabilities/v1`，只选择已启用角色及其既有 capabilities/contract_ref。允许同一角色不同 variant，不写死 Vue/React 或任何项目技术栈。
- 分别绑定 `fact_refs`、`standards`、`confirmation_ref`、`conflict_refs`。必需规范缺失或显式冲突未解决时返回 BLOCKED；关键文件不存在、输入畸形、敏感路径或越界则拒绝。
- 生成 `project-agent-profile-set/v1`，保存来源引用、SHA256、角色版本和依赖，不复制规范正文，不执行规范内的指令。
- `check`：显式要求期望 project_id，核对当前文件并重新派生清单。重算哈希不能掩盖删除依赖、增加 capability 等改写。
- 文档漂移定位受影响角色；请求、注册表或公共角色契约变更保守失效其依赖者。旧清单不改写。
- CLI 只允许新增 `generated/project-agents/` 下文件；拒绝覆盖已有文件、符号链接和治理目录写入。

### 明确尚未实现

S1 **不是**角色完成初始化的真人/模型证明。所有候选始终携带：

```json
{
  "runtime_status": "NOT_RUN",
  "authorization": "not_granted",
  "semantic_review": "not_performed",
  "confirmation_identity": "not_verified"
}
```

`CANDIDATE` 仅表示声明的结构完整且没有已列出的缺项/冲突，不叫 READY 或 APPROVED。S1 不分析规范正文、不发现隐含语义冲突、不证明必需规范列表完整，不认证确认者，不发现宿主，不渲染/安装 OMP 配置，不派工。

本增量尚未内嵌 `initdir.sh`，需从 ANS 源码显式调用；不会声称已安装到业务项目。现有 `drive` 尚未接入本门禁，因此不能声称已阻断所有实际任务。任务/交接失效传播在 S2/S4 集成。

## 5. S1 可运行接口与请求示例

下面命令从 ANS 源码执行，`--root` 指向获准读取的项目。示例路径必须替换为真实文件；示例本身不授予执行权。

```bash
python3 collaboration/project_agents.py --root /authorized/project build \
  --spec intake/agent-init.json \
  --output generated/project-agents/profile-001.json

python3 collaboration/project_agents.py --root /authorized/project check \
  --manifest generated/project-agents/profile-001.json \
  --project-id project-a
```

退出码：0 = 当前结构候选；1 = BLOCKED 或 STALE；2 = 非法输入/写入被拒。0 绝不是授权或发布成功。

```json
{
  "schema": "project-agent-init-request/v1",
  "project_id": "project-a",
  "registry_ref": "schema/collaboration/registry.json",
  "roles": [
    {
      "role_id": "developer_agent",
      "variant": "frontend",
      "required_standards": ["frontend", "api", "sdd"],
      "standards": {
        "frontend": {"source_ref": "docs/frontend.md", "confirmation_ref": "docs/decisions/engineering-baseline.md"},
        "api": {"source_ref": "docs/api.md", "confirmation_ref": "docs/decisions/engineering-baseline.md"},
        "sdd": {"source_ref": "docs/sdd.md", "confirmation_ref": "docs/decisions/engineering-baseline.md"}
      },
      "fact_refs": ["package.json"],
      "conflict_refs": []
    }
  ]
}
```

顶层及绑定对象拒绝未知字段；不能加入 permissions、工具授权或覆盖 system prompt。规范分类名称为项目自定义标识符，不将项目专属要求写入通用内核。只哈希显式源文件，限制文件数量/大小，沿用 Context Pack 的敏感路径策略。

## 6. S1 验收清单

| ID | 检查 | 证据类别 |
|---|---|---|
| AT01 | 同一研发角色在 Vue/React 两个隔离测试项目产生不同配置版本且不串项目 | 确定性文件测试，不是模型执行 |
| AT02 | 既有五角色、可选数据库角色、同角色不同变体可绑定 | 注册表复用测试 |
| AT03 | 事实不能补足缺失的规范；显式冲突保持 BLOCKED | 负向契约测试 |
| AT04 | 来源/确认/公共契约漂移，旧配置 STALE，旧历史保留 | 文件变更回归 |
| AT05 | 错项目、伪造运行状态、重算哈希后的额外 capability/省略依赖被拒 | 负向契约测试 |
| AT06 | 输入类型、路径、符号链接、JSON 重复键/深度、输出覆盖受控 | 安全回归 |
| AT07 | 从完整仓库实际运行 Bootstrap，消费其真实生成角色契约，不修改宿主角色文件 | 生成项目集成测试 |
| AT08 | Collaboration、Observability、P0 示例、Framework/Bootstrap/浏览器回归 | 确切 HEAD GitHub Actions |
| AT09 | 独立专业 Agent 初始化/Review、真实 OMP/原生子 Agent、业务 AT-001 | 本轮 NOT_RUN；不得由 AT01–AT08 代替 |

测试命令：

```bash
python3 -m unittest discover -s collaboration -p 'test_project_agents.py' -v
python3 -m unittest discover -s collaboration -p 'test_*.py' -v
python3 -m unittest discover -s observability -p 'test_*.py' -v
python3 -m unittest discover -s examples/report_subscription/tests -v
python3 observability/embed.py
python3 collaboration/embed.py
python3 scripts/check_bootstrap.py
```

## 7. 本轮 Review / Retro 与后续入口

当前执行环境 `git ls-remote` 返回 DNS 错误，不能取得完整本地检出。通过已连接 GitHub 通道读取精确 SHA 的文件；本地定向测试使用完整 `project_context.py` 与 `registry.json` 原文件，Git blob SHA 分别核对为 `2eaaca93b03038d31541458454221c60d61a72a8` 与 `eeee4c1624cb392933d052703ead98ff1ff03166`。这不是本地全仓库验收。

完整回归交给既有 GitHub Actions，其结果必须绑定本 PR 实际 HEAD，不能借用 #21 或 main 的旧成功记录。确切测试数、CI URL 和最终提交记录在 PR 描述/进展中，未取得结果时保持待核验。

本轮由一个执行 Agent 开发和自查，未声称独立架构/测试 Agent 已运行。独立 Review 和真实宿主验收 NOT_RUN。已有确定性测试只证明工具行为。

可复用经验（candidate）：配置文件应标为 CANDIDATE 而非 READY；manifest 的自报状态和自算哈希不能替代从源请求重新派生；敏感目录读取边界不应为了宿主配置便利而放宽。尚无时间/Token 收益测量。

下一轮从 A05–A07 开始：规范接受记录与角色初始化任务、可读工作说明、现有派工前检查及版本绑定。不得在接入前把这个源代码候选当成已部署的 OMP 多 Agent 系统。
