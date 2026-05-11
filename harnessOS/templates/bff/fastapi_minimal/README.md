# Minimal FastAPI BFF Smoke

This directory contains the V3.5-D2 Minimal BFF Smoke template.

It proves Python SDK JSON-RPC proxy and EventSource proxy feasibility. It is
not a production BFF, not a user system, and not a Meeting or Knowledge demo.

Defaults are platform-neutral (`reference_app/demo/local`) and should be
overridden by the consuming business app.

Boundary:

- Browser -> BFF uses demo identity headers or same-origin app context.
- BFF -> harnessOS uses a server-side configured capability token.
- Browser never receives the long-lived harnessOS capability token.
- `/bff/rpc` is constrained to SDK default surface only.
- EventSource proxy uses `events.subscribe` and `/v1/events/subscribe`, not `/v1/runs/stream`.
