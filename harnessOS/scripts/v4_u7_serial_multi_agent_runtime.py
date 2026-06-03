"""Generate V4-U7 UX-08 provider-backed serial video evidence."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.workflows.v4_u7_real_multi_agent_runtime import (
    U7_EVIDENCE_ROOT,
    render_u7_summary,
    run_serial_video_runtime,
    write_u7_evidence_package,
)


OUTPUT_DIR = U7_EVIDENCE_ROOT / "UX-08-serial-video"


def main() -> int:
    result = run_serial_video_runtime()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if result.get("status") != "completed":
        (OUTPUT_DIR / "runtime-result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        (OUTPUT_DIR / "result-summary.md").write_text(render_u7_summary(result), encoding="utf-8")
        print(json.dumps({"status": "BLOCKED", "output_dir": OUTPUT_DIR.as_posix()}, ensure_ascii=False))
        return 2
    write_u7_evidence_package(result, OUTPUT_DIR)
    print(
        json.dumps(
            {
                "status": "PASS",
                "ux_id": "UX-08",
                "output_dir": OUTPUT_DIR.as_posix(),
                "provider": result["provider"]["provider"],
                "model_ref": result["provider"]["model_ref"],
                "provider_invocation_count": result["provider_invocation_count"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
