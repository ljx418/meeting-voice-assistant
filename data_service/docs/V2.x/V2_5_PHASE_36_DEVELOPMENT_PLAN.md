# V2.5 Phase 36 Development Plan: Provider-Specific Closure

> Generated from repository analysis.
> Phase 36 is closure-only and must not add new product capability.
> Closure must validate provider-enabled and provider-disabled paths with real local artifacts.

## 1. Phase Objective

Close V2.5 provider-specific execution by validating the full local provider-backed ResearchNotebook artifact matrix:

- OCR: local Tesseract real image OCR.
- TTS: local espeak-ng real WAV audio.
- PPTX: local OpenXML real `.pptx` export.
- Disabled fallback: stable unavailable contracts.

## 2. Scope

In scope:

- Add a closure-level E2E test that exercises OCR, TTS/audio, slides, PPTX export, artifact readback, and disabled fallback.
- Run all Phase 32-35 focused suites and V2.5 baseline regression.
- Update final closure audit report.

Out of scope:

- New OCR/TTS/PPTX provider adapters.
- New frontend UI.
- New ResearchNotebook product APIs.

## 3. Closure Checks

Provider-enabled closure must prove:

- local provider health available for OCR/TTS/PPTX;
- real OCR artifact exists;
- real audio binary descriptor exists;
- real PPTX OpenXML package exists;
- public payloads have no local paths;
- artifact list/read/status/download work for binary artifacts.

Provider-disabled closure must prove:

- OCR returns `OCR_REQUIRED`;
- audio returns `AUDIO_OVERVIEW_NOT_READY`;
- PPTX export returns `SLIDE_OUTLINE_ONLY`;
- no fake provider-backed artifacts are written.

## 4. Stop Conditions

Stop and request human confirmation if:

- any Phase 32-35 focused suite regresses;
- closure E2E requires mock-only provider success;
- public payload leaks local paths/secrets;
- closure reveals a PRD major deviation;
- V2.5 baseline provider-disabled behavior regresses.
