# V2.31-V2.36 Full PRD Coverage Matrix

本文档是 V2.31-V2.36 的最终收口矩阵。当前状态为 implementation closure evidence；每个 `accepted` 或 `accepted_with_blockers` row 必须保留真实测试、artifact、E2E 和审计证据。

| PRD 项 | Phase | 目标能力 | 实现状态 | 验收状态 | 必须证据 |
| --- | --- | --- | --- | --- | --- |
| Task-Aware Navigation Index | 97 | task -> capability/surface/symbol/test/doc | implemented | accepted | `V2_31_PHASE_97_TASK_NAVIGATION_ACCEPTANCE_AUDIT_REPORT.md`、task query artifact、data_service 5 tasks、HarnessOS 3 structured blockers |
| Task Taxonomy | 97 | api/mcp/cli/workflow/provider/snapshot/governance/descriptor/entrypoint/bugfix/test/docs/architecture_review | implemented | accepted | `test_v2_31_task_navigation.py`、real task matrix |
| Ranked Candidates | 97 | ranked candidates with evidence or needs_review/blocker | implemented | accepted | candidate ids、evidence refs、needs_review、`TASK_NAVIGATION_ACCEPTED_EVIDENCE_UNAVAILABLE` blocker |
| External Surface Isolation | 97 | external codebase 不注入 data_service MCP tools | implemented | accepted | `test_v2_codebase_inventory_does_not_inject_current_mcp_registry_for_external_repo`、HarnessOS/codexPat `surface_types={}` 复验 |
| No-Surface Navigation Degradation | 97-98 | no public surface 项目继续生成导航/关系并暴露 blocker | implemented | accepted_with_blockers | `test_v2_31_task_navigation_allows_external_repo_without_public_surfaces`、HarnessOS/codexPat blocker 复验 |
| Lightweight Relationship Graph | 98 | accepted/heuristic/blocked relationships | implemented | accepted | `V2_32_PHASE_98_LIGHTWEIGHT_RELATIONSHIP_ACCEPTANCE_AUDIT_REPORT.md`、relationships.jsonl、forbidden scanner |
| AST Direct Call Baseline | 98 | direct_call_ast only from AST | implemented | accepted | line truth sampling、AST source evidence、semantic caveat |
| Handler / Registry / Config Relations | 98 | surface_handled_by、registry_declared、config_declared | implemented | accepted | source line evidence、blocker report |
| Accepted Relationship Evidence Floor | 98 | accepted relationship 必须具备 path/line/evidence | implemented | accepted | 三项目复验 accepted relationships 缺 line/evidence/path = 0/0/0 |
| Forbidden Relationship Guard | 98 | no full call graph/data flow/control flow/type inference | implemented | accepted | forbidden count = 0 on data_service and HarnessOS |
| Change Impact Analysis | 99 | impacted files/symbols/surfaces/docs/tests | implemented | accepted | `V2_33_PHASE_99_CHANGE_IMPACT_TEST_SELECTION_ACCEPTANCE_AUDIT_REPORT.md`、impact report artifact |
| Test Selection | 99 | suggested tests with reason/evidence or needs_review | implemented | accepted | test selection artifact、evidence refs、needs_review |
| Architecture Guardrail Impact | 99 | risk visibility and semantic-limit caveats | implemented | accepted | risk_items、static reference caveats |
| Module Reading Pack | 100 | required/optional/skip reads | implemented | accepted | `V2_34_PHASE_100_MODULE_READING_PACK_ACCEPTANCE_AUDIT_REPORT.md`、JSON + Markdown reading pack、data_service 5 tasks、HarnessOS 3 tasks |
| Token Ledger | 100 | included/omitted/evidence floor | implemented | accepted | `test_v2_34_module_reading_pack.py`、token ledger artifact、small budget test、real E2E token budget checks |
| Reuse Pattern Recommendation | 100 | similar implementation patterns | implemented | accepted | reuse pattern evidence/needs_review guard、recommendation evidence invariant |
| HTTP Public Contract | 101 | task navigation APIs | implemented | accepted | `V2_35_PHASE_101_COPILOT_AGENT_INTEGRATION_ACCEPTANCE_AUDIT_REPORT.md`、HTTP handoff build/read、public surface guard |
| MCP Public Contract | 101 | task navigation MCP tools | implemented | accepted | MCP registry contract、`knowledge_code_agent_handoff_read` readback |
| CLI Public Contract | 101 | task navigation CLI JSON | implemented | accepted | `handoff-read` JSON smoke |
| Agent Handoff | 101 | Copilot/Codex/Claude/generic handoff | implemented | accepted | handoff artifact、data_service 5 tasks、HarnessOS 3 tasks with structured blocker when evidence unavailable |
| HTML UX Report | 102 | human readable task navigation report | implemented | accepted | `V2_36_PHASE_102_CLOSURE_UX_GOVERNANCE_ACCEPTANCE_AUDIT_REPORT.md`、HTML artifact、no unpersisted facts |
| Mermaid Relation Graph | 102 | task relation graph | implemented | accepted | MMD artifact、node integrity test |
| Governance Target Summary | 102 | feedback target candidates and blocker visibility | implemented | accepted | governance target summary artifact、blocker visibility；完整 review queue / feedback workflow 不在本阶段声明为 completed |
| data_service E2E | 97-102 | 5 real tasks accepted plus closure representative task | implemented | accepted_with_blockers | Phase 97-101 5-task matrices、Phase 102 closure E2E report |
| HarnessOS E2E | 97-102 | 3 real tasks accepted or structured blocker plus closure representative task | implemented | accepted_with_blockers | Phase 97-101 3-task matrices、`HANDOFF_EVIDENCE_UNAVAILABLE` blocker evidence |
| Full Regression | 102 | existing tests remain green | implemented | accepted | 修复后 V2.31-V2.36 regression `13 passed`、targeted `7 passed`、MCP/public surface contract `3 passed` |

## Accepted Row 必填字段

每一行从 `pending` 改为 `accepted` 时必须补：

```text
implementation_status:
acceptance_status:
test_command:
test_result:
artifact_paths:
data_service_evidence:
harnessos_evidence:
audit_report:
open_findings:
```

## False-Green Rejection

以下 row 不得标 accepted：

- 无真实 artifact。
- 仅 mock-only。
- skipped test 被当作 pass。
- HarnessOS blocker 被当作 accepted relationship。
- token overlap 被当作 code relationship。
- accepted recommendation 缺 evidence 且未标 needs_review。
- public contract 未覆盖 HTTP/MCP/CLI parity。
