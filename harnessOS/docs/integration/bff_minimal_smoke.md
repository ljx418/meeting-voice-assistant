# V3.5-D2 Minimal BFF Smoke

Status: V3.5-D2 implementation baseline.

The Minimal BFF Smoke proves that a business backend can call harnessOS through
the Python SDK and proxy EventSource without exposing long-lived harnessOS
tokens to the browser.

## Boundaries

- Platform-neutral defaults use `reference_app/demo/local`.
- This is not a Meeting or Knowledge demo.
- This is not a production BFF and does not implement a user system.
- Browser -> BFF uses demo identity headers / same-origin app context.
- BFF -> harnessOS uses a server-side configured capability token.
- Browser never receives the long-lived harnessOS capability token or upstream subscription token.
- BFF runtime does not import GatewayService, RuntimeAdapter, Core Store, or `apps.gateway.service`.

## Implemented Smoke Surface

- `POST /bff/session/start`
- `POST /bff/turn/start`
- `POST /bff/approval/respond`
- `POST /bff/rpc` constrained to SDK default surface
- `GET /bff/events/subscribe`

Denied by default:

- `meeting.*`
- `knowledge.*`
- `approval.approve`
- `approval.reject`
- `pack.execute_stub`
- `workflow.execute_stub`
- `method.list(include_forbidden=true)`
- `scope_mode=all`

## Exit Statement

V3.5-D2 complete means:

```text
Minimal BFF Smoke proves JSON-RPC and EventSource proxy feasibility
```

If V3.5-0/A/B/C/D/D2 tests are all green:

```text
V3.5-MVP dev/local adaptation layer ready
```

It does not mean production-ready external app support, full BFF template
complete, external app ready, or V3.5 complete.
