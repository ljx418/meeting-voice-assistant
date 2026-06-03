# V2.5 Phase 37 Pre-Gate Development Plan: Provider Execution Contract Freeze

> Generated from V2.5B Full PRD Closure Plan.
> This phase is a gate before scanned PDF OCR implementation.
> Business code changes are limited to provider contract boundaries and tests.

## 1. Objective

Freeze the minimal provider execution contract before Phase 37 scanned PDF OCR starts. This prevents OCR, TTS, and later cloud provider paths from creating incompatible private result shapes.

## 2. Scope

In scope:

- define `ProviderExecutionAdapter`;
- define `ProviderExecutionRequest`;
- define `ProviderExecutionResult`;
- define `ProviderCapability`;
- define `ArtifactWriteResult`;
- expose a deterministic provider execution capability resolver;
- prove that provider health support is not execution support;
- add focused tests for supported local adapters and unsupported health-known providers.

Out of scope:

- scanned PDF OCR implementation;
- cloud OCR implementation;
- external TTS implementation;
- direct binary stream implementation;
- route changes.

## 3. Architecture Rule

Provider health and provider execution are separate.

```text
provider_health(kind)
  -> provider name may be known/configured/available

provider_execution_capability(kind, provider)
  -> execution_supported is true only when a local adapter exists and provider health is available
```

A provider such as `azure`, `google`, `elevenlabs`, or `minimax` may be known by configuration or health metadata, but it must return `PROVIDER_UNSUPPORTED` until an executable adapter is implemented and tested.

## 4. Implementation Plan

1. Add `backend/data_service/research_notebook/providers/adapter_contract.py`.
2. Keep provider contract code independent from HTTP route handlers.
3. Reuse existing `provider_error` and `redact_public_value`.
4. Add a focused test file:
   `backend/tests/test_research_notebook_v25_phase37_pre_gate_provider_contract.py`.
5. Run V2.5A provider closure and backend contract regressions.

## 5. Expected Files

Expected business/test changes:

- `backend/data_service/research_notebook/providers/adapter_contract.py`
- `backend/data_service/research_notebook/providers/__init__.py`
- `backend/tests/test_research_notebook_v25_phase37_pre_gate_provider_contract.py`

Expected documentation changes:

- `docs/V2.x/V2_5_PHASE_37_PRE_GATE_DEVELOPMENT_PLAN.md`
- `docs/V2.x/V2_5_PHASE_37_PRE_GATE_ACCEPTANCE_PLAN.md`
- `docs/V2.x/V2_5_PHASE_37_PRE_GATE_AUDIT_REPORT.md`

## 6. Non-Goals

- Do not modify `backend/app/api/v1/data_service.py`.
- Do not add provider SDK logic to route handlers.
- Do not claim scanned PDF OCR success.
- Do not mark any external provider accepted without a real provider-enabled fixture run.
