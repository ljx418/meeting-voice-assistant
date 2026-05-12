# Local Knowledge Governance Service Backend

Standalone backend for MCP-first local knowledge governance.

The backend ingests local files and external payloads, normalizes them, emits traceable distill units, builds readable Wiki artifacts, builds/query graph artifacts through the built-in GraphRAG service, and exposes retrieval and quality governance through MCP, CLI, and HTTP.

## Entrypoints

- HTTP API: `uvicorn app.main:app --reload`
- CLI: `python -m data_service --help`
- Console scripts after packaging: `data-service` and `knowledge`
- MCP stdio: `python -m data_service.mcp_stdio`
- Knowledge Console: build `../frontend`, then open `/knowledge` on the HTTP server

`data_service` is the current compatibility package name and implementation carrier for the Local Knowledge Governance Service.
`knowledge quality ...` is the target quality governance CLI alias and maps to the same `data_service.quality_contract` helpers as `data_service quality ...`.

## Current Format Support

Implemented:

- `json`
- `txt`
- `md`
- `html`
- `csv`
- `pdf`
- `ppt`
- `pptx`

Planned next:

- `docx`
- `yaml` / `yml`

## Workspace Contract

Use `workspace_id` as the external stable ID. A workspace may bind a local `root_path`, but external applications must call MCP / CLI / HTTP instead of reading or writing internal workspace files.

## Environment

- `DATA_SERVICE_WORKSPACE_ROOT`: managed workspace root
- `DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS`: allowed workspace roots
- `DATA_SERVICE_ALLOWED_SOURCE_ROOTS`: allowed source roots
- `DATA_SERVICE_REQUIRE_API_KEY`: default `true`
- `API_KEY`: API key for HTTP access
- `JWT_DEV_MODE`: local dev bypass switch
- `JWT_DEV_BYPASS_AUTH`: local dev bypass auth
