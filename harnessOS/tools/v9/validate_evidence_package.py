from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from tools.v9.common import read_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate V9 evidence package acceptance semantics.")
    parser.add_argument("evidence_package", type=Path)
    args = parser.parse_args()

    data = read_json(args.evidence_package)
    result = validate_evidence_package(data)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "PASS" else 1


def validate_evidence_package(data: dict[str, Any]) -> dict[str, Any]:
    failures: list[str] = []
    required = {
        "evidence_package_id",
        "stage_id",
        "status",
        "evidence_scope",
        "runtime_backed",
        "source_document_refs",
        "runtime_artifact_refs",
        "claim_scan_result",
        "redaction_scan_result",
        "forbidden_raw_content_scan_result",
        "drawio_validation_result",
    }
    missing = sorted(required - set(data))
    if missing:
        failures.append(f"missing required fields: {', '.join(missing)}")
    if data.get("stage_id") == "V9-8" and data.get("runtime_backed") is not True:
        failures.append("V9-8 cannot pass with runtime_backed=false")
    if data.get("runtime_backed") is True and not data.get("runtime_artifact_refs"):
        failures.append("runtime_backed evidence requires runtime_artifact_refs")
    for field in ("claim_scan_result", "redaction_scan_result", "forbidden_raw_content_scan_result", "drawio_validation_result"):
        if data.get(field) == "FAIL":
            failures.append(f"{field}=FAIL")
    return {"status": "PASS" if not failures else "FAIL", "failures": failures}


if __name__ == "__main__":
    raise SystemExit(main())

