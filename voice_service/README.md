# Voice Service

Standalone FunASR service extracted from `meeting-voice-assistant`.

## Team Baseline

The target team baseline is the local `Python 3.12` virtual environment at `.venv`.

Current policy:

- Primary baseline: `.venv`
- Bootstrap command: `./scripts/bootstrap_env.sh`
- Distribution artifacts: `env-dist/`
- Offline models: `models/`

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

Restore Python dependencies from `env-dist/` and FunASR model weights from
`models/`. Both directories are tracked by Git LFS.

Current packaged artifacts:

- `env-dist/requirements-lock.txt`
- `env-dist/wheels/`
- `models/paraformer-zh`
- `models/fsmn-vad`
- `models/cam++`
- `models/ct-punc`

After cloning, run:

```bash
git lfs pull
./scripts/bootstrap_env.sh
```

The default model configuration points at `models/`, so first recognition does
not need to download model weights from ModelScope.

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
