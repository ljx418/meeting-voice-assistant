# V2.5 Full ResearchNotebook Backend PRD Closure Plan

> Generated from ResearchNotebook backend PRD/API/architecture review.
> This plan continues after V2.5A local provider closure.
> Business code is not changed by this document.

## 1. Current Status

V2.5A is accepted for the current local environment:

- URL SSRF protection and public `block_reason`;
- provider-disabled OCR/TTS/PPTX fallback;
- deterministic slides, mindmap, and compare artifacts from real ResearchNotebook Markdown docs;
- local Tesseract image OCR;
- local espeak-ng WAV audio;
- local OpenXML PPTX package generation.

V2.5A is not the full original ResearchNotebook backend PRD closure. The remaining work is V2.5B.

V2.5B progress after Phase 39:

- Phase 37 Pre-Gate accepted the shared provider execution contract.
- Phase 37 accepted local scanned PDF OCR with Tesseract + `pdftoppm`.
- Phase 38 accepted the provider health vs execution adapter boundary.
- Phase 39 accepted external TTS for the configured Minimax provider only.
- Azure, Google, and ElevenLabs TTS remain unaccepted.
- Cloud OCR is explicitly `provider unavailable` for V2.5 unless a real cloud OCR provider is later selected and tested.
- Artifact download uses descriptor-only as the selected V2.5 contract; direct binary streaming is out of scope for V2.5.

## 2. V2.5B Objective

V2.5B closes the remaining original backend PRD items that cannot be honestly claimed after Phase 36:

1. scanned PDF OCR success;
2. executable provider adapter contract;
3. external TTS provider real run where a usable provider is available;
4. external OCR provider decision and optional real run;
5. artifact download contract closure;
6. final PRD coverage matrix.

## 3. Phase Plan

| Phase | Name | Goal | Primary Output |
| --- | --- | --- | --- |
| Phase 37 Pre-Gate | Provider Execution Contract Freeze | Freeze shared provider execution and artifact write result schemas. | Minimal contract referenced by Phase 37-42 |
| Phase 37 | Scanned PDF OCR Success | Prove real scanned PDF OCR through rasterizer + OCR. | OCR artifact from scanned PDF fixture |
| Phase 38 | Provider Adapter Contract Hardening | Separate provider health names from executable support. | Adapter registry and error contract tests |
| Phase 39 | External TTS Provider Real Run | Accept one real external TTS provider if available. | External audio artifact or explicit unavailable status |
| Phase 40 | External OCR Provider Decision | Record cloud OCR as unavailable unless a real provider is selected and tested. | Provider decision record and optional fixture result |
| Phase 41 | Artifact Download Contract Closure | Verify descriptor-only as the V2.5 contract. | Download contract tests and API note |
| Phase 42 | Full PRD Closure Audit | Trace every original PRD/API/architecture item. | Coverage matrix and closure audit |

## 4. Detailed Design

### Phase 37 Pre-Gate: Provider Execution Contract Freeze

Design:

- Freeze `ProviderExecutionAdapter`, `ProviderExecutionRequest`, `ProviderExecutionResult`, `ProviderError`, `ProviderHealth`, `ProviderCapability`, and `ArtifactWriteResult`.
- The result shape must represent `ok`, `capability`, `provider.name`, `provider.kind`, `provider.health_known`, `provider.execution_supported`, `artifact`, `error`, and `redacted`.
- A known provider with health support but no execution adapter must return `PROVIDER_UNSUPPORTED`.
- Phase 37 OCR, Phase 39 TTS, and Phase 40 OCR provider work must reuse this contract.

Implementation areas:

- provider model and adapter docs;
- provider execution tests;
- phase-specific plan templates.

### Phase 37: Scanned PDF OCR Success

Design:

- Use a real scanned PDF fixture with no embedded text.
- Add an automatic embedded-text guard before OCR acceptance.
- Rasterize with Poppler or equivalent local rasterizer.
- Reuse the Tesseract OCR artifact writer.
- Preserve `PDF_RASTERIZER_UNAVAILABLE` when rasterizer is missing.
- Verify API response, persisted artifact JSON, readback payload, and status payload agree on key fields.

