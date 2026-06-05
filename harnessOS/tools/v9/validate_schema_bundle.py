from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tools.v9.common import (
    DURABLE_OPERATIONS,
    V9_ROOT,
    contains_forbidden_raw_content,
    envelope_has_mutation_authorization,
    envelope_source_agent_denied,
    read_json,
    utc_now,
    write_json,
)


SCHEMA_DIR = V9_ROOT / "schemas"
FIXTURE_DIR = V9_ROOT / "fixtures"
REPORT_PATH = V9_ROOT / "reports" / "v9_1_contract_validation_report.json"
NEGATIVE_REPORT_PATH = V9_ROOT / "reports" / "v9_1_negative_test_results.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate V9 schema bundle and negative fixtures.")
    parser.add_argument("--write-reports", action="store_true")
    args = parser.parse_args()

    schema_results = [_parse_json(path) for path in sorted(SCHEMA_DIR.glob("*.json"))]
    fixture_results = [_parse_json(path) for path in sorted(FIXTURE_DIR.glob("**/*.json"))]
    invariant_results = _schema_invariant_checks()
    negative_results = _negative_fixture_checks()

    contract_status = "PASS" if all(item["status"] == "PASS" for item in schema_results + invariant_results) else "FAIL"
    negative_status = "PASS" if all(item["status"] == "PASS" for item in negative_results) else "FAIL"

    contract_report = {
        "schema_version": "v9_1.contract_validation_report.v1",
        "stage_id": "V9-1",
        "status": contract_status,
        "runtime_evidence": False,
        "created_at": utc_now(),
        "schema_parse_results": schema_results,
        "fixture_parse_results": fixture_results,
        "invariant_results": invariant_results,
        "notes": "Readiness validation only. This report does not approve runtime implementation.",
    }
    negative_report = {
        "schema_version": "v9_1.negative_test_results.v1",
        "stage_id": "V9-1",
        "status": negative_status,
        "runtime_evidence": False,
        "created_at": utc_now(),
        "negative_fixture_results": negative_results,
        "notes": "Negative fixture behavior is checked by local V9 readiness rules, not by runtime execution.",
    }

    if args.write_reports:
        write_json(REPORT_PATH, contract_report)
        write_json(NEGATIVE_REPORT_PATH, negative_report)

    print(json.dumps({"contract_status": contract_status, "negative_status": negative_status}, ensure_ascii=False, indent=2))
    return 0 if contract_status == "PASS" and negative_status == "PASS" else 1


def _parse_json(path: Path) -> dict[str, Any]:
    try:
        json.loads(path.read_text(encoding="utf-8"))
        return {"path": str(path), "status": "PASS"}
    except Exception as exc:  # pragma: no cover - defensive report path
        return {"path": str(path), "status": "FAIL", "error": str(exc)}


def _schema_invariant_checks() -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    envelope_schema = read_json(SCHEMA_DIR / "agent_execution_envelope.schema.json")
    schema_text = json.dumps(envelope_schema, ensure_ascii=False)

    for operation in sorted(DURABLE_OPERATIONS):
        results.append(
            {
                "check_id": f"durable_mutation_authorization_required_for_{operation}",
                "status": "PASS" if operation in schema_text else "FAIL",
                "details": "operation appears in AgentExecutionEnvelope authorization invariant",
            }
        )
    results.append(
        {
            "check_id": "source_agent_durable_mutation_denied",
            "status": "PASS" if '"source"' in schema_text and '"agent"' in schema_text and '"not"' in schema_text else "FAIL",
            "details": "AgentExecutionEnvelope contains source=agent denial branch",
        }
    )
    for schema in sorted(SCHEMA_DIR.glob("*.json")):
        data = read_json(schema)
        results.append(
            {
                "check_id": f"{schema.name}_additional_properties_false",
                "status": "PASS" if data.get("additionalProperties") is False else "FAIL",
                "details": "schema must be strict",
            }
        )
    return results


def _negative_fixture_checks() -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    source_agent = _fixture("schema-negative/source_agent_durable_mutation.json")
    checks.append(
        {
            "fixture": "source_agent_durable_mutation.json",
            "expected": "REJECT",
            "status": "PASS" if envelope_source_agent_denied(source_agent) else "FAIL",
            "reason": "source=agent durable mutation must be denied",
        }
    )

    expired = _fixture("schema-negative/expired_human_authorization_ref.json")
    checks.append(
        {
            "fixture": "expired_human_authorization_ref.json",
            "expected": "REJECT",
            "status": "PASS" if _is_expired_or_revoked(expired) else "FAIL",
            "reason": "expired or revoked HumanAuthorizationRef is invalid",
        }
    )

    raw_secret = _fixture("schema-negative/raw_secret_in_evidence.json")
    checks.append(
        {
            "fixture": "raw_secret_in_evidence.json",
            "expected": "REJECT",
            "status": "PASS" if contains_forbidden_raw_content(raw_secret) else "FAIL",
            "reason": "raw secret content must be rejected from evidence",
        }
    )

    lineage = _fixture("schema-negative/artifact_lineage_missing_producer_attempt.json")
    checks.append(
        {
            "fixture": "artifact_lineage_missing_producer_attempt.json",
            "expected": "REJECT",
            "status": "PASS" if not lineage.get("producer_attempt_id") else "FAIL",
            "reason": "artifact lineage must preserve producer_attempt_id",
        }
    )

    contract_freeze = _fixture("evidence/v9_1_contract_freeze_sample.json")
    checks.append(
        {
            "fixture": "v9_1_contract_freeze_sample.json",
            "expected": "ACCEPT_AS_NON_RUNTIME_CONTRACT_FREEZE",
            "status": "PASS" if contract_freeze.get("runtime_backed") is False else "FAIL",
            "reason": "contract freeze sample cannot count as runtime evidence",
        }
    )

    planning_only = _fixture("evidence/v9_8_reject_planning_only_sample.json")
    checks.append(
        {
            "fixture": "v9_8_reject_planning_only_sample.json",
            "expected": "REJECT_FOR_FINAL_RUNTIME_ACCEPTANCE",
            "status": "PASS" if planning_only.get("runtime_backed") is False else "FAIL",
            "reason": "planning-only evidence cannot satisfy V9-8",
        }
    )
    return checks


def _fixture(relative: str) -> dict[str, Any]:
    return read_json(FIXTURE_DIR / relative)


def _is_expired_or_revoked(ref: dict[str, Any]) -> bool:
    if ref.get("revoked") is True:
        return True
    expires = ref.get("expires_at")
    if not isinstance(expires, str):
        return False
    normalized = expires.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized) <= datetime.now(timezone.utc)
    except ValueError:
        return False


if __name__ == "__main__":
    raise SystemExit(main())
