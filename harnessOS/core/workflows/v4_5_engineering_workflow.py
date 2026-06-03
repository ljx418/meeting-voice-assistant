"""Deterministic V4.5 long-running engineering workflow helpers."""

from __future__ import annotations

import json
from copy import deepcopy
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


FORBIDDEN_TERMS = (
    "capability_token",
    "subscription_token",
    "Authorization",
    "Bearer",
    "secret",
    "raw_trace_payload",
    "raw_artifact_content",
    "raw_connector_payload",
    "raw prompt",
    "upstream signed URL",
    "/v1/rpc",
    "/v1/events/subscribe",
    "Agent executor ready",
    "controlled executor ready",
    "production-ready external app support",
    "full multi-Agent orchestration ready",
)

STAGES = [
    ("product_planning", "产品规划", "product_plan.md"),
    ("specification", "规格梳理", "specification.md"),
    ("project_blueprint", "项目计划蓝图", "project_blueprint.md"),
    ("architecture_review", "总架构评审", "architecture_review.md"),
    ("substage_plan_audit", "子阶段计划审计", "substage_plan_audit.md"),
    ("substage_architecture_review", "子阶段架构评审", "substage_architecture_review.md"),
    ("implementation_run", "开发实施", "implementation_run.md"),
    ("development_acceptance", "开发验收", "development_acceptance.md"),
    ("code_review", "代码检视", "code_review.md"),
    ("e2e_acceptance", "E2E 验收", "e2e_acceptance.md"),
    ("human_confirmation", "人工确认", "human_confirmation.md"),
]


def build_engineering_spec(task_path: str = "tests/fixtures/v4_5/engineering_task/product_task.md") -> dict[str, Any]:
    return {
        "metadata": {
            "workflow_spec_id": "v45_long_running_engineering_workflow",
            "schema_version": "v4.5",
            "name": "长时工程任务工作流",
            "stage": "V4.5 Long-Running Engineering Workflow MVP",
            "runtime_truth_boundary": "WorkflowSpec is a review artifact and does not replace WorkflowDraft or WorkflowVersion runtime truth.",
            "generated_from": "v4_5_dev_local_engineering_fixture",
        },
        "stages": [
            {"stage_id": stage_id, "name": name, "artifact_name": artifact_name, "quality_gate": stage_id in {"architecture_review", "code_review", "e2e_acceptance", "human_confirmation"}}
            for stage_id, name, artifact_name in STAGES
        ],
        "edges": [
            {"edge_id": f"edge_{STAGES[index][0]}_{STAGES[index + 1][0]}", "from_stage_id": STAGES[index][0], "to_stage_id": STAGES[index + 1][0]}
            for index in range(len(STAGES) - 1)
        ],
        "context_refs": [{"context_ref_id": "engineering_task_path", "value_label": task_path}],
        "governance": {"user_confirmed_required": True, "source_agent_can_mutate": False, "real_code_modification": False},
        "evidence_refs": [{"evidence_ref_id": "runtime_result", "resource_id": "runtime-result.json"}],
    }


def validate_engineering_spec(spec: dict[str, Any]) -> None:
    if set(spec) != {"metadata", "stages", "edges", "context_refs", "governance", "evidence_refs"}:
        raise ValueError("V4.5 engineering spec has unknown or missing fields.")
    assert_no_forbidden_text(spec)
    if [stage["stage_id"] for stage in spec["stages"]] != [stage[0] for stage in STAGES]:
        raise ValueError("V4.5 engineering stages are not in required order.")
    if spec["governance"]["source_agent_can_mutate"] is not False:
        raise ValueError("V4.5 must not allow Agent mutation.")


def run_engineering_workflow(*, task_text: str, task_path: str, scope: dict[str, Any] | None = None) -> dict[str, Any]:
    now = _now_iso()
    workflow_instance_id = f"v45_engineering_instance_{uuid4().hex[:12]}"
    nodes = []
    artifacts = []
    for index, (stage_id, name, artifact_name) in enumerate(STAGES):
        nodes.append({"stage_id": stage_id, "name": name, "status": "completed", "attempts": [_attempt(stage_id, 1, "completed", None, now)], "updated_at": now})
        artifacts.append(_artifact(workflow_instance_id, stage_id, artifact_name, name, task_text, index))
    return {
        "workflow_instance_id": workflow_instance_id,
        "workflow_template_id": "v45_engineering_template",
        "workflow_version_id": "v45_engineering_version_1",
        "status": "completed",
        "backed_by": "v4_5_engineering_workflow_runtime",
        "runtime_mode": "dev_local_deterministic_engineering_runner",
        "scope": scope or {},
        "task_path": task_path,
        "nodes": nodes,
        "artifacts": artifacts,
        "quality_report": _quality_report(artifacts),
        "downstream_stale": [],
        "agent_mutation_allowed": False,
        "user_confirmed_required": True,
        "redaction_status": "redacted",
    }


