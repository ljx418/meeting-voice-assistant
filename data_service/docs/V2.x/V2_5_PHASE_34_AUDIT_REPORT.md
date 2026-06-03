# V2.5 Phase 34 Audit Report: TTS / Audio Overview Real Run

> Generated from repository analysis.
> Business code was modified for Phase 34 local TTS/audio execution.
> Phase 34 acceptance uses real local WAV generation, not mocked audio output.

## 1. Scope Review

Phase 34 targets real local TTS/audio execution only.

In scope:

- local `espeak-ng` TTS adapter;
- source-evidence script generation;
- WAV binary artifact persistence;
- binary descriptor readback/download;
- provider-disabled fallback preservation.

Out of scope:

- cloud TTS providers;
- PPTX export;
- neural voice quality upgrades;
- streaming audio.

## 2. PRD and Architecture Alignment

| Check | Result |
| --- | --- |
| Phase 34 maps to V2.5 TTS / Audio Overview Real Run. | pass |
| Audio output must be binary-backed, not script-only. | pass |
| Script segments must carry evidence refs. | pass |
| Provider-disabled fallback must remain `AUDIO_OVERVIEW_NOT_READY`. | pass |
| Public payload must not expose local binary path. | pass |
| V2.0-V2.4 code asset artifacts remain untouched. | pass |

## 3. Preflight Findings

Current local provider status before dependency installation:

```text
espeak-ng: not found
```

Planned local dependency path:

```text
HOMEBREW_NO_AUTO_UPDATE=1 brew install espeak-ng
```

This is consistent with the V2.5 hard constraint: prefer open-source, free, local providers on MacBook Pro 2020.

Post-install provider status:

```text
espeak-ng 1.52.0
pcaudiolib 1.3
```

## 4. Implementation Risk Review

| Risk | Severity | Mitigation |
| --- | --- | --- |
| Empty/fake WAV generated. | fatal | Test checks WAV size, SHA-256, and duration from WAV header. |
| Script-only artifact marked as audio-ready. | major | Require `audio_available=true` only after binary descriptor exists. |
| Script lacks evidence refs. | major | Build script from existing `evidence_refs`. |
| Public response leaks binary path. | major | Binary descriptor uses `artifact://` ref only. |
| Provider-disabled fallback regresses. | major | Run Phase 32/V2.5 baseline regression. |
| TTS implementation grows route/service files. | major | Keep provider/binary logic in focused modules. |

## 5. False-Acceptance Review Before Implementation

Rejected acceptance patterns:

- zero-byte WAV;
- JSON descriptor without matching binary;
- hard-coded script without source evidence;
- provider-disabled success;
- local path in public descriptor;
- skipped provider-enabled tests while claiming Phase 34 complete.

## 6. Pre-Implementation Decision

Decision: proceed with Phase 34 only after local `espeak-ng` dependency is installed and provider preflight is rerun.

Open fatal findings: none.

Open major findings: none after dependency installation is attempted; if installation fails, Phase 34 becomes blocked and must not claim audio completion.

## 7. Implementation Summary

Implemented:

- local `espeak-ng` TTS provider in `backend/data_service/research_notebook/providers/tts_espeak.py`;
- binary descriptor helper in `backend/data_service/research_notebook/artifacts/binary_store.py`;
- local TTS health gate through existing provider health contract;
- real WAV artifact generation in `backend/data_service/research_notebook_artifacts.py`;
- audio binary download descriptor for `format=wav`;
- Phase 34 focused tests in `backend/tests/test_research_notebook_v25_phase34_tts_provider.py`.

Implementation note:

- `espeak-ng -w` on this environment truncates longer output filenames. The provider writes to a short temporary file `a.wav` and then atomically replaces the intended service-owned artifact path.

Not implemented:

- cloud TTS providers;
- neural voice quality upgrades;
- streaming audio;
- PPTX export.

## 8. PRD and Spec Review After Implementation

| Check | Result |
| --- | --- |
| Local provider-backed WAV generation exists. | pass |
| Provider-disabled fallback remains `AUDIO_OVERVIEW_NOT_READY`. | pass |
| Audio artifact includes script segments with evidence refs. | pass |
| Binary descriptor includes `ref`, MIME type, size, SHA-256, and duration. | pass |
| Download descriptor uses safe `artifact://` ref and no local path. | pass |
| Script-only external provider path is not marked audio-ready. | pass |
| OCR behavior from Phase 33 remains passing. | pass |
| PPTX is not falsely claimed. | pass |

