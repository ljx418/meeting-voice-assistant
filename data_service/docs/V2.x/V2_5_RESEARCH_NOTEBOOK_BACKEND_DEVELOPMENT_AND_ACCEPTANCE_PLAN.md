# V2.5 ResearchNotebook Backend Development and Acceptance Plan

Phase 25-31 are the accepted provider-gated baseline. Phase 32-36 are the accepted V2.5A local provider closure for the current local environment. Phase 37-42 are the V2.5B full ResearchNotebook backend PRD closure plan.

## Phase 25: Documentation Baseline

Deliver:

- V2.5 PRD;
- target architecture;
- development and acceptance plan;
- document audit report.

Acceptance:

- references ResearchNotebook backend V2 docs;
- separates P0 mandatory work from provider-gated optional work;
- no fatal PRD conflict with V2.0-V2.4.

## Phase 26: URL SSRF Hardening

Deliver:

- explicit URL block reason model;
- blocked URL source placeholder;
- source detail readback for URL fields;
- redirect/content-type/timeout status mapping.

Acceptance:

- localhost, private IP, metadata IP, and redirect-to-private return blocked payloads;
- normal URL import remains ready;
- no raw internal path or raw exception leakage.

## Phase 27: Provider Health and Capability Gates

Deliver:

- OCR health;
- TTS health;
- capability manifest provider flags.

Acceptance:

- no provider returns `available=false`;
- OCR/TTS capabilities remain false;
- deterministic outline capabilities are explicit.

## Phase 28: Unified Artifact Store

Deliver:

- list/read/delete/status/download descriptor;
- artifact JSON persistence;
- artifact refs.

Acceptance:

- artifacts are written to disk, read back, listed, and deleted;
- download descriptors do not expose filesystem paths.

## Phase 29: Slides, Mindmap, Compare

Deliver:

- slide outline generation with evidence refs;
- mindmap tree generation with evidence refs;
- compare output with pair evidence;
- PPTX export fallback.

Acceptance:

- insufficient sources returns stable error artifact;
- `SLIDE_OUTLINE_ONLY` is returned when PPTX provider is absent;
- every ready artifact has evidence refs;
- real ResearchNotebook backend docs can be imported and used to generate slides, mindmap, and compare artifacts;
- public artifact responses redact local filesystem paths even when source text contains absolute paths.

## Phase 30: OCR/TTS Operation Contracts

Deliver:

- source OCR create/status endpoints;
- audio artifact provider-gated response.

Acceptance:

- no provider returns `OCR_REQUIRED` and `AUDIO_OVERVIEW_NOT_READY`;
- no fake OCR pages or fake audio file is produced.

## Phase 31: Closure

Deliver:

- focused test run;
- public surface guard;
- PRD/spec review;
- false-acceptance review.

Acceptance:

- focused tests pass;
- existing ResearchNotebook preview/studio tests pass;
- real-input acceptance using `/Users/Zhuanz/Desktop/workspace/research-notebook/docs/backend` passes locally;
- no open fatal or major finding.

## Acceptance Boundary

Automated V2.5 acceptance covers:

- real URL guard inputs for blocked SSRF/private/metadata cases;
- real ResearchNotebook backend Markdown documents as source input for slides/mindmap/compare artifacts;
- provider-disabled OCR/TTS/PPTX fallback contracts.

Automated V2.5 acceptance does not claim:

- real public internet URL fetch success in restricted-network environments;
- real OCR/TTS/PPTX provider execution without configured providers;
- browser frontend integration for ResearchNotebook.

## Phase 32: Provider Config and Safety Boundary

Deliver:

- provider config normalization for OCR, TTS, and PPTX/exporter;
- Provider Error Contract implementation for all provider and exporter failure paths;
- Provider Health Contract implementation for OCR/TTS/PPTX export;
- health payloads that distinguish no provider, missing key, auth failure, timeout, unsupported provider, quota failure, and available provider;
- secret, endpoint, raw exception, and local path redaction for provider outputs;
- timeout and retry metadata in provider health and artifact generation metadata;
- redaction checker for provider health payloads, artifact failure payloads, artifact metadata, and provider raw error bodies.

Acceptance:

