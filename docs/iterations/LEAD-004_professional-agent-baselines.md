# LEAD-004：所有专业 Agent 的方法基线

日期：2026-11-26。状态：研发候选，基于 PR #27 的 `68c408e26c1e0f1dbe0450eb0987c785de4022c0`；不合并 main、不升级框架版本、不宣布 V1.5 发布。

## 目标与选择

用户要求在已有前端/DBA 之上，为全部专业 Agent 补齐可复用基线。复用当前默认六角色与 opt-in Sprint 八角色、Lead、原 Engine/Journal/Context Pack、V1.3 observability 以及已有流程 Skill。外部调研核验 4 个一手仓库中 8 个候选正文、固定提交和许可证；选取专业方法编写 ANS 自身的适配基线，没有安装或复制第三方调度体系。

完整角色映射、专业产出、外部来源与项目实例化要求见 [专业 Agent 基线](../professional-agent-baselines.md)。

## 实际变更

- 新增 `professional-baseline` 共同方法，统一任务/项目/规范版本、权限、可验证交接及失效处理。
- 新增导演、产品、架构、UI/UX、通用研发、测试、运维 7 个专业方法入口；前端/DBA 两份原 Skill 增加共同入口，保留既有专项内容。共 10 份 practice Skill。
- 两套 registry 明确绑定共同与各角色方法；默认六角色与 Sprint 八角色的 policy 不变。原生 Codex/Claude 五角色模板、DBA 与 Sprint 导演/UIUX profile 同步引用。
- 通过实际 `collaboration/embed.py --apply` 分发方法与说明文档，保留初始化/升级的非空文件与定制保护。Sprint 角色及策略仍为 opt-in，方法存在不使其自动安装/启动。
- 更新 Lead 交付说明、README 与 Quickstart；候选获取分支改为本轮分支，说明用户级 Lead 安装不等于业务项目方法升级。
- 新增 6 项专业基线协议测试；Sprint fixture helper 从真实源补齐专业方法；扩展生成项目验证，涵盖全部方法、默认原生 profile 与 Sprint 非默认安装边界。

Engine、CodexAdapter、默认/Sprint policy 未修改。角色选择、授权、Journal 和原有配置写域/哈希/失效检查继续复用，不新增调度器、准入旁路或生命周期状态。

## 验收结果

| 检查 | 本轮实际结果 |
|---|---|
| 10 份 practice + ans-lead 格式检查 | Skill Creator quick_validate 全部 PASS |
| 专业基线协议 | 6/6 PASS；实际文本/哈希、8 角色包、缺引用拒绝、变更在 adapter 前拦截、两项目 fixture 规范区分 |
| 原 Sprint 回归 | 27/27 PASS，267.221s |
| 生成项目/升级/Schema/SQLite integration | 5/5 PASS，53.306s；回执仍为 fixture，真实 Agent 验收 NOT_RUN |
| 既有前端/DBA 绑定 | 3/3 PASS，0.048s |
| README Quickstart 回归 | 6/6 PASS，0.019s |
| 必需隔离 bootstrap | PASS，exit 0；现有定制和业务资料保留 |
| 嵌入一致性、shell、diff | 两套 embed 无差异；`bash -n`、`git diff --check` PASS |
| 文档 | 10 个本地链接目标可解析、3 段 Quickstart shell 语法 PASS |
| 独立文本演练 | 2 次真实云端子 Agent 返回；QA 拒绝旧版本/错误原生证据，架构保留当前项目技术栈和授权。只证明这两份演练的输出，不代表所有角色已在真实项目验收 |

测试和演练记录见 [本轮证据](../../generated/reports/2026-11-26-professional-agent-baselines.txt)。本候选提交的远端 CI 以本次 PR 上精确 head 的 Actions 结果为准；本文件不预写尚未执行的远端成功。

本轮顺带核实上游 PR #27 的原 head：4 条 CI 工作流/5 个 job 全部成功，Collaboration 145 tests/226.201s，并在该 PR 描述补齐具体 job 链接。其结果不代替本候选新增内容的验证。

## 仍未完成的验收

用户真实登录 Codexhost、原生 spawn_agent、专业角色在实际项目中按当前方法工作、两个真实项目的隔离/规范失效与恢复、完整技术/导演联合验收均为 NOT_RUN。Codexhost → Engine 适配仍 BLOCKED；app-server runtime_session 不作为原生子 Agent。INIT-S2 仍需单独核实和整合，不能通过本轮新增 Skill 绕过。

本轮没有生产数据库、部署、权限扩大、main 合并或发布。专业方法的注册、传递和哈希检查不证明收益；遗漏率、返工、耗时和维护成本均未测量。下一步在已授权的真实项目完成规范绑定、实际方法使用与独立验收，再讨论基线增益和 V1.5 发布门槛。
