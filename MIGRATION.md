# Local Migration Guide

This repository is designed for low-cost local deployment on macOS.

## Requirements

- Git
- Git LFS
- Python 3.12
- Node.js 18+
- npm

## Restore on a New Machine

```bash
git clone https://github.com/ljx418/meeting-voice-assistant.git
cd meeting-voice-assistant

git lfs install
git lfs pull

./scripts/bootstrap_all.sh
./scripts/start_local.sh
```

Open:

```text
http://127.0.0.1:5173
```

## Health Checks

```bash
curl -sS http://127.0.0.1:8001/health
curl -sS http://127.0.0.1:8003/api/v1/health
curl -sS http://127.0.0.1:8000/api/v1/health
```

## Stop Services

```bash
./scripts/stop_local.sh
```

## Offline Assets

Python dependencies for `voice_service` are stored in:

```text
voice_service/env-dist/wheels/
```

FunASR models are stored in:

```text
voice_service/models/
```

Both are tracked by Git LFS. Run `git lfs pull` after cloning before starting
the service.
