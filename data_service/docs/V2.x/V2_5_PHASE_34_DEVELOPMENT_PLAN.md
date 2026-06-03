# V2.5 Phase 34 Development Plan: TTS / Audio Overview Real Run

> Generated from repository analysis.
> Business code must only change after this phase audit has no fatal or major open findings.
> Phase 34 must prove real audio binary generation from source evidence; script-only output is not audio-ready.

## 1. Phase Objective

Implement the first provider-backed audio overview path for ResearchNotebook using local, free, open-source tooling on the current MacBook Pro 2020 environment.

Target provider stack:

- TTS provider: local `espeak-ng` CLI.
- Audio format: WAV.
- Artifact owner: ResearchNotebook V2.5 artifact store.

Phase 34 does not implement PPTX export and does not change Phase 33 OCR behavior.

## 2. Scope

In scope:

- Add focused local TTS provider implementation under `backend/data_service/research_notebook/providers/`.
- Add binary artifact helper under `backend/data_service/research_notebook/artifacts/`.
- Update ResearchNotebook audio artifact creation to generate real audio when `TTS_PROVIDER=local`.
- Preserve provider-disabled `AUDIO_OVERVIEW_NOT_READY` fallback.
- Persist audio JSON descriptor and WAV binary under service-owned artifact storage.
- Return safe `artifact://` refs and download descriptor without local paths.
- Add real source-evidence E2E tests that inspect binary size, MIME type, SHA-256, duration, and script evidence refs.

Out of scope:

- Cloud TTS provider adapters.
- Voice quality optimization.
- Long-form chapter audio generation.
- Streaming audio.
- Real PPTX export.

## 3. Technical Design

### 3.1 Module Layout

```text
backend/data_service/research_notebook/
  providers/
    tts_espeak.py
  artifacts/
    binary_store.py
```

`backend/data_service/research_notebook_artifacts.py` remains the compatibility facade and may call these focused modules.

### 3.2 Audio Artifact Contract

Ready audio artifacts must include:

```json
{
  "artifact_type": "audio_overview",
  "status": "ready",
  "artifact_available": true,
  "script_available": true,
  "audio_available": true,
  "script": [
    {
      "text": "...",
      "evidence_refs": []
    }
  ],
  "voice_metadata": {
    "provider": "local",
    "engine": "espeak-ng",
    "voice_id": "en",
    "language": "en-US"
  },
  "binary": {
    "ref": "artifact://workspace_id/artifact_id?binary=audio",
    "mime_type": "audio/wav",
    "size_bytes": 12345,
    "sha256": "...",
    "duration_ms": 1000
  }
}
```

### 3.3 No-Fake Audio Rule

Audio-ready output must be backed by a real WAV file:

- binary file exists;
- `size_bytes` matches disk size;
- `sha256` matches disk bytes;
- duration is greater than zero according to WAV header;
- script segments are derived from source evidence.

## 4. Implementation Steps

1. Install/check local TTS tool: `espeak-ng`.
2. Add provider preflight/version detection.
3. Add binary store helper for service-owned binary paths and descriptors.
4. Generate evidence-backed script segments before TTS execution.
5. Call `espeak-ng -w` to write WAV output.
6. Persist audio descriptor and binary metadata.
7. Update download descriptor for binary audio format.
8. Add tests:
   - provider-disabled fallback;
   - real local TTS E2E;
   - binary descriptor integrity;
   - script evidence refs;
   - no local path exposure;
   - Phase 33/32/V2.5 regression.
9. Update Phase 34 audit report with commands, evidence, PRD review, and false-acceptance review.

## 5. Architecture Gates

- Do not generate empty WAV files.
- Do not mark script-only output as `audio_available=true`.
- Do not expose binary filesystem paths.
- Do not add TTS implementation logic to `backend/app/api/v1/data_service.py`.
- Do not claim cloud TTS support unless provider-enabled cloud fixture tests pass.
- Do not mutate V2.0-V2.4 code asset artifacts.

## 6. Stop Conditions

Stop and request human confirmation if:

- local TTS installation cannot complete;
- `espeak-ng` cannot generate a valid WAV from a real source-evidence script;
- audio descriptor integrity cannot be verified;
- public payload leaks local paths or provider details;
- provider-disabled fallback regresses;
- implementation requires broad changes to legacy API/service files.
