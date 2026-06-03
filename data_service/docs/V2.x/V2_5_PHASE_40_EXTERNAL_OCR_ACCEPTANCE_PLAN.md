# V2.5 Phase 40 Acceptance Plan: External OCR Provider Decision

## 1. Acceptance Modes

Accepted cloud OCR requires:

- provider decision record;
- real provider-enabled fixture run;
- OCR artifact with pages, blocks, text, confidence, locators, evidence refs, provider metadata;
- persisted artifact JSON and readback/status consistency;
- public redaction checks.

Provider unavailable acceptance requires:

- provider decision record;
- explicit `provider unavailable` or `out of scope` status;
- local Tesseract image OCR and scanned PDF OCR regressions remain accepted;
- final coverage matrix does not mark cloud OCR as accepted.

The current Phase 40 decision record selects `none` and sets cloud OCR to `provider unavailable`. A later accepted provider run must update the decision record and add real fixture evidence before any coverage row may move to `accepted`.

## 2. Required Tests

Focused tests are defined during implementation based on the provider decision.

Always run:

```text
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase37_scanned_pdf_ocr.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase38_provider_adapter_hardening.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase39_minimax_tts_provider.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase36_provider_closure.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_backend_contract.py backend/tests/test_research_notebook_v25_real_input_acceptance.py -q
```

## 3. False-Green Rejection

Reject the phase if:

- cloud OCR is marked accepted without a real provider run;
- TTS provider health or credentials are used as OCR provider acceptance;
- local Tesseract output is relabeled as cloud OCR;
- provider response lacks evidence-compatible page/block metadata and is still accepted.
