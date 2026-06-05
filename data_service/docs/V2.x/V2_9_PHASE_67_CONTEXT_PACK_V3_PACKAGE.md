# V2.9 Phase 67 Package: Architecture Context Pack v3

> Phase-specific development, acceptance, and pre-implementation audit package.

Date: 2026-06-05

## 1. Goal

Phase 67 creates role-aware and task-aware context packs from V2.9 artifacts so external agents can consume architecture evidence, relationship paths, calibrated risks, and human review notes.

## 2. Required Inputs

- Phase 63 evidence.
- Phase 64 relationships and clusters.
- Phase 65 ranking and review queue.
- Phase 66 human report.
- V2.8 Architecture Context Pack v2 for compatibility comparison.

## 3. Output Artifacts

```text
workspace/assets/codebase/{codebase_id}/architecture/v2_9/
  architecture_context_pack_v3/{pack_id}.json
```

## 4. Modes and Roles

Required modes:

```text
project_brief
task_context
architecture_review
```

Required roles:

```text
maintainer
coding_agent
documentation_agent
architecture_reviewer
```

## 5. Recommendation Contract

Every recommendation must have:

```text
recommendation_id
summary
target_refs
evidence_refs or needs_review
risk_level
reason_codes
source_artifact_refs
source_phase_refs
```

Recommendations without evidence must be marked `needs_review`. They must not appear as accepted implementation guidance.

## 6. Token Budget Policy

When `max_tokens` is small:

- omit low-priority recommendations before removing evidence;
- do not keep a recommendation while dropping its evidence;
- put removed material in `omitted_items`;
- preserve fatal/major risk summaries;
- preserve `needs_review` warnings.

## 7. Required Development Work

- Build JSON pack from persisted V2.9 artifacts.
- Render optional Markdown content from the same JSON model.
- Support readback by `pack_id`.
- Expose context pack create/read through HTTP/MCP/CLI parity.
- Include token estimate, omitted items, warnings, unresolved, evidence refs, and source artifact refs.
- Include `source_phase_refs`, proving the pack consumed Phase 63, 64, 65, and 66 artifacts where available.

## 8. Acceptance Tests

- `project_brief` summarizes architecture, public surfaces, evidence coverage, risks, and unresolved items.
- `task_context` for a code-change task includes implementation paths and tests where evidence exists.
- `architecture_review` highlights ranking lanes, blockers, and review actions.
- Small token budget does not produce unsupported recommendations.
- data_service and HarnessOS packs reference V2.9 artifacts.
- v3 packs include `source_phase_refs` and do not rely only on V2.8 artifacts.
- HTTP/MCP/CLI outputs agree on stable ids, counts, warnings, unresolved, and artifact refs.

## 9. False-Green Rejection

Reject Phase 67 if:

- recommendation lacks evidence and is not `needs_review`;
- token trimming removes evidence while keeping recommendation;
- pack references raw absolute paths;
- pack uses V2.8 data only and ignores V2.9 artifacts;
- `source_phase_refs` is missing or excludes available V2.9 phases;
- HTTP/MCP/CLI parity is skipped;
- readback by `pack_id` fails.

## 10. Phase 67 Audit Opinion

Planning status: ready after Phase 66 acceptance.

Open fatal findings: none.

Open major findings: none.

Required closure output:

```text
docs/V2.x/V2_9_PHASE_67_ACCEPTANCE_AUDIT_REPORT.md
```
