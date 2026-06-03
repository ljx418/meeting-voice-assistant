# V2.5 Phase 39 Audit Report: External TTS Provider Real Run

> Initial audit report for external TTS provider run.

## 1. PRD/Spec Review

Decision: do not call an external provider until provider availability and approval are confirmed.

Reason:

- external TTS can transmit source-derived script text outside the machine;
- external TTS can incur provider cost;
- V2.5B acceptance explicitly allows `provider unavailable`, but rejects fake accepted provider success.

## 2. Architecture Review

No fatal or major architecture deviation identified before provider decision.

Guardrails:

- no external provider SDK logic in route handlers;
- no provider key logging;
- no provider-disabled fallback counted as external success;
- local espeak-ng remains accepted regression only.

## 3. Validation Results

Status: passed for configured Minimax TTS provider.

Non-secret environment availability check:

```text
minimax: MINIMAX_API_KEY=false, MINIMAX_GROUP_ID=false, MINIMAX_ENDPOINT=false
azure: AZURE_TTS_API_KEY=false, AZURE_TTS_ENDPOINT=false, TTS_API_KEY=false, TTS_ENDPOINT=false
google: GOOGLE_APPLICATION_CREDENTIALS=false, GOOGLE_TTS_API_KEY=false
elevenlabs: ELEVENLABS_API_KEY=false
```

Initial check before implementation did not call external provider APIs.

Updated decision after user instruction:

```text
selected_external_tts_provider=minimax
credential_source_candidates=TTS_API_KEY | MINIMAX_API_KEY | DATA_SERVICE_AI_API_KEY
explicit_provider_required=TTS_PROVIDER=minimax
network_api_call_status=completed
```

Real provider execution result:

```text
provider=minimax
health.available=true
execution.ok=true
artifact.status=ready
artifact.artifact_available=true
artifact.audio_available=true
artifact_id=art_audio_overview_d04deeab04d8
binary.mime_type=audio/wav
binary.size_bytes=432134
binary.duration_ms=6733
script_count=1
evidence_ref_count=1
```

No provider secret was printed or persisted in public payload.

Commands run:

```text
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase39_minimax_tts_provider.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase38_provider_adapter_hardening.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase34_tts_provider.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase36_provider_closure.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase37_scanned_pdf_ocr.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_backend_contract.py backend/tests/test_research_notebook_v25_real_input_acceptance.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase32_provider_safety.py -q
PYTHONPATH=backend python3 -m py_compile backend/data_service/research_notebook/providers/health.py backend/data_service/research_notebook/providers/adapter_contract.py backend/data_service/research_notebook/providers/tts_minimax.py backend/data_service/research_notebook_artifacts.py backend/tests/test_research_notebook_v25_phase39_minimax_tts_provider.py
git diff --check -- backend/data_service/research_notebook/providers/health.py backend/data_service/research_notebook/providers/adapter_contract.py backend/data_service/research_notebook/providers/tts_minimax.py backend/data_service/research_notebook_artifacts.py backend/tests/test_research_notebook_v25_phase39_minimax_tts_provider.py docs/V2.x/V2_5_PHASE_39_EXTERNAL_TTS_DEVELOPMENT_PLAN.md docs/V2.x/V2_5_PHASE_39_EXTERNAL_TTS_ACCEPTANCE_PLAN.md docs/V2.x/V2_5_PHASE_39_EXTERNAL_TTS_AUDIT_REPORT.md docs/V2.x/V2_5_PHASE_39_TTS_PROVIDER_DECISION.json
```

Results:

```text
Phase 39 Minimax mocked provider tests: 2 passed.
Phase 38 provider adapter hardening regression: 3 passed.
Phase 34 local TTS regression: 3 passed.
Phase 36 provider closure regression: 2 passed.
Phase 37 scanned PDF OCR regression: 1 passed.
V2.5 backend contract + real-input regression: 7 passed.
Phase 32 provider safety regression: 5 passed.
py_compile: passed.
git diff --check: passed.
```

Provider acceptance matrix:

```text
TTS:
  local_espeak: accepted from V2.5A regression
  external: accepted for configured Minimax provider only
```

False-acceptance decision:

- provider-disabled fallback is not counted as external TTS success;
- local espeak-ng is not counted as external TTS success;
- no placeholder audio artifact was generated.

## 4. Audit Decision

Current decision: Phase 39 passed for Minimax.

This does not accept Azure, Google, or ElevenLabs TTS. Those providers remain health-known candidates without executable adapter acceptance unless separately implemented and tested.
