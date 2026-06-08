from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from tools.v9.common import FORBIDDEN_RAW_TERMS, V9_ROOT, utc_now, write_json


REPORT_PATH = V9_ROOT / "reports" / "v9_1_redaction_scan.json"
SCAN_SUFFIXES = {".md", ".drawio", ".json", ".html", ".txt", ".log"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan V9 docs and fixtures for forbidden raw content terms.")
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args()

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
            lowered = line.lower()
            for term in FORBIDDEN_RAW_TERMS:
                if term.lower() in lowered and not _allowed_raw_term_context(path, line, current_heading):
                    violations.append({"path": str(path), "line": lineno, "term": term, "text": line.strip()})

    report = {
        "schema_version": "v9_1.redaction_scan.v1",
        "stage_id": "V9-1",
        "status": "PASS" if not violations else "FAIL",
        "runtime_evidence": False,
        "created_at": utc_now(),
        "forbidden_terms": list(FORBIDDEN_RAW_TERMS),
        "violations": violations,
        "notes": "Terms are allowed only when defining forbidden fields or negative fixtures.",
    }
    if args.write_report:
        write_json(REPORT_PATH, report)
    print(json.dumps({"status": report["status"], "violations": len(violations)}, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "PASS" else 1


def _allowed_raw_term_context(path: Path, line: str, heading: str) -> bool:
    lower = line.lower()
    heading_lower = heading.lower()
    if "schema-negative" in str(path):
        return True
    if path.name == "v9_chatgpt_external_audit_single_file_pack.md":
        return True
    if lower.strip() in {term.lower() for term in FORBIDDEN_RAW_TERMS} and "persistence model" in heading_lower:
        return True
    if "_in_evidence" in lower or "fixture" in lower:
        return True
    if "_exposed" in lower and "false" in lower:
        return True
    if "_configured" in lower and "true" in lower:
        return True
    return any(
        marker in lower
        for marker in (
            "forbidden",
            "must not",
            "not ",
            "no ",
            "不得",
            "禁止",
            "redaction",
            "raw content",
            "sensitive",
            "not contain",
            "denied",
            "rejected",
            "leakage",
            "scan",
            "negative",
            "appears in evidence",
            "blocks",
            "泄露",
        )
    ) or any(
        marker in heading_lower
        for marker in (
            "redaction",
            "forbidden",
            "forbidden persistence",
            "rejection cases",
            "required negative fixtures",
            "global schema rules",
            "stop",
            "success criteria",
            "validation",
            "scan",
            "contract schema",
        )
    )


def _excluded_scan_path(path: Path) -> bool:
    relative = path.relative_to(V9_ROOT)
    if relative.parts and relative.parts[0] in {"reports", "decisions"}:
        return True
    return path.name == "v9_chatgpt_external_audit_single_file_pack.md"


if __name__ == "__main__":
    raise SystemExit(main())
