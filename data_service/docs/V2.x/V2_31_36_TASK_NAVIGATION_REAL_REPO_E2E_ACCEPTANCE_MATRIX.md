# V2.31-V2.36 真实仓库 E2E 验收矩阵

## 1. 验收仓库

| 仓库 | 用途 | 必须结论 |
| --- | --- | --- |
| `/Users/Zhuanz/Desktop/workspace/data_service` | 本项目自举验收 | accepted task navigation、impact、test selection、reading pack、public contract |
| `/Users/Zhuanz/Desktop/workspace/harnessOS` | 大项目泛化验收 | accepted relationship 或 structured blocker；不得项目特化伪成功 |

## 2. data_service 真实任务

| 任务 | 必须输出 | 不可接受情况 |
| --- | --- | --- |
| 新增 MCP tool | MCP registry、handler、CLI、HTTP、tests、public surface guard | 只返回搜索关键词，无文件/行号 evidence |
| 修改 codebase snapshot | snapshot service、registry、tests、artifact schema、secret skip gate | 把 generated artifacts 当作输入事实 |
| 新增 architecture report 字段 | report builder、HTML renderer、context pack、tests | HTML 中出现 artifact 不存在的新事实 |
| 修改 provider adapter | provider registry、health、execution boundary、security tests | provider unavailable 被写成 accepted |
| 调整 quality governance | feedback/rules/review/plan、read-time overlay、tests | approved rule 改写原始 artifact |

## 3. HarnessOS 真实任务

| 任务 | 必须输出 | 允许 blocker |
| --- | --- | --- |
| 修改 workflow dispatch | workflow files、runtime adapter、tests 或 blocker | dynamic dispatch unresolved |
| 新增 station/agent descriptor | descriptor、registry、orchestration evidence 或 blocker | descriptor registry missing |
| 审查 mission TUI entrypoint | entrypoint、workflow relation、test relation 或 blocker | TUI launch relation unavailable |

## 4. 共通验收指标

| 指标 | 门槛 |
| --- | --- |
| required_reads 非空 | 必须 |
| 每条 recommendation 有 evidence 或 needs_review | 必须 |
| token ledger 存在 | 必须 |
| omitted_items 有 reason | 必须 |
| forbidden relationship count | 0 |
| public path leak | 0 |
| HTTP/MCP/CLI parity | 必须 |
| HTML/Mermaid no unpersisted facts | 必须 |
| full backend regression | 必须通过或记录环境性非产品阻塞 |

## 5. False-Green Rejection

以下情况不得验收通过：

- 用 mock-only 数据替代真实仓库。
- 把 import dependency 写成 runtime call。
- 把 token overlap 当成 accepted relationship。
- 为 HarnessOS 写硬编码路径规则但未泛化到 artifact contract。
- 删除 evidence 后保留高置信 recommendation。
- HTML/Mermaid 生成 artifact 中不存在的节点。
- public payload 泄露绝对路径、secret、traceback。
