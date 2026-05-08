#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"
PYTHON_BIN="${PYTHON_BIN:-python3.12}"
WHEEL_DIR="${ROOT_DIR}/env-dist/wheels"

PIP_SOURCE_ARGS=()
if [ -d "${WHEEL_DIR}" ] && [ "$(find "${WHEEL_DIR}" -maxdepth 1 | wc -l | tr -d ' ')" -gt 1 ]; then
  PIP_SOURCE_ARGS=(--no-index --find-links "${WHEEL_DIR}")
fi

if [ ! -x "${VENV_DIR}/bin/python" ]; then
  "${PYTHON_BIN}" -m venv "${VENV_DIR}"
fi

if [ "${BOOTSTRAP_UPGRADE_PIP:-false}" = "true" ]; then
  "${VENV_DIR}/bin/python" -m pip install --upgrade pip
fi

# Install the service/runtime stack first.
"${VENV_DIR}/bin/python" -m pip install \
  "${PIP_SOURCE_ARGS[@]}" \
  "fastapi>=0.100.0" \
  "mcp>=1.0.0" \
  "python-multipart>=0.0.6" \
  "uvicorn>=0.23.0" \
  "websockets>=11.0" \
  "requests>=2.31.0" \
  "pyyaml>=6.0.0" \
  "numpy<2"

# Install the core FunASR runtime without pulling the full optional dependency tree.
"${VENV_DIR}/bin/python" -m pip install --no-deps \
  "${PIP_SOURCE_ARGS[@]}" \
  "torch==2.2.2" \
  "torchaudio==2.2.2" \
  "funasr==1.3.1"

# Install the subset required by AutoModel import and local model execution.
"${VENV_DIR}/bin/python" -m pip install \
  "${PIP_SOURCE_ARGS[@]}" \
  filelock \
  fsspec \
  jinja2 \
  networkx \
  sympy \
  tqdm \
  omegaconf \
  hydra-core \
  kaldiio \
  modelscope \
  oss2 \
  pytorch-wpe \
  scipy \
  sentencepiece \
  soundfile \
  tensorboardX \
  torch-complex \
  editdistance \
  jaconv \
  jamo \
  jieba

echo "voice_service environment is ready at ${VENV_DIR}"
