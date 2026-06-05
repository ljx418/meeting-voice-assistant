# V2.8 Full PRD Coverage Matrix

> Coverage matrix scaffold for V2.8.
> No row may be marked accepted without real artifact and test evidence.

Allowed acceptance statuses:

```text
planned
implemented
accepted
conditionally_accepted
not_implemented
out_of_scope
```

| PRD item | Capability | Artifact / Interface | Phase | Implementation status | Acceptance status | Required evidence before accepted |
| --- | --- | --- | --- | --- | --- | --- |
| US-028-001 | readable architecture report | `architecture_reading_dashboard.json`, HTML/Mermaid views | 56 | implemented | accepted | `V2_8_PHASE_56_ACCEPTANCE_AUDIT_REPORT.md`; data_service + HarnessOS real dashboard artifacts |
| US-028-002 | graph aggregation/filtering | graph summary, clusters, views | 57 | implemented | accepted | `V2_8_PHASE_57_ACCEPTANCE_AUDIT_REPORT.md`; cluster counts, view artifacts, unsupported edge count = 0 |
| US-028-003 | deeper code fact chains | `architecture_code_fact_chains.jsonl` | 58 | implemented | accepted | `V2_8_PHASE_58_ACCEPTANCE_AUDIT_REPORT.md`; data_service accepted chains, HarnessOS unresolved chains not falsely accepted |
| US-028-003 | runtime boundary hints | `architecture_runtime_boundaries.jsonl` | 58 | implemented | accepted | `V2_8_PHASE_58_ACCEPTANCE_AUDIT_REPORT.md`; deterministic/runtime boundary status tests |
| US-028-004 | signal ranking | `architecture_signal_ranking.json` | 59 | implemented | accepted | `V2_8_PHASE_59_ACCEPTANCE_AUDIT_REPORT.md`; visible score components/reason codes |
| US-028-004 | review queue v2 | `architecture_review_queue_v2.json` | 59 | implemented | accepted | `V2_8_PHASE_59_ACCEPTANCE_AUDIT_REPORT.md`; major/fatal findings pinned |
| US-028-005 | design-intent evidence | `architecture_intent_evidence.jsonl` | 60 | implemented | accepted | `V2_8_PHASE_60_ACCEPTANCE_AUDIT_REPORT.md`; documented/code/audit/mismatch states separated |
| US-028-005 | document conflict detection | quality v2 findings + intent mismatch states | 60 | implemented | accepted | `V2_8_PHASE_60_ACCEPTANCE_AUDIT_REPORT.md`; mismatch and needs_review rows persisted |
| US-028-006 | context pack v2 | `architecture_context_pack_v2/{pack_id}.json` | 61 | implemented | accepted | `V2_8_PHASE_61_ACCEPTANCE_AUDIT_REPORT.md`; evidence-backed project brief and task context |
| Public contract | HTTP reads | V2.8 endpoints | 56-61 | implemented | accepted | `backend/tests/test_v2_8_reading_dashboard.py`; HTTP envelope tests |
| Public contract | MCP tools | V2.8 tools | 56-61 | implemented | accepted | `backend/tests/test_v2_8_reading_dashboard.py`; MCP call tests; `test_public_surface_guard.py` |
| Public contract | CLI commands | V2.8 CLI commands | 56-61 | implemented | accepted | `backend/tests/test_v2_8_reading_dashboard.py`; JSON stdout tests |
| Closure | real E2E | all V2.8 artifacts | 62 | implemented | accepted | data_service + HarnessOS real E2E results in Phase 56-61 reports and closure audit |
| Non-goal | full call graph / data flow / control flow | none | all | out_of_scope | out_of_scope | closure audit confirms no claim |
| Non-goal | pure code recovery of human design intent | none | all | out_of_scope | out_of_scope | intent evidence model keeps code-observed separate |

## Final Closure Rule

Phase 62 cannot mark V2.8 complete until every in-scope row is either `accepted`, `conditionally_accepted`, `not_implemented`, or `out_of_scope`, with evidence for every accepted row.