- no provider keeps existing `available=false` and fallback behavior;
- invalid provider config returns structured unavailable errors;
- error codes cover `PROVIDER_NOT_CONFIGURED`, `PROVIDER_UNSUPPORTED`, `PROVIDER_MISSING_CREDENTIAL`, `PROVIDER_AUTH_FAILED`, `PROVIDER_TIMEOUT`, `PROVIDER_QUOTA_EXCEEDED`, `PROVIDER_UNAVAILABLE`, `PROVIDER_BAD_RESPONSE`, `PROVIDER_EXECUTION_FAILED`, `PROVIDER_OUTPUT_INVALID`, `EXPORTER_NOT_CONFIGURED`, `EXPORTER_UNSUPPORTED`, and `PDF_RASTERIZER_UNAVAILABLE`;
- health payloads never expose API keys, tokens, local paths, or raw provider tracebacks;
- provider artifact failure payloads never expose API keys, tokens, local paths, raw provider tracebacks, or internal endpoints;
- provider-disabled V2.5 baseline tests still pass;
- public surface guard remains stable except explicitly planned provider-specific additions.

Exit gate:

- config/health/failure-mode tests pass;
- provider-specific acceptance matrix is created and referenced by Phase 33-36 reports;
- document audit confirms no claim of real OCR/TTS/PPTX output before provider-enabled tests exist.

## Phase 33: OCR Provider Real Run

Deliver:

- at least one real OCR provider path, preferably local Tesseract for deterministic local acceptance;
- OCR artifact schema with source id, pages, text blocks, confidence, language, locators, evidence refs, status, and generation metadata;
- source OCR create/status behavior that transitions to ready when OCR succeeds;
- image fixture for mandatory real OCR acceptance;
- scanned PDF fixture path with either rasterizer support or structured `PDF_RASTERIZER_UNAVAILABLE` response.

Acceptance:

- provider disabled returns `OCR_REQUIRED`;
- provider enabled processes a real image fixture and writes an OCR artifact;
- scanned PDF is either processed through real rasterization or returns `PDF_RASTERIZER_UNAVAILABLE`;
- OCR artifact readback contains extracted text, confidence, locator data, and source evidence;
- low-confidence OCR is marked and is not treated as high-confidence text;
- embedded-text PDF is not accepted as scanned-PDF OCR evidence;
- fixture preloaded text is not used as provider output;
- public responses contain no local paths or provider secrets.

Exit gate:

- real OCR fixture E2E passes;
- fallback OCR tests still pass;
- artifact disk inspection and path redaction checks pass.

## Phase 34: TTS / Audio Overview Real Run

Deliver:

- at least one configured TTS provider path;
- audio request builder from source evidence;
- evidence-backed script segments;
- generated audio artifact descriptor with voice metadata, duration, status, and evidence refs;
- safe download descriptor for audio output;
- binary artifact integrity fields: MIME type, size, sha256, duration, and descriptor ref.

Acceptance:

- provider disabled returns `AUDIO_OVERVIEW_NOT_READY`;
- provider enabled creates a real audio artifact from real source evidence;
- binary file exists and size is greater than the minimum threshold chosen in the phase design;
- descriptor `size_bytes` matches the stored binary size;
- duration is greater than zero;
- MIME type and extension match provider output;
- every script segment has evidence refs or is marked unavailable;
- audio descriptor can be listed, read, status-checked, and download-described;
- script-only output must not be marked as audio-ready;
- raw local file paths and provider secrets are not exposed.

Exit gate:

- provider-enabled audio E2E passes with a controlled fixture;
- provider failure-mode tests cover auth failure and timeout;
- V2.5 baseline artifact tests still pass.

## Phase 35: PPTX Export Real Run

Deliver:

- local PPTX exporter, preferably based on existing slides artifact and a local exporter library;
- generated PPTX artifact descriptor with source slides artifact id, slide count, file size, status, and evidence lineage;
- safe download descriptor for PPTX output;
- PPTX package integrity checks using zip/OpenXML structure.

Acceptance:

- exporter disabled returns `SLIDE_OUTLINE_ONLY`;
- exporter enabled creates a real `.pptx` artifact from a real slides artifact;
- `.pptx` file exists, has nonzero size, and opens as a zip package;
- package contains `[Content_Types].xml` and `ppt/presentation.xml`;
- slide XML count equals source outline slide count;
- slide count matches the source outline;
- descriptor `slide_count`, `size_bytes`, and `sha256` match stored output;
- source slides artifact id and evidence lineage are retained;
- generated descriptor is persisted and read back;
- no local path leaks in export or download payloads.

Exit gate:

- PPTX real export E2E passes;
- exporter-disabled fallback tests still pass;
- artifact disk inspection confirms descriptor and binary output are internally stored.

## Phase 36: Provider-Specific Closure

Deliver:

- provider-specific closure audit;
- PRD/spec review;
- false-acceptance review;
- real fixture evidence log;
- drawio/document consistency check;
- provider acceptance matrix with accepted/unaccepted provider statuses.

Acceptance:

- Phase 32-35 tests pass;
- provider-disabled and provider-enabled paths both pass where configured;
- real fixture E2E covers OCR, TTS/audio, and PPTX export;
- public payload redaction checks pass;
- no open fatal or major finding.

