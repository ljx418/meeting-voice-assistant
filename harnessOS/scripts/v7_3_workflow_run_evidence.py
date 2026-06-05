"""Generate V7-3 workflow creation and controlled run evidence."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.product_console.v7_3_workflow_run import DEFAULT_V73_OUTPUT_DIR, V73RunConfig, run_v7_3_workflow  # noqa: E402
from core.workflows.v4_u5e_local_document_workflow import load_provider_config  # noqa: E402


def main() -> int:
    goal = os.getenv("V7_3_GOAL") or "递归总结 tests/fixtures/desktop/技术分享 下的 Markdown 技术文档"
    requested_path = os.getenv("V7_3_FOLDER_PATH") or "tests/fixtures/desktop/技术分享"
    output_dir = Path(os.getenv("V7_3_OUTPUT_DIR") or DEFAULT_V73_OUTPUT_DIR)
    provider_config = load_provider_config()
    result = run_v7_3_workflow(
        V73RunConfig(goal=goal, requested_path=requested_path, user_confirmed=True, output_dir=output_dir),
        provider_config=provider_config,
    )
    acceptance = result["acceptance"]
    print(
        json.dumps(
            {
                "stage_id": "V7-3",
                "status": acceptance["status"],
                "evidence_scope": acceptance["evidence_scope"],
                "runtime_backed": acceptance["runtime_backed"],
                "scanner_actual_read_count": acceptance["scanner_actual_read_count"],
                "provider_invocation_count": acceptance["provider_invocation_count"],
                "fallback_demo_only": acceptance["fallback_demo_only"],
                "output_dir": str(output_dir.relative_to(REPO_ROOT) if output_dir.is_absolute() and output_dir.is_relative_to(REPO_ROOT) else output_dir),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if acceptance["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
