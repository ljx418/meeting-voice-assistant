# V2.5 Phase 33 Audit Report: OCR Provider Real Run

> Generated from repository analysis.
> Business code was modified for Phase 33 OCR provider execution.
> Phase 33 acceptance uses real local OCR execution, not mocked OCR output.

## 1. Scope Review

Phase 33 targets real OCR execution only.

In scope:

- local Tesseract OCR adapter;
- image source OCR;
- optional PDF rasterizer handling;
- OCR artifact persistence/readback/status;
- provider-disabled fallback preservation.

Out of scope:

- TTS/audio;
- PPTX export;
- cloud OCR provider acceptance;
- full PDF OCR acceptance without rasterizer proof.

## 2. PRD and Architecture Alignment

| Check | Result |
| --- | --- |
| Phase 33 maps to V2.5 OCR Provider Real Run. | pass |
| OCR image fixture is mandatory. | pass |
| PDF OCR must use rasterizer or return `PDF_RASTERIZER_UNAVAILABLE`. | pass |
| No fake OCR output is allowed. | pass |
| Provider-disabled fallback must remain `OCR_REQUIRED`. | pass |
| V2.0-V2.4 code asset artifacts remain untouched. | pass |

## 3. Preflight Findings

Current local provider status before dependency installation:

```text
tesseract: not found
pdftoppm: not found
PIL: missing
pytesseract: missing
```

Planned local dependency path:

```text
brew install tesseract tesseract-lang poppler
```

This is consistent with the V2.5 hard constraint: prefer open-source, free, local providers on MacBook Pro 2020.

Post-install provider status:

```text
tesseract 5.5.2
pdftoppm version 26.04.0
brew list --versions: poppler 26.04.0, tesseract 5.5.2, tesseract-lang 4.1.0
```

The first `brew install` attempt stalled during auto-update. It was stopped and rerun with auto-update disabled:

```text
HOMEBREW_NO_AUTO_UPDATE=1 brew install tesseract tesseract-lang poppler
```

The command installed the required packages. It exited with code 1 after install output, likely due to Homebrew cleanup/postinstall behavior, so acceptance was based on actual executable/version checks rather than the Homebrew exit code.

## 4. Implementation Risk Review

| Risk | Severity | Mitigation |
| --- | --- | --- |
| Fake OCR artifact generated from fixture expected text. | fatal | Tests must generate image input and assert provider execution metadata. |
| Image upload suffix rewritten to `.txt`. | major | Preserve OCR image suffixes in target source upload allowlist. |
| PDF OCR falsely accepted from embedded text. | major | Only accept PDF OCR when `pdftoppm` rasterization path is used. |
| Public response leaks local path. | major | Reuse V2.5 redaction helper and existing path assertion. |
| Provider-disabled fallback regresses. | major | Run Phase 32 and V2.5 baseline regression. |
| OCR implementation grows legacy route/service files. | major | Keep implementation in focused provider/artifact modules. |

## 5. False-Acceptance Review Before Implementation

Rejected acceptance patterns:

- empty OCR pages with `status=ready`;
- hard-coded OCR text;
- test monkeypatch bypassing the provider;
- provider-disabled success;
- image fixture stored as text;
- path leaks hidden by only checking selected fields;
- skipped provider-enabled tests while claiming Phase 33 complete.

## 6. Pre-Implementation Decision

Decision: proceed with Phase 33 only after local OCR dependencies are installed and provider preflight is rerun.

Open fatal findings: none.

Open major findings: none after dependency installation is attempted; if installation fails, Phase 33 becomes blocked and must not claim OCR completion.

## 7. Implementation Summary

Implemented:

- local Tesseract OCR provider in `backend/data_service/research_notebook/providers/ocr_tesseract.py`;
- OCR artifact persistence/readback/status in `backend/data_service/research_notebook/artifacts/ocr_artifacts.py`;
- ResearchNotebook OCR facade exports in `backend/data_service/research_notebook_artifacts.py`;
- OCR HTTP create/status behavior in `backend/app/api/v1/research_notebook.py`;
- image upload suffix preservation and image source type inference in `backend/app/api/v1/data_service.py`;
- narrow ProviderError uppercase preservation in `backend/data_service/mcp_common.py`;
- Phase 33 focused tests in `backend/tests/test_research_notebook_v25_phase33_ocr_provider.py`.

Not implemented:

- TTS/audio;
- PPTX export;
- cloud OCR provider adapters;
- full scanned PDF OCR success fixture. PDF rasterizer failure is represented with `PDF_RASTERIZER_UNAVAILABLE`.

## 8. PRD and Spec Review After Implementation

| Check | Result |
| --- | --- |
| Local provider-backed image OCR exists. | pass |
| Provider-disabled fallback remains `OCR_REQUIRED`. | pass |
| OCR artifact includes pages, blocks, text, confidence, locator, evidence refs, provider metadata, and generation metadata. | pass |
| Image source upload keeps image suffix and `source_type=image`. | pass |
| PDF rasterizer failure does not become OCR success. | pass |
| ProviderError code remains public uppercase for V2.5 provider/exporter errors. | pass |
| TTS/PPTX are not falsely claimed. | pass |

