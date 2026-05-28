# V5.6 Photo Personalization Security Boundary

status: passed-scoped

date: 2026-05-28

## Sensitive Inputs

- user cat photos.
- photo file names and local paths.
- prompt text that may describe private context.
- external provider tokens.
- generated provider raw payloads.

## Rules

- photos stay local unless a later provider adapter receives explicit user authorization.
- evidence must not contain photo paths or raw prompt/provider payloads.
- generated assets must be imported through V5.8 validation.
- renderer adapters receive only safe action IDs and safe asset metadata.

## Forbidden Claims

```text
photo-to-3D ready
automatic personalized 3D generation ready
provider integration verified
custom asset import ready
production signed release ready
```
