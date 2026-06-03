# V2.5 Handoff Summary: ResearchNotebook Backend PRD Closure

> Freeze handoff document for another terminal/agent.
> Scope: V2.5 ResearchNotebook backend service closure in `data_service`.
> This document summarizes implemented behavior, acceptance evidence, explicit limitations, and handoff risks.

## 1. Handoff Verdict

V2.5 is frozen as **accepted with explicit classifications**.

This means:

- accepted items are implemented and backed by tests or real-input contract evidence;
- cloud OCR is classified as `provider unavailable`;
- direct binary streaming / signed URL stream is classified as `out of scope for V2.5`;
- Minimax is accepted only for TTS in the current configuration, not for OCR;
- V2.5 closure does not claim every optional cloud provider is implemented.

Primary closure evidence:

- `docs/V2.x/V2_5_FULL_PRD_COVERAGE_MATRIX.md`
- `docs/V2.x/V2_5_PHASE_42_CLOSURE_AUDIT_REPORT.md`
- `docs/V2.x/V2_5_PHASE_41_DOWNLOAD_CONTRACT_AUDIT_REPORT.md`
- `docs/V2.x/V2_5_PHASE_39_EXTERNAL_TTS_AUDIT_REPORT.md`
- `docs/V2.x/V2_5_PHASE_37_SCANNED_PDF_OCR_AUDIT_REPORT.md`

## 2. Product Scope

V2.5 implements the ResearchNotebook backend requirements handed off from:

- `/Users/Zhuanz/Desktop/workspace/research-notebook/docs/backend/V2_BACKEND_SERVICE_PRD.md`
- `/Users/Zhuanz/Desktop/workspace/research-notebook/docs/backend/V2_BACKEND_API_MATRIX.md`
- `/Users/Zhuanz/Desktop/workspace/research-notebook/docs/backend/V2_TARGET_ARCHITECTURE.md`

V2.5 covers:

- URL source SSRF hardening and `block_reason`;
- provider health and execution boundary;
- OCR fallback, local image OCR, local scanned PDF OCR;
- TTS fallback, local TTS, configured Minimax TTS;
- deterministic slide, mindmap, and compare artifacts;
- local OpenXML PPTX export;
- artifact read/status/list/delete;
- descriptor-only artifact download contract;
- provider error and public redaction rules;
- final PRD coverage matrix and closure audit.

## 3. Implemented User-Facing Capabilities

### 3.1 URL Source Safety

Implemented:

- backend-side SSRF/private IP/metadata URL blocking;
- blocked URL source records with `block_reason`;
- redirect safety handling;
- normal public URL import path remains available.

Relevant tests:

- `backend/tests/test_research_notebook_v25_backend_contract.py`
- `backend/tests/test_target_http_url_sources.py`

### 3.2 Capability Manifest and Provider Health

Implemented provider-gated capability flags:

- `ocr`
- `scanned_pdf_ocr`
- `tts`
- `audio_overview`
- `slides`
- `slide_outline`
- `pptx_export`
- `mindmap`
- `compare`

Provider health endpoints:

- `POST /api/ocr/provider/health`
- `POST /api/ocr/provider/execution`
- `POST /api/tts/provider/health`
- `POST /api/tts/provider/execution`
- `POST /api/pptx/provider/health`
- `POST /api/pptx/provider/execution`

Key rule:

- health-known provider names are not equal to executable provider support.
- unsupported execution returns structured provider errors such as `PROVIDER_UNSUPPORTED`.

Relevant implementation:

- `backend/data_service/research_notebook/providers/health.py`
- `backend/data_service/research_notebook/providers/adapter_contract.py`
- `backend/data_service/research_notebook/providers/errors.py`
- `backend/data_service/research_notebook/providers/redaction.py`

Relevant tests:

- `backend/tests/test_research_notebook_v25_phase32_provider_safety.py`
- `backend/tests/test_research_notebook_v25_phase37_pre_gate_provider_contract.py`
- `backend/tests/test_research_notebook_v25_phase38_provider_adapter_hardening.py`

### 3.3 OCR

Implemented:

- provider-disabled fallback: `OCR_REQUIRED`;
- local image OCR through Tesseract;
- scanned PDF OCR through PDF rasterization plus Tesseract;
- persisted OCR artifacts with pages/blocks/text/confidence/locators/evidence refs;
- status/readback consistency.

Accepted OCR paths:

- local Tesseract image OCR;
- local scanned PDF OCR with `pdftoppm`.

Explicit limitation:

- cloud OCR is `provider unavailable`;
- Minimax TTS evidence must not be reused as OCR evidence.

Relevant implementation:

- `backend/data_service/research_notebook/artifacts/ocr_artifacts.py`
- `backend/data_service/research_notebook/providers/ocr_tesseract.py`

