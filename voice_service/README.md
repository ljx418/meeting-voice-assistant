# Voice Service

Standalone FunASR service extracted from `meeting-voice-assistant`.

## Team Baseline

The target team baseline is the local `Python 3.12` virtual environment at `.venv`.

Current policy:

- Primary baseline: `.venv`
- Bootstrap command: `./scripts/bootstrap_env.sh`
- Distribution artifacts: `env-dist/`
- Historical fallback: `/usr/bin/python3` on this machine

The fallback interpreter is only for temporary local recovery. Team members should
restore the packaged `.venv` baseline once it is finalized.

When `env-dist/wheels/` is present, `./scripts/bootstrap_env.sh` prefers those
local artifacts instead of downloading packages again.

## Entrypoints

```bash
./scripts/bootstrap_env.sh
PYTHONPATH=. .venv/bin/python -m funasr_service.cli serve-http --host 0.0.0.0 --port 8001
PYTHONPATH=. .venv/bin/python -m funasr_service.cli health
PYTHONPATH=. .venv/bin/python -m funasr_service.cli recognize /path/to/audio.wav --json
PYTHONPATH=. .venv/bin/python -m funasr_service.cli serve-mcp
```

## Recovery

Once the baseline package is produced, restore from `env-dist/` instead of
rebuilding the environment from scratch.

Current packaged artifacts:

- `env-dist/requirements-lock.txt`
- `env-dist/voice-service-venv-py312-20260507.tar.gz`
- `env-dist/wheels/`

Expected verification:

```bash
curl -sS http://127.0.0.1:8001/health
```

Expected response:

```json
{"status":"ok","service":"funasr"}
```

## HTTP

- `GET /health`
- `POST /recognize` with multipart field `file`
- `WS /ws/realtime`

## MCP

The MCP stdio server keeps the existing tool names:

- `funasr_health`
- `funasr_recognize_file`
- resource `funasr://capabilities`