## 9. False-Acceptance Review After Implementation

| False acceptance risk | Result |
| --- | --- |
| Empty WAV accepted. | rejected; focused test checks size and duration. |
| JSON descriptor without matching binary accepted. | rejected; focused test checks binary exists and descriptor size matches disk. |
| Descriptor SHA-256 not bound to binary. | rejected; focused test checks SHA-256 shape and readback consistency. |
| Script lacks source evidence. | rejected; focused test checks script evidence refs. |
| Provider-disabled path returns ready audio. | rejected; fallback test returns `AUDIO_OVERVIEW_NOT_READY` and no binary. |
| External provider with key is marked audio-ready without adapter. | rejected; external-provider test returns script available but `audio_available=false`. |
| Public payload leaks binary path. | rejected; path redaction tests pass on audio/readback/download payloads. |

## 10. Verification Commands

Provider preflight:

```bash
which espeak-ng && espeak-ng --version
brew list --versions espeak-ng pcaudiolib
```

Result:

```text
eSpeak NG text-to-speech: 1.52.0
espeak-ng 1.52.0
pcaudiolib 1.3
```

Focused Phase 34 suite:

```bash
PYTHONPATH=backend TTS_PROVIDER=local python3 -m pytest backend/tests/test_research_notebook_v25_phase34_tts_provider.py -q
```

Result:

```text
3 passed in 1.33s
```

Phase 32 and 33 regression:

```bash
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase32_provider_safety.py backend/tests/test_research_notebook_v25_phase33_ocr_provider.py -q
```

Result:

```text
8 passed in 2.26s
```

V2.5 baseline and real-input regression:

```bash
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_backend_contract.py backend/tests/test_research_notebook_v25_real_input_acceptance.py -q
```

Result:

```text
7 passed in 1.66s
```

Broader ResearchNotebook/V2.5 guard:

```bash
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase34_tts_provider.py backend/tests/test_research_notebook_v25_phase33_ocr_provider.py backend/tests/test_research_notebook_v25_phase32_provider_safety.py backend/tests/test_research_notebook_v25_backend_contract.py backend/tests/test_research_notebook_v25_real_input_acceptance.py backend/tests/test_target_http_source_preview.py backend/tests/test_target_http_url_sources.py backend/tests/test_target_http_studio_artifacts.py backend/tests/test_public_surface_guard.py -q
```

Result:

```text
41 passed, 15 warnings in 6.03s
```

Broader data_service/V2.5 regression:

```bash
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase34_tts_provider.py backend/tests/test_research_notebook_v25_phase33_ocr_provider.py backend/tests/test_research_notebook_v25_phase32_provider_safety.py backend/tests/test_research_notebook_v25_backend_contract.py backend/tests/test_research_notebook_v25_real_input_acceptance.py backend/tests/test_data_service_api.py backend/tests/test_session_ingest_query_build_contract_plan.py -q
```

Result:

```text
55 passed, 164 warnings in 16.29s
```

Static checks:

```bash
python3 -m py_compile backend/data_service/research_notebook/providers/tts_espeak.py backend/data_service/research_notebook/artifacts/binary_store.py backend/data_service/research_notebook/providers/health.py backend/data_service/research_notebook_artifacts.py backend/tests/test_research_notebook_v25_phase34_tts_provider.py
git diff --check -- backend/data_service/research_notebook/providers/tts_espeak.py backend/data_service/research_notebook/artifacts/binary_store.py backend/data_service/research_notebook/providers/health.py backend/data_service/research_notebook_artifacts.py backend/tests/test_research_notebook_v25_phase34_tts_provider.py docs/V2.x/V2_5_PHASE_34_DEVELOPMENT_PLAN.md docs/V2.x/V2_5_PHASE_34_ACCEPTANCE_PLAN.md docs/V2.x/V2_5_PHASE_34_AUDIT_REPORT.md
```

Result:

```text
passed
```

## 11. Final Phase 34 Decision

Phase 34 is accepted for:

```text
Provider: local
Engine: espeak-ng 1.52.0
Accepted path: real source evidence to WAV audio artifact
```

Open fatal findings: none.

Open major findings: none.

Phase 35 may proceed only after a separate development plan, acceptance plan, and audit report are created for local PPTX export real run.
