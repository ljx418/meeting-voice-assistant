#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
RUNTIME_DIR="${ROOT_DIR}/runtime"
LOG_DIR="${RUNTIME_DIR}/logs"
PID_DIR="${RUNTIME_DIR}/pids"

FUNASR_PORT="${FUNASR_PORT:-8001}"
DATA_SERVICE_PORT="${DATA_SERVICE_PORT:-8003}"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"

mkdir -p "${LOG_DIR}" "${PID_DIR}"

is_healthy() {
  local url="$1"
  curl -fsS "${url}" >/dev/null 2>&1
}

wait_for_service() {
  local url="$1"
  local name="$2"
  local attempt=1
  while [ "${attempt}" -le 60 ]; do
    if is_healthy "${url}"; then
      echo "${name} is ready"
      return 0
    fi
    sleep 1
    attempt=$((attempt + 1))
  done
  echo "${name} did not become ready: ${url}" >&2
  return 1
}

start_process() {
  local name="$1"
  local work_dir="$2"
  local health_url="$3"
  shift 3

  if is_healthy "${health_url}"; then
    echo "${name} is already running"
    return 0
  fi

  echo "Starting ${name}..."
  (
    cd "${work_dir}"
    nohup "$@" >"${LOG_DIR}/${name}.log" 2>&1 &
    echo "$!" >"${PID_DIR}/${name}.pid"
  ) &
  local launcher_pid="$!"
  wait "${launcher_pid}"
  wait_for_service "${health_url}" "${name}"
}

start_process \
  funasr \
  "${ROOT_DIR}/voice_service" \
  "http://127.0.0.1:${FUNASR_PORT}/health" \
  env PYTHONPATH="${ROOT_DIR}/voice_service" \
  "${ROOT_DIR}/voice_service/.venv/bin/python" -m funasr_service.cli serve-http --host 0.0.0.0 --port "${FUNASR_PORT}"

start_process \
  data_service \
  "${ROOT_DIR}/data_service/backend" \
  "http://127.0.0.1:${DATA_SERVICE_PORT}/api/v1/health" \
  env DATA_SERVICE_REQUIRE_API_KEY="${DATA_SERVICE_REQUIRE_API_KEY:-false}" \
  PYTHONPATH="${ROOT_DIR}/data_service/backend" \
  "${ROOT_DIR}/data_service/backend/.venv/bin/python" -m uvicorn app.main:app --host 0.0.0.0 --port "${DATA_SERVICE_PORT}"

start_process \
  backend \
  "${ROOT_DIR}/meeting-voice-assistant/backend" \
  "http://127.0.0.1:${BACKEND_PORT}/api/v1/health" \
  env ASR_ENGINE="${ASR_ENGINE:-funasr}" \
  ASR_FUNASR_ENDPOINT="${ASR_FUNASR_ENDPOINT:-http://127.0.0.1:${FUNASR_PORT}}" \
  KNOWLEDGE_SERVICE_SERVICE_URL="${KNOWLEDGE_SERVICE_SERVICE_URL:-http://127.0.0.1:${DATA_SERVICE_PORT}/api/v1/knowledge}" \
  PYTHONPATH="${ROOT_DIR}/meeting-voice-assistant/backend" \
  "${ROOT_DIR}/meeting-voice-assistant/backend/venv312/bin/python" -m uvicorn app.main:app --host 0.0.0.0 --port "${BACKEND_PORT}"

start_process \
  frontend \
  "${ROOT_DIR}/meeting-voice-assistant/frontend" \
  "http://127.0.0.1:${FRONTEND_PORT}" \
  env VITE_API_BASE_URL="${VITE_API_BASE_URL:-http://127.0.0.1:${BACKEND_PORT}}" \
  VITE_WS_URL="${VITE_WS_URL:-ws://127.0.0.1:${BACKEND_PORT}/api/v1/ws/voice}" \
  npm run dev -- --host 0.0.0.0 --port "${FRONTEND_PORT}"

echo "Local stack is running:"
echo "  frontend:     http://127.0.0.1:${FRONTEND_PORT}"
echo "  backend:      http://127.0.0.1:${BACKEND_PORT}"
echo "  data_service: http://127.0.0.1:${DATA_SERVICE_PORT}"
echo "  funasr:       http://127.0.0.1:${FUNASR_PORT}"
