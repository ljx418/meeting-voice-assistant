# V2.38 项目里程碑与出门条件

## M0：文档基线完成

出门条件：

- PRD、目标架构、开发验收计划、Gap、drawio 已落盘。
- 文档审计无 fatal / major。

## M1：版本索引完成

出门条件：

- 可读取 latest architecture understanding version。
- 可比较两个版本。
- artifact hash gate 生效。

## M2：增量影响分析完成

出门条件：

- 代码变更可映射到 impacted architecture nodes。
- stale artifacts 可见。
- 不需要全仓重读即可生成影响摘要。

## M3：能力链路完成

出门条件：

- data_service 至少 5 条 capability chain accepted。
- HarnessOS 至少完成 chain extractor attempt，成功或 structured blocker 都要有证据。

## M4：Verification v3 完成

出门条件：

- supported / weakly_supported / unsupported / contradicted / code_not_documented 全部可见。
- supported 双边 evidence 规则自动测试通过。

## M5：人类报告与 Agent Pack 完成

出门条件：

- HTML 报告可读，有图表，不展示源码。
- Agent Pack 可用于任务级代码阅读，包含 token budget 和 omitted_items。

## M6：V2.38 Closure

出门条件：

- data_service、HarnessOS、codexPat E2E 完成或 structured unavailable。
- public surface guard 通过。
- V2.38 focused suite 通过。
- PRD coverage matrix 每个 accepted 行都有证据。

## 后续路线里程碑

### M7：大型项目性能基线

出门条件：

- 大型项目 scale profile 可生成。
- scan budget、timeout、partial artifact 状态可见。
- artifact readback 支持分页。

### M8：多语言 AST/LSP Provider 基线

出门条件：

- Python AST mandatory provider 通过。
- TS/JS fixture 通过基础 symbol/import 抽取。
- tree-sitter/LSP 未配置时 structured unavailable。

### M9：Workflow / Runtime Candidate 基线

出门条件：

- workflow manifest、runtime adapter、agent registry、CLI/TUI/console entrypoint 至少完成 extractor attempt。
- 成功或 blocker 都有 evidence。
- 不输出 production runtime topology。

### M10：关系链路与文档语义增强

出门条件：

- capability chain v3 输出 edge provenance、confidence 和 completeness score。
- drawio page/lane/group/edge semantics 可抽取。
- drawio document claim 与 code fact 不混淆。

### M11：Token 与 Profile 治理闭环

出门条件：

- context pack 输出 cache_hit、token estimate、omitted_items。
- profile/taxonomy 可配置。
- data_service、HarnessOS、codexPat 持续回归矩阵通过或 structured unavailable。
