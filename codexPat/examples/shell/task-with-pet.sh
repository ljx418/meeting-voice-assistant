#!/usr/bin/env bash
set -u

usage() {
  printf 'Usage: %s -- <command> [args...]\n' "$0" >&2
}

if [ "${1:-}" != "--" ]; then
  usage
  exit 2
fi

shift

if [ "$#" -eq 0 ]; then
  usage
  exit 2
fi

notify_pet() {
  petctl notify \
    --source-id script.local \
    --source-kind custom \
    --source-name "Local Script" \
    "$@" >/dev/null 2>&1 || true
}

notify_pet \
  --level running \
  --title "脚本正在执行" \
  --message "$*"

"$@"
status=$?

if [ "$status" -eq 0 ]; then
  notify_pet \
    --level success \
    --title "脚本执行完成" \
    --message "$*" \
    --sound success_chime
else
  notify_pet \
    --level error \
    --title "脚本执行失败" \
    --message "$*" \
    --sound error_chime
fi

exit "$status"

