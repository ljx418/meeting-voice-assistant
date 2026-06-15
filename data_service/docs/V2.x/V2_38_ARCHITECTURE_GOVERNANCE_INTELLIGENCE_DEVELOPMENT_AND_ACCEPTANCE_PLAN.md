# V2.38 开发及验收计划

## 1. 阶段拆分

### Phase 109：Architecture Version Index

开发：

- 新增 v2_38 artifact root。
- 记录 docs/code/report/hash/version。
- 支持 latest / previous / diff 查询。

验收：

- data_service 真实仓库生成 version index。
- 修改一个受控 fixture 文件后 version diff 变化。
- 不改写 V2.0-V2.37 artifacts。

### Phase 110：Incremental Architecture Impact Analyzer

开发：

- 消费 snapshot diff / git diff。
- 生成 impacted files、symbols、surfaces、claims、tests。
- 标记 stale artifacts。

验收：

- 修改真实 repo 中 V2.38 相关代码，impact 能定位到对应模块和 claim。
- 未受影响 artifacts 不重建。
- impact 输出不泄露绝对路径。

### Phase 111：Capability-to-Implementation Chain v2

开发：

- 构建 capability -> surface -> handler/symbol -> module -> test/reference 链路。
- 区分 deterministic / heuristic。
- 缺失时输出 blocker。

验收：

- data_service 至少 5 条链路具备 file/line evidence。
- HarnessOS 若不能生成 accepted chain，必须输出 structured blocker。
- 不出现 full_call_graph / data_flow / control_flow 类型声明。

### Phase 112：Verification v3 + Drift Findings v3

开发：

- 强化 V2.37 verification。
- 加入 version/stale/chain evidence。
- 生成 contradicted / code_not_documented 视图。

验收：

- supported 行必须有 document evidence + code evidence。
- token_overlap_only 不能 supported。
- code_not_documented 计数可见。

### Phase 113：Human Report v3

开发：

- 生成 HTML + SVG 图表。
- 图表包括 target/current/diff、capability chains、impact map。
- 报告展示 token/caching/omitted 指标。

验收：

- HTML 图表原位渲染，不展示 Mermaid 源码。
- 报告中每个可点击/可见节点可追溯 artifact id。
- 人类可在 3 分钟内理解项目目标架构、当前实现和主要风险。

### Phase 114：Architecture Context Pack v5

开发：

- 面向 coding_agent / architecture_reviewer / documentation_agent 生成上下文包。
- 支持 task_context、project_brief、architecture_review。
- 支持 token budget。

验收：

- 每条 recommendation 必须有 evidence_refs 或 needs_review。
- 小 token budget 不保留无证据建议。
- 输出 recommended reading order、tests、risk boundaries。

### Phase 115：Closure Acceptance

开发：

- 汇总 PRD coverage matrix。
- 汇总 data_service / HarnessOS / codexPat E2E。
- 输出 closure audit report。

验收：

- 无 fatal / major open finding。
- 所有 accepted 项都有 test command、artifact path、真实项目证据。
- HarnessOS 不能被硬编码；如未完整支持，只能 structured blocker。

## 2. 共享验收门槛

- 必须使用真实项目验收。
- 必须检查 artifact 落盘和 readback。
- 必须检查 HTTP/MCP/CLI parity。
- 必须检查 public payload 无绝对路径。
- 必须跑 public surface guard。
- 必须跑 V2.38 focused tests。
- 全量测试若受环境阻塞，必须记录，不得伪装通过。

## 3. 停止条件

发现以下任一情况必须停止并找人确认：

- supported 缺 document evidence 或 code evidence。
- 把 heuristic chain 写成 runtime call graph。
- 把 HarnessOS profile 硬编码进通用逻辑。
- HTML 报告展示未经 artifact 支撑的新事实。
- 增量更新误改 V2.0-V2.37 artifacts。

## 4. 后续开发路线大纲

