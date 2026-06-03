# V2.5 Phase 34 Acceptance Plan: TTS / Audio Overview Real Run

> Generated from repository analysis.
> Real local audio generation is mandatory for Phase 34 acceptance.
> Script-only output must not be accepted as audio-ready.

## 1. Acceptance Scope

Phase 34 is accepted only for the local TTS provider actually configured and tested.

Accepted target:

```text
TTS provider: local
Engine: espeak-ng
Output: WAV
Required fixture: real text source evidence
```

Phase 34 must not claim:

- cloud TTS provider readiness;
- streaming audio;
- PPTX export readiness;
- higher-quality neural voices.

## 2. Functional Acceptance

Provider-disabled fallback:

- `TTS_PROVIDER` unset returns unavailable health.
- `POST /api/workspaces/{workspace_id}/artifacts/audio` returns `AUDIO_OVERVIEW_NOT_READY`.
- No fake audio binary is written.

Provider-enabled real audio:

- `TTS_PROVIDER=local` health returns available only when `espeak-ng` is present.
- A real text source is imported and used as evidence.
- Audio create endpoint generates evidence-backed script segments.
- Audio create endpoint executes real `espeak-ng`.
- Response status is `ready`.
- Artifact list/read/status/download can retrieve the audio descriptor.
- Persisted artifact has `artifact_type=audio_overview`, `audio_available=true`, `binary.mime_type=audio/wav`, `binary.size_bytes`, `binary.sha256`, and `binary.duration_ms > 0`.

## 3. Security and Redaction Acceptance

Public payloads must not contain:

- local binary filesystem path;
- API keys, tokens, secrets, authorization headers;
- raw provider traceback;
- `file://` refs.

Binary refs must use:

```text
artifact://{workspace_id}/{artifact_id}?binary=audio
```

## 4. No-Fake Audio Acceptance

Reject acceptance if:

- WAV file is missing;
- WAV file size is zero or below the phase minimum threshold;
- descriptor `size_bytes` does not match disk;
- descriptor `sha256` does not match disk;
- duration is zero;
- script has no evidence refs;
- provider-disabled path returns a ready audio artifact;
- script-only output is marked as audio-ready.

## 5. Required Tests

Focused provider suite:

```bash
PYTHONPATH=backend TTS_PROVIDER=local python3 -m pytest backend/tests/test_research_notebook_v25_phase34_tts_provider.py -q
```

Phase 32 and 33 regression:

```bash
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase32_provider_safety.py backend/tests/test_research_notebook_v25_phase33_ocr_provider.py -q
```

V2.5 baseline regression:

```bash
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_backend_contract.py backend/tests/test_research_notebook_v25_real_input_acceptance.py -q
```

Broader ResearchNotebook guard:

```bash
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase34_tts_provider.py backend/tests/test_research_notebook_v25_phase33_ocr_provider.py backend/tests/test_research_notebook_v25_phase32_provider_safety.py backend/tests/test_research_notebook_v25_backend_contract.py backend/tests/test_research_notebook_v25_real_input_acceptance.py backend/tests/test_target_http_source_preview.py backend/tests/test_target_http_url_sources.py backend/tests/test_target_http_studio_artifacts.py backend/tests/test_public_surface_guard.py -q
```

Static checks:

```bash
python3 -m py_compile backend/data_service/research_notebook/providers/tts_espeak.py backend/data_service/research_notebook/artifacts/binary_store.py backend/data_service/research_notebook_artifacts.py backend/app/api/v1/research_notebook.py backend/tests/test_research_notebook_v25_phase34_tts_provider.py
git diff --check -- backend/data_service/research_notebook/providers/tts_espeak.py backend/data_service/research_notebook/artifacts/binary_store.py backend/data_service/research_notebook_artifacts.py backend/app/api/v1/research_notebook.py backend/tests/test_research_notebook_v25_phase34_tts_provider.py docs/V2.x/V2_5_PHASE_34_DEVELOPMENT_PLAN.md docs/V2.x/V2_5_PHASE_34_ACCEPTANCE_PLAN.md docs/V2.x/V2_5_PHASE_34_AUDIT_REPORT.md
```

## 6. Exit Criteria

Phase 34 passes only if:

- local `espeak-ng` real audio E2E passes;
- binary artifact is persisted and read back from disk;
- provider-disabled fallback still passes;
- Phase 32/33 and V2.5 baseline regressions pass;
- PRD/spec review finds no major deviation;
- false-acceptance review has no fatal or major open finding.
