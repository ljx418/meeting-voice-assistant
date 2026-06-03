# V2.5 Phase 37 Acceptance Plan: Scanned PDF OCR Success

> Acceptance plan for real scanned PDF OCR.

## 1. Focused Acceptance

Run:

```text
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase37_scanned_pdf_ocr.py -q
```

Required assertions:

- scanned PDF fixture has no embedded text according to `pdftotext`;
- OCR provider result contains `embedded_text_probe.has_embedded_text = false`;
- OCR artifact status is `ready`;
- `generation_metadata.rasterizer = pdftoppm`;
- OCR artifact pages, blocks, text, confidence, locators, and evidence refs are present;
- persisted artifact JSON exists and matches API/readback/status payloads;
- public output has no absolute local path or secret.

## 2. Regression Acceptance

Run:

```text
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase37_pre_gate_provider_contract.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase36_provider_closure.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_backend_contract.py backend/tests/test_research_notebook_v25_real_input_acceptance.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase32_provider_safety.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase33_ocr_provider.py -q
```

Static validation:

```text
PYTHONPATH=backend python3 -m py_compile backend/data_service/research_notebook/providers/ocr_tesseract.py backend/data_service/research_notebook/artifacts/ocr_artifacts.py
git diff --check -- <changed-files>
```

## 3. False-Green Rejection

Reject the phase if:

- embedded-text PDF is used as scanned OCR proof;
- rasterizer is skipped but the phase is marked accepted;
- OCR artifact contains text without page/block/evidence metadata;
- provider-disabled fallback regresses;
- public payload leaks `/Users/`, `/private/tmp/`, provider secrets, or raw traceback.

## 4. Provider Acceptance Matrix Update

Expected status after this phase:

```text
OCR:
  local_image: accepted
  scanned_pdf: accepted if focused test passes; otherwise provider unavailable / conditionally accepted contract
  cloud: provider unavailable / not implemented
TTS:
  local_espeak: accepted
  external: not implemented
PPTX:
  local_openxml: accepted
Download:
  descriptor: accepted
  stream: not implemented
```
