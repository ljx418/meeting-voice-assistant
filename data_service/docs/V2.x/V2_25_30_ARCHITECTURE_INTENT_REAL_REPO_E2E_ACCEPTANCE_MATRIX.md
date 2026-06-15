# V2.25-V2.30 真实仓库 E2E 验收矩阵

## 1. 验收仓库

| 仓库 | 用途 |
| --- | --- |
| data_service | 自举验证：文档、MCP、HTTP、CLI、artifact contract、治理闭环都有明确实现线索。 |
| HarnessOS | 大项目验证：复杂工作流、多 Agent 设计文档、动态入口和大量历史文档。 |

## 2. data_service 验收

| 能力 | 期望结果 | 拒绝条件 |
| --- | --- | --- |
| Source Model | V2.x PRD、target architecture、drawio、phase audit 均被登记。 | 空 registry 或绝对路径泄露。 |
| Diagram Claims | V2.18-V2.24 / V2.25-V2.30 drawio 节点和边可追踪。 | drawio 节点无 cell id 或无法定位。 |
| Proof Graph | MCP/HTTP/CLI/platform modules 能形成 proof nodes。 | import 被标为 runtime call。 |
| Intent Candidate | 能生成“项目智能平台、MCP 工具目录、artifact contract、治理闭环”等候选意图。 | LLM-only intent 被 accepted。 |
| Diagram Verification | 架构图节点能区分 accepted/weak/missing/conflict。 | token-only accepted。 |
| Report UX | HTML 显示 target/current/inferred/confirmed/diff。 | 报告隐藏 needs_review。 |

## 3. HarnessOS 验收

| 能力 | 期望结果 | 拒绝条件 |
| --- | --- | --- |
| Source Model | HarnessOS 设计文档、drawio、workflow docs、代码入口被登记。 | 只读取 data_service，不跑 HarnessOS。 |
| Diagram Claims | workflow、agent、station、runtime、governance 节点成为 document claims。 | 把架构图复制为 code-derived architecture。 |
| Proof Graph | 能识别可证据化代码事实或输出 structured blocker。 | 没证据却 accepted。 |
| Intent Candidate | 能表达“受控多 Agent workflow / governance / station binding”等候选意图并标注证据强度。 | 把文档愿景当作当前实现。 |
| Diagram Verification | 图中节点/边落地状态清楚：accepted/weak/missing/conflict/stale。 | weak match 隐藏在 accepted 里。 |
| Human Review | 低置信关系进入 review queue。 | review queue 为空但存在 weak/missing。 |

## 4. 必须采集的指标

```text
source_count
diagram_claim_count
diagram_relation_count
proof_node_count
proof_edge_count
intent_candidate_count
accepted_verification_count
weak_match_count
missing_code_evidence_count
conflict_count
needs_review_count
redaction_violation_count
```

## 5. 出门门槛

- 两个真实仓库均跑通，不允许 mock-only。
- data_service 至少产生 accepted verification。
- HarnessOS 至少产生 diagram claims 和 structured verification result；如果 accepted 少，必须有 blocker 分类。
- public payload 无绝对路径、secret、raw traceback。
- 报告中的每个 visible node 都能追溯到 artifact。
