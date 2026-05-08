#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PID_DIR="${ROOT_DIR}/runtime/pids"

if [ ! -d "${PID_DIR}" ]; then
  echo "No runtime pids found."
  exit 0
fi

for pid_file in "${PID_DIR}"/*.pid; do
  [ -e "${pid_file}" ] || continue
  pid="$(cat "${pid_file}")"
  name="$(basename "${pid_file}" .pid)"
  if kill -0 "${pid}" >/dev/null 2>&1; then
    echo "Stopping ${name} (${pid})"
    kill "${pid}" >/dev/null 2>&1 || true
  fi
  rm -f "${pid_file}"
done
