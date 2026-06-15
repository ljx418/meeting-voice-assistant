# V2.37 Full PRD Coverage Matrix

当前为 planning baseline，不是 closure evidence。每一行从 `planned` 改为 `accepted` 时必须补 test command、artifact path、data_service evidence、HarnessOS evidence、audit report。

| PRD 项 | Phase | 能力 | 状态 | 验收状态 | 必须证据 |
| --- | --- | --- | --- | --- | --- |
| Document Authority Registry v2 | 103 | docs 权威索引 | planned | pending | documents.jsonl、authority summary、stale/superseded tests |
| Architecture Claim Graph v2 | 104 | claims + relations | planned | pending | claims.jsonl、relations.jsonl、drawio cell refs |
| Project Term Taxonomy | 104 | 项目术语映射 | planned | pending | taxonomy artifact、no hardcode audit |
| Current Implementation Model | 105 | code facts 汇总 | planned | pending | current_model.json、upstream hash gate |
| Claim-to-Code Verification | 106 | 双边证据核查 | planned | pending | verification_matrix.jsonl、supported evidence tests |
| Drift Findings | 106 | unsupported/contradicted/code_not_documented | planned | pending | drift_findings.jsonl |
| Reconstruction Report v2 | 107 | HTML + Mermaid target/current/diff | planned | pending | HTML、MMD/SVG、node integrity test |
| Agent Architecture Brief | 107 | role-aware architecture brief | planned | pending | brief JSON/MD、token budget test |
| HTTP/MCP/CLI Contract | 103-107 | build/read/report/brief | planned | pending | parity tests |
| data_service E2E | 108 | self-hosted acceptance | planned | pending | acceptance report |
| HarnessOS E2E | 108 | docs-grounded architecture verification | planned | pending | at least 10 classified claims |
| codexPat E2E | 108 | desktop/package project acceptance | planned | pending | report + blockers |
| Closure Audit | 108 | final evidence and PRD review | planned | pending | closure audit report |

## Accepted Row 必填字段

```text
implementation_status:
acceptance_status:
test_command:
test_result:
artifact_paths:
data_service_evidence:
harnessos_evidence:
codexpat_evidence:
audit_report:
open_findings:
```
