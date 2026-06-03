# V2.5 Phase 40 Development Plan: External OCR Provider Decision

> Generated after Phase 39 Minimax TTS acceptance.
> This phase decides cloud OCR scope and optionally runs a real external OCR provider.

## 1. Objective

Close the cloud OCR gap honestly. Phase 40 must either accept a real external OCR provider with provider-enabled evidence or record `provider unavailable` / `out of scope` with a durable decision record.

## 2. Scope

In scope:

- create an OCR provider decision record;
- evaluate candidates: Minimax, Azure, Google, none;
- verify whether any candidate exposes an OCR-capable endpoint compatible with V2.5 OCR artifact schema;
- optionally implement and run a provider adapter if a usable OCR provider is confirmed and approved;
- keep local image OCR and local scanned PDF OCR regressions green.

Out of scope:

- treating Minimax TTS support as Minimax OCR support;
- accepting cloud OCR without real provider-enabled evidence;
- changing local Tesseract OCR artifact schema.

## 3. Design

Decision record path:

```text
docs/V2.x/V2_5_PHASE_40_OCR_PROVIDER_DECISION.json
```

Required fields:

```text
capability
phase
candidates
selected_provider
decision
reason
provider_endpoint_family
auth_mode
expected_response_schema
real_fixture_evidence
unsupported_providers
acceptance_status
security_notes
```

If a provider is selected, it must reuse `ProviderExecutionResult` and write the standard OCR artifact fields: pages, blocks, confidence, locators, evidence refs, provider metadata, and generation metadata.

## 4. Implementation Plan

1. Inspect original ResearchNotebook PRD/API matrix for cloud OCR requirements.
2. Check configured OCR provider variables without printing secrets.
3. Produce provider decision record.
4. If provider is unavailable, add focused tests proving explicit unavailable status and no fake accepted OCR.
5. If provider is available and approved, implement adapter and real fixture E2E.
6. Run Phase 37, 38, 39, V2.5A, and real-input regressions.

## 5. Stop Conditions

Stop for human review if:

- cloud OCR provider credentials are required but not configured;
- provider API requires uploading private source content outside approved scope;
- provider API cannot produce OCR blocks/locators/confidence compatible with artifact schema;
- implementation would fake OCR output or copy fixture text into artifact.
