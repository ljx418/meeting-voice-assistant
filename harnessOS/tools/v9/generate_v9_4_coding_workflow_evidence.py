from __future__ import annotations

import json

from core.workflows.v9_4_coding_workflow_pilot import (
    V94CodingWorkflowConfig,
    run_v9_4_coding_workflow_pilot,
)
from tools.v9.common import V9_ROOT


OUT_DIR = V9_ROOT / "evidence" / "v9-4-coding-workflow-runtime"
SUMMARY_PATH = V9_ROOT / "v9_4_runtime_acceptance_closure.md"


def main() -> int:
    payload = run_v9_4_coding_workflow_pilot(V94CodingWorkflowConfig(evidence_dir=OUT_DIR))
    acceptance = payload["acceptance"]
    SUMMARY_PATH.write_text((OUT_DIR / "result-summary.md").read_text(encoding="utf-8"), encoding="utf-8")
    print(json.dumps({"status": acceptance["status"], "output": str(OUT_DIR / "index.html")}, ensure_ascii=False, indent=2))
    return 0 if acceptance["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
