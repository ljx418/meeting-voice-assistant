from __future__ import annotations

import json

from core.workflows.v9_3_multi_agent_orchestration_runtime import (
    V93OrchestrationConfig,
    run_v9_3_multi_agent_orchestration,
)
from tools.v9.common import V9_ROOT


OUT_DIR = V9_ROOT / "evidence" / "v9-3-orchestration-runtime"
SUMMARY_PATH = V9_ROOT / "v9_3_runtime_acceptance_closure.md"


def main() -> int:
    payload = run_v9_3_multi_agent_orchestration(V93OrchestrationConfig(evidence_dir=OUT_DIR))
    acceptance = payload["acceptance"]
    SUMMARY_PATH.write_text((OUT_DIR / "result-summary.md").read_text(encoding="utf-8"), encoding="utf-8")
    print(json.dumps({"status": acceptance["status"], "output": str(OUT_DIR / "index.html")}, ensure_ascii=False, indent=2))
    return 0 if acceptance["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
