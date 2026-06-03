# V2.5 ResearchNotebook Backend Contract and Provider-Specific PRD

> Generated from repository and `/Users/Zhuanz/Desktop/workspace/research-notebook/docs/backend` analysis.
> Business goal: satisfy ResearchNotebook V2.x backend requests without reopening V2.0-V2.4 Project Intelligence scope.

## 1. Positioning

V2.5 is the ResearchNotebook backend contract closure and provider-specific execution phase for `data_service`.

It provides:

- server-side URL SSRF protection with public `block_reason`;
- provider-gated OCR/TTS/PPTX contracts;
- unified ResearchNotebook artifact APIs for audio, slides, mindmap, compare, and stored artifact readback;
- capability manifest flags that frontends can trust;
- a provider-specific expansion path for real OCR, real TTS audio, and real PPTX export when providers are configured.

It does not provide:

- fake media generation when providers are absent;
- a replacement for V2.0-V2.4 codebase/project-intelligence artifacts;
- frontend UI changes in `research-notebook`;
- complex multi-provider orchestration, quota management UI, or SaaS provider administration.

## 1.1 Current Baseline and Target Gap

Current V2.5 is split into two acceptance layers:

- **V2.5A Local Provider Closure**: accepted for the current local environment. It covers URL hardening, provider-disabled fallback, deterministic slides/mindmap/compare artifacts, real Tesseract image OCR, real espeak-ng WAV audio, and local OpenXML PPTX export.
- **V2.5B Full ResearchNotebook Backend PRD Closure**: not yet accepted. It closes the remaining original ResearchNotebook backend PRD gaps: scanned PDF OCR success, provider execution adapter contracts, at least one external TTS provider real run, explicit external OCR provider decision/run, and artifact download contract closure.

Current V2.5 Phase 25-31 baseline is accepted for provider-gated contracts:

- blocked URL payloads include `block_reason`;
- OCR/TTS/PPTX absence is represented as stable capability false or not-ready response;
- slides, mindmap, and compare artifacts can be generated deterministically from source evidence;
- real ResearchNotebook backend Markdown docs pass source import -> artifact generation -> persistence -> readback -> path-redaction acceptance.

Provider-specific V2.5 extends that baseline from:

```text
provider-gated contract implemented
```

to:

```text
provider-backed real artifact generation implemented
```

The remaining product gap after Phase 36 is no longer local provider execution. The remaining gap is full PRD closure beyond the local environment:

- scanned PDF OCR success fixture, not only image OCR;
- external/cloud provider execution contract, not only provider health names;
- at least one external TTS real run when a usable key is available;
- explicit Azure/Google/Minimax OCR decision and acceptance status;
- artifact download semantics closure: safe descriptor only vs real binary stream;
- full PRD coverage matrix against the original ResearchNotebook backend docs.

## 2. Required Scope

### P0 Mandatory

URL imports through `POST /api/workspaces/{workspace_id}/sources` must enforce backend security even if frontend validation is bypassed.

Blocked URL output must include:

- `source.import_state = "blocked"`;
- `source.block_reason`;
- user-facing `warnings`;
- no raw internal exception string;
- no absolute filesystem path.

Supported `block_reason` values:

```text
ssrf
private_ip
timeout
unsupported_content_type
robots_blocked
permission_denied
paywall
```

### P1 Provider-Gated

OCR and TTS are optional. When providers are not configured:

- OCR health returns `available=false`;
- TTS health returns `available=false`;
- source OCR returns stable `OCR_REQUIRED`;
- audio artifact returns `AUDIO_OVERVIEW_NOT_READY`;
- capability flags remain false.

### P2 Artifact Contracts

Slides, mindmap, and compare APIs must provide stable backend contracts. Deterministic evidence-backed outline outputs are valid; unsupported provider-dependent exports must return explicit not-ready errors.

### P3 Provider-Specific Execution

When providers or local exporters are configured, backend APIs must produce real provider-backed artifacts rather than only not-ready contracts.

Required provider-specific capabilities:

- OCR real run for scanned PDF/image sources, producing OCR text, page/block locators, confidence, and evidence references.
- TTS real run for audio overview, producing an audio artifact descriptor, script segments, voice metadata, duration, and evidence references.
- PPTX real export from existing slides artifact, producing a downloadable PPTX artifact descriptor with slide count and source artifact lineage.
- Provider health checks that distinguish no provider, auth failure, timeout, unsupported provider, and available provider.
- Public responses that redact secrets, local paths, raw provider exceptions, and internal endpoints.

## 2.1 Provider Error Contract

This contract is the V2.5 `ProviderError` public contract.

Provider-specific implementation must use stable public error codes:

```text
PROVIDER_NOT_CONFIGURED
PROVIDER_UNSUPPORTED
PROVIDER_MISSING_CREDENTIAL
PROVIDER_AUTH_FAILED
PROVIDER_TIMEOUT
PROVIDER_QUOTA_EXCEEDED
PROVIDER_UNAVAILABLE
PROVIDER_BAD_RESPONSE
PROVIDER_EXECUTION_FAILED
PROVIDER_OUTPUT_INVALID
EXPORTER_NOT_CONFIGURED
EXPORTER_UNSUPPORTED
PDF_RASTERIZER_UNAVAILABLE
```

Public provider failure payloads must follow this shape:

```json
{
  "ok": false,
  "status": "unavailable",
  "capability": "ocr | tts | pptx_export",
  "provider": {
    "name": "tesseract",
    "kind": "local",
    "available": false
  },
  "error": {
    "code": "PROVIDER_TIMEOUT",
    "message": "OCR provider timed out.",
    "retryable": true
  },
  "warnings": [],
  "next_actions": []
}
```

Public payloads must never contain:

```text
api_key
token
secret
Authorization
endpoint secret
raw traceback
absolute local path
provider raw exception body
```

## 2.2 Provider Health Contract

Provider health responses must include:

```json
{
  "available": false,
  "capability": "ocr | tts | pptx_export",
  "provider": {
    "name": "tesseract",
    "kind": "local | external | exporter",
    "version": "optional",
    "model": "optional"
  },
  "latency_ms": null,
  "unsupported_reason": "PROVIDER_NOT_CONFIGURED",
  "error": {
    "code": "PROVIDER_NOT_CONFIGURED",
    "message": "Provider is not configured.",
    "retryable": false
  }
}
```

## 2.3 Binary Artifact Descriptor Contract

Provider-backed binary artifacts must expose descriptors, not local file paths:

```json
{
  "artifact_id": "audio_xxx",
  "artifact_type": "audio | pptx | ocr",
  "status": "ready",
  "binary": {
    "ref": "artifact://workspace_id/audio_xxx",
    "mime_type": "audio/wav",
    "size_bytes": 12345,
    "sha256": "..."
  },
  "download": {
    "descriptor_id": "download_xxx",
    "method": "GET",
    "expires_at": null
  },
  "evidence_refs": []
}
```

Supported binary MIME types:

```text
audio/wav
audio/mpeg
audio/ogg
application/vnd.openxmlformats-officedocument.presentationml.presentation
```

## 2.4 OCR Artifact Contract

OCR artifacts must include text, confidence, and locators:

```json
{
  "artifact_id": "ocr_xxx",
  "artifact_type": "ocr",
  "status": "ready",
  "source_id": "src_xxx",
  "provider": {
    "name": "tesseract",
    "kind": "local",
    "version": "5.x",
    "languages": ["eng"]
  },
  "pages": [
    {
      "page_index": 0,
      "blocks": [
        {
          "block_id": "p0_b0",
          "text": "extracted text",
          "confidence": 0.91,
          "locator": {
            "page": 1,
            "block_index": 0,
            "bbox": [0, 0, 100, 40]
          },
          "evidence_refs": ["source://src_xxx#page=1&block=0"]
        }
      ]
    }
  ],
  "generation": {
    "created_at": "...",
    "duration_ms": 1234
  }
}
```

Image OCR fixture is mandatory. Scanned PDF fixture is accepted only if PDF rasterization is available; otherwise the service must return `PDF_RASTERIZER_UNAVAILABLE` and must not fake OCR success.

