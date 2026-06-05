# V2.9 Full PRD Coverage Matrix

> Coverage matrix scaffold for V2.9.
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

| PRD item | Capability | Artifact / Interface | Phase | Implementation status | Acceptance status | Required evidence before accepted | Final closure fields |
| --- | --- | --- | --- | --- | --- | --- | --- |
| US-029-001 | public surface evidence v2 | `architecture_public_surface_evidence_v2.jsonl` | 63 | planned | planned | data_service + HarnessOS line evidence or blockers | test command, artifact path, V2.8 baseline ref, V2.9 artifact ref, truth-sampling result, comparison result, audit ref |
| US-029-002 | code relationship layer v2 | `architecture_code_relationships_v2.jsonl` | 64 | planned | planned | shallow relationship paths with evidence | test command, artifact path, V2.9 artifact ref, forbidden-type scan, semantic-claim scan, audit ref |
| US-029-002 | module clusters v2 | `architecture_module_clusters_v2.json` | 64 | planned | planned | cluster counts and member evidence | test command, artifact path, member-ref integrity, audit ref |
| US-029-003 | ranking calibration v2 | `architecture_signal_ranking_v2.json` | 65 | planned | planned | grouping metrics and pinned major/fatal tests | test command, artifact path, hidden_major_count=0, hidden_fatal_count=0, audit ref |
| US-029-003 | review queue v3 | `architecture_review_queue_v3.json` | 65 | planned | planned | top queue items with reason codes | test command, artifact path, evidence-preservation result, audit ref |
| US-029-004 | human review report v2 | `architecture_human_review_report_v2.json`, HTML/Mermaid views | 66 | planned | planned | readable report and artifact refs | test command, artifact path, JSON/HTML/Mermaid consistency, redaction result, audit ref |
| US-029-005 | context pack v3 | `architecture_context_pack_v3/{pack_id}.json` | 67 | planned | planned | evidence-backed project brief, task context, architecture review | test command, artifact path, token-budget result, source_phase_refs result, audit ref |
| Public contract | HTTP reads | V2.9 endpoints | 63-67 | planned | planned | HTTP response envelope tests | test command, route list, success/error parity result, audit ref |
| Public contract | MCP tools | V2.9 tools | 63-67 | planned | planned | MCP registry and call tests | test command, tool list, success/error parity result, audit ref |
| Public contract | CLI commands | V2.9 CLI commands | 63-67 | planned | planned | JSON stdout and parity tests | test command, command list, success/error parity result, audit ref |
| Closure | real E2E | all V2.9 artifacts | 68 | planned | planned | data_service + HarnessOS acceptance matrix | test command, baseline artifact refs, V2.9 artifact inventory, comparison results, false-green scan, open findings, audit ref |
| Non-goal | full call graph / data flow / control flow | none | all | out_of_scope | out_of_scope | closure audit confirms no claim | audit ref |
| Non-goal | pure code recovery of human design intent | none | all | out_of_scope | out_of_scope | evidence model keeps code-observed separate | audit ref |

## Final Closure Rule

Phase 68 cannot mark V2.9 complete until every in-scope row is either `accepted`, `conditionally_accepted`, `not_implemented`, or `out_of_scope`, with evidence for every accepted row.
