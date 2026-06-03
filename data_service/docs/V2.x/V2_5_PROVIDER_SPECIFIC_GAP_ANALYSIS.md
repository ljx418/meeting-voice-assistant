# V2.5 Provider-Specific Gap Analysis

## 1. Baseline

Current V2.5 Phase 25-31 is accepted for provider-gated backend contracts:

- URL SSRF hardening returns source-shaped `block_reason` payloads.
- OCR/TTS/PPTX absence returns stable unavailable responses.
- Slides, mindmap, and compare artifacts persist deterministic evidence-backed outputs.
- Real ResearchNotebook backend Markdown docs pass source import, artifact generation, persistence, readback, and path-redaction acceptance.

Phase 36 later accepted V2.5A for the current local provider environment:

- local Tesseract image OCR;
- local espeak-ng WAV audio;
- local OpenXML PPTX export;
- provider-disabled fallback.

V2.5A still does not claim:

- cloud OCR provider execution;
- advanced PPTX visual fidelity;
- direct binary streaming if a future PRD/API decision reopens streaming beyond the selected V2.5 descriptor-only contract.

V2.5B status after Phase 39:

- local scanned PDF OCR is accepted with Tesseract + `pdftoppm`;
- provider health vs execution boundary is accepted;
- external TTS is accepted for configured Minimax only;
- Azure, Google, and ElevenLabs TTS are not accepted;
- cloud OCR is explicitly `provider unavailable` for V2.5 after Phase 40 decision;
- download direct stream is out of scope for V2.5 after Phase 41 descriptor-only decision.

## 2. Target

Provider-specific V2.5A targeted real local provider-backed artifact generation:

- OCR provider processes scanned PDF/image fixtures and produces OCR artifacts.
- TTS provider produces audio overview artifacts from evidence-backed scripts.
- PPTX exporter turns slides artifacts into real PPTX outputs.
- Provider failure modes are structured, redacted, and testable.
- Provider-disabled fallback remains stable.

V2.5B targets full ResearchNotebook backend PRD closure:

- scanned PDF OCR success, not only image OCR;
- executable provider adapter contracts, not only health names;
- one external TTS provider real run where a usable key/API is available;
- explicit external OCR provider decision and optional real run;
- download contract closure;
- full PRD coverage matrix.

## 3. Gap Matrix

| Gap | Current State | Target State | Phase |
| --- | --- | --- | --- |
| Provider config safety | Env-driven provider presence checks only. | Normalized config, health probes, redacted errors, timeout/auth/quota states. | Phase 32 |
| OCR execution | `OCR_REQUIRED` fallback when provider absent. | Real OCR artifact with pages, text blocks, locators, confidence, evidence refs. | Phase 33 |
| TTS execution | `AUDIO_OVERVIEW_NOT_READY` fallback when provider absent. | Real audio artifact descriptor with script segments, voice metadata, duration, evidence refs. | Phase 34 |
| PPTX export | `SLIDE_OUTLINE_ONLY` fallback when exporter absent. | Real PPTX artifact descriptor and safe download descriptor. | Phase 35 |
| Binary artifact storage | JSON artifact contracts only. | Service-owned binary storage with public `artifact://` refs and no path leaks. | Phase 34-35 |
| Provider failure handling | Basic unsupported reasons. | Structured public errors for auth failure, timeout, quota, unsupported provider, provider unavailable. | Phase 32-36 |
| Provider error schema | No unified provider error payload. | Stable Provider Error Contract and Health Contract. | Phase 32 |
| Binary descriptor integrity | JSON artifact contracts only. | `mime_type`, `size_bytes`, `sha256`, safe download descriptor. | Phase 34-35 |
| OCR fixture specificity | No real OCR fixture. | Image fixture mandatory; scanned PDF requires rasterizer or `PDF_RASTERIZER_UNAVAILABLE`. | Phase 33 |
| TTS fake artifact risk | Audio fallback only. | Real binary size/duration/MIME/descriptor checks; script-only cannot be audio-ready. | Phase 34 |
| PPTX fake export risk | PPTX fallback only. | OpenXML zip validation and slide XML count checks. | Phase 35 |
| Real fixture acceptance | Real Markdown docs for slides/mindmap/compare only. | Real OCR fixture, real TTS fixture, real PPTX fixture. | Phase 33-36 |
| False acceptance guard | Provider-disabled contracts accepted. | Provider-backed claims require provider-enabled real fixture tests. | Phase 36 |
| Scanned PDF success | Accepted with local Tesseract + `pdftoppm`. | Keep regression green; do not use embedded-text PDF as evidence. | Phase 37 accepted |
| Health vs execution ambiguity | Accepted provider execution boundary. | Keep negative `PROVIDER_UNSUPPORTED` tests green. | Phase 38 accepted |
| External TTS | Accepted for configured Minimax only. | Keep Minimax regression and local fallback green; other providers remain unaccepted. | Phase 39 accepted |
| External OCR | Tesseract local image/scanned-PDF OCR accepted; no cloud OCR provider selected. | Cloud OCR remains `provider unavailable` unless a real provider-enabled fixture is later run. | Phase 40 |
| Download semantics | Safe descriptors exist. | Descriptor-only is the accepted V2.5 contract after focused descriptor verification. Direct stream is out of scope. | Phase 41 |
| Full PRD closure | Phase 36 accepted only local environment. | Original ResearchNotebook backend PRD coverage matrix is complete. | Phase 42 |
| Provider execution contract | OCR/TTS provider paths can evolve separately. | Minimal shared `ProviderExecutionResult` and `ArtifactWriteResult` freeze before Phase 37. | Phase 37 Pre-Gate |
| Binary integrity consistency | Audio/PPTX checks exist in local closure. | All provider-backed artifacts use common JSON/binary/sha256/size/mime/status/ref checks. | Phase 37-42 |
| Provider matrix drift | Matrix finalized at closure. | Matrix is updated after every phase. | Phase 37-42 |

