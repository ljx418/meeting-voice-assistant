# V2.25-V2.30 PRD：证据支撑的架构意图推断与架构图反推代码事实

## 1. 阶段定位

V2.25-V2.30 接续已验收的 V2.18-V2.24 平台产品化阶段，目标不是继续增加孤立扫描器，而是补齐两个长期能力缺口：

1. 从代码、配置、测试、运行证据和文档中恢复“可证据支撑的架构意图模型”。
2. 把 PRD、drawio、Mermaid、Markdown 架构图中的设计声明反推到实际代码证据，判断落地、缺失、偏差、过期和需要人工确认的部分。

本阶段必须坚持 evidence-first 原则。系统可以推断架构意图，但不能把推断伪装成确定事实。

## 2. 当前基础

当前项目已经具备：

- Codebase registry、snapshot、public surface、symbols、evidence trace。
- DevWiki、Code Graph、Quality Governance。
- 文档资产登记、架构 claim 抽取、文档-代码对齐。
- 大项目 profile、pattern evidence、structured blocker、review queue。
- Human Review Report、Architecture Context Pack、MCP tool catalog、product console。
- Artifact schema、public contract、增量构建、provider plugin、governance feedback、CI readiness。

当前仍存在的主要 Gap：

- 只能做局部架构事实和浅层关系，不能把“设计意图”作为分层证据模型表达。
- 架构图节点可被抽取为 document claim，但不能系统性反推代码落地证据。
- 代码事实、文档声明、运行/测试佐证之间缺少统一 proof graph。
- 对大型项目如 HarnessOS，能展示规模和结构，但仍可能缺少 accepted line-level fact chain。
- 用户无法一眼区分“文档目标架构”“当前代码架构”“推断意图”“人工确认事实”。

## 3. 产品目标

### 3.1 总目标

让用户能够对一个大型项目执行：

```text
导入代码与文档
  -> 解析架构图和设计文档
  -> 构建代码事实与配置/测试/运行佐证
  -> 生成架构意图候选模型
  -> 将目标架构图反推到代码证据
  -> 输出 target/current/inferred/confirmed/diff 视图
  -> 把低置信关系送入人工确认与治理闭环
```

### 3.2 核心用户体验

用户打开报告后应能回答：

- 这个项目文档里声称的目标架构是什么？
- 代码实际暴露了哪些入口、能力、模块和边界？
- 架构图里的每个关键节点是否有代码、配置、测试或运行证据？
- 哪些设计只是文档愿景，哪些已经落地，哪些落地但文档缺失？
- 哪些关系只是名称匹配，哪些有 handler/test/runtime 佐证？
- 如果我是 Coding Agent，应该优先查看哪些文件、能力、风险和待确认项？

## 4. In Scope

1. 架构源模型：统一 Markdown、drawio、Mermaid、PlantUML、README、PRD、目标架构、gap、验收文档。
2. 架构图解析：节点、边、层、边界、能力、数据/控制词汇、里程碑和验收门槛。
3. 代码事实增强：入口、symbol、manifest、config、test reference、runtime evidence descriptor。
4. 证据分层 proof graph：document_claim、code_fact、config_fact、test_fact、runtime_observed、human_confirmed。
5. 架构意图候选模型：intent candidates、confidence、evidence bundle、counter evidence、needs_review。
6. 架构图反推代码验证：diagram node/edge 到 code facts 的多策略匹配、缺失与偏差。
7. 用户报告：target/current/inferred/confirmed/diff 五区块可视化。
8. HTTP/MCP/CLI 读取接口与 Architecture Context Pack 扩展。
9. data_service 与 HarnessOS 真实仓库 E2E 验收。

## 5. Out of Scope

本阶段不承诺：

- 从代码 100% 自动恢复人类完整设计意图。
- full call graph、data flow、control flow、runtime trace、type inference。
- 没有证据的自动架构结论。
- 自动修改文档或代码。
- 自动执行 patch、git commit、git push。
- 把 drawio / PRD 中的节点直接当作 code fact。
- 仅凭 token overlap 标记为 accepted architecture fact。

## 6. 阶段划分

| 阶段 | 名称 | 产品目标 |
| --- | --- | --- |
| V2.25 / Phase 91 | Architecture Source Model | 统一文档、图、代码事实、测试、配置、运行证据的输入模型。 |
| V2.26 / Phase 92 | Diagram-to-Claim Parser | 将架构图与文档结构化为可追踪 claim/relation。 |
| V2.27 / Phase 93 | Code Proof Graph | 建立代码、配置、测试、运行佐证 proof graph。 |
| V2.28 / Phase 94 | Intent Inference Engine | 输出证据支撑的架构意图候选，不把推断当事实。 |
| V2.29 / Phase 95 | Diagram-to-Code Verification | 反推架构图节点/边到代码证据，输出 matched/weak/missing/conflict。 |
| V2.30 / Phase 96 | UX Report, Governance, Closure | 生成高可读报告、Context Pack、治理闭环和最终验收矩阵。 |

## 7. 成功指标

| 指标 | 目标 |
| --- | --- |
| 架构源覆盖 | data_service 与 HarnessOS 的 Markdown/drawio/代码/配置/测试输入均被登记。 |
| 反推可信度 | accepted diagram-to-code match 必须有双边 evidence 和非 token-only 策略。 |
| 意图推断透明度 | 每条 intent candidate 显示 evidence、counter_evidence、confidence、needs_review。 |
| 可读性 | 用户无需看 raw JSON，即可理解 target/current/inferred/confirmed/diff。 |
| 安全边界 | 无绝对路径、secret、raw traceback 泄露。 |
| 假通过防线 | weak/token-only/inferred 不得标记为 accepted fact。 |
