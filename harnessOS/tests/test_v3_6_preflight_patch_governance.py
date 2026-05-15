"""V3.6/V4.0 preflight workflow patch governance tests."""

from __future__ import annotations

import asyncio
import json

from apps.gateway.protocol import RpcRequest
from apps.gateway.service import GatewayService


def _scope() -> dict[str, str]:
    return {"app_id": "meeting", "project_id": "demo", "workspace_id": "local"}


def _template() -> dict:
    return {
        "workflow_template_id": "workflow_patch_governance",
        "name": "Patch Governance",
        "stations": [
            {
                "station_id": "station_a",
                "name": "A",
                "connector_refs": ["safe_connector"],
                "output_contracts": [{"contract_id": "out", "artifact_kind": "generic.report", "direction": "output"}],
            },
            {"station_id": "station_b", "name": "B", "approval_required": True},
        ],
        "edges": [{"edge_id": "a_to_b", "from_station_id": "station_a", "to_station_id": "station_b"}],
        "quality_contracts": [{"contract_id": "q", "rubric_id": "rubric", "threshold": 0.8}],
    }


async def _rpc(service: GatewayService, method: str, params: dict | None = None):
    return await service.handle_rpc(RpcRequest(id=method, method=method, params=params or {}))


async def _create(service: GatewayService) -> dict:
    created = await _rpc(service, "workflow.template.create", {"template": _template(), "scope": _scope()})
    assert created.error is None
    return created.result


async def _propose(service: GatewayService, operation: str, payload: dict):
    proposed = await _rpc(
        service,
        "workflow.patch.propose",
        {
            "workflow_template_id": "workflow_patch_governance",
            "patch": {"operation": operation, "payload": payload, "actor_type": "user", "actor_id": "user_1"},
            "scope": _scope(),
        },
    )
    assert proposed.error is None
    assert proposed.result["patch"]["requires_approval"] is True
    return proposed.result["patch"]


def test_high_risk_patch_apply_is_blocked_without_mutation_and_redacted_trace() -> None:
    async def run() -> None:
        service = GatewayService()
        created = await _create(service)
        before_draft = created["draft"]
        patch = await _propose(service, "update_connector", {"station_id": "station_a", "connector_refs": ["risky_connector"]})

        applied = await _rpc(service, "workflow.patch.apply", {"workflow_patch_id": patch["workflow_patch_id"], "actor_type": "user", "scope": _scope()})
        assert applied.error.code == "WORKFLOW_ACTION_FORBIDDEN"
        assert "connector_change" in applied.error.data["risk_flags"]

        draft = await _rpc(service, "workflow.draft.save", {"workflow_draft_id": before_draft["workflow_draft_id"], "draft": before_draft["draft"], "expected_revision": before_draft["revision"], "scope": _scope()})
        assert draft.error is None
        assert draft.result["draft"]["revision"] == before_draft["revision"] + 1

        stored = await _rpc(service, "workflow.patch.diff", {"workflow_patch_id": patch["workflow_patch_id"], "scope": _scope()})
        assert stored.error is None
        traces = service.trace_store.list_records(app_id="meeting", project_id="demo", workspace_id="local")
        blocked = [record for record in traces if record.get("event_type") == "workflow.patch.apply_blocked"]
        assert blocked
        raw = json.dumps(blocked, ensure_ascii=False)
        for forbidden in ("capability_token", "subscription_token", "Authorization", "Bearer ", "raw_trace_payload", "secret"):
            assert forbidden not in raw

    asyncio.run(run())


def test_all_high_risk_patch_operations_are_rejected_without_approval_flow() -> None:
    async def run() -> None:
        service = GatewayService()
        await _create(service)
        before_approvals = len(service.approval_store.list_approvals(app_id="meeting", project_id="demo", workspace_id="local"))
        cases = [
            ("update_connector", {"station_id": "station_a", "connector_refs": ["changed"]}),
            ("update_approval_point", {"station_id": "station_b", "approval_required": False}),
            ("update_artifact_contract", {"station_id": "station_a", "contract_id": "out", "contract_patch": {"required": False}}),
            ("update_quality_rule", {"quality_contract_id": "q", "quality_patch": {"required": False}}),
        ]
        for operation, payload in cases:
            patch = await _propose(service, operation, payload)
            applied = await _rpc(service, "workflow.patch.apply", {"workflow_patch_id": patch["workflow_patch_id"], "actor_type": "user", "scope": _scope()})
            assert applied.error.code == "WORKFLOW_ACTION_FORBIDDEN"

        approvals = service.approval_store.list_approvals(app_id="meeting", project_id="demo", workspace_id="local")
        assert len(approvals) == before_approvals

    asyncio.run(run())