## 3. Public APIs

Provider health:

```text
POST /api/ocr/provider/health
POST /api/tts/provider/health
```

Source hardening:

```text
POST /api/workspaces/{workspace_id}/sources
GET  /api/workspaces/{workspace_id}/sources/{source_id}
POST /api/workspaces/{workspace_id}/sources/{source_id}/ocr
GET  /api/workspaces/{workspace_id}/sources/{source_id}/ocr/status
```

Artifact management:

```text
GET    /api/workspaces/{workspace_id}/artifacts
GET    /api/workspaces/{workspace_id}/artifacts/{artifact_id}
DELETE /api/workspaces/{workspace_id}/artifacts/{artifact_id}
GET    /api/workspaces/{workspace_id}/artifacts/{artifact_id}/status
GET    /api/workspaces/{workspace_id}/artifacts/{artifact_id}/download
POST   /api/workspaces/{workspace_id}/artifacts/audio
POST   /api/workspaces/{workspace_id}/artifacts/slides
POST   /api/workspaces/{workspace_id}/artifacts/slides/export
POST   /api/workspaces/{workspace_id}/artifacts/mindmap
POST   /api/workspaces/{workspace_id}/artifacts/compare
```

Provider-specific execution uses the same public APIs. The response changes from unavailable fallback to ready provider-backed artifact only when provider configuration is valid.

## 4. Acceptance Definition

V2.5 is accepted when:

- P0 URL blocked cases return PRD-defined status and `block_reason`;
- blocked URL source can be read back by `GET source`;
- provider-disabled OCR/TTS paths return stable unavailable payloads;
- slides/mindmap/compare artifacts are persisted and read back;
- PPTX export without provider returns `SLIDE_OUTLINE_ONLY`;
- all important generated artifact claims carry evidence or are explicitly unavailable;
- public payloads do not expose local paths;
- focused tests and public surface guard pass.

Provider-specific V2.5 is accepted when:

- provider-disabled fallback tests still pass;
- provider-enabled OCR creates a real OCR artifact from a real scanned fixture;
- provider-enabled TTS creates a real audio artifact from real source evidence;
- PPTX exporter creates a real PPTX artifact from a real slides artifact;
- artifact list/read/status/download descriptors work for generated OCR/audio/PPTX outputs;
- provider failure modes return structured errors without leaking secrets or local paths;
- real fixture E2E and PRD/spec review pass without fatal or major findings.
- provider-specific acceptance matrix is completed for OCR, TTS/audio, and PPTX export.

## 4.1 Provider-Specific Acceptance Matrix

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

## 5. Milestones

| Milestone | Target | Exit Condition |
| --- | --- | --- |
| M0 Baseline Accepted | Phase 25-31 provider-gated contract | Current V2.5 tests and real-input artifact test pass. |
| M1 Provider Safety | Phase 32 config and safety boundary | Health checks and failure errors are structured and redacted. |
| M2 OCR Real Run | Phase 33 OCR provider | Real scanned fixture produces OCR artifact with confidence and locators. |
| M3 TTS Real Run | Phase 34 TTS provider | Real source evidence produces audio artifact descriptor and script. |
| M4 PPTX Real Export | Phase 35 exporter | Real `.pptx` artifact generated from slides outline. |
| M5 Closure | Phase 36 final acceptance | Provider-enabled and provider-disabled suites pass with no major audit gap. |

## 6. V2.5B Full PRD Closure Scope

V2.5B is the remaining work required before the project can claim the original ResearchNotebook backend PRD is fully closed.

It must not reopen V2.0-V2.4 Project Intelligence scope and must not degrade V2.5A local provider closure.

### Phase 37 Pre-Gate: Provider Execution Contract Freeze

Before Phase 37 implementation starts, the project must freeze a minimal execution contract that Phase 37 OCR and Phase 38 provider adapters both use.

Minimum public model names:

```text
ProviderExecutionAdapter
ProviderExecutionRequest
ProviderExecutionResult
ProviderError
ProviderHealth
ProviderCapability
ArtifactWriteResult
```

Minimum result semantics:

