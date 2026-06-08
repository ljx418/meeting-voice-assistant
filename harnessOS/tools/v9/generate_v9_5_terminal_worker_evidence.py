from __future__ import annotations

import json

from core.terminal_workers.v9_5_governed_terminal_worker import run_v9_5_governed_terminal_worker


def main() -> int:
    payload = run_v9_5_governed_terminal_worker()
    print(
        json.dumps(
            {
                "status": payload["acceptance"]["status"],
                "output": str(payload["acceptance"].get("dashboard_ref", "docs/design/V9.x/evidence/v9-5-terminal-worker/index.html")),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if payload["acceptance"]["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
