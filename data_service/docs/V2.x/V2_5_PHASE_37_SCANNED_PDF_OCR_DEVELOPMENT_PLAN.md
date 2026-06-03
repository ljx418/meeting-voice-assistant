# V2.5 Phase 37 Development Plan: Scanned PDF OCR Success

> Generated after Phase 37 Pre-Gate passed.
> This phase implements real scanned PDF OCR using the shared provider execution contract boundary.

## 1. Objective

Prove real scanned PDF OCR with a fixture that has no embedded text layer. The fixture must pass through PDF rasterization and Tesseract OCR before the artifact can be accepted.

## 2. Scope

In scope:

- add an embedded-text probe for PDF OCR inputs;
- persist probe metadata in OCR artifact generation metadata;
- test a generated image-only PDF fixture with `pdftotext` proving no embedded text;
- verify rasterizer path uses `pdftoppm`;
- verify persisted OCR artifact, readback payload, and status payload agree on artifact identity and readiness.

Out of scope:

- cloud OCR;
- external OCR adapter implementation;
- Minimax/Azure/Google OCR execution;
- direct download streaming.

## 3. Implementation Plan

1. Extend `ocr_tesseract.py` with `pdftotext_available()` and `pdf_embedded_text_probe()`.
2. Include `embedded_text_probe` in PDF OCR provider result.
3. Persist `embedded_text_probe` in OCR artifact `generation_metadata`.
4. Add `backend/tests/test_research_notebook_v25_phase37_scanned_pdf_ocr.py`.
5. Generate a real image-only PDF fixture in the test:
   - render text to PNG via `pango-view`;
   - convert PNG to JPEG via macOS `sips`;
   - embed JPEG bytes into a minimal PDF image XObject using Python stdlib;
   - assert `pdftotext` output is empty before OCR.
6. Run focused and V2.5A regression suites.

## 4. Stop Conditions

Stop for human review if:

- the environment lacks `pdftoppm` and scanned PDF success cannot be proven;
- a test attempts to use an embedded-text PDF as OCR success evidence;
- the OCR artifact copies fixture text without running rasterization/OCR;
- public output leaks local paths, provider secrets, or raw command output.

## 5. Expected Changes

- `backend/data_service/research_notebook/providers/ocr_tesseract.py`
- `backend/data_service/research_notebook/artifacts/ocr_artifacts.py`
- `backend/tests/test_research_notebook_v25_phase37_scanned_pdf_ocr.py`
- `docs/V2.x/V2_5_PHASE_37_SCANNED_PDF_OCR_DEVELOPMENT_PLAN.md`
- `docs/V2.x/V2_5_PHASE_37_SCANNED_PDF_OCR_ACCEPTANCE_PLAN.md`
- `docs/V2.x/V2_5_PHASE_37_SCANNED_PDF_OCR_AUDIT_REPORT.md`
