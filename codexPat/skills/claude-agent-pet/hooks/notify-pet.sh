#!/usr/bin/env bash
set -u

event="${1:-notification}"
script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
root="$(CDPATH= cd -- "$script_dir/../../.." && pwd)"
petctl_js="$root/packages/petctl/dist/cli.js"

if [ ! -f "$petctl_js" ]; then
  exit 0
fi

level="need_input"
title="Claude Code needs attention"
sound="need_input_chime"
cooldown_key="need_input"
cooldown_seconds=8

case "$event" in
  notification)
    level="need_input"
    title="Claude Code needs attention"
    sound="need_input_chime"
    cooldown_key="notification_need_input"
    ;;
  error)
    level="error"
    title="Claude Code hook reported an error"
    sound="error_chime"
    cooldown_key="hook_error"
    ;;
  *)
    exit 0
    ;;
esac

now="$(date +%s)"
stamp="/tmp/agent-desktop-pet-claude-hook-${cooldown_key}.stamp"
last="0"

if [ -f "$stamp" ]; then
  last="$(cat "$stamp" 2>/dev/null || printf '0')"
fi

case "$last" in
  ''|*[!0-9]*) last="0" ;;
esac

elapsed=$((now - last))
if [ "$elapsed" -lt "$cooldown_seconds" ]; then
  exit 0
fi

sent="0"

if node "$petctl_js" notify \
  --source-id claude-code.local \
  --source-kind claude_code \
  --source-name "Claude Code" \
  --level "$level" \
  --title "$title" \
  --sound "$sound" \
  >/dev/null 2>&1; then
  sent="1"
fi

if [ "$sent" != "1" ] && command -v curl >/dev/null 2>&1; then
  token="${AGENT_DESKTOP_PET_TOKEN:-}"
  if [ -z "$token" ]; then
    token="$(node -e 'const fs=require("fs"); const os=require("os"); const path=require("path"); const p=path.join(os.homedir(),"Library/Application Support/com.agentdesktoppet.desktop/api-token.json"); try { process.stdout.write(JSON.parse(fs.readFileSync(p,"utf8")).token || ""); } catch { process.exit(0); }' 2>/dev/null || true)"
  fi

  if [ -n "$token" ]; then
    payload="{\"source\":{\"id\":\"claude-code.local\",\"kind\":\"claude_code\",\"name\":\"Claude Code\"},\"level\":\"$level\",\"title\":\"$title\",\"sound\":\"$sound\"}"
    if curl -fsS \
      -H "Authorization: Bearer $token" \
      -H "Content-Type: application/json" \
      --data "$payload" \
      http://127.0.0.1:17321/api/events \
      >/dev/null 2>&1; then
      sent="1"
    fi
  fi
fi

if [ "$sent" = "1" ]; then
  printf '%s' "$now" > "$stamp" 2>/dev/null || true
fi

exit 0
