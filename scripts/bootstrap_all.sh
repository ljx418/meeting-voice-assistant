#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3.12}"

create_venv() {
  local venv_dir="$1"
  if [ ! -x "${venv_dir}/bin/python" ]; then
    "${PYTHON_BIN}" -m venv "${venv_dir}"
  fi
}

install_python_requirements() {
  local work_dir="$1"
  local venv_dir="$2"
  local requirements="$3"
  create_venv "${venv_dir}"
  if [ "${BOOTSTRAP_UPGRADE_PIP:-false}" = "true" ]; then
    "${venv_dir}/bin/python" -m pip install --upgrade pip
  fi
  "${venv_dir}/bin/python" -m pip install -r "${requirements}"
}

install_node_dependencies() {
  local work_dir="$1"
  local npm_cache="${ROOT_DIR}/.npm-cache"
  if ! command -v npm >/dev/null 2>&1; then
    echo "npm is required for ${work_dir}" >&2
    exit 1
  fi
  mkdir -p "${npm_cache}"
  cd "${work_dir}"
  if [ -f node_modules/.package-lock.json ] && [ "${FORCE_NPM_INSTALL:-false}" != "true" ]; then
    echo "node_modules already exists in ${work_dir}; skipping npm install."
    return 0
  fi
  if [ -f package-lock.json ]; then
    npm ci --cache "${npm_cache}"
  else
    npm install --cache "${npm_cache}"
  fi
}

cd "${ROOT_DIR}"

if ! command -v git-lfs >/dev/null 2>&1 && ! git lfs version >/dev/null 2>&1; then
  echo "git-lfs is required. Install it first, then rerun this script." >&2
  exit 1
fi

git lfs install --local || echo "Warning: could not update local Git LFS config; continuing with git lfs pull." >&2
git lfs pull

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  echo "${PYTHON_BIN} is required. Set PYTHON_BIN=/path/to/python if needed." >&2
  exit 1
fi

cd "${ROOT_DIR}/voice_service"
./scripts/bootstrap_env.sh

install_python_requirements \
  "${ROOT_DIR}/data_service/backend" \
  "${ROOT_DIR}/data_service/backend/.venv" \
  "${ROOT_DIR}/data_service/backend/requirements.txt"

install_python_requirements \
  "${ROOT_DIR}/meeting-voice-assistant/backend" \
  "${ROOT_DIR}/meeting-voice-assistant/backend/venv312" \
  "${ROOT_DIR}/meeting-voice-assistant/backend/requirements.txt"

install_node_dependencies "${ROOT_DIR}/meeting-voice-assistant/frontend"

if [ -f "${ROOT_DIR}/data_service/frontend/package.json" ]; then
  install_node_dependencies "${ROOT_DIR}/data_service/frontend"
fi

echo "All local environments are ready."
