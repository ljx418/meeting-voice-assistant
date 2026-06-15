# V2.25-V2.30 项目里程碑与出门条件

## 1. 里程碑

| 里程碑 | 对应阶段 | 完成标志 |
| --- | --- | --- |
| M1 输入源统一 | Phase 91 | architecture source model 覆盖文档、图、代码、配置、测试、运行描述符。 |
| M2 架构图结构化 | Phase 92 | drawio/Mermaid/Markdown diagram 输出 claim/relation。 |
| M3 证据图成型 | Phase 93 | proof graph 建立，runtime/test/config 语义边界明确。 |
| M4 意图候选可信 | Phase 94 | intent candidates 有 evidence/counter evidence/confidence。 |
| M5 图到代码验证 | Phase 95 | diagram-to-code verification 输出 accepted/weak/missing/conflict。 |
| M6 用户报告闭环 | Phase 96 | HTML/Context Pack/Governance/Coverage Matrix 完成。 |

## 2. Phase 出门条件

### Phase 91

- data_service 与 HarnessOS source model 非空。
- 文档权威性字段存在。
- source path repo-relative。

### Phase 92

- drawio cell id 或 Markdown line range 可追踪。
- diagram relation 不可解析时输出 blocker。
- 不把 diagram claim 标为 code fact。

### Phase 93

- proof graph 引用真实 code/config/test/runtime evidence。
- import/test/config/runtime 语义边界明确。
- forbidden edge scan 通过。

### Phase 94

- 每条 intent candidate 有 evidence_bundle 或 needs_review。
- counter_evidence 可见。
- LLM-only / token-only 不 accepted。

### Phase 95

- accepted verification 有双边 evidence。
- weak/missing/conflict/stale 不被隐藏。
- confidence 阈值和 match_strategy 可解释。

### Phase 96

- HTML 报告可读。
- Context Pack 保留 evidence。
- Governance confirm/revoke 不改原始 artifact。
- coverage matrix 每个 accepted row 有测试和 artifact evidence。

## 3. 高风险停机条件

出现以下情况必须暂停并要求人工确认：

- 产品目标被实现为“自动恢复完整设计意图”，且没有 needs_review 边界。
- 需要接入外部 provider 发送代码或文档内容。
- 需要执行非只读 runtime 采集。
- 需要自动修改代码、文档、git 状态。
- 发现 public payload 泄露 secret 或绝对路径。
