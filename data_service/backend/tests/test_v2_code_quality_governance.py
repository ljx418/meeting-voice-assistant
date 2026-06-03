import asyncio
import hashlib
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from data_service.code_assets.artifacts import (
    agent_context_dir,
    architecture_code_boundaries_path,
    architecture_code_derived_model_path,
    architecture_code_layers_path,
    architecture_code_roles_path,
    architecture_design_code_drift_path,
    architecture_pattern_candidates_path,
    code_graph_dir,
    code_quality_feedback_path,
    code_quality_plan_path,
    code_quality_reviews_path,
    code_quality_rules_path,
    code_quality_summary_path,
    devwiki_dir,
    inventory_capabilities_path,
    inventory_surfaces_path,
    read_jsonl,
    snapshot_dir,
    symbols_path,
)
from data_service.code_assets.architecture.service import ArchitectureService
from data_service.code_assets.context.service import CodebaseAgentContextService
from data_service.code_assets.devwiki.persistence import read_page
from data_service.code_assets.devwiki.service import CodebaseDevWikiService
from data_service.code_assets.graph.persistence import read_edges
from data_service.code_assets.graph.service import CodeGraphService
from data_service.code_assets.inventory import CodebaseInventoryService
from data_service.code_assets.overview import CodebaseOverviewService
from data_service.code_assets.quality.service import CodeQualityService
from data_service.code_assets.registry import CodebaseRegistry
from data_service.code_assets.snapshot import CodebaseSnapshotService
from data_service.code_assets.symbols import CodebaseSymbolIndexService
from data_service.code_assets.trace import CodebaseTraceService


def _create_workspace(client: TestClient, name: str) -> str:
    response = client.post("/api/workspaces", json={"name": name})
    assert response.status_code == 200
    return response.json()["workspace_id"]


def _prepare_real_repo(workspace: Path, workspace_id: str, repo_root: Path):
    registry = CodebaseRegistry(workspace, workspace_id=workspace_id)
    asset = registry.import_codebase(path=str(repo_root))["asset"]
    snapshot_id = CodebaseSnapshotService(workspace, workspace_id=workspace_id).create_snapshot(asset.codebase_id)["snapshot"]["snapshot_id"]
    CodebaseInventoryService(workspace, workspace_id=workspace_id).build_inventory(asset.codebase_id, snapshot_id=snapshot_id)
    CodebaseSymbolIndexService(workspace, workspace_id=workspace_id).build_symbol_index(asset.codebase_id, snapshot_id=snapshot_id)
    CodebaseTraceService(workspace, workspace_id=workspace_id).build_trace(asset.codebase_id, snapshot_id=snapshot_id)
    CodebaseOverviewService(workspace, workspace_id=workspace_id).build_overview(asset.codebase_id, snapshot_id=snapshot_id)
    CodebaseDevWikiService(workspace, workspace_id=workspace_id).build_devwiki(asset.codebase_id, snapshot_id=snapshot_id)
    CodeGraphService(workspace, workspace_id=workspace_id).build_graph(asset.codebase_id, snapshot_id=snapshot_id)
    pack = CodebaseAgentContextService(workspace, workspace_id=workspace_id).create_pack(
        asset.codebase_id,
        snapshot_id=snapshot_id,
        mode="task_context",
        task="新增 code quality governance",
        output_format="json",
    )
    return asset.codebase_id, snapshot_id, pack["pack_id"]


def _v2(payload: dict) -> dict:
    if "v2" in payload:
        return payload["v2"]
    return payload["data"]["v2"]