```json
{
  "ok": false,
  "capability": "ocr | tts",
  "provider": {
    "name": "minimax",
    "kind": "external",
    "health_known": true,
    "execution_supported": false
  },
  "artifact": null,
  "error": {
    "code": "PROVIDER_UNSUPPORTED",
    "message": "Provider has no execution adapter.",
    "retryable": false
  },
  "redacted": true
}
```

This pre-gate prevents Phase 37 from introducing an OCR-only result shape that would need to be replaced in Phase 38.

### Phase 37: Scanned PDF OCR Success

Target:

- accept a real scanned PDF fixture;
- rasterize pages with a real rasterizer such as Poppler;
- pass rasterized pages to OCR;
- write OCR artifact with pages, text blocks, confidence, locators, and source evidence refs.

Acceptance:

- the scanned PDF fixture must be automatically proven to have no embedded text or text below the acceptance threshold;
- embedded-text PDF is not accepted as scanned-PDF evidence;
- OCR output is provider-generated, not fixture-preloaded text;
- `PDF_RASTERIZER_UNAVAILABLE` remains stable when rasterizer is absent;
- artifact API response, persisted artifact JSON, artifact readback, and artifact status must agree on `artifact_id`, `source_id`, `page_count`, `block_count`, text presence, confidence, locators, evidence refs, and provider metadata;
- rasterizer unavailable is `provider unavailable` or `conditionally accepted contract`; it is not accepted scanned PDF OCR;
- public payload contains no local path, key, endpoint, or traceback.

### Phase 38: Provider Adapter Contract Hardening

Target:

- define a provider execution interface for OCR and TTS;
- separate health-only provider declaration from executable provider support;
- normalize auth failure, timeout, quota, bad response, unsupported provider, and unavailable provider errors;
- keep provider-disabled fallback stable.

Acceptance:

- provider health names do not imply execution support unless an adapter exists;
- unsupported provider execution returns structured `PROVIDER_UNSUPPORTED`;
- cloud provider config can be validated without leaking secrets;
- no provider adapter logic is added to large legacy route files.

### Phase 39: External TTS Provider Real Run

Target:

- run at least one external TTS provider with a real key and real source evidence;
- Minimax may be used if its API supports the required TTS/audio output contract;
- otherwise use one provider from the original PRD set: Azure, Google, or ElevenLabs.

Acceptance:

- generated binary is real audio, not an empty or synthetic placeholder;
- descriptor size, sha256, MIME type, and duration match the stored binary;
- every script segment has evidence refs or is marked unavailable;
- bad key, timeout, and quota failure paths are structured and redacted.

### Phase 40: External OCR Provider Decision and Optional Real Run

Target:

- decide whether Azure, Google, or another OCR provider is part of this V2.5 closure;
- if a provider key is available, run a real OCR fixture;
- if no key is available, mark cloud OCR as explicitly unavailable, not accepted.

Acceptance:

- accepted cloud OCR requires a provider-enabled real fixture;
- unavailable cloud OCR remains capability false or structured unavailable;
- health-only support is not counted as execution acceptance.

### Phase 41: Artifact Download Contract Closure

Target:

- decide whether ResearchNotebook needs safe download descriptors only or direct binary streaming from `data_service`;
- if direct streaming is required, plan and implement a secured download path;
- preserve descriptor semantics for clients that do not need direct streaming.

Acceptance:

- audio and PPTX download payloads never expose absolute paths;
- artifact refs, MIME, size, sha256, and status are consistent;
- unsupported format, missing artifact, expired descriptor, and unauthorized access produce structured errors.

### Phase 42: Full V2.5 PRD Closure Audit

Target:

- trace every original ResearchNotebook backend PRD/API Matrix/Target Architecture item to implementation, accepted fallback, or explicit provider-unavailable status.

Acceptance:

- PRD coverage matrix includes `accepted`, `conditionally accepted`, `provider unavailable`, `not implemented`, and `out of scope`;
- no cloud provider is marked accepted without real provider-enabled evidence;
- no scanned PDF OCR claim is accepted without real scanned PDF fixture evidence;
- no fatal or major open finding remains.
