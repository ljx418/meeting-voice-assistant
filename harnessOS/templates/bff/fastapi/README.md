# harnessOS Full FastAPI BFF Template

V3.5-F provides this copyable FastAPI BFF template for dev/local external app
integration smoke.

This is not a production-ready BFF. It does not implement a complete user
system, OAuth, SSO, or an admin tenant permission console. It does not issue
harnessOS capability tokens and does not expose the server-side harnessOS token
to browsers.

## Boundaries

- Use `templates/bff/fastapi` as the copyable template.
- Keep `templates/bff/fastapi_minimal` as the V3.5-D2 smoke artifact.
- This template does not import or depend on `fastapi_minimal`.
- This template calls harnessOS through `harnessos_client` only.
- Browser event subscriptions must use `/bff/events/subscribe`; `/bff/rpc`
  rejects `events.subscribe` by default to avoid exposing upstream subscription
  tokens.

## Configuration

Copy `.env.example` and provide a server-side harnessOS token:

```bash
HARNESSOS_BASE_URL=http://127.0.0.1:8000
HARNESSOS_CAPABILITY_TOKEN=<server-side-token>
BFF_DEMO_IDENTITY_MODE=true
BFF_ALLOWED_ORIGINS=http://localhost:5173
```

`BFF_DEMO_IDENTITY_MODE` must be explicitly enabled for the sample identity
provider. In normal mode, a missing `HARNESSOS_CAPABILITY_TOKEN` makes proxy
routes unusable.

## Routes

- `POST /bff/sessions`
- `POST /bff/turns`
- `GET /bff/artifacts`
- `POST /bff/artifacts/external`
- `GET /bff/artifacts/{artifact_id}/metadata`
- `GET /bff/artifacts/{artifact_id}/lineage`
- `GET /bff/jobs`
- `GET /bff/jobs/{job_id}`
- `POST /bff/approvals/{approval_id}/respond`
- `GET /bff/packs`
- `GET /bff/packs/{pack_id}`
- `GET /bff/connectors/{connector_id}/health`
- `GET /bff/events/subscribe`
- `POST /bff/rpc` as a constrained escape hatch

Trace routes are intentionally not exposed by default.
