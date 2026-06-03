# V2.5 Phase 39 Acceptance Plan: External TTS Provider Real Run

## 1. Acceptance Modes

Accepted external TTS requires:

- selected provider decision record;
- real provider-enabled run;
- audio binary exists and size exceeds threshold;
- descriptor `size_bytes`, `sha256`, MIME type, and duration match the binary;
- script segments are evidence-backed;
- bad-key and timeout paths are structured and redacted.

Provider unavailable acceptance requires:

- selected provider decision record;
- explicit `provider unavailable` status;
- local espeak-ng and provider-disabled fallback regressions still pass;
- no placeholder audio is marked ready.

## 2. Required Tests

Focused tests are defined during implementation based on the selected provider or unavailable mode.

Always run:

```text
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase38_provider_adapter_hardening.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase37_scanned_pdf_ocr.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase36_provider_closure.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_backend_contract.py backend/tests/test_research_notebook_v25_real_input_acceptance.py -q
```

## 3. False-Green Rejection

Reject the phase if:

- provider-disabled path is counted as external provider success;
- empty/tiny placeholder audio is marked ready;
- script-only artifact is marked audio-ready;
- key, endpoint, raw provider body, traceback, or local path leaks;
- external provider is called without approval.
