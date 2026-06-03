# V2.5 ResearchNotebook Backend Document Audit Report

## Audit Result

Status: accepted for the implemented provider-gated scope after real-input artifact acceptance was added. Provider-specific real OCR/TTS/PPTX execution is conditionally approved for planning but not yet implemented.

## Reviewed Inputs

- `/Users/Zhuanz/Desktop/workspace/research-notebook/docs/backend/V2_BACKEND_SERVICE_PRD.md`
- `/Users/Zhuanz/Desktop/workspace/research-notebook/docs/backend/V2_BACKEND_API_MATRIX.md`
- `/Users/Zhuanz/Desktop/workspace/research-notebook/docs/backend/V2_TARGET_ARCHITECTURE.md`
- current `data_service` ResearchNotebook target HTTP routes
- `docs/V2.x/V2_5_RESEARCH_NOTEBOOK_BACKEND_PRD.md`
- `docs/V2.x/V2_5_RESEARCH_NOTEBOOK_BACKEND_ARCHITECTURE.md`
- `docs/V2.x/V2_5_RESEARCH_NOTEBOOK_BACKEND_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md`
- `docs/V2.x/V2_5_PROVIDER_SPECIFIC_GAP_ANALYSIS.md`
- `docs/V2.x/V2_5_TARGET_STATE.drawio`

## Findings

| Finding | Severity | Resolution |
| --- | --- | --- |
| P0 URL SSRF block_reason was not contract-complete in current backend. | major | V2.5 Phase 26 makes it mandatory. |
| P1/P2 provider requirements are optional and should not block P0. | minor | V2.5 treats provider absence as stable capability false / not-ready response. |
| Artifact API was not unified for ResearchNotebook-specific artifacts. | major | V2.5 Phases 28-29 add artifact store/read contracts. |
| Existing `data_service.py` is already large. | major | V2.5 routes and services are placed in ResearchNotebook-specific modules except minimal source import compatibility edits. |
| Initial V2.5 validation used synthetic artifact inputs. | major | Added real-input acceptance using ResearchNotebook backend PRD/API/architecture docs and fixed public artifact path redaction found by that test. |
| Provider-specific real OCR/TTS/PPTX execution is not implemented in current baseline. | major | Added Phase 32-36 provider-specific plan, target architecture, gap analysis, milestones, drawio, and explicit non-claim language. |
| Provider-specific plan needed harder contracts before Phase 32. | major | Added Provider Error Contract, Provider Health Contract, Binary Artifact Descriptor Contract, acceptance matrix, fixture strategy, and no-fake-artifact checks. |

## False-Acceptance Risks

- blocked URL returns only raw 422 detail and no source-shaped payload;
- URL success/redirect tests rely on monkeypatch and must not be treated as real public-network acceptance;
- artifact tests must include real ResearchNotebook backend docs, not only synthetic text;
- provider-disabled path is treated as failure instead of stable unavailable contract;
- slides/mindmap/compare artifacts are returned in memory but not persisted;
- artifact output includes unsupported claims without evidence;
- public payload leaks local filesystem paths.
- provider-backed success is claimed without provider-enabled real fixture evidence;
- binary artifact download descriptors expose local paths;
- provider-disabled fallback regresses after provider-specific adapters are added.

## Implementation Acceptance

Implemented V2.5 outputs:

- URL block_reason source contract for target source import.
- Provider health routes for OCR/TTS.
- Provider-gated capability flags.
- Unified ResearchNotebook artifact store and routes.
- Deterministic slides, mindmap, and compare artifact contracts.
- Provider-disabled OCR/audio unavailable responses.
- Public artifact text redaction for local filesystem paths found inside source document snippets.
- Real-input artifact E2E using ResearchNotebook V2 backend docs.

Verification commands:

```bash
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_real_input_acceptance.py -q
```

Result:

```text
1 passed
```

```bash
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_backend_contract.py backend/tests/test_research_notebook_v25_real_input_acceptance.py backend/tests/test_target_http_source_preview.py backend/tests/test_target_http_url_sources.py backend/tests/test_target_http_studio_artifacts.py backend/tests/test_public_surface_guard.py backend/tests/test_data_service_api.py backend/tests/test_session_ingest_query_build_contract_plan.py -q
```

Result:

```text
67 passed
```

Earlier focused runs before the real-input acceptance addition:

```bash
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_backend_contract.py backend/tests/test_target_http_url_sources.py backend/tests/test_target_http_source_preview.py::test_v11be_capability_manifest_source_preview_contract backend/tests/test_target_http_studio_artifacts.py backend/tests/test_public_surface_guard.py -q
```

Result:

```text
21 passed
```

