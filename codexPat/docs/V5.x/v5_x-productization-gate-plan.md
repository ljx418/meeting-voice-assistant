# V5.x Productization Gate Plan

status: planned-audit-ready

date: 2026-05-28

## Goal

Close V5.x productization only after UI import, runtime imported rendering, guided personalization, visual QA, security scan, claim scan, and license attribution are complete.

## Required Gates

- V5.11 import UI accepted.
- V5.12 runtime imported pack rendering accepted.
- V5.13 guided photo-to-asset workflow accepted.
- V5.14 provider adapter remains feasibility-only or passes explicit-consent smoke.
- V5.15 visual quality and action QA accepted.
- License and attribution recorded for all bundled and generated assets.
- Security scan finds no token, Authorization, raw payload, full local path, workspace path, config path, remote asset URL, or executable/script reference.
- Claim scan confirms forbidden claims appear only in forbidden / not-ready contexts.

## Final Allowed Claims

If V5.14 remains feasibility-only:

```text
V5.x personalized cat renderer and asset workflow productization passed for tested local import, runtime rendering, and guided external asset instruction scenarios. External provider generation remains not verified.
```

If V5.14 real provider smoke passes with explicit consent, credential, retention, license, and import-validation evidence:

```text
V5.x personalized cat renderer and asset workflow productization passed for tested local import, runtime rendering, guided external asset instructions, and one explicit-consent provider smoke scenario.
```

This still does not imply production signed release readiness unless release signing, installer, notarization, and distribution gates pass in a separate release track.

## Forbidden Claims Until Separate Evidence

```text
automatic photo-to-3D ready
provider integration verified
remote asset loading ready
asset marketplace ready
production signed release ready
cross-platform ready
```
