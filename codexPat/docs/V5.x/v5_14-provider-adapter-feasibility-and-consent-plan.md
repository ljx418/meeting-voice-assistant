# V5.14 Provider Adapter Feasibility And Consent Plan

status: planned-audit-ready

date: 2026-05-28

## Goal

Evaluate and, only if safe, prototype an explicit-consent external generation adapter for personalized cat assets.

V5.14 must not make provider upload a default behavior.

## Required Consent Model

- User must explicitly choose a provider.
- User must explicitly confirm what will be uploaded.
- User must see cost, privacy, retention, and attribution notes before upload.
- Generated outputs must be downloaded into app-managed storage and validated by V5.8 rules.

## Adapter Boundary

Provider adapter may receive only user-approved generation inputs. It must not receive:

- token or Authorization values from this app.
- workspace path.
- config path.
- shell history.
- Codex payloads.
- terminal payloads.
- raw PetEvent payloads.

## Acceptance

V5.14 can pass only as either:

- feasibility-only with no upload, or
- real provider smoke with explicit consent evidence and imported output validation.

## Evidence

- `docs/V5.x/evidence/v5_14-provider-adapter-smoke-YYYY-MM-DD.md`
- `docs/V5.x/v5_14-final-acceptance-report.md`

## Allowed Claims

```text
V5.14 external generation provider feasibility completed with explicit consent boundary.
```

If real provider smoke passes later:

```text
V5.14 explicit-consent provider adapter smoke passed for tested local personalized asset generation scenario.
```

## Forbidden Claims

```text
automatic photo-to-3D ready
provider integration verified
remote asset loading ready
production signed release ready
```