Exit gate:

- V2.5 is accepted only for providers actually configured and tested;
- unsupported providers remain explicitly marked as unavailable, not silently accepted;
- `V2_5_TARGET_STATE.drawio`, PRD, architecture, gap analysis, and this plan are mutually consistent.

## Provider-Specific Acceptance Matrix

| Scenario | OCR | TTS | PPTX |
| --- | --- | --- | --- |
| no provider | `OCR_REQUIRED` | `AUDIO_OVERVIEW_NOT_READY` | `SLIDE_OUTLINE_ONLY` |
| unsupported provider | structured unavailable | structured unavailable | structured unavailable |
| missing key | structured unavailable | structured unavailable | n/a for local exporter |
| auth failure | structured error | structured error | n/a for local exporter |
| timeout | structured retryable error | structured retryable error | structured retryable/local failure |
| quota exceeded | structured non-ready error | structured non-ready error | n/a for local exporter |
| provider enabled success | real OCR artifact | real audio artifact | real `.pptx` artifact |
| public redaction | no key/path/traceback | no key/path/traceback | no local path |
| disk inspection | JSON OCR artifact | JSON + binary audio | JSON + binary PPTX |
| download descriptor | optional | safe descriptor | safe descriptor |

## Provider Acceptance Matrix Template

Closure reports must include:

```text
provider_acceptance_matrix:
  OCR:
    provider: tesseract
    enabled: true
    real_fixture_passed: true
    accepted: true
  TTS:
    provider: configured_provider_or_none
    enabled: true_or_false
    real_fixture_passed: true_or_false
    accepted: true_or_false
  PPTX:
    exporter: local_exporter
    enabled: true
    real_fixture_passed: true
    accepted: true
```

## V2.5B Full ResearchNotebook Backend PRD Closure

V2.5B exists because Phase 36 explicitly does not accept cloud OCR/TTS providers, full scanned PDF OCR success, or download streaming semantics. These phases close the remaining original ResearchNotebook backend PRD gaps without weakening V2.5A.

Shared V2.5B rules:

- use real inputs for final acceptance;
- provider-disabled fallback must remain stable;
- no provider success claim is accepted without provider-enabled real fixture evidence;
- no public payload may leak local paths, provider keys, endpoints, or raw tracebacks;
- provider health support is not the same as provider execution support;
- provider acceptance matrix must be updated after every phase, not only at Phase 42;
- V2.5A regression must run in every phase: Phase 36 provider closure, backend contract, and real-input artifact acceptance;
- all phase reports must include a false-acceptance review.

## Phase 37 Pre-Gate: Provider Execution Contract Freeze

Deliver before Phase 37 implementation:

- minimal `ProviderExecutionAdapter`, `ProviderExecutionRequest`, `ProviderExecutionResult`, `ProviderError`, `ProviderHealth`, `ProviderCapability`, and `ArtifactWriteResult` schema;
- documented rule that provider health support is not execution support;
- negative case where a known provider with no execution adapter returns `PROVIDER_UNSUPPORTED`;
- artifact write result contract used by OCR, TTS, and download/readback tests.

Acceptance:

- Phase 37 scanned PDF OCR is required to use this contract;
- contract supports both local and external providers;
- contract has stable fields for `ok`, `capability`, `provider.name`, `provider.kind`, `provider.health_known`, `provider.execution_supported`, `artifact`, `error`, and `redacted`;
- schema is referenced by Phase 37-42 phase documents.

Exit gate:

- no OCR-only private result shape may be introduced in Phase 37.

## Phase 37: Scanned PDF OCR Success

Deliver:

- scanned PDF fixture strategy;
- PDF rasterization path using a real local rasterizer when available;
- scanned PDF OCR artifact path reusing the OCR artifact contract;
- structured fallback when rasterizer is unavailable.

Acceptance:

- real scanned PDF fixture produces OCR pages and blocks;
- PDF text extraction proves the fixture has no embedded text or text below the threshold defined in Phase 37 design;
- OCR output contains confidence, locators, language, evidence refs, and generation metadata;
- embedded-text PDF is not accepted as scanned-PDF OCR evidence;
- rasterizer absence returns `PDF_RASTERIZER_UNAVAILABLE`;
- rasterizer absence is recorded as `provider unavailable` or `conditionally accepted contract`, never as accepted scanned PDF OCR;
- fixture text is not preloaded into artifact output;
- API response, artifact JSON, readback response, and status response agree on key artifact fields;
- OCR disabled fallback still returns `OCR_REQUIRED`;
- public payload redaction passes.

Exit gate:

