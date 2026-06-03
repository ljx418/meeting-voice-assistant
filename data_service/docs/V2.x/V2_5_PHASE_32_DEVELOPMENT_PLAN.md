# V2.5 Phase 32 Development Plan: Provider Config and Safety Boundary

## Objective

Implement the Provider Config + Safety Boundary before any real OCR/TTS/PPTX adapter work.

Phase 32 must not claim real OCR, real TTS, or real PPTX execution. It only hardens provider configuration, health payloads, structured errors, and redaction.

## Scope

In scope:

- Provider error code normalization.
- Provider health payload shape for OCR, TTS, and PPTX export.
- Redaction checker for public provider and artifact payloads.
- Backward-compatible health fields for existing V2.5 callers.
- Provider-disabled baseline preservation.
- Failure-mode tests for no provider, unsupported provider, missing credential, auth failure, timeout, quota, bad response, execution failure, output invalid, and exporter not configured.

Out of scope:

- Real OCR provider execution.
- Real TTS audio generation.
- Real PPTX generation.
- New frontend UI.
- V2.0-V2.4 code asset artifact changes.

## Implementation Design

Add a focused provider package:

```text
backend/data_service/research_notebook/
  __init__.py
  providers/
    __init__.py
    errors.py
    redaction.py
    health.py
```

Keep `backend/data_service/research_notebook_artifacts.py` as a compatibility facade and update it to call the new provider helpers.

Provider health payloads must include:

- `available`
- `status`
- `capability`
- `provider`
- `provider_detail`
- `error`
- `unsupported_reason`
- `warnings`
- `next_actions`

Compatibility rule:

- Existing top-level `provider` and `unsupported_reason` fields are preserved.
- New structured fields are additive.

Provider environment simulation for Phase 32 tests:

- `{PREFIX}_PROVIDER` selects provider.
- `{PREFIX}_API_KEY` controls credential availability.
- `{PREFIX}_SIMULATE_ERROR` can be set to `auth_failed`, `timeout`, `quota_exceeded`, `bad_response`, `execution_failed`, or `output_invalid`.
- `PPTX_PROVIDER` / `PPTX_SIMULATE_ERROR` follows exporter semantics.

## Architecture Gates

- Do not add provider-specific implementation logic to `backend/app/api/v1/data_service.py`.
- Do not implement real OCR/TTS/PPTX adapters in Phase 32.
- Do not remove existing provider-disabled fallback fields.
- Do not expose API keys, tokens, endpoint secrets, raw tracebacks, local paths, or provider raw response bodies.
