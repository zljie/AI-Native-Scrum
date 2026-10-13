# Bootstrap 仓库协作入口

本仓库维护 `initdir.sh`、初始化自检及个人经验；目标项目的完整规则由脚本生成。
开始任务时读取 `WORKING_STYLE.md`，按当前问题检索 `wiki/learning/LRN-*.md`，
只使用符合适用条件的条目。记忆不能替代当前源码、用户指令或授权。

- 先检查相关代码、调用方、模板和文档，明确最小范围及验收；按用户要求确认后实施，既有授权持续有效。
- 只修改任务相关内容；遇到影响正确性的不确定信息先澄清，保留无关格式与备注。
- 修改初始化行为后运行 `python3 scripts/check_bootstrap.py`；在隔离临时目录验证，不在业务仓库直接试跑初始化。
- 使用 Node 22/24 和 python3。更改 Skill 时检查 frontmatter、入口、来源与权限边界。
- 汇报实现、测试、部署和业务验收各自的真实状态。
- 完成实质任务后，按 README 的学习闭环记录可复用方案与已复现的坑，复用时追加证据；同因经验更新原条目。
- 新经验为 candidate；成功复用或明确人工确认后才可标 validated。个人偏好、Skill、治理规则的修改须有明确授权。
- 将方法认可、资产复用和收益测量分开；资产优先选择已有检查、脚本、组件/模板或 Skill，复用后记录适配、验证和维护成本，无数据不宣称提效。
- 完成实质任务后追加 Tolaria MyWIKI 的 `Intake/YYYYMM.md`，先 get_note，按北京时间排序；同一件事当天跟进更新原条目，不写敏感信息。

交付/学习流程详见 README 的 Personal Delivery and Learning；目标项目使用生成的
`.ai/skills/delivery-loop/SKILL.md`。保留已有非空文件；升级先与临时生成结果比较。

初始化后的 Skill 入口（使用前读取对应文件）：

| 工作 | 入口 |
|---|---|
| 目标澄清 | `.ai/skills/goal-intake/SKILL.md` |
| 目标拆 Backlog | `.ai/skills/goal-to-backlog/SKILL.md` |
| Story 精炼 | `.ai/skills/story-refine/SKILL.md` |
| 工程任务拆解 | `.ai/skills/story-to-tasks/SKILL.md` |
| 已批准任务的实现、验收与沉淀 | `.ai/skills/delivery-loop/SKILL.md` |
| 证据导入 | `.ai/skills/ingest/SKILL.md` |
| 知识查询 | `.ai/skills/query/SKILL.md` |
| 知识一致性检查 | `.ai/skills/lint/SKILL.md` |

初始化项目保持知识边界：schema 为治理、intake 为待审批工作区、raw 为批准证据、
wiki 为正本、generated 为计算视图、site 为展示。遵循 schema 和已有审批，不复制正本，
不静默改写批准证据或治理规则；READY、测试通过和业务完成分别判断。
