# Voice Service Environment Build Notes

Status: baseline packaged on 2026-05-07.

Target baseline:

- Python 3.12 virtual environment at `voice_service/.venv`
- HTTP entrypoint: `python -m funasr_service.cli serve-http`
- MCP entrypoint: `python -m funasr_service.cli serve-mcp`

Current baseline strategy:

- Bootstrap with `scripts/bootstrap_env.sh`
- Install `torch`, `torchaudio`, and `funasr` with `--no-deps`
- Install the subset required by `AutoModel` import and local model execution
- Avoid the `librosa -> numba -> llvmlite` chain unless a future feature proves it is required

Validation evidence:

- `PYTHONPATH=. .venv/bin/python -m funasr_service.cli serve-http --host 127.0.0.1 --port 8015`
- `curl http://127.0.0.1:8015/health` -> `{"status":"ok","service":"funasr"}`
- `from funasr import AutoModel` succeeds under `.venv`

Historical fallback:

- `/usr/bin/python3` on this machine can already start the service and return `{"status":"ok","service":"funasr"}` from `/health`
- This fallback is runtime evidence only and is not the long-term team baseline

Distribution contract:

- Keep reusable artifacts under `env-dist/wheels/`
- Keep the finalized packaged virtual environment under `env-dist/`
- Do not treat the baseline as complete until `.venv` can pass the health check on its own

Packaged artifacts:

- `env-dist/requirements-lock.txt`
- `env-dist/voice-service-venv-py312-20260507.tar.gz`
- `env-dist/wheels/`
- SHA256: `a290d7c43dabb7a2e45d0c663784ecc552ec0d89c4ec964ce86d86bb77507bc6`

Note:

- `env-dist/wheels/` includes some upstream transitive artifacts such as `numba` and `llvmlite`
- The supported bootstrap path is still `scripts/bootstrap_env.sh`, which intentionally avoids installing the `librosa -> numba -> llvmlite` chain for the current service baseline
