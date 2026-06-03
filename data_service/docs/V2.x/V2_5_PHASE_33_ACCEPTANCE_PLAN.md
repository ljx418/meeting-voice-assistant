# V2.5 Phase 33 Acceptance Plan: OCR Provider Real Run

> Generated from repository analysis.
> Real image OCR is mandatory for Phase 33 acceptance.
> Scanned PDF OCR must either pass through real rasterization or return `PDF_RASTERIZER_UNAVAILABLE`.

## 1. Acceptance Scope

Phase 33 is accepted only for the local OCR provider actually configured and tested.

Accepted target:

```text
OCR provider: tesseract
Provider kind: local
Required fixture: real image source
Optional fixture: scanned PDF source via pdftoppm
```

Phase 33 must not claim:

- TTS/audio readiness;
- PPTX export readiness;
- cloud OCR provider readiness;
- full scanned PDF support if rasterizer tests do not pass.

## 2. Functional Acceptance

Provider-disabled fallback:

- `OCR_PROVIDER` unset returns unavailable health.
- `POST /api/workspaces/{workspace_id}/sources/{source_id}/ocr` returns `OCR_REQUIRED`.
- No OCR artifact with fake pages is written.

Provider-enabled real image OCR:

- `OCR_PROVIDER=tesseract` health returns available only when the executable is present.
- A real image source is imported with an image suffix preserved.
- OCR create endpoint executes real Tesseract on the stored image file.
- Response status is `ready`.
- Response returns an OCR artifact id/ref.
- Artifact list/read/status can retrieve the OCR artifact.
- Persisted artifact has `artifact_type=ocr`, `status=ready`, non-empty `pages`, non-empty `blocks`, extracted `text`, `confidence`, `confidence_band`, `locator`, and `evidence_refs`.

PDF rasterizer behavior:

- If `pdftoppm` is available and a scanned PDF fixture is available, PDF OCR must use rasterized pages.
- If rasterization is unavailable or fixture support is not implemented in this phase, PDF OCR must return `PDF_RASTERIZER_UNAVAILABLE`.
- Embedded text extraction must not be counted as scanned-PDF OCR success.

## 3. Security and Redaction Acceptance

Public payloads must not contain:

- API keys, tokens, secrets, authorization headers;
- raw provider traceback;
- local absolute paths such as `/Users/...`, `/private/tmp/...`, or `file://...`;
- provider raw response bodies.

Artifact refs must use:

```text
artifact://{workspace_id}/{artifact_id}
source://{source_id}#page=...&block=...
```

## 4. No-Fake OCR Acceptance

Reject acceptance if:

- expected fixture text is passed to the OCR artifact writer;
- OCR artifact text is hard-coded in tests or implementation;
- provider-disabled path writes fake pages;
- image source is actually stored as `.txt`;
- PDF success comes from embedded PDF text extraction rather than rasterized image OCR;
- low-confidence OCR is reported as high-confidence.

## 5. Required Tests

Focused provider suite:

```bash
PYTHONPATH=backend OCR_PROVIDER=tesseract python3 -m pytest backend/tests/test_research_notebook_v25_phase33_ocr_provider.py -q
```

Phase 32 safety regression:

```bash
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase32_provider_safety.py -q
```

V2.5 baseline regression:

```bash
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_backend_contract.py backend/tests/test_research_notebook_v25_real_input_acceptance.py -q
```

Broader ResearchNotebook guard:

```bash
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase33_ocr_provider.py backend/tests/test_research_notebook_v25_phase32_provider_safety.py backend/tests/test_research_notebook_v25_backend_contract.py backend/tests/test_research_notebook_v25_real_input_acceptance.py backend/tests/test_target_http_source_preview.py backend/tests/test_target_http_url_sources.py backend/tests/test_target_http_studio_artifacts.py backend/tests/test_public_surface_guard.py -q
```

Static checks:

```bash
python3 -m py_compile backend/data_service/research_notebook/providers/ocr_tesseract.py backend/data_service/research_notebook/artifacts/ocr_artifacts.py backend/data_service/research_notebook_artifacts.py backend/app/api/v1/research_notebook.py backend/tests/test_research_notebook_v25_phase33_ocr_provider.py
git diff --check -- backend/data_service/research_notebook/providers/ocr_tesseract.py backend/data_service/research_notebook/artifacts/ocr_artifacts.py backend/data_service/research_notebook_artifacts.py backend/app/api/v1/research_notebook.py backend/tests/test_research_notebook_v25_phase33_ocr_provider.py docs/V2.x/V2_5_PHASE_33_DEVELOPMENT_PLAN.md docs/V2.x/V2_5_PHASE_33_ACCEPTANCE_PLAN.md docs/V2.x/V2_5_PHASE_33_AUDIT_REPORT.md
```

## 6. Exit Criteria

Phase 33 passes only if:

- local Tesseract real image OCR E2E passes;
- OCR artifact is persisted and read back from disk;
- provider-disabled fallback still passes;
- Phase 32 safety tests still pass;
- V2.5 real-input baseline still passes;
- PRD/spec review finds no major deviation;
- false-acceptance review has no fatal or major open finding.
