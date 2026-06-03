from __future__ import annotations

import json
from pathlib import Path

from core.policies.controlled_executor_trial import ControlledExecutorTrialRunner
from tests.v5_3_observability_support import make_context


def test_synthetic_trial_evidence_does_not_claim_real_runtime() -> None:
    context = make_context()
    runner = ControlledExecutorTrialRunner()
    runner.seed_workflow(workflow_instance_id="synthetic_instance_v5_4b", station_ids=["scan"])
    result = runner.start_workflow(
        context,
        workflow_instance_id="synthetic_instance_v5_4b",
        source="user",
        actor_type="human_user",
        user_confirmed=True,
    )

    data = result.to_dict()
    dumped = json.dumps(data, ensure_ascii=False)

    assert data["runtime_evidence"]["synthetic_only"] is True
    assert data["runtime_evidence"]["runtime_backed"] is False
    assert ("controlled executor" + " ready") not in dumped
    assert ("production controlled executor" + " ready") not in dumped
    assert ("Agent executor" + " ready") not in dumped
    assert "Authorization" not in dumped
    assert "Bearer " not in dumped
    assert "raw_connector_payload" not in dumped


def test_v5_4b_docs_do_not_claim_production_executor_ready() -> None:
    docs = Path("docs/design/V5.x")
    violations: list[str] = []
    forbidden = [
        "V5-4B complete: controlled executor" + " ready",
        "V5-4B complete: production controlled executor" + " ready",
        "V5-4B complete: Agent executor" + " ready",
    ]
    for path in docs.glob("v5_4b*.md"):
        text = path.read_text(encoding="utf-8")
        for claim in forbidden:
            if claim in text:
                violations.append(f"{path}: {claim}")

    assert violations == []