Relevant tests:

- `backend/tests/test_research_notebook_v25_phase33_ocr_provider.py`
- `backend/tests/test_research_notebook_v25_phase37_scanned_pdf_ocr.py`
- `backend/tests/test_research_notebook_v25_phase36_provider_closure.py`

Decision record:

- `docs/V2.x/V2_5_PHASE_40_OCR_PROVIDER_DECISION.json`

### 3.4 Audio Overview / TTS

Implemented:

- provider-disabled fallback: `AUDIO_OVERVIEW_NOT_READY`;
- local `espeak-ng` WAV audio generation;
- configured Minimax TTS real run;
- evidence-backed script segments;
- audio binary descriptor with `artifact://` ref, MIME, size, sha256, and duration.

Accepted TTS paths:

- local `espeak-ng`;
- configured Minimax provider.

Explicit limitation:

- Azure/Google/ElevenLabs are not accepted unless separately configured and tested.

Relevant implementation:

- `backend/data_service/research_notebook/providers/tts_espeak.py`
- `backend/data_service/research_notebook/providers/tts_minimax.py`
- `backend/data_service/research_notebook_artifacts.py`

Relevant tests:

- `backend/tests/test_research_notebook_v25_phase34_tts_provider.py`
- `backend/tests/test_research_notebook_v25_phase39_minimax_tts_provider.py`

Decision record:

- `docs/V2.x/V2_5_PHASE_39_TTS_PROVIDER_DECISION.json`

### 3.5 Slides and PPTX

Implemented:

- deterministic evidence-backed slide outline generation;
- fallback `SLIDE_OUTLINE_ONLY` when PPTX exporter is unavailable;
- local OpenXML PPTX package export;
- PPTX descriptor with `artifact://` ref, MIME, size, sha256;
- slide count and lineage checks.

Relevant implementation:

- `backend/data_service/research_notebook/providers/pptx_exporter.py`
- `backend/data_service/research_notebook_artifacts.py`

Relevant tests:

- `backend/tests/test_research_notebook_v25_phase35_pptx_export.py`
- `backend/tests/test_research_notebook_v25_phase36_provider_closure.py`

### 3.6 Mindmap and Compare

Implemented:

- deterministic mindmap artifact from source evidence;
- deterministic compare artifact from at least two sources;
- insufficient source handling.

Explicit limitation:

- LLM-enhanced mindmap/compare quality is out of V2.5 closure unless separately scoped.

Relevant implementation:

- `backend/data_service/research_notebook_artifacts.py`

Relevant tests:

- `backend/tests/test_research_notebook_v25_backend_contract.py`
- `backend/tests/test_research_notebook_v25_real_input_acceptance.py`

### 3.7 Artifact Store and Download

Implemented:

- artifact list/read/delete/status;
- JSON/Markdown descriptor downloads;
- audio WAV descriptor downloads;
- PPTX descriptor downloads;
- structured unsupported format error;
- structured missing artifact download error;
- public payload path redaction.

Selected V2.5 contract:

- descriptor-only.

Explicit limitation:

- direct binary streaming / signed URL stream is out of scope for V2.5.

Relevant implementation:

- `backend/app/api/v1/research_notebook.py`
- `backend/data_service/research_notebook_artifacts.py`
- `backend/data_service/research_notebook/artifacts/binary_store.py`

Relevant tests:

- `backend/tests/test_research_notebook_v25_phase41_download_contract.py`

Decision record:

- `docs/V2.x/V2_5_PHASE_41_DOWNLOAD_CONTRACT_DECISION.json`

## 4. HTTP API Summary

Provider APIs:

```text
POST /api/ocr/provider/health
POST /api/ocr/provider/execution
POST /api/tts/provider/health
POST /api/tts/provider/execution
POST /api/pptx/provider/health
POST /api/pptx/provider/execution
```

Workspace artifact APIs:

```text
GET    /api/workspaces/{workspace_id}/artifacts
GET    /api/workspaces/{workspace_id}/artifacts/{artifact_id}
DELETE /api/workspaces/{workspace_id}/artifacts/{artifact_id}
GET    /api/workspaces/{workspace_id}/artifacts/{artifact_id}/status
GET    /api/workspaces/{workspace_id}/artifacts/{artifact_id}/download
POST   /api/workspaces/{workspace_id}/artifacts/audio
POST   /api/workspaces/{workspace_id}/artifacts/slides
POST   /api/workspaces/{workspace_id}/artifacts/slides/export
POST   /api/workspaces/{workspace_id}/artifacts/mindmap
POST   /api/workspaces/{workspace_id}/artifacts/compare
```

OCR APIs:

```text
POST /api/workspaces/{workspace_id}/sources/{source_id}/ocr
GET  /api/workspaces/{workspace_id}/sources/{source_id}/ocr/status
```