Implementation areas:

- `backend/data_service/research_notebook/providers/ocr_tesseract.py`
- `backend/data_service/research_notebook/artifacts/ocr_artifacts.py`
- OCR tests and fixtures

### Phase 38: Provider Adapter Contract Hardening

Design:

- Introduce an execution adapter contract distinct from provider health.
- Provider health may know `azure`, `google`, `elevenlabs`, or `minimax`, but execution support requires an adapter.
- Unsupported executable path returns `PROVIDER_UNSUPPORTED`.
- Simulated failure modes remain available for deterministic tests.

Implementation areas:

- `backend/data_service/research_notebook/providers/`
- provider health/error tests

### Phase 39: External TTS Provider Real Run

Design:

- Prefer a provider for which the user can supply a real key and that returns audio bytes.
- Minimax is a candidate only if its available endpoint satisfies the TTS artifact contract.
- Otherwise use Azure, Google, or ElevenLabs from the original PRD.
- The same evidence-backed script segments must feed local and external TTS.
- Write a selected provider decision record before claiming acceptance.

Implementation areas:

- TTS provider adapter module
- artifact binary store
- external-provider guarded tests

### Phase 40: External OCR Provider Decision

Design:

- Document the OCR provider decision even if no cloud provider is implemented.
- Treat Minimax OCR as a candidate only after confirming an actual OCR-capable endpoint and response schema.
- The current V2.5 decision selects no cloud OCR provider and marks cloud OCR as `provider unavailable`.
- If key/API is later approved and available, run a real provider fixture before changing the decision.
- If not, keep cloud OCR as `provider unavailable`, not accepted.
- Store the decision record with candidates, selected provider, decision, reason, evidence refs, and unsupported providers.
- Preserve local Tesseract image and scanned PDF OCR as accepted regressions.

Implementation areas:

- OCR provider adapter module if selected
- PRD coverage matrix

### Phase 41: Artifact Download Contract Closure

Design:

- The selected V2.5 backend public contract is safe descriptor only.
- Direct binary streaming is out of scope for V2.5 and must not be claimed as implemented.
- If direct stream is required in a later version, define route behavior, auth, MIME, error shape, and redaction.
- Future direct stream design must explicitly cover `content-type`, `content-length`, `content-disposition`, range support yes/no, expiry semantics, and missing/unauthorized/expired errors.
- Descriptor-only closure must prove audio/PPTX descriptors match actual binaries by `mime_type`, `size_bytes`, `sha256`, and status.

Implementation areas:

- `backend/app/api/v1/research_notebook.py`
- artifact binary store and download descriptor tests

### Phase 42: Full PRD Closure Audit

Design:

- Produce a trace matrix against:
  - `/Users/Zhuanz/Desktop/workspace/research-notebook/docs/backend/V2_BACKEND_SERVICE_PRD.md`
  - `/Users/Zhuanz/Desktop/workspace/research-notebook/docs/backend/V2_BACKEND_API_MATRIX.md`
  - `/Users/Zhuanz/Desktop/workspace/research-notebook/docs/backend/V2_TARGET_ARCHITECTURE.md`
- Mark each item as `accepted`, `conditionally accepted`, `provider unavailable`, `not implemented`, or `out of scope`.
- Required matrix fields: PRD item id/API row/architecture item, capability area, endpoint or artifact, provider dependency, implementation status, acceptance status, evidence, fallback behavior, public security check result, open question, and owner.

## 5. Required Gates

Each phase must pass:

- phase-specific tests;
- provider-disabled regression;
- V2.5A local provider regression;
- Phase 36 provider closure regression;
- V2.5 backend contract regression;
- real-input artifact regression;
- artifact disk inspection where artifacts are generated;
- public payload redaction;
- PRD/spec review;
- false-acceptance review.
- provider acceptance matrix update.

Stop and ask for human review if:

- cloud provider credentials are required but unavailable;
- provider API capability does not match the PRD contract;
- a test tries to fake provider success;
- the implementation would expose absolute paths or secrets;
- the direct download contract requires a product decision.
