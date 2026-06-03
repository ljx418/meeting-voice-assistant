# V2.5 Phase 37 Pre-Gate Acceptance Plan

> Acceptance plan for provider execution contract freeze.
> This gate must pass before scanned PDF OCR implementation begins.

## 1. Required Checks

Phase 37 Pre-Gate passes only if all checks below pass:

- `ProviderExecutionAdapter`, `ProviderExecutionRequest`, `ProviderExecutionResult`, `ProviderCapability`, and `ArtifactWriteResult` exist in code.
- `ProviderExecutionResult.to_public()` includes `ok`, `capability`, `provider.name`, `provider.kind`, `provider.health_known`, `provider.execution_supported`, `artifact`, `error`, and `redacted`.
- A health-known external provider without execution adapter returns `PROVIDER_UNSUPPORTED`.
- Unsupported provider execution output is redacted and does not leak API keys, endpoints, raw tracebacks, or local paths.
- Local provider support remains compatible with V2.5A local closure.

## 2. Focused Tests

Run:

```text
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase37_pre_gate_provider_contract.py -q
```

Regression:

```text
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase36_provider_closure.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_backend_contract.py backend/tests/test_research_notebook_v25_real_input_acceptance.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase32_provider_safety.py -q
```

Static validation:

```text
PYTHONPATH=backend python3 -m py_compile backend/data_service/research_notebook/providers/adapter_contract.py
git diff --check -- backend/data_service/research_notebook/providers/adapter_contract.py backend/data_service/research_notebook/providers/__init__.py backend/tests/test_research_notebook_v25_phase37_pre_gate_provider_contract.py docs/V2.x/V2_5_PHASE_37_PRE_GATE_DEVELOPMENT_PLAN.md docs/V2.x/V2_5_PHASE_37_PRE_GATE_ACCEPTANCE_PLAN.md docs/V2.x/V2_5_PHASE_37_PRE_GATE_AUDIT_REPORT.md
```

## 3. False-Green Rejection

Reject the phase if:

- provider health availability is treated as execution availability;
- a health-known provider silently falls back to a local provider;
- provider execution returns a private OCR-only shape;
- public output leaks local paths, keys, endpoints, or raw provider exception text;
- V2.5A local provider closure regresses.

## 4. Provider Acceptance Matrix Update

Expected status after this gate:

```text
OCR:
  local_image: accepted from V2.5A regression
  scanned_pdf: not implemented
  cloud: provider unavailable / not implemented
TTS:
  local_espeak: accepted from V2.5A regression
  external: not implemented
PPTX:
  local_openxml: accepted from V2.5A regression
Download:
  descriptor: accepted from V2.5A regression
  stream: not implemented
```
