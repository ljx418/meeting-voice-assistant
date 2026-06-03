"""Generate V4-U5E real LLM local document workflow evidence."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.workflows.v4_u5e_local_document_workflow import (  # noqa: E402
    V4U5EWorkflowError,
    load_provider_config,
    run_local_document_workflow,
    write_u5e_evidence_package,
)


OUTPUT_DIR = REPO_ROOT / "docs" / "design" / "V4.x" / "evidence" / "unified-experience" / "UX-12"


def main() -> int:
    config = load_provider_config()
    if not config.api_key:
        print(
            json.dumps(
                {
                    "status": "BLOCKED",
                    "reason": "missing_llm_key",
                    "provider": config.redacted(),
                    "output_dir": str(OUTPUT_DIR.relative_to(REPO_ROOT)),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 2 if config.real_llm_required else 0
    try:
        requested_path = os.getenv("V4_U5E_FOLDER_PATH") or "tests/fixtures/desktop/技术分享"
        result = run_local_document_workflow(
            requested_path=requested_path,
            user_confirmed=True,
            source="mission_console",
            provider_config=config,
        )
        write_u5e_evidence_package(result, OUTPUT_DIR)
        print(
            json.dumps(
                {
                    "status": result["status"],
                    "real_llm_backed": result["real_llm_backed"],
                    "fallback_demo_only": result["fallback_demo_only"],
                    "scanner_actual_read_count": result["quality_report"]["scanner_actual_read_count"],
                    "provider_invocation_count": result["quality_report"]["provider_invocation_count"],
                    "output_dir": str(OUTPUT_DIR.relative_to(REPO_ROOT)),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0 if result["real_llm_backed"] else 2
    except V4U5EWorkflowError as exc:
        print(
            json.dumps(
                {
                    "status": "BLOCKED",
                    "error_code": exc.code,
                    "message": str(exc),
                    "details": exc.details,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
