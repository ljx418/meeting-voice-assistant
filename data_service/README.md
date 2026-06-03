# Local Knowledge Governance Service

An independent MCP-first local knowledge governance service. It turns text, document blocks, meeting transcripts, code analysis artifacts, and local files into traceable knowledge units, entity-relation graphs, readable Wiki artifacts, quality rules, and retrievable context.

## What This Is

This repository is the minimum separable service unit for local knowledge governance. Meeting apps, learning apps, interview tools, code assistants, and agents should call this service through MCP, CLI, or HTTP. They must not read or write the internal workspace layout directly.

Current implementation components:

- `backend/data_service`: current implementation carrier for orchestration, workspace lifecycle, distill, query, quality, CLI, and MCP.
- `backend/app/llmwiki`: readable Wiki solidification engine.
- `backend/app/graphrag`: built-in GraphRAG execution and graph query service.
- `backend/app/api/v1/data_service.py`: HTTP boundary for service calls.
- `frontend`: Knowledge Service Console, built as static assets and served by FastAPI at `/knowledge`.

## Boundaries

Included:

- workspace / tenant management
- source registry and recursive local folder scanning
- multi-format parsing
- external text, document blocks, meeting transcripts, and code analysis artifacts
- normalize, typed distill units, entity and relation extraction
- LLMWiki, GraphRAG, retrieval, Source Trace, quality feedback, correction rules, correction plan, and read-time governance
- MCP server, CLI, HTTP API, and service governance console

Not included:

- meeting recording, ASR, speaker diarization, realtime captions, or meeting UI
- learning platform UI, question-bank product, interview realtime assistant UI, or IDE plugin
- code hosting, full IDE behavior, large static analyzer ownership, or generic Agent workflow orchestration

Meeting scenarios should pass already-transcribed text. Code understanding scenarios should pass structured code analysis outputs such as README, file tree, symbols, imports, call graph, class graph, routes, and dependency graph.

## Workspace Model

`Workspace = Tenant = controlled local knowledge space`.

External contracts should use `workspace_id` as the stable identifier. A workspace can bind a local `root_path`, and the service can recursively scan supported files under that path. `root_path` can be displayed in the console, but it is not the stable API identity.

## Entrypoints

```bash
cd backend
python -m data_service --help
python -m data_service.mcp_stdio
uvicorn app.main:app --reload

cd ../frontend
npm install
npm run build
```

Current compatibility names still use `data_service`. They are the current implementation carrier for the Local Knowledge Governance Service.

The backend package also declares console script entrypoints in `backend/pyproject.toml`:

```text
data-service -> data_service.__main__:main
knowledge -> data_service.__main__:knowledge_main
```

`knowledge quality ...` is the target CLI alias for the quality governance capability group. `data_service quality ...` remains the compatibility CLI.

After `npm run build`, the backend serves the console at:

```text
http://127.0.0.1:8003/knowledge
```

## Current Format Support

Implemented today:

- `json`
- `txt`
- `md`
- `html`
- `csv`
- `pdf`
- `ppt`
- `pptx`

Target near-term expansion:

- `docx`
- `yaml` / `yml`

External adapters can pass already-extracted OCR text, video transcripts, code analysis artifacts, or structured JSON for complex binary and multimodal files.

## Validation

```bash
python3 -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q
cd frontend && npm run build
```

See [docs/V1.x/data_service/README.md](docs/V1.x/data_service/README.md) for the V1.x architecture, roadmap, and acceptance plan.
