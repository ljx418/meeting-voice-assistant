# V2.5 Phase 38 Development Plan: Provider Adapter Contract Hardening

> Generated after Phase 37 scanned PDF OCR passed.
> This phase hardens the distinction between provider health and provider execution.

## 1. Objective

Make provider execution support publicly queryable and testable without confusing it with provider health. A provider can be health-known or configured, but it is executable only when an adapter exists and local/runtime prerequisites pass.

## 2. Scope

In scope:

- add public execution status helpers;
- expose HTTP execution status endpoints for OCR, TTS, and PPTX exporter;
- test health-known external provider without adapter returns `PROVIDER_UNSUPPORTED`;
- test unsupported provider does not fall back to local provider;
- preserve all V2.5A and Phase 37 regressions.

Out of scope:

- implement external TTS or cloud OCR adapters;
- choose Minimax/Azure/Google/ElevenLabs provider;
- direct binary stream contract closure.

## 3. API Design

New endpoints:

```text
POST /api/ocr/provider/execution
POST /api/tts/provider/execution
POST /api/pptx/provider/execution
```

Response shape:

```json
{
  "ok": false,
  "status": "unavailable",
  "capability": "tts",
  "provider": {
    "name": "azure",
    "kind": "external",
    "health_known": true,
    "health_available": true,
    "execution_supported": false
  },
  "artifact": null,
  "error": {
    "code": "PROVIDER_UNSUPPORTED",
    "message": "Provider 'azure' has no execution adapter for tts.",
    "retryable": false
  },
  "warnings": ["execution_adapter_unavailable"],
  "redacted": true
}
```

## 4. Implementation Plan

1. Add `provider_execution_status()` to `adapter_contract.py`.
2. Re-export it through `research_notebook_artifacts.py`.
3. Add provider execution endpoints to `research_notebook.py`.
4. Add focused Phase 38 tests.
5. Run Phase 37 and V2.5A regressions.

## 5. Non-Goals

- Do not mark cloud providers accepted.
- Do not use health route availability as execution availability.
- Do not silently choose local provider when an explicit external provider is configured.
