# V2.5 Phase 32 Acceptance Plan: Provider Config and Safety Boundary

## Required Acceptance

Phase 32 is accepted only when:

- OCR/TTS/PPTX provider health responses include structured `error`, `capability`, and `provider_detail`.
- Existing provider-disabled V2.5 behavior still passes.
- Provider failure modes return stable public codes.
- Redaction checker passes for provider health and artifact failure payloads.
- Real ResearchNotebook Markdown docs still pass source import -> artifact generation -> persistence -> readback acceptance.
- No provider-enabled real OCR/TTS/PPTX success is claimed.

## Failure Mode Matrix

| Scenario | Expected Code |
| --- | --- |
| no provider | `PROVIDER_NOT_CONFIGURED` or `EXPORTER_NOT_CONFIGURED` |
| unsupported provider | `PROVIDER_UNSUPPORTED` or `EXPORTER_UNSUPPORTED` |
| missing key | `PROVIDER_MISSING_CREDENTIAL` |
| auth failure | `PROVIDER_AUTH_FAILED` |
| timeout | `PROVIDER_TIMEOUT` |
| quota exceeded | `PROVIDER_QUOTA_EXCEEDED` |
| bad response | `PROVIDER_BAD_RESPONSE` |
| execution failure | `PROVIDER_EXECUTION_FAILED` |
| output invalid | `PROVIDER_OUTPUT_INVALID` |

## Test Commands

Focused Phase 32:

```bash
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase32_provider_safety.py -q
```

V2.5 regression:

```bash
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_backend_contract.py backend/tests/test_research_notebook_v25_real_input_acceptance.py -q
```

Broader ResearchNotebook/V2.5 guard:

```bash
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_backend_contract.py backend/tests/test_research_notebook_v25_real_input_acceptance.py backend/tests/test_target_http_source_preview.py backend/tests/test_target_http_url_sources.py backend/tests/test_target_http_studio_artifacts.py backend/tests/test_public_surface_guard.py -q
```

## Stop Conditions

Stop for human review if:

- provider-enabled success is claimed without real provider execution;
- existing fallback returns regress;
- public payload leaks key/token/secret/endpoint/path/raw traceback;
- provider-specific logic is added to `backend/app/api/v1/data_service.py`;
- real ResearchNotebook docs E2E no longer passes.
