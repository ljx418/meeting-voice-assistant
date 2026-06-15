# V2.39-V2.45 开发及验收计划

## 0. 当前状态与审计口径

本计划最初用于支撑 V2.39-V2.45 的阶段开发；截至当前 closure，Phase 116-122 均已完成 implementation、真实项目 E2E、artifact inspection、HTTP/MCP/CLI parity、PRD/spec review 和 acceptance audit。

2026-06-12 外部审计意见中的“planning / implementation baseline ready、不能声明 implementation complete”适用于当时的开发前口径。当前仓库已经补齐各阶段 acceptance audit 与 `V2_39_45_ARCHITECTURE_SCALE_SEMANTIC_CLOSURE_AUDIT_REPORT.md`，因此可声明：

```text
V2.39-V2.45 scoped implementation accepted.
```

但该声明只覆盖本计划定义的范围，不扩展为 full call graph、data flow、control flow、production runtime topology、type inference 或完整恢复人类设计意图。

## 1. 共享开发规则

- 每个子阶段开始前必须产出 phase-specific development plan、acceptance plan、pre-implementation audit。
- 每个子阶段完成后必须产出 acceptance audit report。
- 必须使用真实项目：data_service、HarnessOS、codexPat；不可用时只能 structured unavailable。
- 不允许 mock-only 验收。
- 不允许将 provider unavailable、skipped test 或 blocker 写成 accepted。
- 不允许把 HarnessOS profile 写死进通用代码。

## 2. Phase 116：V2.39 大型项目性能优化

开发：

- 增加 scale profile builder。
- 增加 scan budget policy：max files、max LOC、max file size、timeout、generated/vendor skip。
- 增加 artifact shard writer 和 paginated readback。
- 增加 partial artifact 状态和 blocker reason。

验收：

- data_service 与至少一个大型项目生成 scale profile。
- 超限样例返回 `SCAN_BUDGET_EXCEEDED` 或等价 structured blocker。
- shard readback 可分页读取。
- public payload 不泄露绝对路径。

## 3. Phase 117：V2.40 多语言 AST/LSP Provider Contract

开发：

- 定义 `AstProviderResult`、`LanguageProviderStatus`、`SymbolFact`、`ReferenceFact`。
- Python AST mandatory。
- TS/JS fixture 支持基础 module/function/import。
- tree-sitter/LSP optional，未配置返回 provider_unavailable。

验收：

- Python 真实仓库符号抽取仍通过。
- TS/JS fixture 至少产生 symbol/import facts。
- LSP 未配置不得 accepted。
- provider failed/timeout/unsupported language 有稳定 error code。

## 4. Phase 118：V2.41 Workflow / Runtime Extractor v2

开发：

- 增加 workflow manifest extractor。
- 增加 runtime adapter candidate extractor。
- 增加 agent registry、CLI/TUI/console entrypoint extractor。
- 引入 profile/taxonomy 驱动的 pattern catalog。

验收：

- HarnessOS 执行 extractor attempt。
- 成功时 candidate 有 path/line/config evidence。
- 失败时 blocker reason 精确。
- 不输出 production runtime topology。

## 5. Phase 119：V2.42 调用/依赖链路增强 v3

开发：

- 建立 relationship chain artifact。
- 增加 edge provenance、confidence、source extractor、completeness score。
- 串联 capability、entrypoint、handler、dependency/reference、test/config/doc claim。

验收：

- data_service 至少 10 条 accepted chain。
- HarnessOS 输出 accepted chain 或 structured blocker。
- forbidden edge type scan 通过。
- heuristic edge 不得被渲染成 runtime call。

## 6. Phase 120：V2.43 drawio / 文档语义解析 v3

开发：

- 解析 drawio page、lane、group、container、edge、legend、milestone、gate。
- Markdown claim extraction 增强 acceptance criteria、non-goal、stop condition。
- 建立 claim confidence policy。