Existing source APIs are extended for URL source safety and `block_reason`.

## 5. Storage Layout

ResearchNotebook artifacts are stored under workspace local FS:

```text
{workspace}/research_notebook/artifacts/
  {artifact_id}.json
  binaries/
    {artifact_id}.wav
    {artifact_id}.pptx
```

Public outputs must use safe refs:

```text
artifact://{workspace_id}/{artifact_id}
artifact://{workspace_id}/{artifact_id}?binary=audio
artifact://{workspace_id}/{artifact_id}?binary=pptx
```

Public outputs must not expose absolute local paths.

## 6. Provider Configuration Notes

Recognized provider env families:

```text
OCR_PROVIDER=tesseract|azure|google
OCR_API_KEY
OCR_ENDPOINT

TTS_PROVIDER=local|minimax|azure|google|elevenlabs
TTS_API_KEY
TTS_ENDPOINT
MINIMAX_API_KEY
MINIMAX_TTS_ENDPOINT
MINIMAX_ENDPOINT
DATA_SERVICE_AI_API_KEY
DATA_SERVICE_AI_BASE_URL

PPTX_PROVIDER=local|python-pptx
PPTX_EXPORTER_ENABLED=1
```

Local tools used in accepted paths:

- Tesseract for local OCR;
- `pdftoppm` for scanned PDF rasterization;
- `espeak-ng` for local WAV generation;
- local OpenXML exporter for PPTX.

## 7. Final Acceptance Evidence

Final command set recorded in closure:

```text
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase41_download_contract.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase35_pptx_export.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase36_provider_closure.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_backend_contract.py backend/tests/test_research_notebook_v25_real_input_acceptance.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase39_minimax_tts_provider.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase37_scanned_pdf_ocr.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase38_provider_adapter_hardening.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase34_tts_provider.py -q
python3 -m py_compile backend/data_service/research_notebook_artifacts.py backend/app/api/v1/research_notebook.py backend/tests/test_research_notebook_v25_phase41_download_contract.py
```

Additional reassessment run before this handoff:

```text
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase41_download_contract.py backend/tests/test_research_notebook_v25_phase39_minimax_tts_provider.py backend/tests/test_research_notebook_v25_phase37_scanned_pdf_ocr.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_backend_contract.py backend/tests/test_research_notebook_v25_real_input_acceptance.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_v2_project_overview.py backend/tests/test_v2_agent_context_pack.py backend/tests/test_v2_devwiki_baseline.py backend/tests/test_v2_code_graph_baseline.py backend/tests/test_v2_code_quality_governance.py backend/tests/test_v2_code_architecture_inference.py -q
```

Observed results:

```text
ResearchNotebook focused: 5 passed
ResearchNotebook backend contract + real-input: 7 passed
Project Intelligence focused: 12 passed
```

## 8. Explicit Non-Claims

Do not claim:

- cloud OCR is accepted;
- Minimax OCR is supported;
- Azure/Google/ElevenLabs TTS is accepted;
- direct binary streaming is implemented;
- signed URL streaming is implemented;
- every optional provider from the original PRD is implemented;
- descriptor-only download is equivalent to streaming download;
- LLM-enhanced artifact quality is part of V2.5 closure.

## 9. Architecture Notes

No fatal architecture drift was found for V2.5.

The implementation uses:

- `backend/app/api/v1/research_notebook.py` for ResearchNotebook HTTP routes;
- `backend/data_service/research_notebook/` for provider/artifact support modules;
- `backend/data_service/research_notebook_artifacts.py` as artifact facade and deterministic artifact service.

Risk:

- `research_notebook_artifacts.py` is now a broad facade. If V2.6+ adds direct streaming, more external providers, or LLM-enhanced artifact generation, split it into focused modules before expanding it further.

## 10. Worktree / Release Risk

At handoff time, `git status --short` still reports V2.5-related files as untracked or modified, including:

- `backend/app/api/v1/research_notebook.py`
- `backend/data_service/research_notebook/`
- `backend/data_service/research_notebook_artifacts.py`
- `backend/tests/test_research_notebook_v25_phase41_download_contract.py`
- `docs/V2.x/`

The next terminal should not treat V2.5 as a committed release until these files are reviewed, added, committed, and optionally tagged.

## 11. Recommended Handoff Checklist

1. Review this file and `V2_5_FULL_PRD_COVERAGE_MATRIX.md`.
2. Confirm no V2.5 file is accidentally omitted from git tracking.
3. Re-run the final acceptance command set.
4. Commit all V2.5 code, tests, docs, and drawio artifacts.
5. Tag or record the commit as the V2.5 freeze point.
6. Do not reopen cloud OCR or direct streaming without a new phase plan.
