# V2.9 Real Repo E2E Acceptance Matrix

> Real-repository acceptance matrix for V2.9.
> This is a planning artifact until Phase 68 closure.

## 1. Required Repositories

```text
/Users/Zhuanz/Desktop/workspace/data_service
/Users/Zhuanz/Desktop/workspace/harnessOS
```

## 2. Phase Matrix

Pre-gate before Phase 63:

```text
V2_8_PHASE_62_CLOSURE_AUDIT_REPORT.md exists
data_service V2.8 artifacts readable
HarnessOS V2.8 artifacts readable
HarnessOS V2.8 accepted_chains baseline readable
V2.0-V2.8 input artifact hash inventory captured
```

| Phase | Capability | data_service required evidence | HarnessOS required evidence | Acceptance status |
| --- | --- | --- | --- | --- |
| 63 | public surface evidence v2 | line-level HTTP/MCP/CLI evidence and truth sampling | improved workflow/console/CLI/TUI evidence or structured blocker | planned |
| 64 | code relationships v2 | capability/surface/module/test paths with allowed relationship types | workflow/console/module/test paths where evidence exists | planned |
| 65 | ranking calibration v2 | grouped ranking, queue v3, score components, major/fatal invariant | grouped ranking, queue v3, score components, major/fatal invariant | planned |
| 66 | human review report v2 | readable HTML/Mermaid report with artifact-backed nodes | readable HTML/Mermaid report with artifact-backed nodes | planned |
| 67 | context pack v3 | project brief, task context, architecture review packs | project brief, task context, architecture review packs | planned |
| 68 | closure | coverage matrix accepted with test/artifact/audit refs | coverage matrix accepted with test/artifact/audit refs | planned |

## 3. False-Green Rejection

| False-green case | Result |
| --- | --- |
| mock-only repo accepted | reject |
| HarnessOS evidence unchanged but claimed improved | reject unless structured blocker exists |
| documentation-only surface treated as code evidence | reject |
| import dependency shown as runtime call | reject |
| ranking hides major/fatal finding | reject |
| duplicate grouping removes evidence refs | reject |
| human report hides needs_review | reject |
| context pack recommendation lacks evidence or needs_review | reject |
| local absolute path leak | reject |
| accepted evidence without line-range truth check | reject |
| forbidden relationship type emitted | reject |
| invalid or missing relationship semantic_claim | reject |
| ranking hidden_major_count or hidden_fatal_count is non-zero | reject |
| HTML/Mermaid introduces unpersisted facts | reject |
| HTML/Mermaid node id absent from report JSON | reject |
| context pack trims evidence but keeps recommendation | reject |
| context pack missing source_phase_refs | reject |
| V2.0-V2.8 input artifact hash changes unexpectedly | reject |

## 4. HarnessOS Specific Checks

HarnessOS E2E must verify:

- V2.9 evidence extractor attempts workflow, console, CLI, TUI, and registry patterns;
- accepted evidence improves over V2.8 or exact missing pattern blockers are reported;
- document-derived V4/V6 architecture remains separate from code-derived evidence;
- unresolved architecture intent remains visible;
- default report explains why a claim is accepted, reviewable, or blocked.
- closure compares V2.9 accepted evidence against V2.8 accepted fact-chain caveat.

## 5. Phase 63 Category Coverage

Phase 63 truth sampling must include:

```text
data_service HTTP >= 3
data_service MCP >= 3
data_service CLI >= 2
HarnessOS workflow attempted
HarnessOS console attempted
HarnessOS CLI attempted
HarnessOS TUI attempted
HarnessOS registry attempted
```

Each attempted HarnessOS category must produce accepted evidence or an exact blocker.
