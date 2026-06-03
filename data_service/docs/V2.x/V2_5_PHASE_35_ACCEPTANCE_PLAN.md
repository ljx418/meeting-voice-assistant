# V2.5 Phase 35 Acceptance Plan: PPTX Export Real Run

> Generated from repository analysis.
> Real OpenXML `.pptx` generation is mandatory for Phase 35 acceptance.
> JSON/Markdown renamed to `.pptx` must be rejected.

## 1. Acceptance Scope

Phase 35 is accepted only for the local PPTX exporter actually configured and tested.

Accepted target:

```text
PPTX provider: local
Exporter flag: PPTX_EXPORTER_ENABLED=1
Output: OpenXML .pptx zip package
Required fixture: real slides artifact generated from source evidence
```

Phase 35 must not claim:

- external PPTX provider readiness;
- visual theme fidelity;
- PPTX template editing;
- new LLM slide generation.

## 2. Functional Acceptance

Exporter-disabled fallback:

- `PPTX_PROVIDER` unset or `PPTX_EXPORTER_ENABLED` unset returns unavailable health.
- `POST /api/workspaces/{workspace_id}/artifacts/slides/export` returns `SLIDE_OUTLINE_ONLY`.
- No fake PPTX binary is written.

Exporter-enabled real PPTX:

- `PPTX_PROVIDER=local` and `PPTX_EXPORTER_ENABLED=1` health returns available.
- A real slides artifact is generated from real source evidence.
- Slides export endpoint writes a real `.pptx` binary.
- Response returns a `pptx_export` artifact descriptor.
- Descriptor includes `source_slides_artifact_id`, `slide_count`, binary descriptor, and evidence refs.
- Artifact list/read/status/download can retrieve the PPTX descriptor.

## 3. OpenXML Acceptance

The stored `.pptx` must:

- exist and have nonzero size;
- open as a zip package;
- include `[Content_Types].xml`;
- include `ppt/presentation.xml`;
- include `ppt/slides/slide{n}.xml`;
- have slide XML count equal to source slides count;
- not be JSON or Markdown renamed to `.pptx`.

## 4. Security and Redaction Acceptance

Public payloads must not contain:

- local binary filesystem path;
- `file://` refs;
- raw tracebacks;
- internal temp paths.

Binary refs must use:

```text
artifact://{workspace_id}/{artifact_id}?binary=pptx
```

## 5. Required Tests

Focused exporter suite:

```bash
PYTHONPATH=backend PPTX_PROVIDER=local PPTX_EXPORTER_ENABLED=1 python3 -m pytest backend/tests/test_research_notebook_v25_phase35_pptx_export.py -q
```

Phase 32-34 regression:

```bash
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase32_provider_safety.py backend/tests/test_research_notebook_v25_phase33_ocr_provider.py backend/tests/test_research_notebook_v25_phase34_tts_provider.py -q
```

V2.5 baseline regression:

```bash
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_backend_contract.py backend/tests/test_research_notebook_v25_real_input_acceptance.py -q
```

Broader ResearchNotebook guard:

```bash
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase35_pptx_export.py backend/tests/test_research_notebook_v25_phase34_tts_provider.py backend/tests/test_research_notebook_v25_phase33_ocr_provider.py backend/tests/test_research_notebook_v25_phase32_provider_safety.py backend/tests/test_research_notebook_v25_backend_contract.py backend/tests/test_research_notebook_v25_real_input_acceptance.py backend/tests/test_target_http_source_preview.py backend/tests/test_target_http_url_sources.py backend/tests/test_target_http_studio_artifacts.py backend/tests/test_public_surface_guard.py -q
```

Static checks:

```bash
python3 -m py_compile backend/data_service/research_notebook/providers/pptx_exporter.py backend/data_service/research_notebook_artifacts.py backend/tests/test_research_notebook_v25_phase35_pptx_export.py
git diff --check -- backend/data_service/research_notebook/providers/pptx_exporter.py backend/data_service/research_notebook_artifacts.py backend/tests/test_research_notebook_v25_phase35_pptx_export.py docs/V2.x/V2_5_PHASE_35_DEVELOPMENT_PLAN.md docs/V2.x/V2_5_PHASE_35_ACCEPTANCE_PLAN.md docs/V2.x/V2_5_PHASE_35_AUDIT_REPORT.md
```

## 6. Exit Criteria

Phase 35 passes only if:

- local OpenXML PPTX export E2E passes;
- binary artifact is persisted and read back from disk;
- exporter-disabled fallback still passes;
- Phase 32-34 and V2.5 baseline regressions pass;
- PRD/spec review finds no major deviation;
- false-acceptance review has no fatal or major open finding.
