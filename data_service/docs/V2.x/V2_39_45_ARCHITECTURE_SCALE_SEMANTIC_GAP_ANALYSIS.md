# V2.39-V2.45 Gap Analysis

## 1. 当前状态

当前项目已经具备：

- codebase registry、snapshot、surface、symbol、evidence。
- DevWiki、Graph、Quality、Context Pack。
- 文档驱动架构核查和 claim-to-code verification。
- 初步的 HTML/SVG 报告和 Agent Brief。
- V2.38 规划中的版本化架构治理和增量上下文能力。

## 2. 目标状态

V2.39-V2.45 目标是让项目能更稳定地支撑大型项目：

- 更低的扫描成本。
- 更宽的语言覆盖。
- 更强的 workflow/runtime candidate 识别。
- 更可靠的 capability/dependency chain。
- 更深的 drawio/文档语义解析。
- 更少的 Agent token 浪费。
- 更可治理的 profile/taxonomy。
- 更稳定的真实项目回归。

## 3. Gap Matrix

| Gap | 当前状态 | 目标阶段 | 验收方式 |
| --- | --- | --- | --- |
| 大型项目性能 | 缺预算化扫描和分页 readback | V2.39 | scale profile + shard + timeout blocker |
| 多语言事实 | Python 强，其他语言弱 | V2.40 | provider contract + TS/JS fixture |
| LSP 集成 | 未配置时边界不清 | V2.40 | optional unavailable unless configured |
| workflow/runtime | 候选识别泛化不足 | V2.41 | workflow/runtime/agent/CLI/TUI candidate |
| 调用/依赖链 | capability chain 较浅 | V2.42 | edge provenance + completeness score |
| drawio 语义 | 多为标签级抽取 | V2.43 | page/lane/group/edge/gate semantics |
| token 成本 | 缺缓存和重复阅读指标 | V2.44 | token/cache/omitted metrics |
| profile/taxonomy | 缺项目族配置 | V2.45 | profile registry + no-hardcode audit |
| 持续回归 | 单次验收多，长期矩阵弱 | V2.45 | real repo regression matrix |

## 4. 主要风险

- 为了支持 HarnessOS 而写出不可泛化逻辑。
- 把 workflow/runtime candidate 误报为真实运行拓扑。
- 把 LSP 未配置或 provider failed 当作 accepted。
- HTML 图表为了可读性引入无证据事实。
- 大项目扫描超时后无 structured blocker。
- Token 优化只减少字数，却删除证据导致建议不可审计。

## 5. 缓解策略

- 所有项目适配必须走 profile/taxonomy。
- 所有 provider 状态必须结构化。
- 所有 candidate 必须保留 confidence、evidence、needs_review。
- 所有 report/chart 只能从 persisted artifact 渲染。
- 所有 accepted row 必须有 test command、artifact path、真实项目证据。