## 4. Architecture Gap

Current architecture:

```text
HTTP API -> Provider Health Gates -> Fallback Artifact Contracts
```

Target architecture:

```text
HTTP API
  -> Provider Config + Safety Boundary
  -> OCR/TTS/PPTX Adapter
  -> Operation Status
  -> Artifact Store
  -> Public Read/List/Download Descriptor
  -> Evidence and Redaction Checks
```

## 5. Acceptance Gap

Current acceptance covers:

- real blocked URL guard inputs;
- real ResearchNotebook Markdown docs for deterministic artifacts;
- provider-disabled fallback behavior.

Remaining missing acceptance:

- cloud OCR provider decision or real run;
- exporter-enabled PPTX real export;
- provider auth failure, timeout, quota, and unsupported provider scenarios;
- binary artifact descriptor disk inspection;
- provider-enabled no-path/no-secret public payload checks.
- provider-specific acceptance matrix across no provider, unsupported provider, missing key, auth failure, timeout, quota, success, redaction, disk inspection, and download descriptor.
- explicit cloud OCR provider decision;
- descriptor-only download contract closure;
- full PRD coverage matrix.

## 6. Required Provider-Specific Contracts

Phase 32 must define and protect:

- Provider Error Contract.
- Provider Health Contract.
- Redaction checker for provider health, provider errors, artifact metadata, generated script/text, and binary descriptors.
- Binary Artifact Descriptor Contract.
- Provider-Specific Acceptance Matrix.

Phase 33-35 must prove:

- OCR real output is not embedded PDF text or preloaded fixture text.
- Audio output is not an empty or fake binary.
- PPTX output is a valid OpenXML package, not a renamed JSON artifact.

## 7. Stop Conditions

Stop and require human review if:

- implementation attempts to claim real provider success without provider-enabled real fixture evidence;
- public payload exposes API key, provider secret, endpoint secret, local filesystem path, or raw provider traceback;
- fallback behavior regresses when providers are absent;
- implementation generates fake OCR/audio/PPTX artifacts to satisfy tests;
- provider-specific logic is added into existing large `data_service.py` core paths rather than focused modules.
- provider health support is treated as provider execution support;
- cloud providers are marked accepted without provider-enabled fixture evidence;
- scanned PDF OCR is marked accepted using embedded text or image-only OCR evidence;
- descriptor-only download is claimed as direct binary streaming without product and API contract closure.
- Phase 37 starts without freezing the shared provider execution result schema;
- `research_notebook_artifacts.py` becomes the primary home for new external provider SDK logic;
- provider raw response bodies are not covered by redaction tests;
- a skipped provider-enabled test is counted as accepted.

## 8. V2.5B Full PRD Closure Matrix

| Original PRD Area | V2.5A Status | V2.5B Required Closure |
| --- | --- | --- |
| URL SSRF + `block_reason` | accepted | keep regression tests passing |
| OCR image source | accepted with Tesseract | keep regression tests passing |
| Scanned PDF OCR | accepted with local Tesseract + `pdftoppm` | keep regression passing |
| OCR cloud provider | provider unavailable | Phase 40 provider decision record |
| TTS local audio | accepted with espeak-ng | keep regression tests passing |
| TTS cloud provider | accepted for configured Minimax only | keep Minimax regression passing; other providers unaccepted |
| PPTX export | accepted as local OpenXML package | keep integrity tests passing; visual fidelity remains out unless specified |
| Audio/PPTX download | descriptor-only accepted; direct stream out of scope | Phase 41 descriptor contract audit |
| Mindmap artifact | accepted deterministic artifact | keep real-doc regression passing |
| Compare artifact | accepted deterministic artifact | keep real-doc regression passing |
| Full PRD traceability | not complete | Phase 42 coverage matrix |

## 9. Required Phase 42 Coverage Matrix Fields

Every row must include:

```text
prd_item_id_or_api_row
architecture_item
capability_area
endpoint_or_artifact
provider_dependency
implementation_status
acceptance_status
evidence
fallback_behavior
public_security_check_result
open_question
owner
```