def _hashes(paths: list[Path]) -> dict[str, str]:
    result = {}
    for path in paths:
        if path.is_file():
            result[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def _source_artifact_paths(workspace: Path, codebase_id: str, snapshot_id: str) -> list[Path]:
    paths = []
    for root in [
        snapshot_dir(workspace, codebase_id, snapshot_id),
        devwiki_dir(workspace, codebase_id),
        code_graph_dir(workspace, codebase_id),
        agent_context_dir(workspace, codebase_id),
    ]:
        if root.exists():
            paths.extend(path for path in root.rglob("*") if path.is_file())
    paths.append(workspace / "assets" / "codebase" / codebase_id / "overview.json")
    return paths


def _assert_no_path_values(payloads: list[dict], *paths: Path):
    raw = json.dumps(payloads, ensure_ascii=False)
    for path in paths:
        assert str(path) not in raw


def test_v2_code_quality_governance_real_repo_http_mcp_cli_and_immutability(tmp_path, monkeypatch, capsys):
    repo_root = Path(__file__).resolve().parents[2]
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo_root))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Phase10 Quality")
    workspace = workspace_root / workspace_id
    codebase_id, snapshot_id, pack_id = _prepare_real_repo(workspace, workspace_id, repo_root)

    devwiki_page = read_page(workspace, codebase_id, "project-overview")
    devwiki_section_id = devwiki_page["sections"][0]["section_id"]
    surface_id = next(row["surface_id"] for row in read_jsonl(inventory_surfaces_path(workspace, codebase_id, snapshot_id)) if row["surface_type"] == "http_api")
    capability_id = read_jsonl(inventory_capabilities_path(workspace, codebase_id, snapshot_id))[0]["capability_id"]
    symbol_id = read_jsonl(symbols_path(workspace, codebase_id, snapshot_id))[0]["symbol_id"]
    graph_edge_id = read_edges(workspace, codebase_id)[0]["edge_id"]
    context_item_id = f"{pack_id}#recommended_next_steps:0"

    before_hashes = _hashes(_source_artifact_paths(workspace, codebase_id, snapshot_id))

    feedback_payloads = [
        {"target_type": "devwiki_page", "target_id": "project-overview", "action": "needs_review", "rule_type": "wrong_summary", "reason": "page summary wording needs verification"},
        {"target_type": "devwiki_section", "target_id": f"project-overview#{devwiki_section_id}", "action": "needs_evidence", "rule_type": "missing_evidence", "reason": "section evidence must remain visible"},
        {"target_type": "public_surface", "target_id": surface_id, "action": "remap_capability", "rule_type": "wrong_capability_mapping", "suggested_value": "project_intelligence"},
        {"target_type": "capability", "target_id": capability_id, "action": "mark_low_confidence", "rule_type": "low_confidence_inference"},
        {"target_type": "code_symbol", "target_id": symbol_id, "action": "review_summary", "rule_type": "doc_code_mismatch"},
        {"target_type": "code_graph_edge", "target_id": graph_edge_id, "action": "review_edge", "rule_type": "wrong_surface_mapping"},
        {"target_type": "agent_context_item", "target_id": context_item_id, "action": "trim_context", "rule_type": "overbroad_agent_context"},
    ]

    first = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/quality/feedback", json=feedback_payloads[0])
    assert first.status_code == 200
    for payload in feedback_payloads[1:]:
        result = CodeQualityService(workspace, workspace_id=workspace_id).record_feedback(codebase_id, **payload)
        assert result["feedback"]["feedback_id"]

    assert code_quality_feedback_path(workspace, codebase_id).exists()
    assert not (workspace / "lifecycle" / "sources.json").exists()

    built = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/quality/rules/build")
    assert built.status_code == 200
    rules = _v2(built.json())["data"]["rules"]
    assert len(rules) >= len(feedback_payloads)
    assert code_quality_rules_path(workspace, codebase_id).exists()

    approved = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/quality/rules/{rules[0]['rule_id']}/review",
        json={"status": "approved", "reviewer": "phase10", "note": "accepted"},
    )
    rejected = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/quality/rules/{rules[1]['rule_id']}/review",
        json={"status": "rejected", "reviewer": "phase10", "note": "not applicable"},
    )
    temporary = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/quality/rules/{rules[2]['rule_id']}/review",
        json={"status": "approved", "reviewer": "phase10", "note": "temporary"},
    )
    revoked = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/quality/rules/{rules[2]['rule_id']}/review",
        json={"status": "revoked", "reviewer": "phase10", "note": "revoked"},
    )
    assert {approved.status_code, rejected.status_code, temporary.status_code, revoked.status_code} == {200}
    assert code_quality_reviews_path(workspace, codebase_id).exists()

    plan_response = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/quality/plan")
    assert plan_response.status_code == 200
    plan = _v2(plan_response.json())["data"]["plan"]
    assert rules[0]["rule_id"] in plan["approved_rule_ids"]
    assert rules[1]["rule_id"] not in plan["approved_rule_ids"]
    assert rules[2]["rule_id"] not in plan["approved_rule_ids"]
    assert plan["impacted_targets"]
    assert plan["read_time_overlays"]
    assert code_quality_plan_path(workspace, codebase_id).exists()

    summary = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/quality/summary")
    assert summary.status_code == 200
    summary_data = _v2(summary.json())["data"]["summary"]
    assert summary_data["feedback_count"] == len(feedback_payloads)
    assert summary_data["approved_rule_count"] == 1
    assert summary_data["rejected_rule_count"] == 1
    assert summary_data["revoked_rule_count"] == 1
    assert code_quality_summary_path(workspace, codebase_id).exists()

    from data_service.__main__ import knowledge_main
    from data_service.mcp_build_runtime import BuildRuntime
    from data_service.mcp_dispatcher import MCPToolDispatcher
    from data_service.mcp_workspace_runtime import WorkspaceRuntime

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_summary = asyncio.run(dispatcher.call_tool("knowledge_code_quality_summary", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    assert _v2(mcp_summary)["data"]["summary"]["active_approved_rule_ids"] == summary_data["active_approved_rule_ids"]

    assert knowledge_main(["code", "quality", "summary", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_summary = json.loads(capsys.readouterr().out)
    assert _v2(cli_summary)["data"]["summary"]["feedback_count"] == len(feedback_payloads)

    after_hashes = _hashes(_source_artifact_paths(workspace, codebase_id, snapshot_id))
    assert before_hashes == after_hashes
    _assert_no_path_values([first.json(), built.json(), approved.json(), plan_response.json(), summary.json(), mcp_summary, cli_summary], repo_root, workspace_root)


def test_v2_code_quality_governance_rejects_unknown_targets_and_types(tmp_path, monkeypatch):
    repo_root = Path(__file__).resolve().parents[2]
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo_root))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Phase10 Quality Errors")
    workspace = workspace_root / workspace_id
    codebase_id, _, _ = _prepare_real_repo(workspace, workspace_id, repo_root)

    unknown_target = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/quality/feedback",
        json={"target_type": "devwiki_page", "target_id": "missing", "action": "needs_review", "rule_type": "wrong_summary"},
    )
    unsupported_target = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/quality/feedback",
        json={"target_type": "not_real", "target_id": "missing", "action": "needs_review", "rule_type": "wrong_summary"},
    )
    unsupported_rule = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/quality/feedback",
        json={"target_type": "devwiki_page", "target_id": "project-overview", "action": "needs_review", "rule_type": "not_real"},
    )

    assert unknown_target.status_code == 404
    assert unknown_target.json()["v2"]["error"]["code"] == "QUALITY_TARGET_NOT_FOUND"
    assert unsupported_target.status_code == 400
    assert unsupported_target.json()["v2"]["error"]["code"] == "UNSUPPORTED_TARGET_TYPE"
    assert unsupported_rule.status_code == 400
    assert unsupported_rule.json()["v2"]["error"]["code"] == "UNSUPPORTED_RULE_TYPE"