V2.38 后续路线采用连续小阶段推进，每个阶段都必须先产出 phase-specific development plan、acceptance plan、audit report，再进入实现；每个阶段结束都必须使用真实项目 E2E 和 PRD 规格检视。

### V2.39：大型项目性能优化

开发：

- 增加 scan budget、file budget、artifact shard、readback pagination。
- 为大型 repo 建立 scale profile：文件数、LOC、语言、热区目录、超大文件、generated/vendor 路径。
- 增加缓存命中、跳过原因、超时降级和 partial artifact 状态。

验收：

- data_service、HarnessOS 或等价大项目在预算内完成 profile。
- 超过预算时返回 structured blocker，不伪装成功。
- artifact readback 支持分页，public payload 不泄露绝对路径。

### V2.40：多语言 AST/LSP Provider Contract

开发：

- 定义 `AstProviderResult`、`LspProviderStatus`、`SymbolFact`、`ReferenceFact`。
- Python AST 为 mandatory baseline。
- tree-sitter/LSP 为 optional provider；未配置时必须 `provider_unavailable`。
- 支持 TS/JS 基础 symbol/import fixture；其他语言可先 profile-only。

验收：

- Python provider 真实仓库通过。
- TS/JS fixture 至少抽取 module/function/import。
- LSP 未配置不能被标记 accepted。
- provider error code、timeout、unsupported language 有稳定 public contract。

### V2.41：Workflow / Runtime Extractor v2

开发：

- 抽取 workflow manifest、agent registry、runtime adapter、CLI/TUI/console entrypoint、config-driven pipeline。
- 输出 `workflow_candidate`、`runtime_candidate`、`entrypoint_candidate`，并标记 deterministic / heuristic。
- 支持 profile/taxonomy 驱动的 pattern catalog。

验收：

- HarnessOS 等大型项目必须完成 extractor attempt。
- 成功时提供 repo-relative path + line range；失败时输出 blocker。
- 不声称 production runtime topology，不输出无证据 runtime call。

### V2.42：调用/依赖链路增强 v3

开发：

- 增强 capability -> public surface -> handler -> dependency -> test/reference 链路。
- 引入 relationship confidence、edge provenance、chain completeness score。
- 对 import/reference/call-like hint 做语义分级。

验收：

- data_service 至少 10 条 accepted chain。
- HarnessOS 至少输出 accepted chain 或明确 blocker。
- `runtime_call`、`data_flow`、`control_flow` 禁止出现在 accepted edge type。

### V2.43：drawio / 文档语义解析 v3

开发：

- 解析 drawio page、lane、group、container、edge label、legend、gate、milestone。
- 从 Markdown 表格、验收标准、非目标、停止条件抽取结构化 claim。
- 建立 document claim confidence policy。

验收：

- drawio claim 只能作为 document evidence，不直接成为 code fact。
- 抽取结果包含 page/lane/group relation。
- HTML 报告中 target/current/diff 明确区分，不混淆图上目标声明和代码事实。

### V2.44：Token Budget Optimizer + Context Cache

开发：

- 记录任务级 reading budget、cache hit、reused artifacts、omitted_items。
- 支持按角色生成 context：coding_agent、architecture_reviewer、documentation_agent。
- 小 budget 下优先保留 high-risk/high-evidence 节点。

验收：

- 小 token budget 下不保留无 evidence recommendation。
- 输出 token estimate、cache_hit_ratio、omitted_items。
- 同一任务重复生成时能复用已缓存理解。

### V2.45：Project Profile / Taxonomy + 大型项目持续回归集

开发：

- profile 管理项目族术语、entrypoint patterns、workflow patterns、doc authority rules。
- 建立 data_service / HarnessOS / codexPat 持续回归矩阵。
- 增加 no-hardcode audit：profile 可配置，通用 extractor 不包含 HarnessOS 专用路径。

验收：

- 三个真实项目至少完成 registry/profile/report/context pack E2E。
- HarnessOS profile 可在配置层表达，不进入通用逻辑。
- 回归矩阵记录 accepted、structured blocker、provider_unavailable，不把不可用伪装为通过。
