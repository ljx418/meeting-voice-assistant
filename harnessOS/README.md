# harnessOS

Multi-functional AI framework based on Deep Agents/LangGraph.

## Features

- **Meeting Assistant**: Voice meeting transcription and analysis
- **Interview Coach**: Interview preparation and coaching
- **Knowledge Base**: Graph-based knowledge management with GraphRAG
- **Video Production**: Media orchestration and rendering

## Architecture

Built on Deep Agents/LangGraph with a modular agent system:

```
┌─────────────────────────────────────────────────────┐
│                    API Gateway                       │
│              (FastAPI - apps/api/)                   │
├─────────────────────────────────────────────────────┤
│              Orchestration Layer                     │
│    (Intent Router, Workflow Dispatcher)              │
├─────────────────────────────────────────────────────┤
│               Agent Kernel (Deep Agents)             │
│   Lead Orchestrator │ Meeting Analyst │ Interview   │
│   KB Curator │ Media Orchestrator                    │
├─────────────────────────────────────────────────────┤
│                 Core Services                        │
│   (Memory, Tools, Execution, Workspace)              │
└─────────────────────────────────────────────────────┘
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your API keys

# Run the API server. Use 8010 if 8000 is already occupied.
python3 main.py --port 8010 --no-reload

# Headless CLI
python3 -m cli.main run "你好"

# HTTP run
curl -X POST http://localhost:8010/v1/runs \
  -H 'Content-Type: application/json' \
  -d '{"input":"你好","close_session":true}'

# JSON-RPC
curl -X POST http://localhost:8010/v1/rpc \
  -H 'Content-Type: application/json' \
  -d '{"id":"req_1","method":"health.ping","params":{}}'

# stdio JSONL
python3 -m apps.gateway.stdio_server
```

If startup reports that a port is in use, inspect it with:

```bash
lsof -nP -iTCP:8000 -sTCP:LISTEN
```

## Project Structure

```
harnessOS/
├── apps/
│   └── api/                  # FastAPI application
│       └── routers/         # API route modules
├── core/
│   ├── agents/              # Core agent implementations
│   ├── config/              # Configuration management
│   ├── orchestration/       # Intent routing, workflow dispatch
│   ├── schemas/             # Unified message schemas
│   └── tools/               # Tool definitions
├── execution/               # Execution environment
├── devplane/                # Developer control plane
└── main.py                  # Entry point
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health | Health check |
| POST | /v1/runs | Run one turn and return JSON |
| POST | /v1/runs/stream | Run one turn and stream SSE events |
| POST | /v1/rpc | Gateway JSON-RPC style protocol |
| GET | /v1/sessions | List persisted sessions |
| GET | /v1/sessions/{id} | Read a session snapshot |
| GET | /v1/sessions/{id}/events | Read session event log |
| GET | /v1/sessions/{id}/transcript | Replay session transcript |
| POST | /api/routing/intent | Route request to agent |
| POST | /api/agents/invoke | Invoke specific agent |
| GET | /api/agents/types | List available agents |

## Development

```bash
# Run in development mode
python3 main.py --port 8010 --no-reload

# Run core protocol tests
PYTHONPYCACHEPREFIX=/tmp/harnessos-pycache python3 -m pytest \
  tests/test_gateway_protocol.py \
  tests/test_gateway_interrupt.py \
  tests/test_api_runs.py \
  tests/test_gateway_stdio.py \
  tests/test_cli_headless.py \
  tests/test_rpc_stdio_compat.py \
  tests/test_model_smoke.py

# Optional real-model smoke test
HARNESSOS_RUN_MODEL_SMOKE=1 python3 -m pytest -m smoke_model
```

## License

MIT
