from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from tools.v9.common import ALLOWED_CLAIM_CONTEXT_MARKERS, FORBIDDEN_CLAIM_PATTERN, V9_ROOT, utc_now, write_json


REPORT_PATH = V9_ROOT / "reports" / "v9_1_no_false_green_scan.json"
SCAN_SUFFIXES = {".md", ".drawio", ".json", ".html", ".txt", ".log"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan V9 docs for false-green completion claims.")
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args()

    hits: list[dict[str, Any]] = []
    violations: list[dict[str, Any]] = []
    for path in sorted(V9_ROOT.glob("**/*")):
        if not path.is_file() or path.suffix not in SCAN_SUFFIXES:
            continue
        if _excluded_scan_path(path):
            continue
        current_heading = ""
        for lineno, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
            if line.startswith("#"):
                current_heading = line
            if not FORBIDDEN_CLAIM_PATTERN.search(line):
                continue
            record = {"path": str(path), "line": lineno, "text": line.strip(), "context": current_heading}
            hits.append(record)
            if not _allowed_context(line, current_heading, path):
                violations.append(record)

    report = {
        "schema_version": "v9_1.no_false_green_scan.v1",
        "stage_id": "V9-1",
        "status": "PASS" if not violations else "FAIL",
        "runtime_evidence": False,
        "created_at": utc_now(),
        "allowed_contexts": list(ALLOWED_CLAIM_CONTEXT_MARKERS),
        "hit_count": len(hits),
        "violations": violations,
        "notes": "Forbidden terms are allowed only in guard, stop, audit, boundary or drawio warning contexts.",
    }
    if args.write_report:
        write_json(REPORT_PATH, report)
    print(json.dumps({"status": report["status"], "hit_count": len(hits), "violations": len(violations)}, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "PASS" else 1


def _allowed_context(line: str, heading: str, path: Path) -> bool:
    if path.suffix == ".drawio":
        return any(marker.lower() in line.lower() for marker in ("禁止", "不能", "不得", "not ", "NO-GO", "停止", "warning", "未被升级", "才允许", "ready for review"))
    if path.suffix in {".html", ".txt", ".log"}:
        lowered = line.lower()
        if any(marker in lowered for marker in ("禁止", "不得", "不能", "不是", "不声明", "不证明", "not ", "no-go", "forbidden", "blocked", "false", "ready for review", "reused to claim")):
            return True
    blob = f"{heading}\n{line}"
    return any(marker.lower() in blob.lower() for marker in ALLOWED_CLAIM_CONTEXT_MARKERS)


def _excluded_scan_path(path: Path) -> bool:
    relative = path.relative_to(V9_ROOT)
    if relative.parts and relative.parts[0] in {"reports", "decisions"}:
        return True
    return path.name == "v9_chatgpt_external_audit_single_file_pack.md"


if __name__ == "__main__":
    raise SystemExit(main())
