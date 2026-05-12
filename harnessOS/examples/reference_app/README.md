# V3.5 Reference App

This example proves the dev/local Application Adaptation Layer path:

```text
Reference frontend -> FastAPI BFF template -> harnessOS protocol server
```

It is platform-neutral and does not depend on business reference packs or real
external services.

Included pieces:

- `bff/` contains copyable configuration for `templates/bff/fastapi`.
- `frontend/` contains a minimal React source fixture that calls only `/bff/*`.
- `pack/` contains an instantiated dummy pack manifest.
- `connector/` contains an instantiated dummy connector descriptor.

This is not a production app, a complete AgentTalkWindow, or Workflow Studio.
Production browser integration should keep the BFF between the browser and
harnessOS.

