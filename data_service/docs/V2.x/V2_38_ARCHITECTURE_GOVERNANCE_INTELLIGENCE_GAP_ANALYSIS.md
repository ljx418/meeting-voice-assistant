# V2.38 Gap Analysis

## 1. Current State

当前项目已经具备：

- 文档声明抽取。
- 当前实现模型。
- claim-to-code verification。
- HTML 报告和 Agent Brief。
- HTTP/MCP/CLI 暴露。

## 2. Target State

V2.38 目标是：

- 增量更新架构理解。
- 生成 capability-to-implementation 链路。
- 支持任务级 Agent 上下文压缩。
- 生成更强的人类可读架构报告。
- 建立版本化架构治理视图。

## 3. Gap Matrix

| Gap | 当前状态 | V2.38 目标 | 验收方式 |
| --- | --- | --- | --- |
| 增量理解 | 基础 snapshot，缺架构级 impact | impacted nodes / stale artifacts | 修改真实文件后验证 impact |
| 调用/依赖链路 | 有浅层 evidence，但链路不稳定 | capability chain v2 | 至少 5 条 accepted chain |
| 人类报告 | 有基础 HTML/SVG | 多图表、可读报告 v3 | HTML review + artifact consistency |
| Agent token 成本 | 有 brief，但指标不足 | token/cache/omitted 指标 | 小 budget 测试 |
| 架构版本治理 | 缺版本索引 | version index + diff | 两次构建比较 |
| 多项目泛化 | data_service 较强，HarnessOS 仍需 blocker | data_service/HarnessOS/codexPat E2E | real repo matrix |
| 大型项目性能 | 缺预算化扫描和分片读取 | V2.39 scale profile + budgeted scanner | 大项目 profile + timeout blocker |
| 多语言 AST/LSP | Python 强，其他语言弱 | V2.40 provider contract | Python mandatory + TS/JS fixture + LSP unavailable 测试 |
| workflow/runtime 抽取 | 有基础 pattern，但泛化不足 | V2.41 workflow/runtime candidates | HarnessOS attempt + no runtime topology claim |
| 调用/依赖链路精度 | 链路较浅，confidence 粒度不足 | V2.42 relationship v3 | edge provenance + forbidden edge scan |
| drawio/文档语义 | 标签级抽取多，结构语义少 | V2.43 page/lane/group/edge semantics | drawio semantic fixture + no code fact 混淆 |
| project profile/taxonomy | 缺统一配置治理 | V2.45 profile/taxonomy manager | no-hardcode audit + 多项目 profile |
| 持续回归集 | 单次 E2E 多，长期矩阵不足 | V2.45 real repo regression matrix | data_service/HarnessOS/codexPat 持续矩阵 |

## 4. Major Risks

- 把 heuristic relationship 误写成 runtime call。
- 为 HarnessOS 特化，损害泛用性。
- HTML 报告为了好看引入无证据事实。
- 增量更新漏掉受影响 claim。
- token budget 裁剪后留下无证据建议。

## 5. Mitigation

- 所有 chain edge 必须标记 `edge_kind`、`confidence`、`evidence_refs`。
- HarnessOS 只能通过 profile/taxonomy 配置适配。
- report renderer 只能消费 persisted JSON。
- impact analyzer 必须保留 unresolved / needs_review。
- context pack 裁剪必须同步裁剪 recommendation 和 evidence。
- 大项目扫描必须有 budget、pagination 和 partial status。
- AST/LSP provider 必须区分 configured、unavailable、unsupported 和 failed。
- workflow/runtime extractor 只能输出 candidate，不得伪造生产运行拓扑。
- drawio 语义解析必须保留 document evidence，不得直接转成 code fact。
