# V2.5 Full ResearchNotebook Backend PRD Closure Acceptance Plan

> Acceptance plan for V2.5B Phase 37-42.
> This document defines how full PRD closure is verified.

## 1. Acceptance Principle

V2.5B acceptance must distinguish:

- accepted real capability;
- provider-disabled fallback;
- provider unavailable;
- conditionally accepted contract;
- not implemented.

No phase may convert a missing provider or skipped fixture into an accepted provider-backed capability.

## 2. Shared Test Requirements

Every phase must run:

```text
PYTHONPATH=backend python3 -m pytest <phase-focused-tests> -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_backend_contract.py backend/tests/test_research_notebook_v25_real_input_acceptance.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase36_provider_closure.py -q
```

The exact focused test file names are defined during each phase implementation.

Every phase must also run:

```text
git diff --check -- <changed-files>
```

Every phase must update the provider acceptance matrix:

```text
OCR:
  local_image: accepted
  scanned_pdf: accepted | provider unavailable | conditionally accepted contract
  cloud: accepted | provider unavailable | not implemented
TTS:
  local_espeak: accepted
  external: accepted | provider unavailable | not implemented
PPTX:
  local_openxml: accepted
Download:
  descriptor: accepted
  stream: accepted | out_of_scope | not implemented
```

Every phase must keep these regressions green:

- Phase 36 provider closure regression;
- V2.5 backend contract regression;
- real-input artifact regression.

## 3. Phase Acceptance

### Phase 37 Pre-Gate: Provider Execution Contract Freeze

Acceptance checks:

- `ProviderExecutionAdapter`, `ProviderExecutionRequest`, `ProviderExecutionResult`, `ProviderError`, `ProviderHealth`, `ProviderCapability`, and `ArtifactWriteResult` are defined in phase design;
- a known provider with health support but no execution adapter returns `PROVIDER_UNSUPPORTED`;
- Phase 37 uses this result shape for scanned PDF OCR;
- result includes `ok`, `capability`, `provider.name`, `provider.kind`, `provider.health_known`, `provider.execution_supported`, `artifact`, `error`, and `redacted`.

False-green rejection:

- OCR introduces a private OCR-only result shape;
- provider health availability is used as execution availability.

### Phase 37: Scanned PDF OCR Success

Acceptance checks:

- real scanned PDF fixture has no embedded text;
- embedded text is verified automatically with PDF text extraction below the threshold defined in phase design;
- rasterizer is invoked or unavailable is structured;
- OCR artifact contains pages, blocks, text, confidence, locators, evidence refs;
- artifact is persisted and read back;
- API response, artifact JSON, readback payload, and status payload agree on `artifact_id`, `source_id`, page count, block count, text presence, confidence, locator presence, evidence refs, and provider metadata;
- disabled provider still returns `OCR_REQUIRED`;
- public output has no local path or secret.

False-green rejection:

- embedded-text PDF used as scanned OCR proof;
- fixture text copied into artifact without OCR;
- skipped rasterizer test marked accepted.
- rasterizer unavailable marked as accepted scanned PDF OCR.

### Phase 38: Provider Adapter Contract Hardening

Acceptance checks:

- known provider without adapter returns `PROVIDER_UNSUPPORTED`;
- missing external key returns `PROVIDER_MISSING_CREDENTIAL`;
- simulated auth failure, timeout, quota, unavailable, bad response, and invalid output return stable error codes;
- health and execution output are redacted;
- local provider paths still pass.

False-green rejection:

- provider health name counted as executable provider;
- unsupported provider silently falls back to local provider;
- raw exception or endpoint leaks.

### Phase 39: External TTS Provider Real Run

Acceptance checks:

- selected external provider is documented;
- selected provider decision record includes provider name, API endpoint family, auth mode, audio bytes support, metadata support, and acceptance status;
- real provider-enabled fixture produces audio binary;
- binary size, sha256, MIME type, and duration match descriptor;
- script segments have evidence refs;
- bad key and timeout paths are structured;
- local espeak-ng and disabled fallback still pass.

False-green rejection:

- empty or tiny placeholder audio marked ready;
- script-only artifact marked audio-ready;
- provider-disabled path counted as external provider success.

### Phase 40: External OCR Provider Decision and Optional Real Run

Acceptance checks:

- provider decision record exists;
- provider decision record includes candidates, selected provider, decision, reason, real fixture evidence, and unsupported providers;
- accepted provider has a real fixture run;
- unavailable providers are explicit in the coverage matrix;
- scanned PDF local OCR regression passes.

False-green rejection:

- cloud OCR accepted without real key/API run;
- health-only support accepted as OCR execution.

### Phase 41: Artifact Download Contract Closure

Acceptance checks:

- descriptor-only or direct stream behavior is documented;
- descriptor-only acceptance explicitly states `data_service` does not provide direct binary stream in this phase;
- direct stream acceptance defines authorization, `content-type`, `content-length`, `content-disposition`, range support yes/no, expiry semantics, and structured missing/expired/unauthorized errors;
- audio/PPTX refs, MIME type, size, sha256, and status are consistent;
- unsupported format, missing artifact, unauthorized access, and expired descriptor errors are structured;
- public output has no absolute path.

False-green rejection:

- local path returned as download URL;
- descriptor-only behavior claimed as direct streaming without contract update.

### Phase 42: Full PRD Closure Audit

Acceptance checks:

- PRD coverage matrix covers the original ResearchNotebook PRD, API Matrix, and Target Architecture;
- every row has status and evidence;
- every row includes PRD item id/API row/architecture item, capability area, endpoint or artifact, provider dependency, implementation status, acceptance status, evidence, fallback behavior, public security check result, open question, and owner;
- no fatal or major open finding remains;
- drawio, PRD, architecture, gap analysis, and acceptance plan are consistent.

False-green rejection:

- a cloud provider is marked accepted without provider-enabled test evidence;
- scanned PDF OCR is accepted without scanned PDF fixture evidence;
- skipped tests are counted as pass.

## 4. Provider Acceptance Matrix

| Capability | Accepted only if | Unavailable if |
| --- | --- | --- |
| Scanned PDF OCR | real scanned PDF fixture produces OCR artifact | rasterizer/provider missing returns structured unavailable |
| External TTS | real external provider returns valid audio binary | no usable key/API |
| External OCR | real external provider returns valid OCR artifact | no usable key/API or provider not selected |
| Download streaming | direct stream route tested | descriptor-only contract is chosen |

## 5. Exit Criteria

V2.5 full PRD closure passes only when:

- Phase 37-42 either pass or explicitly mark provider-dependent work unavailable;
- no accepted capability relies on mock-only tests;
- no public payload leaks local paths or secrets;
- V2.5A regressions remain green;
- final PRD coverage matrix has no fatal or major open gaps.