- Phase 37 focused tests pass;
- artifact disk inspection confirms OCR JSON output;
- automatic embedded-text guard passes;
- PRD/spec review finds no major deviation.

## Phase 38: Provider Adapter Contract Hardening

Deliver:

- executable provider adapter interface for OCR and TTS;
- adapter registry that distinguishes known provider names from implemented execution adapters;
- common provider execution result shape;
- failure-mode matrix for unsupported, missing key, auth failure, timeout, quota, unavailable, bad response, and output invalid.

Acceptance:

- configured provider without adapter returns `PROVIDER_UNSUPPORTED`;
- configured external provider without key returns `PROVIDER_MISSING_CREDENTIAL`;
- simulated auth, timeout, quota, and bad response map to stable public errors;
- health payloads and artifact failure payloads are redacted;
- V2.5A local provider tests still pass.

Exit gate:

- provider adapter contract tests pass;
- no new provider logic is added to `backend/app/api/v1/data_service.py`;
- document audit confirms provider health is not counted as execution support.

## Phase 39: External TTS Provider Real Run

Deliver:

- one external TTS adapter implementation selected from available credentials;
- Minimax is allowed only if it can produce real audio binary output matching the artifact contract;
- evidence-backed script request builder shared with local TTS;
- external provider artifact metadata.
- selected provider decision record with provider name, API family, auth mode, binary output capability, metadata support, and acceptance status.

Acceptance:

- provider-enabled run creates real audio binary from real source evidence;
- descriptor size, sha256, MIME type, and duration match the stored binary;
- every script segment has evidence refs or is marked unavailable;
- bad key, timeout, and quota paths return structured redacted errors;
- local espeak-ng path and provider-disabled fallback still pass.
- if no real external key/API is available, the phase exits as `provider unavailable`, not as accepted.

Exit gate:

- provider-enabled real fixture passes for the selected external TTS provider;
- if no usable key/API exists, Phase 39 exits as `provider unavailable`, not `accepted`.

## Phase 40: External OCR Provider Decision and Optional Real Run

Deliver:

- explicit OCR provider decision record for Azure, Google, Minimax, or no cloud OCR;
- adapter contract integration if a provider is selected;
- real OCR fixture only when a usable OCR provider key/API exists.

Acceptance:

- selected provider with key produces a real OCR artifact, or cloud OCR is explicitly marked unavailable;
- unsupported providers return `PROVIDER_UNSUPPORTED`;
- health-only support is not accepted as execution support;
- scanned PDF local OCR from Phase 37 remains stable.

Exit gate:

- provider decision is documented;
- accepted cloud OCR requires real fixture evidence;
- unavailable providers are listed in the final PRD coverage matrix.
- decision record contains candidates, selected provider, decision, reason, real fixture evidence refs, and unsupported providers.

## Phase 41: Artifact Download Contract Closure

Deliver:

- product decision for descriptor-only download vs direct binary stream;
- if direct stream is required, route design with authorization, artifact existence, MIME, size, and redaction boundaries;
- if descriptor-only remains the contract, explicit PRD alignment note.

Acceptance:

- audio and PPTX download contract is unambiguous;
- if descriptor-only is chosen, documentation explicitly states that `data_service` does not provide binary stream for this phase;
- if direct stream is chosen, route behavior defines authorization, `content-type`, `content-length`, `content-disposition`, range support yes/no, expiry semantics, and structured errors;
- artifact refs, MIME type, size, sha256, status, and source lineage are consistent;
- missing artifact, unsupported format, and unauthorized access return structured errors;
- no download payload exposes local paths.

Exit gate:

- download contract tests pass;
- clients can rely on either descriptor-only or direct stream behavior without guessing.

## Phase 42: Full V2.5 PRD Closure Audit

Deliver:

- full PRD coverage matrix against ResearchNotebook `V2_BACKEND_SERVICE_PRD.md`, `V2_BACKEND_API_MATRIX.md`, and `V2_TARGET_ARCHITECTURE.md`;
- final provider acceptance matrix;
- final false-acceptance audit;
- final document/drawio consistency review.

Acceptance:

- every PRD item is marked `accepted`, `conditionally accepted`, `provider unavailable`, `not implemented`, or `out of scope`;
- every coverage row includes PRD item id/API matrix row/architecture item, capability area, endpoint or artifact, provider dependency, implementation status, acceptance status, evidence, fallback behavior, public security check result, open question, and owner;
- no accepted item depends only on mock data;
- cloud providers are not marked accepted without real provider-enabled evidence;
- scanned PDF OCR is not marked accepted without scanned PDF fixture evidence;
- no fatal or major finding remains open.

Exit gate:

- V2.5 full PRD closure can be claimed only if Phase 42 passes.
