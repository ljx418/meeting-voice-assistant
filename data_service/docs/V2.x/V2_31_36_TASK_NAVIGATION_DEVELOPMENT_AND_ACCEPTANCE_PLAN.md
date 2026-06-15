# V2.31-V2.36 开发及验收计划

## 1. 共享开发规则

- 每个 Phase 开始前必须产出 phase development plan、phase acceptance plan、pre-implementation audit。
- Pre-implementation audit 无 open fatal/major 后才允许进入业务实现。
- 每个 Phase 完成后必须产出 acceptance audit、PRD/spec review、false-green review。
- 真实数据验收必须覆盖 data_service；HarnessOS 作为大项目验收样例，无法完成时必须 structured blocker。
- 不允许 mock-only acceptance。
- 不允许将 heuristic relationship、import dependency、token overlap 写成 deterministic runtime call。
- 每个 accepted artifact 必须可落盘、读回、通过 schema validation。
- Public Surface Inventory 不得把当前运行中的 data_service MCP registry 注入外部 codebase；外部项目的 MCP surface 必须来自其自身生产源码。
- 没有确定性 public surface 的大型项目必须 `accepted_with_blockers` 继续生成任务导航、关系图、impact、reading pack、handoff、closure；不能返回硬失败，也不能伪造 surface。
- 每个 accepted relationship 必须有 repo-relative path、line_range、evidence_refs；缺任一项必须降级为 `needs_review` 并进入审计统计。

## 2. Phase 97：Task-Aware Navigation Index

开发内容：

- 定义 task taxonomy：api、mcp_tool、cli、workflow、provider、bugfix、test、docs、architecture_review、unknown。
- 从 surfaces、symbols、architecture intent、context packs、tests、docs 中建立 task navigation index。
- 支持 task query artifact，输出 ranked candidates、evidence、needs_review、blockers。

验收：

- data_service 5 个真实任务返回非空 ranked candidates。
- 每个 candidate 有 evidence 或 needs_review。
- HarnessOS 3 个任务返回结果或 blocker。
- 无 public surface 的真实/fixture 项目返回 `TASK_NAVIGATION_PUBLIC_SURFACES_UNAVAILABLE` blocker，但 index build 成功。
- Index artifact 不修改 V2.0-V2.30 输入 artifacts。

## 3. Phase 98：Lightweight Call & Impact Graph

开发内容：

- Python AST direct call baseline。
- import/reference graph。
- handler dispatch、MCP registry、CLI parser relation。
- config/test references。
- forbidden relationship scanner。

验收：

- forbidden relationship count = 0。
- `direct_call_ast` 只来自 AST 可验证语法。
- `module_imports_module` 不被写成 runtime call。
- 抽样至少 30 条 evidence line range 真实性。
- 所有 accepted relationship 自动检查 line_range、evidence_refs、repo-relative path。
- 无 surfaces/mappings/imports 时输出结构化 relationship blocker，但不阻断可从 symbols/tests/config 生成的关系。
- HarnessOS 输出 accepted relationship 或 structured blocker，不允许项目特化伪成功。

## 4. Phase 99：Change Impact & Test Selection

开发内容：

- impact analyzer v2。
- upstream/downstream/reference/doc/test/architecture guardrail 分类。
- likely test ranking。
- risk budget 与 major/fatal pinning。

验收：

- data_service 5 个真实任务均给出 impacted files 和 suggested tests。
- 每条 suggested test 有 evidence 或 needs_review。
- fatal/major architecture guardrail 不被 ranking 隐藏。
- HarnessOS 若无法给出测试推荐，必须说明缺失 evidence 类型。

## 5. Phase 100：Module Reading Pack & Token Ledger

开发内容：

- 生成 required/optional/skip 阅读包。
- token estimate、omitted reason、cache key。
- Markdown + JSON 输出。
- Role-specific reading pack：coding_agent、review_agent、maintainer、documentation_agent。

验收：

- 小 token budget 下不保留无 evidence 建议。
- 至少 5 个任务证明 reading pack 比 naive all-related files 更小。
- `omitted_items` 非空时必须有 reason。
- Token ledger 必须保留 evidence floor，不允许删除 evidence 后保留高置信 recommendation。

## 6. Phase 101：Copilot Agent Integration API

开发内容：

- HTTP/MCP/CLI public contracts。
- task_navigation、task_impact_analyze、module_reading_pack、agent_handoff、closure。
- `test_selection` 由 `impact-v2` payload 返回；`reuse_patterns` 由 `reading-pack` payload 返回。
- stable envelope parity。
- Tool catalog 和 public surface guard 更新。

验收：

- HTTP/MCP/CLI 三端 stable fields 一致。
- CLI 输出合法 JSON。
- MCP tool specs 出现在 tool catalog。
- public surface guard 更新并通过。
- Error envelope 在 success/failure path 上三端一致。

## 7. Phase 102：Closure, UX Report, Governance

开发内容：

- HTML 可读报告。
- Mermaid 关键关系图。
- governance target summary / accepted blocker visibility / needs_review visibility。
- 完整 review queue 与 feedback workflow 不在本阶段声明为 completed capability。
- full coverage matrix。
- data_service + HarnessOS benchmark summary。

验收：

- data_service 与 HarnessOS E2E 报告可读。
- HTML 至少包含：任务解释、必读模块、关系图、影响范围、测试建议、风险、token ledger、blocker。
- Mermaid 中每个 node id 可回溯到 persisted artifact。
- 全量 backend tests 通过或记录环境性非产品阻塞；产品测试不得跳过。

## 8. 出门条件

- 所有 accepted row 有真实测试、artifact、E2E、审计报告。
- 无 open fatal/major。
- 不声称 full call graph / data flow / control flow / type inference。
- Copilot 类 Agent 可以通过 MCP 获取任务级最小上下文。
- Human reviewer 可以通过 HTML 报告判断任务导航质量和 blocker。
