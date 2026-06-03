# V2.5 Phase 38 Acceptance Plan: Provider Adapter Contract Hardening

## 1. Focused Acceptance

Run:

```text
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase38_provider_adapter_hardening.py -q
```

Required assertions:

- health-known `azure` TTS with API key can be health-available;
- execution status for `azure` TTS returns `PROVIDER_UNSUPPORTED`;
- execution status includes `provider.health_known`, `provider.health_available`, and `provider.execution_supported`;
- unsupported provider returns `PROVIDER_UNSUPPORTED` and does not fall back to local;
- output is redacted.

## 2. Regression Acceptance

Run:

```text
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase37_scanned_pdf_ocr.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase37_pre_gate_provider_contract.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase36_provider_closure.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_backend_contract.py backend/tests/test_research_notebook_v25_real_input_acceptance.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase32_provider_safety.py -q
```

Static validation:

```text
PYTHONPATH=backend python3 -m py_compile backend/data_service/research_notebook/providers/adapter_contract.py backend/app/api/v1/research_notebook.py
git diff --check -- <changed-files>
```

## 3. False-Green Rejection

Reject the phase if:

- health availability is counted as executable support;
- an unsupported provider falls back to local provider;
- raw key, endpoint, traceback, or local path leaks;
- Phase 37 scanned PDF OCR regresses.