def test_v24_architecture_quality_overlay_is_read_time_only(tmp_path, monkeypatch):
    repo_root = Path(__file__).resolve().parents[2]
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo_root))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Phase24 Architecture Quality")
    workspace = workspace_root / workspace_id
    registry = CodebaseRegistry(workspace, workspace_id=workspace_id)
    asset = registry.import_codebase(path=str(repo_root))["asset"]
    snapshot_id = CodebaseSnapshotService(workspace, workspace_id=workspace_id).create_snapshot(asset.codebase_id)["snapshot"]["snapshot_id"]
    CodebaseInventoryService(workspace, workspace_id=workspace_id).build_inventory(asset.codebase_id, snapshot_id=snapshot_id)
    CodebaseSymbolIndexService(workspace, workspace_id=workspace_id).build_symbol_index(asset.codebase_id, snapshot_id=snapshot_id)
    arch_service = ArchitectureService(workspace, workspace_id=workspace_id)
    try:
        arch_service.build_architecture(asset.codebase_id, snapshot_id=snapshot_id)
    except FileNotFoundError:
        pass
    architecture = arch_service.build_code_architecture(asset.codebase_id, snapshot_id=snapshot_id)
    role_id = architecture["roles"][0]["role_id"]
    pattern_id = architecture["patterns"][0]["pattern_id"]
    drift_id = architecture["drift"][0]["finding_id"] if architecture["drift"] else None

    artifact_paths = [
        architecture_code_roles_path(workspace, asset.codebase_id),
        architecture_code_layers_path(workspace, asset.codebase_id),
        architecture_code_boundaries_path(workspace, asset.codebase_id),
        architecture_pattern_candidates_path(workspace, asset.codebase_id),
        architecture_code_derived_model_path(workspace, asset.codebase_id),
        architecture_design_code_drift_path(workspace, asset.codebase_id),
    ]
    before_hashes = _hashes(artifact_paths)

    quality = CodeQualityService(workspace, workspace_id=workspace_id)
    feedbacks = [
        quality.record_feedback(asset.codebase_id, target_type="architecture_role", target_id=role_id, action="review_role", rule_type="low_confidence_inference", reason="role needs governance review"),
        quality.record_feedback(asset.codebase_id, target_type="architecture_pattern", target_id=pattern_id, action="review_pattern", rule_type="doc_code_mismatch", reason="pattern needs design confirmation"),
    ]
    if drift_id:
        feedbacks.append(quality.record_feedback(asset.codebase_id, target_type="architecture_drift_finding", target_id=drift_id, action="review_drift", rule_type="doc_code_mismatch", reason="drift needs human review"))
    rules = quality.build_rules(asset.codebase_id)["rules"]
    for rule in rules:
        quality.review_rule(asset.codebase_id, rule["rule_id"], status="approved", reviewer="phase24", note="accepted")
    plan = quality.build_plan(asset.codebase_id)["plan"]
    assert plan["read_time_overlays"]

    read_payload = arch_service.read_code_architecture(asset.codebase_id)
    overlayed_role = next(role for role in read_payload["roles"] if role["role_id"] == role_id)
    overlayed_pattern = next(pattern for pattern in read_payload["patterns"] if pattern["pattern_id"] == pattern_id)
    assert overlayed_role["applied_rules"]
    assert overlayed_role["governed_by"] == [plan["plan_id"]]
    assert overlayed_pattern["applied_rules"]
    if drift_id:
        overlayed_drift = next(item for item in read_payload["drift"] if item["finding_id"] == drift_id)
        assert overlayed_drift["applied_rules"]

    after_hashes = _hashes(artifact_paths)
    assert before_hashes == after_hashes
    _assert_no_path_values([read_payload, *feedbacks, {"plan": plan}], repo_root, workspace_root)
