#!/usr/bin/env bash
set -u

url="${AGENT_DESKTOP_PET_URL:-http://127.0.0.1:17321}"
token="${AGENT_DESKTOP_PET_TOKEN:-}"
level="${1:-success}"

if [ -z "$token" ]; then
  printf 'AGENT_DESKTOP_PET_TOKEN is required. Token will not be printed.\n' >&2
  exit 2
fi

case "$level" in
  running|success|error|need_input|warning|thinking) ;;
  *)
    printf 'Unsupported level: %s\n' "$level" >&2
    exit 2
    ;;
esac

sound="none"
case "$level" in
  success) sound="success_chime" ;;
  warning) sound="warning_chime" ;;
  error) sound="error_chime" ;;
  need_input) sound="need_input_chime" ;;
esac

curl -sS -X POST "$url/api/events" \
  -H "Authorization: Bearer $token" \
  -H "Content-Type: application/json" \
  -d "{
    \"source\": {\"id\": \"curl.local\", \"kind\": \"custom\", \"name\": \"curl smoke\"},
    \"level\": \"$level\",
    \"title\": \"curl smoke: $level\",
    \"sound\": \"$sound\"
  }"

