# V2.5 Phase 39 Development Plan: External TTS Provider Real Run

> Generated after Phase 38 provider adapter hardening passed.
> This phase is provider-gated and may require human approval for external network/API use.

## 1. Objective

Accept one real external TTS provider only if a usable provider, key, endpoint, and explicit execution approval are available. Otherwise mark external TTS as `provider unavailable` and keep local espeak-ng plus provider-disabled fallback accepted.

## 2. Scope

In scope:

- write a provider decision record for external TTS;
- evaluate configured candidates without printing secrets;
- implement adapter only for an approved and usable provider;
- validate real audio binary size, duration, MIME type, sha256, download descriptor, and evidence-backed script segments.

Out of scope:

- cloud OCR;
- scanned PDF OCR changes;
- direct binary streaming;
- claiming external TTS accepted without a real provider-enabled run.

## 3. Candidate Providers

Candidates:

- Minimax, only if its API can return real audio bytes compatible with the V2.5 binary artifact contract;
- Azure;
- Google;
- ElevenLabs.

If no candidate is configured or approved, Phase 39 records `provider unavailable`.

Current selected path:

- selected candidate: `minimax`;
- explicit provider selector: `TTS_PROVIDER=minimax`;
- credential lookup order: `TTS_API_KEY`, `MINIMAX_API_KEY`, `DATA_SERVICE_AI_API_KEY`;
- endpoint lookup order: `TTS_ENDPOINT`, `MINIMAX_TTS_ENDPOINT`, `MINIMAX_ENDPOINT`, default `https://api.minimax.io/v1/t2a_v2`;
- model lookup order: `MINIMAX_TTS_MODEL`, `TTS_MODEL`, default `speech-2.8-hd`.

The existing dotenv currently contains `DATA_SERVICE_AI_API_KEY`; it does not define dedicated `TTS_API_KEY` or `MINIMAX_API_KEY`. Therefore Minimax TTS must be explicitly selected and must not auto-enable when `TTS_PROVIDER` is absent.

## 4. High-Risk Gate

External TTS real run may send source-derived script text to a third-party provider and may incur provider cost. Human review is required before any network/API call.

Without approval, implementation must not call external provider APIs.

## 5. Implementation Plan

1. Check environment for candidate provider configuration without logging secrets.
2. Create `research_notebook/provider_decisions/tts_provider_decision.json` during acceptance.
3. If approved and provider is usable, add a focused external TTS adapter module.
4. If not approved or unavailable, add tests proving explicit `provider unavailable` status and no fake audio acceptance.
5. Run V2.5A, Phase 37, and Phase 38 regressions.
