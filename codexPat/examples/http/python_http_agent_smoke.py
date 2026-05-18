#!/usr/bin/env python3
import json
import os
import sys
import urllib.error
import urllib.request

url = os.environ.get("AGENT_DESKTOP_PET_URL", "http://127.0.0.1:17321").rstrip("/")
token = os.environ.get("AGENT_DESKTOP_PET_TOKEN")
level = sys.argv[1] if len(sys.argv) > 1 else "success"

allowed = {"thinking", "running", "success", "warning", "error", "need_input"}
sounds = {
    "success": "success_chime",
    "warning": "warning_chime",
    "error": "error_chime",
    "need_input": "need_input_chime",
}

if not token:
    print("AGENT_DESKTOP_PET_TOKEN is required. Token will not be printed.", file=sys.stderr)
    sys.exit(2)

if level not in allowed:
    print(f"Unsupported level: {level}", file=sys.stderr)
    sys.exit(2)

payload = {
    "source": {
        "id": "http-python.local",
        "kind": "custom",
        "name": "HTTP Python Smoke",
    },
    "level": level,
    "title": f"Python HTTP smoke: {level}",
    "sound": sounds.get(level, "none"),
}

request = urllib.request.Request(
    f"{url}/api/events",
    data=json.dumps(payload).encode("utf-8"),
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    },
    method="POST",
)

try:
    with urllib.request.urlopen(request, timeout=10) as response:
        print(response.read().decode("utf-8"))
except urllib.error.HTTPError as error:
    print(error.read().decode("utf-8"), file=sys.stderr)
    sys.exit(1)
except OSError as error:
    print(str(error), file=sys.stderr)
    sys.exit(4)