```bash
PYTHONPATH=backend python3 -m pytest backend/tests/test_target_http_source_preview.py backend/tests/test_target_http_url_sources.py backend/tests/test_target_http_studio_artifacts.py backend/tests/test_research_notebook_v25_backend_contract.py backend/tests/test_public_surface_guard.py -q
```

Result:

```text
29 passed
```

```bash
PYTHONPATH=backend python3 -m pytest backend/tests/test_data_service_api.py backend/tests/test_session_ingest_query_build_contract_plan.py -q
```

Result:

```text
37 passed
```

```bash
git diff --check -- backend/app/api/__init__.py backend/app/api/v1/data_service.py backend/app/api/v1/research_notebook.py backend/data_service/url_source_contract.py backend/data_service/research_notebook_artifacts.py backend/tests/test_research_notebook_v25_backend_contract.py backend/tests/test_target_http_url_sources.py backend/tests/test_target_http_source_preview.py backend/tests/test_public_surface_guard.py docs/V2.x/V2_5_RESEARCH_NOTEBOOK_BACKEND_PRD.md docs/V2.x/V2_5_RESEARCH_NOTEBOOK_BACKEND_ARCHITECTURE.md docs/V2.x/V2_5_RESEARCH_NOTEBOOK_BACKEND_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md docs/V2.x/V2_5_RESEARCH_NOTEBOOK_BACKEND_DOCUMENT_AUDIT_REPORT.md
```

Result: passed.

## Audit Decision

No open fatal or major finding after implementation.

V2.5 ResearchNotebook backend contract is accepted for the implemented provider-gated scope. The acceptance now includes real ResearchNotebook backend Markdown documents flowing through source import, artifact generation, persistence, readback, and path-redaction checks.

Remaining non-claims:

- Real public internet URL success is not fully accepted in the automated suite because the restricted test environment cannot guarantee external network access.
- Real OCR/TTS/PPTX providers remain intentionally unimplemented unless configured and planned in a later provider-specific phase.

## Provider-Specific Planning Audit

The updated V2.5 documents now split the phase into:

- Phase 25-31: accepted provider-gated baseline.
- Phase 32-36: provider-specific real execution expansion.

Document consistency checks:

| Check | Result |
| --- | --- |
| PRD includes Phase 32-36 target capabilities and does not claim they are complete. | pass |
| Architecture distinguishes current provider gate from target provider adapter execution. | pass |
| Development plan includes phase-level deliverables, acceptance, and exit gates. | pass |
| Gap analysis maps each unimplemented target to a phase. | pass |
| Drawio includes current-vs-target, target architecture, development/acceptance plan, milestones, and exit gates. | pass |
| PRD defines provider error, health, OCR, and binary descriptor contracts. | pass |
| Development plan includes acceptance matrix and provider acceptance matrix template. | pass |
| Gap analysis includes fake artifact, fixture, binary descriptor, and error schema gaps. | pass |

Phase-specific planning audit:

| Phase | Audit Status | Required Evidence Before Implementation Acceptance |
| --- | --- | --- |
| Phase 32 | planned | Provider health and failure-mode tests prove structured errors and redaction. |
| Phase 33 | planned | Real OCR fixture E2E proves scanned source to OCR artifact. |
| Phase 34 | planned | Real TTS fixture E2E proves source evidence to audio artifact descriptor. |
| Phase 35 | planned | Real PPTX fixture E2E proves slides artifact to `.pptx` descriptor. |
| Phase 36 | planned | Closure audit proves provider-enabled and provider-disabled paths with no fatal/major finding. |

Provider-specific implementation may start only after a pre-development phase audit confirms actual provider availability or local fixture strategy.

## Required Phase 32 Pre-Development Gate

Before coding provider adapters, Phase 32 must lock:

1. Provider Error public codes and payload shape.
2. Provider Health payload shape.
3. Redaction checker for keys, tokens, endpoints, raw traceback, local paths, generated artifact text, and metadata.
4. Provider-specific acceptance matrix.
5. Binary artifact descriptor fields: ref, MIME, size, sha256, download descriptor.
6. OCR fixture strategy: image mandatory; scanned PDF requires rasterizer or `PDF_RASTERIZER_UNAVAILABLE`.
7. TTS real audio checks: size, duration, MIME, script evidence, download descriptor.
8. PPTX export checks: zip structure, `[Content_Types].xml`, `ppt/presentation.xml`, slide XML count, outline count match.

Audit decision for Phase 32 entry:

```text
Pass with required gates documented. Business implementation may begin only by implementing Provider Config + Safety Boundary first; provider adapters must not be started before the Phase 32 contracts are protected by tests.
```