def rerun_engineering_stage(run: dict[str, Any], stage_id: str) -> dict[str, Any]:
    stage_ids = [stage[0] for stage in STAGES]
    if stage_id not in stage_ids:
        raise ValueError("Unknown V4.5 engineering stage.")
    rerun = deepcopy(run)
    now = _now_iso()
    stale = []
    downstream = False
    for node in rerun["nodes"]:
        attempts = list(node.get("attempts") or [])
        if node["stage_id"] == stage_id:
            attempts.append(_attempt(stage_id, len(attempts) + 1, "completed", None, now))
            node["attempts"] = attempts
            node["status"] = "completed"
            downstream = True
            continue
        if downstream:
            node["status"] = "stale"
            stale.append({"stage_id": node["stage_id"], "reason": f"upstream_rerun:{stage_id}", "requires_user_confirmed_continue": True})
    rerun["status"] = "waiting_user_confirmation"
    rerun["downstream_stale"] = stale
    return rerun


def continue_engineering_downstream(run: dict[str, Any]) -> dict[str, Any]:
    continued = deepcopy(run)
    now = _now_iso()
    for node in continued["nodes"]:
        if node["status"] == "stale":
            attempts = list(node.get("attempts") or [])
            attempts.append(_attempt(node["stage_id"], len(attempts) + 1, "completed", None, now))
            node["attempts"] = attempts
            node["status"] = "completed"
    continued["status"] = "completed"
    continued["downstream_stale"] = []
    continued["quality_report"] = _quality_report(continued.get("artifacts") or [])
    return continued


def attempt_history(run: dict[str, Any]) -> dict[str, Any]:
    return {"workflow_instance_id": run["workflow_instance_id"], "stages": [{"stage_id": node["stage_id"], "status": node["status"], "attempts": node.get("attempts") or []} for node in run["nodes"]], "redaction_status": "redacted"}


def assert_no_forbidden_text(value: Any) -> None:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True) if not isinstance(value, str) else value
    for term in FORBIDDEN_TERMS:
        if term in text:
            raise AssertionError(f"Forbidden term leaked: {term}")


def _artifact(workflow_instance_id: str, stage_id: str, artifact_name: str, name: str, task_text: str, index: int) -> dict[str, Any]:
    content = f"# {name}\n\n## 输入任务\n{_task_title(task_text)}\n\n## 阶段产物\n- 阶段序号：{index + 1}\n- 状态：completed\n- 说明：deterministic dev/local engineering artifact，不执行真实代码修改。\n"
    return {"artifact_id": f"v45_artifact_{uuid4().hex[:12]}", "workflow_instance_id": workflow_instance_id, "stage_id": stage_id, "name": artifact_name, "kind": "markdown", "content": content, "metadata": {"redaction_status": "redacted"}, "redaction_status": "redacted"}


def _quality_report(artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    expected = {stage[2] for stage in STAGES}
    generated = {artifact["name"] for artifact in artifacts}
    return {"status": "passed" if expected.issubset(generated) else "failed", "stage_count": len(STAGES), "artifact_coverage": {"expected": sorted(expected), "generated": sorted(generated), "missing": sorted(expected - generated)}, "risk_flags": ["dev_local_only", "no_real_code_mutation"], "redaction_status": "redacted"}


def _attempt(stage_id: str, attempt: int, status: str, error: str | None, created_at: str) -> dict[str, Any]:
    return {"attempt_id": f"attempt_{stage_id}_{attempt}", "attempt": attempt, "status": status, "error": error, "created_at": created_at}


def _task_title(task_text: str) -> str:
    for line in task_text.splitlines():
        stripped = line.strip("# ").strip()
        if stripped:
            return stripped[:100]
    return "未命名工程任务"


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()