验收：

- drawio semantic fixture 通过。
- drawio claim 只能进入 document claim artifact。
- HTML 报告明确区分 target document claim 与 current code fact。
- XSS/HTML escaping 和 Mermaid label escaping 通过。

## 7. Phase 121：V2.44 Token Budget Optimizer + Context Cache

开发：

- 增加 task reading budget planner。
- 增加 cache hit、artifact reuse、repeated reading reduction metrics。
- Context Pack 支持 role-based compression。
- 裁剪策略保留 evidence-backed high-risk items。

验收：

- 小 token budget 不保留无 evidence recommendation。
- 输出 token_estimate、cache_hit_ratio、omitted_items。
- 重复任务生成能复用缓存。
- omitted_items 包含裁剪原因。

## 8. Phase 122：V2.45 Project Profile / Taxonomy + 持续回归集

开发：

- 增加 project profile registry。
- 增加 taxonomy manager：terms、entrypoint_patterns、workflow_patterns、authority_rules。
- 建立 real repo regression matrix。
- 增加 no-hardcode audit。

验收：

- data_service、HarnessOS、codexPat 均有 profile 或 structured unavailable。
- HarnessOS 特殊术语只能出现在 profile，不得出现在通用 extractor。
- 回归矩阵记录 accepted、structured blocker、provider_unavailable。
- closure audit 无 fatal / major。

## 9. 共享停止条件

发现以下情况必须停止：

- accepted 结论缺 evidence。
- provider unavailable 被标记 accepted。
- runtime candidate 被表述成生产 runtime topology。
- token budget 裁剪后留下无证据建议。
- drawio document claim 被直接当作 code fact。
- 大型项目超时却没有 structured blocker。
- 通用逻辑中出现 HarnessOS-only hardcode。

## 10. 当前阶段验收摘要

| Phase | Scope | Current Status | Acceptance Report |
| --- | --- | --- | --- |
| V2.39 / Phase 116 | 大型项目性能优化 | accepted | `V2_39_PHASE_116_SCALE_PROFILE_ACCEPTANCE_AUDIT_REPORT.md` |
| V2.40 / Phase 117 | 多语言 AST/LSP Provider Contract | accepted | `V2_40_PHASE_117_LANGUAGE_PROVIDER_ACCEPTANCE_AUDIT_REPORT.md` |
| V2.41 / Phase 118 | Workflow / Runtime Extractor v2 | accepted | `V2_41_PHASE_118_WORKFLOW_RUNTIME_ACCEPTANCE_AUDIT_REPORT.md` |
| V2.42 / Phase 119 | 调用/依赖链路增强 v3 | accepted | `V2_42_PHASE_119_RELATIONSHIP_CHAIN_ACCEPTANCE_AUDIT_REPORT.md` |
| V2.43 / Phase 120 | drawio / 文档语义解析 v3 | accepted | `V2_43_PHASE_120_DOCUMENT_SEMANTICS_ACCEPTANCE_AUDIT_REPORT.md` |
| V2.44 / Phase 121 | Token Budget Optimizer + Context Cache | accepted | `V2_44_PHASE_121_TOKEN_CACHE_ACCEPTANCE_AUDIT_REPORT.md` |
| V2.45 / Phase 122 | Project Profile / Taxonomy + 持续回归集 | accepted | `V2_45_PHASE_122_PROFILE_TAXONOMY_REGRESSION_ACCEPTANCE_AUDIT_REPORT.md` |

最终 closure 以 `V2_39_45_ARCHITECTURE_SCALE_SEMANTIC_CLOSURE_AUDIT_REPORT.md` 和 `V2_39_45_ARCHITECTURE_SCALE_SEMANTIC_FULL_COVERAGE_MATRIX.md` 为准。后续若修改相关代码或 artifact contract，必须重新执行 scoped regression、真实项目 E2E 和 false-green audit。
