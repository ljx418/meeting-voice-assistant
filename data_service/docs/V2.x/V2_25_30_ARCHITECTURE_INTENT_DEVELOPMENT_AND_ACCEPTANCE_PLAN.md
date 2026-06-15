# V2.25-V2.30 开发及验收计划

## 1. 阶段总览

| Phase | 阶段 | 开发目标 | 出门验收 |
| --- | --- | --- | --- |
| 91 | Architecture Source Model | 登记文档、图、代码事实、配置、测试、运行证据源。 | data_service 与 HarnessOS 均生成非空 source model，路径 repo-relative。 |
| 92 | Diagram-to-Claim Parser | 解析 drawio/Mermaid/Markdown diagram 为 claim/relation。 | 架构图节点/边可追踪到 cell id 或 line range，无法解析时 structured blocker。 |
| 93 | Code Proof Graph | 建立 code/config/test/runtime proof graph。 | proof nodes/edges 可追踪到真实 source evidence，禁止 runtime overclaim。 |
| 94 | Intent Inference Engine | 生成证据支撑的 intent candidates。 | 每条 intent 有 evidence 或 needs_review，counter evidence 不被隐藏。 |
| 95 | Diagram-to-Code Verification | 将目标架构图反推到代码事实并输出差异。 | accepted match 必须有双边 evidence、非 token-only、confidence >= 0.80。 |
| 96 | UX Report & Closure | 生成 HTML/Mermaid/Context Pack/治理闭环与最终验收矩阵。 | 用户可读报告通过真实仓库 E2E，coverage matrix 无 fatal/major open finding。 |

## 2. 共享开发规则

- 只做本阶段文档和后续实现范围内的能力，不重新打开 ResearchNotebook V2.5 或 V2.18-V2.24 已验收范围。
- 所有 artifacts 必须包含 schema_version、workspace_id、codebase_id、snapshot_id、source_artifact_refs、warnings、needs_review。
- HTTP/MCP/CLI 是 thin wrapper，核心逻辑放入 focused architecture intent modules。
- 报告渲染层不得创造 artifact 中不存在的新事实。
- 大项目失败不能 silent pass，必须输出 blocker taxonomy。

## 3. 共享验收规则

每个 Phase 必须完成：

1. Phase-specific development plan。
2. Phase-specific acceptance plan。
3. Pre-implementation audit，无 fatal/major open finding。
4. 实现后真实仓库 E2E：`data_service` 与 `HarnessOS`。
5. Artifact disk inspection。
6. HTTP/MCP/CLI parity 或明确说明本阶段尚未暴露 public read。
7. PRD 规格检视。
8. False-green review。
9. Regression：既有 V2.18-V2.24 platform tests 不被破坏。

## 4. 真实仓库验收

### data_service

必须验证：

- V2.x 文档和 drawio 被登记。
- 目标架构、PRD、验收计划中的 claims 被抽取。
- code facts 能映射到已有 HTTP/MCP/CLI、symbols、platform modules。
- 意图候选能指出“项目智能平台 / artifact contract / MCP tool catalog / governance / CI readiness”等主题。

### HarnessOS

必须验证：

- V4/V9/V10 或当前设计文档中的架构图和目标声明被登记。
- 图中 workflow、agent、station、runtime、governance 等节点被抽取为 document claims。
- 代码侧能找到 exact evidence 或输出 structured blockers。
- 不允许把 HarnessOS 文档图复制为 code-derived architecture。

## 5. 假通过拒绝条件

以下任一出现即不得通过：

- 只用 mock 文档或 fixture，不跑真实仓库。
- drawio 节点直接被标为 code fact。
- token overlap only 被标为 accepted。
- 没有 line/cell evidence 的 claim 被标为 accepted。
- import/reference 被写成 runtime call。
- LLM-only intent candidate 被写成 confirmed fact。
- 报告隐藏 missing/conflict/needs_review。
- public payload 泄露绝对路径或 secret。
- Governance confirm 修改原始 artifact，而不是生成 overlay。

## 6. 最终完成定义

V2.25-V2.30 可宣布完成，当且仅当：

1. data_service 和 HarnessOS 都完成 source model、diagram claims、proof graph、intent candidates、diagram verification、human report。
2. 所有 accepted diagram-to-code match 都有双边 evidence。
3. 所有 inferred intent 都有 evidence bundle 或 needs_review。
4. HTML 报告能清晰解释目标架构、当前实现、推断意图、已确认事实和偏差。
5. Architecture Context Pack 可供 Coding Agent 使用，并保留 evidence。
6. Governance confirmation/revoke 可跑通，且 source artifact hash 不变。