Minor note:

- The Phase 33 PDF test currently verifies structured rasterizer failure using a broken PDF fixture. A full scanned PDF success fixture remains outside this subphase's accepted claim and should only be added if a stable PDF image fixture is introduced.

## 9. False-Acceptance Review After Implementation

| False acceptance risk | Result |
| --- | --- |
| Fake OCR text copied from expected fixture. | rejected; test generates image and asserts Tesseract provider metadata plus recognized tokens. |
| Provider-disabled path writes OCR pages. | rejected; disabled test returns `OCR_REQUIRED` and no artifact. |
| Image source stored as `.txt`. | rejected; source type is `image` and upload suffix is preserved. |
| Broken/scanned PDF accepted through embedded text extraction. | rejected; rasterizer failure returns `PDF_RASTERIZER_UNAVAILABLE` and empty pages. |
| Public payload leaks local path. | rejected; existing `_assert_no_internal_paths` checks pass on OCR responses and readback. |
| Phase 33 claims TTS/PPTX. | rejected; implementation scope is OCR only. |

## 10. Verification Commands

Provider preflight:

```bash
which tesseract && tesseract --version
which pdftoppm && pdftoppm -v
brew list --versions tesseract tesseract-lang poppler
```

Result:

```text
tesseract 5.5.2
pdftoppm version 26.04.0
poppler 26.04.0
tesseract 5.5.2
tesseract-lang 4.1.0
```

Focused Phase 33 suite:

```bash
PYTHONPATH=backend OCR_PROVIDER=tesseract python3 -m pytest backend/tests/test_research_notebook_v25_phase33_ocr_provider.py -q
```

Result:

```text
3 passed in 2.19s
```

Phase 32 safety regression:

```bash
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase32_provider_safety.py -q
```

Result:

```text
5 passed in 1.59s
```

V2.5 baseline and real-input regression:

```bash
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_backend_contract.py backend/tests/test_research_notebook_v25_real_input_acceptance.py -q
```

Result:

```text
7 passed in 1.78s
```

Broader ResearchNotebook/V2.5 guard:

```bash
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase33_ocr_provider.py backend/tests/test_research_notebook_v25_phase32_provider_safety.py backend/tests/test_research_notebook_v25_backend_contract.py backend/tests/test_research_notebook_v25_real_input_acceptance.py backend/tests/test_target_http_source_preview.py backend/tests/test_target_http_url_sources.py backend/tests/test_target_http_studio_artifacts.py backend/tests/test_public_surface_guard.py -q
```

Result:

```text
38 passed, 15 warnings in 5.91s
```

Broader data_service/V2.5 regression:

```bash
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase33_ocr_provider.py backend/tests/test_research_notebook_v25_phase32_provider_safety.py backend/tests/test_research_notebook_v25_backend_contract.py backend/tests/test_research_notebook_v25_real_input_acceptance.py backend/tests/test_data_service_api.py backend/tests/test_session_ingest_query_build_contract_plan.py -q
```

Result:

```text
52 passed, 164 warnings in 15.56s
```

Static checks:

```bash
python3 -m py_compile backend/data_service/mcp_common.py backend/data_service/research_notebook/providers/ocr_tesseract.py backend/data_service/research_notebook/artifacts/ocr_artifacts.py backend/data_service/research_notebook/artifacts/__init__.py backend/data_service/research_notebook/providers/health.py backend/data_service/research_notebook_artifacts.py backend/app/api/v1/research_notebook.py backend/app/api/v1/data_service.py backend/tests/test_research_notebook_v25_phase33_ocr_provider.py
git diff --check -- backend/data_service/mcp_common.py backend/data_service/research_notebook/providers/ocr_tesseract.py backend/data_service/research_notebook/artifacts/__init__.py backend/data_service/research_notebook/artifacts/ocr_artifacts.py backend/data_service/research_notebook/providers/health.py backend/data_service/research_notebook_artifacts.py backend/app/api/v1/research_notebook.py backend/app/api/v1/data_service.py backend/tests/test_research_notebook_v25_phase33_ocr_provider.py docs/V2.x/V2_5_PHASE_33_DEVELOPMENT_PLAN.md docs/V2.x/V2_5_PHASE_33_ACCEPTANCE_PLAN.md docs/V2.x/V2_5_PHASE_33_AUDIT_REPORT.md
```

Result:

```text
passed
```

## 11. Final Phase 33 Decision

Phase 33 is accepted for:

```text
Provider: tesseract
Provider kind: local
Accepted path: real image source OCR
PDF behavior: structured rasterizer failure for invalid PDF fixture
```

Open fatal findings: none.

Open major findings: none.

Phase 34 may proceed only after a separate development plan, acceptance plan, and audit report are created for local TTS/audio real run.
