# V2.9 Phase 63 Package: Public Surface Evidence v2

> Phase-specific development, acceptance, and pre-implementation audit package.
> Business code implementation must not start until this package has no open fatal or major planning finding.

Date: 2026-06-05

## 1. Goal

Phase 63 hardens line-level evidence for public surfaces so architecture review outputs can trace accepted surfaces to implementation files.

V2.8 caveat addressed:

- HarnessOS generated code fact chains but accepted chains remained `0` because deterministic public-surface line evidence was missing.

## 2. Required Inputs

- V2.0 surfaces, symbols, and evidence artifacts.
- V2.7 document-code architecture governance artifacts.
- V2.8 dashboard, graph, code fact chains, ranking, intent, and context artifacts.
- V2.8 closure and baseline artifacts:
  - `docs/V2.x/V2_8_PHASE_62_CLOSURE_AUDIT_REPORT.md`;
  - data_service V2.8 architecture artifacts;
  - HarnessOS V2.8 architecture artifacts;
  - HarnessOS V2.8 `accepted_chains` baseline count.
- Real repositories:
  - `/Users/Zhuanz/Desktop/workspace/data_service`
  - `/Users/Zhuanz/Desktop/workspace/harnessOS`

If HarnessOS is unavailable, Phase 63 must stop. Mock-only acceptance is forbidden.

If the V2.8 closure report or HarnessOS V2.8 baseline artifacts are unavailable, Phase 63 must not claim evidence improvement. It must stop or emit a structured baseline blocker.

## 3. Output Artifact

```text
workspace/assets/codebase/{codebase_id}/architecture/v2_9/
  architecture_public_surface_evidence_v2.jsonl
```

Each row must follow `ArchitecturePublicSurfaceEvidenceV2` from `V2_9_ARTIFACT_SCHEMA_AND_PUBLIC_CONTRACT.md`.

## 4. Extractor Catalog

Phase 63 must attempt these extractors:

| Extractor | Surface types | Accepted evidence rule |
| --- | --- | --- |
| `python_decorator_route` | `http_api` | Decorator line and handler line are both resolvable. |
| `fastapi_router_registry` | `http_api` | Router registration and route handler line are resolvable. |
| `mcp_tool_registry` | `mcp_tool` | Tool name/spec line and dispatcher/handler line are resolvable. |
| `cli_parser_definition` | `cli_command` | Parser/subcommand branch line and invoked handler/helper line are resolvable. |
| `workflow_manifest_entrypoint` | `workflow_entrypoint` | Manifest entry and referenced module/file line are resolvable. |
| `console_entrypoint_scan` | `console_entrypoint` | Console command/action and implementation file line are resolvable. |
| `tui_entrypoint_scan` | `tui_entrypoint` | TUI command/action and implementation file line are resolvable. |
| `storage_artifact_declaration` | `storage_artifact` | Artifact path/schema declaration line is resolvable. |
| `generated_artifact_declaration` | `generated_artifact` | Generation call or descriptor declaration line is resolvable. |

Pattern-only, doc-only, or name-only matches must be `needs_review` or `blocked`, never `accepted`.

## 5. Confidence and Status Policy

```text
accepted:
  confidence >= 0.85
  repo-relative path exists
  line_range is valid
  line_range truth check passes
  extractor is deterministic

needs_review:
  0.40 <= confidence < 0.85
  pattern is plausible but handler/line linkage is incomplete

blocked:
  extractor attempted but missing required code shape, missing file, dynamic registry, or unsupported language pattern
```

Blocker reasons:

```text
NO_DECORATOR_PATTERN
DYNAMIC_REGISTRY_UNRESOLVED
ENTRYPOINT_NOT_LINE_RESOLVED
HANDLER_NOT_RESOLVED
WORKFLOW_MANIFEST_UNSUPPORTED
CONSOLE_PATTERN_UNSUPPORTED
TUI_PATTERN_UNSUPPORTED
SOURCE_FILE_MISSING
LINE_RANGE_INVALID
```

## 6. Required Development Work

- Add focused implementation under the V2.9 architecture layer, not in legacy large files.
- Consume existing V2 artifacts read-only.
- Record before/after hashes for V2.0-V2.8 input artifacts and verify they are unchanged after Phase 63.
- Persist evidence rows under `architecture/v2_9`.
- Expose read/build through existing architecture HTTP/MCP/CLI surfaces using thin handlers.
- Include artifact summary counts by repo, surface type, status, extractor, and blocker reason.
- Compare V2.9 evidence against the V2.8 HarnessOS baseline.

## 7. Evidence Improvement Metrics

Phase 63 must report:

```text
v28_accepted_chains_count
v29_accepted_evidence_count
status_distribution
blocker_count
extractor_attempted_count
v29_vs_v28_delta
```

## 8. Acceptance Tests

Minimum test scenarios:

- `data_service` extracts representative HTTP, MCP, CLI, storage, and generated artifact evidence.
- HarnessOS attempts workflow, console, CLI, TUI, and registry patterns.
- At least 20 accepted evidence rows across real repositories pass truth sampling:
  - path exists;
  - start/end line in file bounds;
  - source snippet is non-empty;
  - snippet contains expected route/tool/command/entrypoint hint or handler name.
- Truth sampling must include category coverage:
  - data_service HTTP >= 3;
  - data_service MCP >= 3;
  - data_service CLI >= 2;
  - HarnessOS workflow, console, CLI, TUI, and registry patterns are all attempted;
  - each attempted HarnessOS category has accepted evidence or an exact blocker.
- HarnessOS accepted evidence improves over V2.8, or exact blockers are persisted.
- Public payloads use repo-relative paths and do not expose absolute local paths.
- HTTP/MCP/CLI reads agree on counts, artifact refs, warnings, unresolved, and schema version.
- V2.0-V2.8 input artifact hashes are unchanged after the phase.

## 9. False-Green Rejection

Reject Phase 63 if:

- mock repository is used as acceptance evidence;
- V2.8 baseline is unavailable but improvement is claimed;
- doc/drawio claim is marked as code evidence;
- pattern-only match is marked `accepted`;
- HarnessOS evidence is claimed improved without comparing V2.8 baseline;
- all 20 truth samples come from one repository or one surface type;
- accepted row lacks repo-relative path or line range;
- line-range truth sampling is skipped;
- V2.0-V2.8 input artifact hash changes unexpectedly;
- public payload leaks absolute paths or secrets.

## 10. Phase 63 Audit Opinion

Planning status: ready for implementation after external audit.

Open fatal findings: none.

Open major findings: none.

Required closure output:

```text
docs/V2.x/V2_9_PHASE_63_ACCEPTANCE_AUDIT_REPORT.md
```
