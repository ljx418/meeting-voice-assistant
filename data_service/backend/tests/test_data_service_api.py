import json
import sys
import time
import tomllib
from pathlib import Path

from fastapi.testclient import TestClient

from app.config import config
from app.main import app
from data_service import DataService

V15_DOCS_ROOT = Path("docs/V1.5")


def _assert_no_public_path_keys(payload):
    path_keys = {"path", "paths", "workspace_path", "original_path", "bound_paths", "roots", "files", "artifacts"}

    def walk(value, *, in_debug=False):
        if isinstance(value, dict):
            for key, item in value.items():
                if in_debug:
                    continue
                assert key not in path_keys
                walk(item, in_debug=key == "debug_paths")
        elif isinstance(value, list):
            for item in value:
                walk(item, in_debug=in_debug)

    walk(payload)


def _cli_quality_subcommands():
    from data_service.__main__ import _build_parser

    parser = _build_parser()
    subparser_action = next(action for action in parser._actions if getattr(action, "choices", None))
    quality_parser = subparser_action.choices["quality"]
    quality_action = next(action for action in quality_parser._actions if getattr(action, "choices", None))
    return set(quality_action.choices)


def test_knowledge_api_rejects_workspace_outside_allowed_roots(tmp_path, monkeypatch):
    allowed = tmp_path / "allowed"
    blocked = tmp_path / "blocked" / "workspace"
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(allowed))

    client = TestClient(app)
    response = client.post("/api/v1/knowledge/summary", json={"workspace": str(blocked)})

    assert response.status_code == 400
    assert "outside allowed roots" in response.json()["detail"]


def test_knowledge_api_rejects_source_path_outside_allowed_roots(tmp_path, monkeypatch):
    root = tmp_path / "knowledge"
    workspace = root / "workspace"
    source_dir = root / "row"
    outside = tmp_path / "outside" / "secret.md"
    source_dir.mkdir(parents=True)
    outside.parent.mkdir(parents=True)
    outside.write_text("# Secret\n", encoding="utf-8")
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_SOURCE_ROOTS", str(source_dir))

    client = TestClient(app)
    response = client.post(
        "/api/v1/knowledge/ingest",
        json={"workspace": str(workspace), "paths": [str(outside)]},
    )

    assert response.status_code == 400
    assert "Source path is outside allowed roots" in response.json()["detail"]


def test_knowledge_api_can_require_api_key(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    monkeypatch.delenv("DATA_SERVICE_REQUIRE_API_KEY", raising=False)
    monkeypatch.setattr(config.api, "api_key", "test-key")
    monkeypatch.setattr(config.jwt, "dev_mode", False)
    monkeypatch.setattr(config.jwt, "dev_bypass_auth", False)

    client = TestClient(app)
    unauthorized = client.post("/api/v1/knowledge/summary", json={"workspace": str(workspace)})
    authorized = client.post(
        "/api/v1/knowledge/summary",
        json={"workspace": str(workspace)},
        headers={"X-API-Key": "test-key"},
    )

    assert unauthorized.status_code == 401
    assert authorized.status_code == 200


def test_phaseg3_distill_contract_shared_by_http_and_cli(tmp_path, monkeypatch, capsys):
    from data_service.__main__ import main as cli_main

    workspace = tmp_path / "workspace"
    doc = tmp_path / "phaseg3-distill.md"
    doc.write_text("# PhaseG3 Distill\n\nPhaseG3 aligns HTTP and CLI distill preview contracts.\n", encoding="utf-8")
    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])
    service.build_distilled_units(plan)

    http_payload = TestClient(app).post(
        "/api/v1/knowledge/distill",
        json={"workspace": str(workspace), "limit": 5, "typed_unit_type": "concept"},
    ).json()

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "data_service",
            "distill",
            "--workspace",
            str(workspace),
            "--limit",
            "5",
            "--typed-type",
            "concept",
        ],
    )
    assert cli_main() == 0
    cli_payload = json.loads(capsys.readouterr().out)

    expected_keys = {
        "workspace",
        "schema_version",
        "manifest",
        "schema",
        "sources",
        "source_profiles",
        "source",
        "units",
        "available_source_count",
        "provenance_overview",
        "filters",
    }
    assert set(http_payload) == expected_keys
    assert set(cli_payload) == expected_keys
    assert cli_payload["workspace"] == http_payload["workspace"]
    assert cli_payload["schema_version"] == http_payload["schema_version"]
    assert cli_payload["filters"] == http_payload["filters"]
    assert [unit["unit_id"] for unit in cli_payload["units"]] == [unit["unit_id"] for unit in http_payload["units"]]
    assert [source["source_id"] for source in cli_payload["source_profiles"]] == [
        source["source_id"] for source in http_payload["source_profiles"]
    ]


def test_phaseg4_source_trace_target_contract_documents_current_surface(tmp_path, monkeypatch):
    from app.api.v1.data_service import router
    from data_service.__main__ import _build_parser
    from data_service.mcp_tool_registry import all_tool_specs

    contract_doc = (V15_DOCS_ROOT / "source-trace-contract.md").read_text(encoding="utf-8")
    matrix_doc = (V15_DOCS_ROOT / "interface-convergence-matrix.md").read_text(encoding="utf-8")
    frontend_contract = Path("frontend/src/data/mcpContract.ts").read_text(encoding="utf-8")

    route_paths = {getattr(route, "path", "") for route in router.routes}
    assert "/knowledge/source/trace" in route_paths
    assert "knowledge_source_trace" in {spec["name"] for spec in all_tool_specs()}

    parser = _build_parser()
    subparser_action = next(action for action in parser._actions if getattr(action, "choices", None))
    assert "trace" not in set(subparser_action.choices)

    for text in [contract_doc, matrix_doc, frontend_contract]:
        assert "knowledge_source_trace" in text
        assert "/api/v1/knowledge/source/trace" in text
        assert "knowledge trace source" in text

    assert "PhaseG29 开放 MCP `knowledge_source_trace`" in contract_doc
    assert "PhaseG23 开放 `knowledge trace source` CLI alias" in contract_doc
    assert "不新增 HTTP route" in contract_doc


def test_phaseg4_source_trace_response_shape_stays_stable(tmp_path):
    workspace = tmp_path / "workspace"
    doc = tmp_path / "phaseg4-trace.md"
    doc.write_text("# PhaseG4 Trace\n\nPhaseG4 traces source evidence through distill and graph artifacts.\n", encoding="utf-8")
    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])
    service.run_default_pipeline(plan)

    source_id = service.read_distill_bundle(limit=5)["sources"][0]["source_id"]
    response = TestClient(app).post(
        "/api/v1/knowledge/source/trace",
        json={"workspace": str(workspace), "source_id": source_id, "limit": 5},
    )
    assert response.status_code == 200
    payload = response.json()

    assert {"workspace", "source_id", "source", "distill", "llmwiki", "graphrag", "trace_summary"} <= set(payload)
    assert {"units", "unit_count", "provenance_summary", "profile_debug"} <= set(payload["distill"])
    assert {"pages", "page_count"} <= set(payload["llmwiki"])
    assert {
        "nodes",
        "edges",
        "communities",
        "node_count",
        "edge_count",
        "community_count",
        "graph_model_version",
    } <= set(payload["graphrag"])
    assert {
        "source_title",
        "unit_count",
        "llmwiki_page_count",
        "graph_node_count",
        "graph_community_count",
    } <= set(payload["trace_summary"])
    assert payload["source_id"] == source_id
    assert payload["distill"]["unit_count"] >= 1


def test_phaseg5_source_trace_http_uses_shared_contract_helper(tmp_path):
    from data_service.source_trace_contract import source_trace_payload

    workspace = tmp_path / "workspace"
    doc = tmp_path / "phaseg5-trace.md"
    doc.write_text("# PhaseG5 Trace\n\nPhaseG5 keeps source trace payloads behind one serializer.\n", encoding="utf-8")
    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])
    service.run_default_pipeline(plan)

    source_id = service.read_distill_bundle(limit=5)["sources"][0]["source_id"]
    helper_payload = source_trace_payload(service, source_id, limit=5)
    response = TestClient(app).post(
        "/api/v1/knowledge/source/trace",
        json={"workspace": str(workspace), "source_id": source_id, "limit": 5},
    )

    assert response.status_code == 200
    assert response.json() == helper_payload

    from data_service.__main__ import _build_parser
    from data_service.mcp_tool_registry import all_tool_specs

    assert "knowledge_source_trace" in {spec["name"] for spec in all_tool_specs()}
    parser = _build_parser()
    subparser_action = next(action for action in parser._actions if getattr(action, "choices", None))
    assert "trace" not in set(subparser_action.choices)


def test_phaseg30_workspace_scoped_target_http_routes_reuse_shared_contracts(tmp_path, monkeypatch):
    from data_service.models import QueryMode

    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_SOURCE_ROOTS", str(root))
    workspace_id = "research-vault"
    workspace = root / workspace_id
    root.mkdir(parents=True, exist_ok=True)
    doc = root / "phaseg30-target-http.md"
    doc.write_text("# PhaseG30 Target HTTP\n\nPhaseG30 validates workspace-scoped target routes.\n", encoding="utf-8")

    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])
    service.run_default_pipeline(plan)
    source_id = service.read_distill_bundle(limit=5)["sources"][0]["source_id"]

    client = TestClient(app)
    legacy_query = client.post(
        "/api/v1/knowledge/query",
        json={"workspace": str(workspace), "query": "PhaseG30", "mode": QueryMode.HYBRID.value, "top_k": 5},
    )
    target_query = client.post(
        f"/api/workspaces/{workspace_id}/query",
        json={"query": "PhaseG30", "mode": QueryMode.HYBRID.value, "top_k": 5},
    )
    assert legacy_query.status_code == 200
    assert target_query.status_code == 200
    assert target_query.json()["query"] == legacy_query.json()["query"]
    assert target_query.json()["coverage_status"] in {"no_sources", "insufficient_evidence", "source_supported"}

    legacy_distill = client.post(
        "/api/v1/knowledge/distill",
        json={"workspace": str(workspace), "limit": 5, "typed_unit_type": "concept"},
    )
    target_distill = client.post(
        f"/api/workspaces/{workspace_id}/distill",
        json={"limit": 5, "typed_unit_type": "concept"},
    )
    assert legacy_distill.status_code == 200
    assert target_distill.status_code == 200
    assert target_distill.json() == legacy_distill.json()

    legacy_trace = client.post(
        "/api/v1/knowledge/source/trace",
        json={"workspace": str(workspace), "source_id": source_id, "limit": 5},
    )
    target_trace = client.get(f"/api/workspaces/{workspace_id}/sources/{source_id}/trace", params={"limit": 5})
    assert legacy_trace.status_code == 200
    assert target_trace.status_code == 422

    created_workspace = client.post("/api/workspaces", json={"name": "Trace Registry"})
    assert created_workspace.status_code == 200
    target_workspace_id = created_workspace.json()["workspace_id"]
    imported = client.post(
        f"/api/workspaces/{target_workspace_id}/sources",
        json={"paths": [str(doc)], "metadata": {"phase": "g30"}},
    )
    assert imported.status_code == 200
    target_source_id = imported.json()["data"]["sources"][0]["source_id"]
    target_registry_trace = client.get(
        f"/api/workspaces/{target_workspace_id}/sources/{target_source_id}/trace",
        params={"limit": 5},
    )
    assert target_registry_trace.status_code == 200
    assert target_registry_trace.json()["data"]["trace"]["source_id"] == target_source_id

    route_paths = {getattr(route, "path", "") for route in app.routes}
    assert {
        "/api/workspaces/{workspace_id}/query",
        "/api/workspaces/{workspace_id}/distill",
        "/api/workspaces/{workspace_id}/sources/{source_id}/trace",
        "/api/v1/knowledge/query",
        "/api/v1/knowledge/distill",
        "/api/v1/knowledge/source/trace",
    } <= route_paths

    contract_doc = (V15_DOCS_ROOT / "target-http-routes-contract.md").read_text(encoding="utf-8")
    matrix_doc = (V15_DOCS_ROOT / "interface-convergence-matrix.md").read_text(encoding="utf-8")
    assert "PhaseG30" in contract_doc
    assert "/api/workspaces/{workspace_id}/query" in contract_doc
    assert "/api/workspaces/{workspace_id}/distill" in contract_doc
    assert "/api/workspaces/{workspace_id}/sources/{source_id}/trace" in contract_doc
    assert "旧 `/api/v1/knowledge/*` 兼容入口不废弃" in contract_doc
    assert "PhaseG30 已开放首批目标 HTTP route" in matrix_doc


def test_phaseg6_source_trace_schema_examples_document_shared_contract():
    from data_service.source_trace_contract import (
        SOURCE_TRACE_LIMIT_DEFAULT,
        SOURCE_TRACE_LIMIT_MAX,
        SOURCE_TRACE_LIMIT_MIN,
        source_trace_payload,
    )

    contract_doc = (V15_DOCS_ROOT / "source-trace-contract.md").read_text(encoding="utf-8")

    assert '"workspace": "/absolute/path/to/workspace"' in contract_doc
    assert '"workspace_id": "research-vault"' in contract_doc
    assert "knowledge trace source --workspace-root ./workspaces --workspace-id research-vault --source-id source-123 --limit 12" in contract_doc
    assert "`source_trace_payload`" in contract_doc
    assert "Stage 1" in contract_doc
    assert "Stage 2" in contract_doc
    assert "Stage 3" in contract_doc
    assert "Stage 4" in contract_doc
    assert f"`limit` contract 固定为 {SOURCE_TRACE_LIMIT_MIN}-{SOURCE_TRACE_LIMIT_MAX}，默认 {SOURCE_TRACE_LIMIT_DEFAULT}" in contract_doc

    for field in ["workspace", "source_id", "source", "distill", "llmwiki", "graphrag", "trace_summary"]:
        assert f'"{field}"' in contract_doc

    assert source_trace_payload.__name__ == "source_trace_payload"


def test_phaseg7_low_signal_audit_http_uses_shared_contract_helper(tmp_path, monkeypatch):
    import data_service.quality_contract as quality_contract

    workspace = tmp_path / "workspace"
    doc = tmp_path / "phaseg7-quality.md"
    doc.write_text("# PhaseG7 Quality\n\nPhaseG7 keeps low-signal audit payloads behind one serializer.\n", encoding="utf-8")
    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])
    service.run_default_pipeline(plan)

    monkeypatch.setattr(quality_contract, "_now", lambda: "2026-05-11T00:00:00Z")
    helper_payload = quality_contract.low_signal_audit_payload(service, limit=8)
    response = TestClient(app).post(
        "/api/v1/knowledge/quality/low-signal-audit",
        json={"workspace": str(workspace), "limit": 8},
    )

    assert response.status_code == 200
    assert response.json() == helper_payload
    assert set(response.json()) == {"workspace", "audited_at", "overall_status", "checks", "metrics", "samples", "recommendations"}

    assert _cli_quality_subcommands() == {
        "summary",
        "correction-plan",
        "feedback-list",
        "feedback",
        "rules",
        "rules-build",
        "review",
    }


def test_phaseg10_quality_http_routes_use_shared_contract_helpers(tmp_path, monkeypatch):
    import app.api.v1.data_service as api_module

    calls = {
        "record": 0,
        "feedback_list": 0,
        "rules": 0,
        "rules_build": 0,
        "review": 0,
    }
    original_record = api_module.record_quality_feedback_payload
    original_feedback_list = api_module.quality_feedback_list_payload
    original_rules = api_module.quality_correction_rules_payload
    original_rules_build = api_module.quality_correction_rules_build_payload
    original_review = api_module.quality_correction_rule_review_payload

    def record_wrapper(*args, **kwargs):
        calls["record"] += 1
        return original_record(*args, **kwargs)

    def feedback_list_wrapper(*args, **kwargs):
        calls["feedback_list"] += 1
        return original_feedback_list(*args, **kwargs)

    def rules_wrapper(*args, **kwargs):
        calls["rules"] += 1
        return original_rules(*args, **kwargs)

    def rules_build_wrapper(*args, **kwargs):
        calls["rules_build"] += 1
        return original_rules_build(*args, **kwargs)

    def review_wrapper(*args, **kwargs):
        calls["review"] += 1
        return original_review(*args, **kwargs)

    monkeypatch.setattr(api_module, "record_quality_feedback_payload", record_wrapper)
    monkeypatch.setattr(api_module, "quality_feedback_list_payload", feedback_list_wrapper)
    monkeypatch.setattr(api_module, "quality_correction_rules_payload", rules_wrapper)
    monkeypatch.setattr(api_module, "quality_correction_rules_build_payload", rules_build_wrapper)
    monkeypatch.setattr(api_module, "quality_correction_rule_review_payload", review_wrapper)

    workspace = tmp_path / "workspace"
    client = TestClient(app)
    feedback_response = client.post(
        "/api/v1/knowledge/quality/feedback",
        json={
            "workspace": str(workspace),
            "target_type": "entity",
            "target_id": "phaseg10-topic",
            "action": "rename_suggest",
            "label": "PhaseG10 Topic",
            "suggested_value": "Quality HTTP Contract Topic",
            "reason": "PhaseG10 shared helper route test",
            "metadata": {"phase": "G10"},
        },
    )
    assert feedback_response.status_code == 200
    feedback_payload = feedback_response.json()
    assert set(feedback_payload) == {"workspace", "feedback", "summary"}
    assert feedback_payload["feedback"]["target_id"] == "phaseg10-topic"
    assert feedback_payload["summary"]["feedback_count"] == 1

    feedback_list_response = client.post(
        "/api/v1/knowledge/quality/feedback/list",
        json={"workspace": str(workspace), "limit": 10, "target_type": "entity"},
    )
    assert feedback_list_response.status_code == 200
    assert feedback_list_response.json()["filtered_count"] == 1

    rules_build_response = client.post(
        "/api/v1/knowledge/quality/corrections/build",
        json={"workspace": str(workspace)},
    )
    assert rules_build_response.status_code == 200
    assert rules_build_response.json()["summary"]["rule_count"] == 1

    rules_response = client.post(
        "/api/v1/knowledge/quality/corrections",
        json={"workspace": str(workspace), "limit": 10, "status": "draft"},
    )
    assert rules_response.status_code == 200
    rule = rules_response.json()["items"][0]
    assert rule["status"] == "draft"

    review_response = client.post(
        "/api/v1/knowledge/quality/corrections/review",
        json={
            "workspace": str(workspace),
            "rule_id": rule["rule_id"],
            "status": "approved",
            "reviewer": "phaseg10",
            "note": "shared helper review",
        },
    )
    assert review_response.status_code == 200
    assert review_response.json()["correction_plan"]["source_rule_count"] == 1
    assert calls == {
        "record": 1,
        "feedback_list": 1,
        "rules": 1,
        "rules_build": 1,
        "review": 1,
    }

    assert _cli_quality_subcommands() == {
        "summary",
        "correction-plan",
        "feedback-list",
        "feedback",
        "rules",
        "rules-build",
        "review",
    }


def test_phaseg11_quality_correction_plan_http_uses_shared_contract_helper(tmp_path, monkeypatch):
    import app.api.v1.data_service as api_module

    calls = {"plan": 0}
    original_plan = api_module.quality_correction_plan_payload

    def plan_wrapper(*args, **kwargs):
        calls["plan"] += 1
        return original_plan(*args, **kwargs)

    monkeypatch.setattr(api_module, "quality_correction_plan_payload", plan_wrapper)

    workspace = tmp_path / "workspace"
    client = TestClient(app)
    feedback_response = client.post(
        "/api/v1/knowledge/quality/feedback",
        json={
            "workspace": str(workspace),
            "target_type": "entity",
            "target_id": "phaseg11-topic",
            "action": "rename_suggest",
            "label": "PhaseG11 Topic",
            "suggested_value": "Quality Plan Topic",
            "reason": "PhaseG11 shared plan helper route test",
            "metadata": {"phase": "G11"},
        },
    )
    assert feedback_response.status_code == 200

    rules_response = client.post(
        "/api/v1/knowledge/quality/corrections",
        json={"workspace": str(workspace), "limit": 10, "status": "draft"},
    )
    assert rules_response.status_code == 200
    rule_id = rules_response.json()["items"][0]["rule_id"]

    review_response = client.post(
        "/api/v1/knowledge/quality/corrections/review",
        json={
            "workspace": str(workspace),
            "rule_id": rule_id,
            "status": "approved",
            "reviewer": "phaseg11",
            "note": "approve before plan helper check",
        },
    )
    assert review_response.status_code == 200

    plan_response = client.post(
        "/api/v1/knowledge/quality/corrections/plan",
        json={"workspace": str(workspace)},
    )
    assert plan_response.status_code == 200
    plan_payload = plan_response.json()
    assert set(plan_payload) == {
        "schema_version",
        "workspace",
        "generated_at",
        "source_rule_count",
        "actions",
        "summary",
        "notes",
    }
    assert plan_payload["source_rule_count"] == 1
    assert plan_payload["summary"]["action_count"] == 1
    assert calls == {"plan": 1}

    assert _cli_quality_subcommands() == {
        "summary",
        "correction-plan",
        "feedback-list",
        "feedback",
        "rules",
        "rules-build",
        "review",
    }


def test_phaseg13_quality_cli_read_only_preview_uses_shared_contract_helpers(tmp_path, monkeypatch, capsys):
    import data_service.__main__ as cli_module

    workspace = tmp_path / "workspace"
    service = DataService(workspace)
    service.record_quality_feedback(
        target_type="entity",
        target_id="phaseg13-topic",
        action="rename_suggest",
        label="PhaseG13 Topic",
        suggested_value="Quality CLI Topic",
        reason="PhaseG13 read-only CLI preview",
        metadata={"phase": "G13"},
    )

    calls = {"summary": 0, "plan": 0, "feedback_list": 0, "rules": 0}
    original_summary = cli_module.quality_summary_payload
    original_plan = cli_module.quality_correction_plan_preview_payload
    original_feedback_list = cli_module.quality_feedback_list_payload
    original_rules = cli_module.quality_correction_rules_payload

    def summary_wrapper(*args, **kwargs):
        calls["summary"] += 1
        return original_summary(*args, **kwargs)

    def plan_wrapper(*args, **kwargs):
        calls["plan"] += 1
        return original_plan(*args, **kwargs)

    def feedback_list_wrapper(*args, **kwargs):
        calls["feedback_list"] += 1
        return original_feedback_list(*args, **kwargs)

    def rules_wrapper(*args, **kwargs):
        calls["rules"] += 1
        return original_rules(*args, **kwargs)

    monkeypatch.setattr(cli_module, "quality_summary_payload", summary_wrapper)
    monkeypatch.setattr(cli_module, "quality_correction_plan_preview_payload", plan_wrapper)
    monkeypatch.setattr(cli_module, "quality_feedback_list_payload", feedback_list_wrapper)
    monkeypatch.setattr(cli_module, "quality_correction_rules_payload", rules_wrapper)

    commands = [
        ["data_service", "quality", "summary", "--workspace-id", str(workspace)],
        ["data_service", "quality", "correction-plan", "--workspace-id", str(workspace), "--rebuild"],
        ["data_service", "quality", "feedback-list", "--workspace-id", str(workspace), "--target-type", "entity", "--limit", "5"],
        ["data_service", "quality", "rules", "--workspace-id", str(workspace), "--status", "draft", "--limit", "5"],
    ]
    payloads = []
    for command in commands:
        monkeypatch.setattr(sys, "argv", command)
        assert cli_module.main() == 0
        payloads.append(json.loads(capsys.readouterr().out))

    assert calls == {"summary": 1, "plan": 1, "feedback_list": 1, "rules": 1}
    assert {"workspace", "quality", "quality_feedback", "quality_correction_rules", "quality_correction_plan"} == set(payloads[0])
    assert {"schema_version", "workspace", "generated_at", "source_rule_count", "actions", "summary", "notes"} == set(payloads[1])
    assert payloads[2]["items"][0]["target_id"] == "phaseg13-topic"
    assert payloads[3]["items"][0]["status"] == "draft"
    assert _cli_quality_subcommands() == {
        "summary",
        "correction-plan",
        "feedback-list",
        "feedback",
        "rules",
        "rules-build",
        "review",
    }


def test_phaseg14_quality_cli_write_commands_use_shared_contract_helpers(tmp_path, monkeypatch, capsys):
    import data_service.__main__ as cli_module

    workspace = tmp_path / "workspace"
    calls = {"record": 0, "rules_build": 0, "review": 0}
    original_record = cli_module.record_quality_feedback_payload
    original_rules_build = cli_module.quality_correction_rules_build_payload
    original_review = cli_module.quality_correction_rule_review_payload

    def record_wrapper(*args, **kwargs):
        calls["record"] += 1
        return original_record(*args, **kwargs)

    def rules_build_wrapper(*args, **kwargs):
        calls["rules_build"] += 1
        return original_rules_build(*args, **kwargs)

    def review_wrapper(*args, **kwargs):
        calls["review"] += 1
        return original_review(*args, **kwargs)

    monkeypatch.setattr(cli_module, "record_quality_feedback_payload", record_wrapper)
    monkeypatch.setattr(cli_module, "quality_correction_rules_build_payload", rules_build_wrapper)
    monkeypatch.setattr(cli_module, "quality_correction_rule_review_payload", review_wrapper)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "data_service",
            "quality",
            "feedback",
            "--workspace-id",
            str(workspace),
            "--target-type",
            "entity",
            "--target-id",
            "phaseg14-topic",
            "--action",
            "rename_suggest",
            "--label",
            "PhaseG14 Topic",
            "--suggested-value",
            "Quality CLI Write Topic",
            "--reason",
            "PhaseG14 write CLI",
            "--metadata-json",
            '{"phase":"G14"}',
        ],
    )
    assert cli_module.main() == 0
    feedback_payload = json.loads(capsys.readouterr().out)
    assert feedback_payload["feedback"]["target_id"] == "phaseg14-topic"
    assert feedback_payload["feedback"]["metadata"] == {"phase": "G14"}

    monkeypatch.setattr(sys, "argv", ["data_service", "quality", "rules-build", "--workspace-id", str(workspace)])
    assert cli_module.main() == 0
    rules_build_payload = json.loads(capsys.readouterr().out)
    rule_id = rules_build_payload["rules"][0]["rule_id"]
    assert rules_build_payload["summary"]["rule_count"] == 1

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "data_service",
            "quality",
            "review",
            "--workspace-id",
            str(workspace),
            "--rule-id",
            rule_id,
            "--status",
            "approved",
            "--reviewer",
            "phaseg14",
            "--note",
            "approved from CLI",
        ],
    )
    assert cli_module.main() == 0
    review_payload = json.loads(capsys.readouterr().out)
    assert review_payload["rule"]["status"] == "approved"
    assert review_payload["correction_plan"]["summary"]["action_count"] == 1
    assert calls == {"record": 1, "rules_build": 1, "review": 1}
    assert _cli_quality_subcommands() == {
        "summary",
        "correction-plan",
        "feedback-list",
        "feedback",
        "rules",
        "rules-build",
        "review",
    }


def test_phaseg15_knowledge_quality_alias_entrypoint_reuses_quality_cli_helpers(tmp_path, monkeypatch, capsys):
    import data_service.__main__ as cli_module

    workspace = tmp_path / "workspace"
    service = DataService(workspace)
    service.record_quality_feedback(
        target_type="entity",
        target_id="phaseg15-topic",
        action="rename_suggest",
        label="PhaseG15 Topic",
        suggested_value="Knowledge Quality Alias Topic",
        reason="PhaseG15 knowledge quality alias",
        metadata={"phase": "G15"},
    )

    calls = {"summary": 0, "rules": 0}
    original_summary = cli_module.quality_summary_payload
    original_rules = cli_module.quality_correction_rules_payload

    def summary_wrapper(*args, **kwargs):
        calls["summary"] += 1
        return original_summary(*args, **kwargs)

    def rules_wrapper(*args, **kwargs):
        calls["rules"] += 1
        return original_rules(*args, **kwargs)

    monkeypatch.setattr(cli_module, "quality_summary_payload", summary_wrapper)
    monkeypatch.setattr(cli_module, "quality_correction_rules_payload", rules_wrapper)

    assert cli_module.knowledge_main(["quality", "summary", "--workspace-id", str(workspace)]) == 0
    summary_payload = json.loads(capsys.readouterr().out)
    assert {"workspace", "quality", "quality_feedback", "quality_correction_rules", "quality_correction_plan"} == set(summary_payload)

    assert cli_module.knowledge_main(["quality", "rules", "--workspace-id", str(workspace), "--status", "draft"]) == 0
    rules_payload = json.loads(capsys.readouterr().out)
    assert rules_payload["items"][0]["target_id"] == "phaseg15-topic"
    assert rules_payload["items"][0]["status"] == "draft"
    assert calls == {"summary": 1, "rules": 1}

    parser = cli_module._build_knowledge_parser()
    assert parser.prog == "knowledge"
    subparser_action = next(action for action in parser._actions if getattr(action, "choices", None))
    assert "quality" in set(subparser_action.choices)


def test_phaseg16_packaging_console_scripts_point_to_existing_entrypoints():
    import data_service.__main__ as cli_module

    pyproject = tomllib.loads(Path("backend/pyproject.toml").read_text(encoding="utf-8"))
    scripts = pyproject["project"]["scripts"]

    assert scripts["data-service"] == "data_service.__main__:main"
    assert scripts["knowledge"] == "data_service.__main__:knowledge_main"
    assert pyproject["tool"]["setuptools"]["packages"]["find"]["include"] == ["app*", "data_service*"]
    assert callable(cli_module.main)
    assert callable(cli_module.knowledge_main)
    assert cli_module._build_parser(prog="knowledge").prog == "knowledge"


def test_phaseg27_knowledge_entrypoint_exposes_build_write_aliases_only():
    import data_service.__main__ as cli_module

    parser = cli_module._build_knowledge_parser()
    subparser_action = next(action for action in parser._actions if getattr(action, "choices", None))
    assert parser.prog == "knowledge"
    assert set(subparser_action.choices) == {"quality", "query", "workspace", "source", "build", "graph", "trace", "code"}

    workspace_parser = subparser_action.choices["workspace"]
    workspace_action = next(action for action in workspace_parser._actions if getattr(action, "choices", None))
    assert set(workspace_action.choices) == {"create", "list", "describe", "archive"}

    source_parser = subparser_action.choices["source"]
    source_action = next(action for action in source_parser._actions if getattr(action, "choices", None))
    assert set(source_action.choices) == {"import", "list", "remove"}

    build_parser = subparser_action.choices["build"]
    build_action = next(action for action in build_parser._actions if getattr(action, "choices", None))
    assert set(build_action.choices) == {"start", "status", "cancel"}

    graph_parser = subparser_action.choices["graph"]
    graph_action = next(action for action in graph_parser._actions if getattr(action, "choices", None))
    assert set(graph_action.choices) == {"snapshot", "neighbors", "community", "query", "session"}

    trace_parser = subparser_action.choices["trace"]
    trace_action = next(action for action in trace_parser._actions if getattr(action, "choices", None))
    assert set(trace_action.choices) == {"source"}

    code_parser = subparser_action.choices["code"]
    code_action = next(action for action in code_parser._actions if getattr(action, "choices", None))
    assert set(code_action.choices) == {
        "import",
        "list",
        "snapshot",
        "inventory",
        "symbols",
        "trace",
        "overview",
            "context-pack",
            "devwiki",
            "graph",
            "platform",
            "quality",
            "describe",
            "archive",
            "architecture",
            "architecture-intent",
            "coding-agent",
        }

    data_service_parser = cli_module._build_parser()
    data_service_action = next(action for action in data_service_parser._actions if getattr(action, "choices", None))
    assert {"ingest", "summary", "distill", "boundary", "graphrag-execute", "query", "quality"} == set(data_service_action.choices)


def test_phaseg18_knowledge_query_alias_reuses_query_contract(tmp_path, monkeypatch, capsys):
    import data_service.__main__ as cli_module

    workspace = tmp_path / "workspace"
    doc = tmp_path / "phaseg18-query.md"
    doc.write_text("# PhaseG18 Query\n\nPhaseG18 validates the knowledge query alias.\n", encoding="utf-8")
    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])
    service.run_default_pipeline(plan)

    calls = {"query": 0}
    original_query = cli_module.run_query_contract

    def query_wrapper(*args, **kwargs):
        calls["query"] += 1
        return original_query(*args, **kwargs)

    monkeypatch.setattr(cli_module, "run_query_contract", query_wrapper)

    assert cli_module.knowledge_main(
        [
            "query",
            "PhaseG18",
            "--workspace-id",
            str(workspace),
            "--mode",
            "hybrid",
            "--top-k",
            "3",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)

    assert calls == {"query": 1}
    assert set(payload) == {"mode", "query", "answer", "hits", "engine_payloads"}
    assert payload["query"] == "PhaseG18"
    assert payload["mode"] == "hybrid"

    parser = cli_module._build_knowledge_parser()
    subparser_action = next(action for action in parser._actions if getattr(action, "choices", None))
    assert set(subparser_action.choices) == {"quality", "query", "workspace", "source", "build", "graph", "trace", "code"}


def test_phaseg19_knowledge_workspace_readonly_alias_reuses_workspace_mcp_handler(tmp_path, monkeypatch, capsys):
    import data_service.__main__ as cli_module
    from data_service.mcp_workspace_runtime import WorkspaceRuntime

    root = tmp_path / "managed"
    runtime = WorkspaceRuntime(root / "_default", workspace_root=root)
    workspace_path = root / "research-vault"
    runtime.ensure_workspace_meta(workspace_path, name="Research Vault", owner="harness", tags=["phaseg19"])

    calls = []
    original_handler = cli_module.handle_workspace_tool

    def handler_wrapper(name, arguments, **kwargs):
        calls.append(name)
        return original_handler(name, arguments, **kwargs)

    monkeypatch.setattr(cli_module, "handle_workspace_tool", handler_wrapper)

    assert cli_module.knowledge_main(
        ["workspace", "list", "--workspace-root", str(root), "--owner", "harness", "--limit", "10"]
    ) == 0
    list_payload = json.loads(capsys.readouterr().out)
    assert list_payload["status"] == "ok"
    assert list_payload["workspace_id"] == "root"
    assert list_payload["data"]["items"][0]["workspace_id"] == "research-vault"
    assert list_payload["data"]["items"][0]["name"] == "Research Vault"
    assert "debug_paths" in list_payload["data"]["items"][0]

    assert cli_module.knowledge_main(
        ["workspace", "describe", "--workspace-root", str(root), "--workspace-id", "research-vault"]
    ) == 0
    describe_payload = json.loads(capsys.readouterr().out)
    assert describe_payload["status"] == "ok"
    assert describe_payload["workspace_id"] == "research-vault"
    assert {"layout", "summary", "engines", "latest_build", "quality"} <= set(describe_payload["data"])
    assert "debug_paths" in describe_payload["data"]["layout"]
    assert calls == ["knowledge_workspace_list", "knowledge_workspace_describe"]


def test_phaseg25_knowledge_workspace_write_aliases_reuse_workspace_mcp_handler(tmp_path, monkeypatch, capsys):
    import data_service.__main__ as cli_module

    root = tmp_path / "managed"
    calls = []
    original_handler = cli_module.handle_workspace_tool

    def handler_wrapper(name, arguments, **kwargs):
        calls.append((name, arguments))
        return original_handler(name, arguments, **kwargs)

    monkeypatch.setattr(cli_module, "handle_workspace_tool", handler_wrapper)

    assert cli_module.knowledge_main(
        [
            "workspace",
            "create",
            "--workspace-root",
            str(root),
            "--name",
            "Research Vault",
            "--owner",
            "harness",
            "--tag",
            "phaseg25",
        ]
    ) == 0
    create_payload = json.loads(capsys.readouterr().out)
    assert create_payload["status"] == "ok"
    assert create_payload["workspace_id"] == "research-vault"
    assert create_payload["data"]["capabilities"]["build"] is True
    assert "debug_path" in create_payload["artifact_refs"][0]

    assert cli_module.knowledge_main(
        [
            "workspace",
            "archive",
            "--workspace-root",
            str(root),
            "--workspace-id",
            "research-vault",
            "--reason",
            "phaseg25 done",
        ]
    ) == 0
    archive_payload = json.loads(capsys.readouterr().out)
    assert archive_payload["status"] == "ok"
    assert archive_payload["workspace_id"] == "research-vault"
    assert archive_payload["data"]["workspace"]["status"] == "archived"
    assert archive_payload["data"]["workspace"]["archive_reason"] == "phaseg25 done"

    assert cli_module.knowledge_main(
        ["workspace", "list", "--workspace-root", str(root), "--owner", "harness", "--limit", "10"]
    ) == 0
    list_payload = json.loads(capsys.readouterr().out)
    assert list_payload["data"]["items"][0]["workspace_id"] == "research-vault"
    assert list_payload["data"]["items"][0]["status"] == "archived"

    assert calls == [
        (
            "knowledge_workspace_create",
            {"name": "Research Vault", "owner": "harness", "tags": ["phaseg25"]},
        ),
        (
            "knowledge_workspace_archive",
            {"workspace_id": "research-vault", "reason": "phaseg25 done"},
        ),
        (
            "knowledge_workspace_list",
            {"owner": "harness", "tag": None, "limit": 10},
        ),
    ]


def test_phaseg20_knowledge_source_list_alias_reuses_source_mcp_handler(tmp_path, monkeypatch, capsys):
    import data_service.__main__ as cli_module
    from data_service.mcp_common import write_json
    from data_service.mcp_workspace_runtime import WorkspaceRuntime

    root = tmp_path / "managed"
    runtime = WorkspaceRuntime(root / "_default", workspace_root=root)
    workspace_path = root / "research-vault"
    runtime.ensure_workspace_meta(workspace_path, name="Research Vault")
    write_json(
        runtime.sources_manifest_path(workspace_path),
        {
            "items": [
                {
                    "source_id": "src_phaseg20",
                    "sha256": "abc123",
                    "title": "PhaseG20 Source",
                    "status": "active",
                    "low_signal": {},
                    "ingest_status": "built",
                    "path": str(workspace_path / "sources" / "imported" / "src_phaseg20.md"),
                }
            ]
        },
    )

    calls = []
    original_handler = cli_module.handle_source_tool

    def handler_wrapper(name, arguments, **kwargs):
        calls.append(name)
        return original_handler(name, arguments, **kwargs)

    monkeypatch.setattr(cli_module, "handle_source_tool", handler_wrapper)

    assert cli_module.knowledge_main(
        ["source", "list", "--workspace-root", str(root), "--workspace-id", "research-vault", "--status", "active", "--limit", "10"]
    ) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "ok"
    assert payload["workspace_id"] == "research-vault"
    assert payload["data"]["items"] == [
        {
            "source_id": "src_phaseg20",
            "sha256": "abc123",
            "title": "PhaseG20 Source",
            "status": "active",
            "low_signal": {},
            "ingest_status": "built",
        }
    ]
    assert calls == ["knowledge_source_list"]


def test_phaseg26_knowledge_source_write_aliases_reuse_source_mcp_handler(tmp_path, monkeypatch, capsys):
    import data_service.__main__ as cli_module
    from data_service.mcp_workspace_runtime import WorkspaceRuntime

    root = tmp_path / "managed"
    runtime = WorkspaceRuntime(root / "_default", workspace_root=root)
    workspace_path = root / "research-vault"
    runtime.ensure_workspace_meta(workspace_path, name="Research Vault")

    calls = []
    original_handler = cli_module.handle_source_tool

    def handler_wrapper(name, arguments, **kwargs):
        calls.append((name, arguments))
        return original_handler(name, arguments, **kwargs)

    monkeypatch.setattr(cli_module, "handle_source_tool", handler_wrapper)

    assert cli_module.knowledge_main(
        [
            "source",
            "import",
            "--workspace-root",
            str(root),
            "--workspace-id",
            "research-vault",
            "--text",
            "PhaseG26 source import text.",
            "--title",
            "PhaseG26 Source",
            "--metadata-json",
            '{"stage":"phaseg26"}',
        ]
    ) == 0
    import_payload = json.loads(capsys.readouterr().out)
    source_id = import_payload["data"]["sources"][0]["source_id"]
    assert import_payload["status"] == "ok"
    assert import_payload["workspace_id"] == "research-vault"
    assert import_payload["data"]["sources"][0]["title"] == "PhaseG26 Source"
    assert import_payload["data"]["sources"][0]["status"] == "imported"

    assert cli_module.knowledge_main(
        [
            "source",
            "remove",
            "--workspace-root",
            str(root),
            "--workspace-id",
            "research-vault",
            "--source-id",
            source_id,
            "--reason",
            "phaseg26 done",
        ]
    ) == 0
    remove_payload = json.loads(capsys.readouterr().out)
    assert remove_payload["status"] == "ok"
    assert remove_payload["workspace_id"] == "research-vault"
    assert remove_payload["data"]["source"]["source_id"] == source_id
    assert remove_payload["data"]["source"]["status"] == "removed"

    assert cli_module.knowledge_main(
        ["source", "list", "--workspace-root", str(root), "--workspace-id", "research-vault", "--status", "removed", "--limit", "10"]
    ) == 0
    list_payload = json.loads(capsys.readouterr().out)
    assert list_payload["data"]["items"][0]["source_id"] == source_id
    assert list_payload["data"]["items"][0]["status"] == "removed"

    assert calls == [
        (
            "knowledge_source_import",
            {
                "workspace_id": "research-vault",
                "paths": [],
                "texts": [
                    {
                        "title": "PhaseG26 Source",
                        "content": "PhaseG26 source import text.",
                        "metadata": {},
                    }
                ],
                "metadata": {"stage": "phaseg26"},
            },
        ),
        (
            "knowledge_source_remove",
            {"workspace_id": "research-vault", "source_id": source_id, "reason": "phaseg26 done"},
        ),
        (
            "knowledge_source_list",
            {"workspace_id": "research-vault", "status": "removed", "limit": 10},
        ),
    ]


def test_phaseg21_knowledge_build_status_alias_reuses_build_mcp_handler(tmp_path, monkeypatch, capsys):
    import data_service.__main__ as cli_module
    from data_service.mcp_common import write_json
    from data_service.mcp_workspace_runtime import WorkspaceRuntime

    root = tmp_path / "managed"
    runtime = WorkspaceRuntime(root / "_default", workspace_root=root)
    workspace_path = root / "research-vault"
    runtime.ensure_workspace_meta(workspace_path, name="Research Vault")
    operation_id = "op_phaseg21"
    write_json(
        runtime.operation_path(workspace_path, operation_id),
        {
            "operation_id": operation_id,
            "workspace_id": "research-vault",
            "mode": "llmwiki_only",
            "status": "completed",
            "stage": "completed",
            "progress": 1.0,
            "error": None,
            "retryable": False,
            "artifacts": [],
            "created_at": "2026-05-12T00:00:00Z",
            "updated_at": "2026-05-12T00:00:00Z",
        },
    )

    calls = []
    original_handler = cli_module.handle_build_tool

    def handler_wrapper(name, arguments, **kwargs):
        calls.append(name)
        return original_handler(name, arguments, **kwargs)

    monkeypatch.setattr(cli_module, "handle_build_tool", handler_wrapper)

    assert cli_module.knowledge_main(
        ["build", "status", "--workspace-root", str(root), "--workspace-id", "research-vault", "--operation-id", operation_id]
    ) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "completed"
    assert payload["workspace_id"] == "research-vault"
    assert payload["operation_id"] == operation_id
    assert payload["data"] == {
        "mode": "llmwiki_only",
        "stage": "completed",
        "progress": 1.0,
        "error": {"code": "error", "message": "error", "retryable": False},
        "retryable": False,
        "artifact_refs": [],
        "debug_paths": {"artifacts": []},
    }
    assert calls == ["knowledge_build_status"]


def test_phaseg27_knowledge_build_write_aliases_reuse_build_mcp_handler(tmp_path, monkeypatch, capsys):
    import data_service.__main__ as cli_module
    from data_service.mcp_workspace_runtime import WorkspaceRuntime

    root = tmp_path / "managed"
    runtime = WorkspaceRuntime(root / "_default", workspace_root=root)
    workspace_path = root / "research-vault"
    runtime.ensure_workspace_meta(workspace_path, name="Research Vault")

    calls = []
    original_handler = cli_module.handle_build_tool

    def handler_wrapper(name, arguments, **kwargs):
        calls.append((name, arguments))
        return original_handler(name, arguments, **kwargs)

    monkeypatch.setattr(cli_module, "handle_build_tool", handler_wrapper)
    monkeypatch.setattr(cli_module.BuildRuntime, "ensure_build_worker", lambda self, workspace: None)

    assert cli_module.knowledge_main(
        ["build", "start", "--workspace-root", str(root), "--workspace-id", "research-vault", "--mode", "llmwiki_only"]
    ) == 0
    start_payload = json.loads(capsys.readouterr().out)
    started_operation_id = start_payload["operation_id"]
    assert start_payload["status"] == "queued"
    assert start_payload["workspace_id"] == "research-vault"
    assert start_payload["data"] == {"mode": "llmwiki_only", "stage": "queued", "progress": 0.0}

    assert cli_module.knowledge_main(
        [
            "build",
            "cancel",
            "--workspace-root",
            str(root),
            "--workspace-id",
            "research-vault",
            "--operation-id",
            started_operation_id,
            "--reason",
            "phaseg27 done",
        ]
    ) == 0
    cancel_payload = json.loads(capsys.readouterr().out)
    assert cancel_payload["status"] == "cancelled"
    assert cancel_payload["workspace_id"] == "research-vault"
    assert cancel_payload["operation_id"] == started_operation_id
    assert cancel_payload["data"]["stage"] == "cancelled"
    assert cancel_payload["data"]["retryable"] is False

    assert calls == [
        (
            "knowledge_build_start",
            {"workspace_id": "research-vault", "mode": "llmwiki_only"},
        ),
        (
            "knowledge_build_cancel",
            {"workspace_id": "research-vault", "operation_id": started_operation_id, "reason": "phaseg27 done"},
        ),
    ]
    assert started_operation_id.startswith("op_")


def test_phaseg22_knowledge_graph_snapshot_alias_reuses_session_mcp_handler(tmp_path, monkeypatch, capsys):
    import data_service.__main__ as cli_module
    from data_service.mcp_workspace_runtime import WorkspaceRuntime

    root = tmp_path / "managed"
    runtime = WorkspaceRuntime(root / "_default", workspace_root=root)
    workspace_path = root / "research-vault"
    runtime.ensure_workspace_meta(workspace_path, name="Research Vault")

    calls = []
    original_handler = cli_module.handle_session_tool

    def handler_wrapper(name, arguments, **kwargs):
        calls.append((name, arguments))
        return original_handler(name, arguments, **kwargs)

    monkeypatch.setattr(cli_module, "handle_session_tool", handler_wrapper)

    assert cli_module.knowledge_main(
        ["graph", "snapshot", "--workspace-root", str(root), "--workspace-id", "research-vault", "--max-nodes", "5"]
    ) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "ok"
    assert payload["workspace_id"] == "research-vault"
    assert payload["data"]["scope"] == "workspace"
    assert {"graph_model_version", "nodes", "edges", "communities", "stats"} <= set(payload["data"])
    assert calls == [
        (
            "knowledge_graph_snapshot",
            {
                "workspace_id": "research-vault",
                "workspace": None,
                "scope": "workspace",
                "max_nodes": 5,
            },
        )
    ]


def test_phaseg23_knowledge_trace_source_alias_reuses_source_trace_contract(tmp_path, monkeypatch, capsys):
    import data_service.__main__ as cli_module

    workspace = tmp_path / "workspace"
    doc = tmp_path / "phaseg23-trace.md"
    doc.write_text("# PhaseG23 Trace\n\nPhaseG23 opens the knowledge trace source alias.\n", encoding="utf-8")
    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])
    service.run_default_pipeline(plan)
    source_id = service.read_distill_bundle(limit=5)["sources"][0]["source_id"]

    calls = []
    original_trace = cli_module.source_trace_payload

    def trace_wrapper(*args, **kwargs):
        calls.append((args[1], kwargs.get("limit")))
        return original_trace(*args, **kwargs)

    monkeypatch.setattr(cli_module, "source_trace_payload", trace_wrapper)

    assert cli_module.knowledge_main(
        ["trace", "source", "--workspace", str(workspace), "--source-id", source_id, "--limit", "5"]
    ) == 0
    cli_payload = json.loads(capsys.readouterr().out)
    helper_payload = original_trace(service, source_id, limit=5)

    assert calls == [(source_id, 5)]
    assert cli_payload == helper_payload
    assert {"workspace", "source_id", "source", "distill", "llmwiki", "graphrag", "trace_summary"} <= set(cli_payload)

    parser = cli_module._build_knowledge_parser()
    subparser_action = next(action for action in parser._actions if getattr(action, "choices", None))
    assert set(subparser_action.choices) == {"quality", "query", "workspace", "source", "build", "graph", "trace", "code"}
    trace_parser = subparser_action.choices["trace"]
    trace_action = next(action for action in trace_parser._actions if getattr(action, "choices", None))
    assert set(trace_action.choices) == {"source"}


def test_phaseg24_graph_advanced_cli_migration_window_keeps_advanced_subcommands_planned():
    import data_service.__main__ as cli_module

    graph_contract = (V15_DOCS_ROOT / "graph-cli-contract.md").read_text(encoding="utf-8")
    remaining_plan = Path("docs/V1.5/PHASE-G24-G31-REMAINING-DEVELOPMENT-PLAN-2026-05-12.md").read_text(encoding="utf-8")

    parser = cli_module._build_knowledge_parser()
    subparser_action = next(action for action in parser._actions if getattr(action, "choices", None))
    graph_parser = subparser_action.choices["graph"]
    graph_action = next(action for action in graph_parser._actions if getattr(action, "choices", None))

    assert set(graph_action.choices) == {"snapshot", "neighbors", "community", "query", "session"}

    data_service_parser = cli_module._build_parser()
    data_service_action = next(action for action in data_service_parser._actions if getattr(action, "choices", None))
    assert "graph" not in set(data_service_action.choices)

    for required_text in [
        "PhaseG24 固化 `knowledge graph` advanced 子命令迁移窗口",
        "knowledge graph neighbors",
        "knowledge graph community",
        "knowledge graph query",
        "knowledge graph session",
        "PhaseG24 只固化 planned contract，不开放上述子命令",
        "不把 graph 算法逻辑回填到 `data_service`",
    ]:
        assert required_text in graph_contract
    assert "PhaseG24：Graph advanced CLI 迁移窗口" in remaining_plan


def test_knowledge_api_workspace_and_source_lifecycle(tmp_path, monkeypatch):
    managed_root = tmp_path / "managed"
    source_root = tmp_path / "row"
    source_root.mkdir(parents=True)
    source_file = source_root / "notes.md"
    source_file.write_text("# Personal Knowledge\n\nGraphRAG and llmWiki notes.\n", encoding="utf-8")
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(managed_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_SOURCE_ROOTS", str(source_root))

    client = TestClient(app)

    create_response = client.post(
        "/api/v1/knowledge/workspaces/create",
        json={"name": "Research Vault", "bound_paths": [str(source_root)], "tags": ["personal"]},
    )
    assert create_response.status_code == 200
    create_payload = create_response.json()
    assert create_payload["status"] == "ok"
    workspace = create_payload["data"]["workspace"]
    assert workspace["workspace_id"] == "research-vault"
    assert workspace["debug_paths"]["bound_paths"] == [str(source_root.resolve())]
    _assert_no_public_path_keys(create_payload)
    workspace_path = workspace["debug_paths"]["workspace_path"]

    list_response = client.post("/api/v1/knowledge/workspaces/list", json={"limit": 10})
    assert list_response.status_code == 200
    list_payload = list_response.json()
    assert any(item["workspace_id"] == "research-vault" for item in list_payload["data"]["items"])
    _assert_no_public_path_keys(list_payload)

    describe_empty_response = client.post(
        "/api/v1/knowledge/workspaces/describe",
        json={"workspace_id": "research-vault"},
    )
    assert describe_empty_response.status_code == 200
    assert describe_empty_response.json()["data"]["source_summary"]["source_count"] == 0

    import_response = client.post(
        "/api/v1/knowledge/sources/import",
        json={"workspace": workspace_path, "paths": [str(source_file)], "metadata": {"from": "api-test"}},
    )
    assert import_response.status_code == 200
    import_payload = import_response.json()
    imported = import_payload["data"]["sources"][0]
    assert imported["ingest_status"] == "pending"
    assert imported["debug_paths"]["original_path"] == str(source_file.resolve())
    _assert_no_public_path_keys(import_payload)

    sources_response = client.post(
        "/api/v1/knowledge/sources/list",
        json={"workspace": workspace_path, "limit": 20},
    )
    assert sources_response.status_code == 200
    sources_payload = sources_response.json()
    assert sources_payload["data"]["items"][0]["source_id"] == imported["source_id"]
    assert sources_payload["data"]["items"][0]["status"] == "active"

    describe_response = client.post(
        "/api/v1/knowledge/workspaces/describe",
        json={"workspace": workspace_path},
    )
    assert describe_response.status_code == 200
    assert describe_response.json()["data"]["source_summary"]["source_count"] == 1

    remove_response = client.post(
        "/api/v1/knowledge/sources/remove",
        json={"workspace": workspace_path, "source_id": imported["source_id"], "reason": "test"},
    )
    assert remove_response.status_code == 200
    assert remove_response.json()["data"]["source"]["status"] == "removed"


def test_knowledge_api_build_operation_lifecycle(tmp_path, monkeypatch):
    managed_root = tmp_path / "managed"
    source_root = tmp_path / "sources"
    source_root.mkdir(parents=True)
    source_file = source_root / "build.md"
    source_file.write_text("# Build Note\n\nHTTP build queue content.", encoding="utf-8")
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(managed_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_SOURCE_ROOTS", str(source_root))

    client = TestClient(app)
    created = client.post("/api/v1/knowledge/workspaces/create", json={"name": "HTTP Build KB"}).json()
    workspace = created["data"]["workspace"]["debug_paths"]["workspace_path"]
    imported = client.post(
        "/api/v1/knowledge/sources/import",
        json={"workspace": workspace, "paths": [str(source_file)]},
    )
    assert imported.status_code == 200

    started = client.post(
        "/api/v1/knowledge/build/start",
        json={"workspace": workspace, "mode": "llmwiki_only"},
    )
    assert started.status_code == 200
    started_payload = started.json()
    assert started_payload["status"] == "queued"
    assert started_payload["operation_id"]
    assert started_payload["data"]["stage"] == "queued"
    _assert_no_public_path_keys(started_payload)

    status_payload = None
    for _ in range(100):
        status = client.post(
            "/api/v1/knowledge/build/status",
            json={"workspace": workspace, "operation_id": started_payload["operation_id"]},
        )
        assert status.status_code == 200
        status_payload = status.json()
        if status_payload["status"] in {"completed", "failed", "blocked", "cancelled"}:
            break
        time.sleep(0.05)

    assert status_payload is not None
    assert status_payload["status"] == "completed"
    assert status_payload["data"]["stage"] == "completed"
    assert status_payload["data"]["progress"] == 1.0
    assert status_payload["data"]["retryable"] is False
    _assert_no_public_path_keys(status_payload)

    missing_status = client.post(
        "/api/v1/knowledge/build/status",
        json={"workspace": workspace, "operation_id": "missing-op"},
    )
    assert missing_status.status_code == 200
    missing_payload = missing_status.json()
    assert missing_payload["status"] == "blocked"
    assert missing_payload["data"]["error"]["code"] == "unknown_operation_id"

    sources = client.post("/api/v1/knowledge/sources/list", json={"workspace": workspace, "limit": 20})
    assert sources.status_code == 200
    assert sources.json()["data"]["items"][0]["ingest_status"] == "built"

    completed_cancel = client.post(
        "/api/v1/knowledge/build/cancel",
        json={"workspace": workspace, "operation_id": started_payload["operation_id"], "reason": "test"},
    )
    assert completed_cancel.status_code == 200
    assert completed_cancel.json()["status"] == "completed"
    assert completed_cancel.json()["warnings"]


def test_knowledge_api_directory_scan_detects_changes(tmp_path, monkeypatch):
    managed_root = tmp_path / "managed"
    source_root = tmp_path / "bound"
    source_root.mkdir(parents=True)
    first = source_root / "first.md"
    first.write_text("# First\n\nInitial note.", encoding="utf-8")
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(managed_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_SOURCE_ROOTS", str(source_root))

    client = TestClient(app)
    created = client.post(
        "/api/v1/knowledge/workspaces/create",
        json={"name": "Directory Watch KB", "bound_paths": [str(source_root)]},
    )
    assert created.status_code == 200
    workspace = created.json()["data"]["workspace"]["debug_paths"]["workspace_path"]

    initial_scan = client.post(
        "/api/v1/knowledge/directories/scan",
        json={"workspace": workspace, "limit": 20},
    )
    assert initial_scan.status_code == 200
    initial_payload = initial_scan.json()["data"]
    assert initial_payload["summary"]["new_count"] == 1
    assert initial_payload["summary"]["pending_count"] == 1
    _assert_no_public_path_keys(initial_scan.json())

    first.write_text("# First\n\nModified note.", encoding="utf-8")
    second = source_root / "second.md"
    second.write_text("# Second\n\nNew note.", encoding="utf-8")
    second_scan = client.post(
        "/api/v1/knowledge/directories/scan",
        json={"workspace": workspace, "limit": 20},
    )
    assert second_scan.status_code == 200
    second_payload = second_scan.json()["data"]
    assert second_payload["summary"]["modified_count"] == 1
    assert second_payload["summary"]["new_count"] == 1
    assert second_payload["summary"]["pending_count"] == 2
    _assert_no_public_path_keys(second_scan.json())

    first.unlink()
    third_scan = client.post(
        "/api/v1/knowledge/directories/scan",
        json={"workspace": workspace, "limit": 20},
    )
    assert third_scan.status_code == 200
    third_payload = third_scan.json()["data"]
    assert third_payload["summary"]["deleted_count"] == 1
    assert third_payload["summary"]["pending_count"] == 1


def test_knowledge_api_summary_graph_query_and_page(tmp_path):
    workspace = tmp_path / "workspace"
    doc = tmp_path / "notes.md"
    doc.write_text("# ComfyUI\n\nComfyUI works with OpenClaw.\n", encoding="utf-8")

    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])
    service.run_default_pipeline(plan)

    client = TestClient(app)

    summary_response = client.post("/api/v1/knowledge/summary", json={"workspace": str(workspace)})
    assert summary_response.status_code == 200
    summary_payload = summary_response.json()
    assert "summary_markdown" in summary_payload
    assert "llmwiki_pages" in summary_payload
    assert "quality" in summary_payload
    assert summary_payload["quality"]["graphrag"]["execution_owner"] == "app.graphrag"

    graph_response = client.post("/api/v1/knowledge/graph", json={"workspace": str(workspace), "max_nodes": 20})
    assert graph_response.status_code == 200
    graph_payload = graph_response.json()
    assert graph_payload["graph_model_version"] == DataService.GRAPH_QUERY_MODEL_VERSION
    assert "nodes" in graph_payload
    assert "communities" in graph_payload
    assert "quality_diagnostics" in graph_payload
    assert {"top_communities", "weak_communities", "isolated_nodes", "low_value_nodes"}.issubset(
        graph_payload["quality_diagnostics"].keys()
    )

    distill_response = client.post("/api/v1/knowledge/distill", json={"workspace": str(workspace), "limit": 5})
    assert distill_response.status_code == 200
    distill_payload = distill_response.json()
    assert distill_payload["manifest"]["source_count"] == 1
    assert distill_payload["units"]
    assert distill_payload["source_profiles"]
    assert distill_payload["provenance_overview"]["available_source_count"] == 1
    sources_response = client.post("/api/v1/knowledge/sources/list", json={"workspace": str(workspace), "limit": 20})
    assert sources_response.status_code == 200
    sources_payload = sources_response.json()
    assert sources_payload["data"]["items"][0]["ingest_status"] == "indexed"
    filtered_distill_response = client.post(
        "/api/v1/knowledge/distill",
        json={"workspace": str(workspace), "limit": 5, "kind": "topic_candidate", "min_importance": 0.1},
    )
    assert filtered_distill_response.status_code == 200
    filtered_distill_payload = filtered_distill_response.json()
    assert filtered_distill_payload["filters"]["kind"] == "topic_candidate"
    assert all(unit["kind"] == "topic_candidate" for unit in filtered_distill_payload["units"])
    assert all(float(unit["importance"]) >= 0.1 for unit in filtered_distill_payload["units"])
    typed_distill_response = client.post(
        "/api/v1/knowledge/distill",
        json={"workspace": str(workspace), "limit": 5, "typed_unit_type": "concept"},
    )
    assert typed_distill_response.status_code == 200
    typed_distill_payload = typed_distill_response.json()
    assert typed_distill_payload["filters"]["typed_unit_type"] == "concept"
    assert typed_distill_payload["units"]
    assert all(unit["typed_unit"]["type"] == "concept" for unit in typed_distill_payload["units"])
    authority_distill_response = client.post(
        "/api/v1/knowledge/distill",
        json={"workspace": str(workspace), "limit": 5, "authority": "PRIMARY_DOC", "min_source_density": 0.5},
    )
    assert authority_distill_response.status_code == 200
    authority_distill_payload = authority_distill_response.json()
    assert authority_distill_payload["filters"]["authority"] == "PRIMARY_DOC"
    assert all(unit["authority"] == "PRIMARY_DOC" for unit in authority_distill_payload["units"])
    assert all(float(unit["source_density_score"]) >= 0.5 for unit in authority_distill_payload["units"])

    query_response = client.post(
        "/api/v1/knowledge/query",
        json={"workspace": str(workspace), "query": "ComfyUI", "mode": "hybrid", "top_k": 5},
    )
    assert query_response.status_code == 200
    query_payload = query_response.json()
    assert query_payload["mode"] == "hybrid"
    assert query_payload["hits"]
    assert query_payload["engine_payloads"]["graphrag"]["graph_model_version"] == DataService.GRAPH_QUERY_MODEL_VERSION

    first_page = summary_payload["llmwiki_pages"][0]["slug"]
    page_response = client.post("/api/v1/knowledge/page", json={"workspace": str(workspace), "slug": first_page})
    assert page_response.status_code == 200
    page_payload = page_response.json()
    assert page_payload["page"] is not None

    source_id = distill_payload["sources"][0]["source_id"]
    distill_source_response = client.post(
        "/api/v1/knowledge/distill",
        json={"workspace": str(workspace), "source_id": source_id, "limit": 5},
    )
    assert distill_source_response.status_code == 200
    source_payload = distill_source_response.json()["source"]
    assert source_payload["source_id"] == source_id
    assert source_payload["profile_debug"]["summary_sentences"]
    assert source_payload["provenance_summary"]["path_count"] >= 1

    trace_response = client.post(
        "/api/v1/knowledge/source/trace",
        json={"workspace": str(workspace), "source_id": source_id, "limit": 8},
    )
    assert trace_response.status_code == 200
    trace_payload = trace_response.json()
    assert trace_payload["source_id"] == source_id
    assert trace_payload["distill"]["unit_count"] >= 1
    assert "pages" in trace_payload["llmwiki"]
    assert "nodes" in trace_payload["graphrag"]
    assert trace_payload["trace_summary"]["unit_count"] >= 1

    low_signal_audit_response = client.post(
        "/api/v1/knowledge/quality/low-signal-audit",
        json={"workspace": str(workspace), "limit": 8},
    )
    assert low_signal_audit_response.status_code == 200
    low_signal_audit_payload = low_signal_audit_response.json()
    assert low_signal_audit_payload["overall_status"] in {"passed", "warning", "failed"}
    assert low_signal_audit_payload["metrics"]["source_count"] == 1
    assert low_signal_audit_payload["metrics"]["title_derived_conclusion_count"] == 0
    assert {
        "zero_unit_count",
        "title_derived_conclusion_count",
        "disallowed_title_derived_kind_count",
        "llmwiki_low_signal_title_leak_count",
        "graphrag_low_signal_title_leak_count",
    }.issubset({item["check_id"] for item in low_signal_audit_payload["checks"]})

    missing_distill_response = client.post(
        "/api/v1/knowledge/distill",
        json={"workspace": str(workspace), "source_id": "missing-source", "limit": 5},
    )
    assert missing_distill_response.status_code == 404

    missing_trace_response = client.post(
        "/api/v1/knowledge/source/trace",
        json={"workspace": str(workspace), "source_id": "missing-source", "limit": 5},
    )
    assert missing_trace_response.status_code == 404

    boundary_response = client.post("/api/v1/knowledge/boundary", json={"workspace": str(workspace)})
    assert boundary_response.status_code == 200
    boundary_payload = boundary_response.json()
    assert boundary_payload["contracts"]["llmwiki_input_contract"]["exists"] is True
    assert boundary_payload["contracts"]["graphrag_input_contract"]["exists"] is True
    assert boundary_payload["contracts"]["graphrag_execution_owner"]["exists"] is True
    assert boundary_payload["capability_migration_table"]

    feedback_response = client.post(
        "/api/v1/knowledge/quality/feedback",
        json={
            "workspace": str(workspace),
            "target_type": "page",
            "target_id": first_page,
            "action": "needs_review",
            "label": "ComfyUI",
            "reason": "人工验收标记",
            "metadata": {"from": "api-test"},
        },
    )
    assert feedback_response.status_code == 200
    feedback_payload = feedback_response.json()
    assert feedback_payload["feedback"]["target_id"] == first_page
    assert feedback_payload["summary"]["feedback_count"] == 1

    feedback_list_response = client.post(
        "/api/v1/knowledge/quality/feedback/list",
        json={"workspace": str(workspace), "limit": 10, "target_type": "page"},
    )
    assert feedback_list_response.status_code == 200
    feedback_list_payload = feedback_list_response.json()
    assert feedback_list_payload["filtered_count"] == 1
    assert feedback_list_payload["items"][0]["action"] == "needs_review"

    correction_build_response = client.post(
        "/api/v1/knowledge/quality/corrections/build",
        json={"workspace": str(workspace)},
    )
    assert correction_build_response.status_code == 200
    correction_build_payload = correction_build_response.json()
    assert correction_build_payload["summary"]["rule_count"] == 1
    assert correction_build_payload["rules"][0]["rule_type"] == "review"

    correction_list_response = client.post(
        "/api/v1/knowledge/quality/corrections",
        json={"workspace": str(workspace), "limit": 10, "status": "draft"},
    )
    assert correction_list_response.status_code == 200
    correction_list_payload = correction_list_response.json()
    assert correction_list_payload["filtered_count"] == 1
    assert correction_list_payload["items"][0]["status"] == "draft"

    review_response = client.post(
        "/api/v1/knowledge/quality/corrections/review",
        json={
            "workspace": str(workspace),
            "rule_id": correction_list_payload["items"][0]["rule_id"],
            "status": "approved",
            "reviewer": "api-test",
            "note": "确认复核",
        },
    )
    assert review_response.status_code == 200
    review_payload = review_response.json()
    assert review_payload["rule"]["status"] == "approved"
    assert review_payload["summary"]["status_counts"]["approved"] == 1
    assert review_payload["correction_plan"]["source_rule_count"] == 1

    plan_response = client.post(
        "/api/v1/knowledge/quality/corrections/plan",
        json={"workspace": str(workspace)},
    )
    assert plan_response.status_code == 200
    plan_payload = plan_response.json()
    assert plan_payload["source_rule_count"] == 1
    assert plan_payload["summary"]["action_count"] == 1
    assert plan_payload["actions"][0]["action"] == "flag_reviewed_target"

    revoke_response = client.post(
        "/api/v1/knowledge/quality/corrections/review",
        json={
            "workspace": str(workspace),
            "rule_id": correction_list_payload["items"][0]["rule_id"],
            "status": "revoked",
            "reviewer": "api-test",
            "note": "撤回误批准",
        },
    )
    assert revoke_response.status_code == 200
    revoke_payload = revoke_response.json()
    assert revoke_payload["rule"]["status"] == "revoked"
    assert revoke_payload["correction_plan"]["source_rule_count"] == 0


def test_knowledge_api_ingest_directory_and_reset(tmp_path):
    root = tmp_path / "knowledge"
    workspace = root / "workspace"
    source_dir = root / "row" / "deepseek_split"
    source_dir.mkdir(parents=True)
    (source_dir / "a.json").write_text('{"title":"OpenClaw"}', encoding="utf-8")
    (source_dir / "b.md").write_text("# ComfyUI\n\nGraph notes.\n", encoding="utf-8")

    client = TestClient(app)

    ingest_response = client.post(
        "/api/v1/knowledge/ingest",
        json={"workspace": str(workspace), "paths": [str(source_dir)]},
    )
    assert ingest_response.status_code == 200
    ingest_payload = ingest_response.json()
    assert ingest_payload["results"]

    reset_bad = client.post(
        "/api/v1/knowledge/reset",
        json={"workspace": str(workspace), "confirmation": "Nope"},
    )
    assert reset_bad.status_code == 400

    reset_ok = client.post(
        "/api/v1/knowledge/reset",
        json={"workspace": str(workspace), "confirmation": "Delete"},
    )
    assert reset_ok.status_code == 200
    assert reset_ok.json()["row_preserved"] is True
    assert (source_dir / "a.json").exists()


def test_knowledge_api_ingest_supports_app_graphrag_owner(tmp_path):
    root = tmp_path / "knowledge"
    workspace = root / "workspace"
    source_dir = root / "row" / "deepseek_split"
    source_dir.mkdir(parents=True)
    (source_dir / "a.json").write_text('{"title":"OpenClaw"}', encoding="utf-8")

    client = TestClient(app)

    ingest_response = client.post(
        "/api/v1/knowledge/ingest",
        json={
            "workspace": str(workspace),
            "paths": [str(source_dir)],
            "graphrag_execution_owner": "app.graphrag",
        },
    )
    assert ingest_response.status_code == 200
    ingest_payload = ingest_response.json()
    graphrag_result = next(item for item in ingest_payload["results"] if item["engine"] == "graphrag")
    assert graphrag_result["status"] == "indexed"
    assert graphrag_result["meta"]["execution_owner"] == "app.graphrag"


def test_knowledge_api_graphrag_execute(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    doc = tmp_path / "notes.md"
    doc.write_text("# OpenClaw\n\nOpenClaw works.\n", encoding="utf-8")

    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)], graphrag_execution_owner="app.graphrag")
    monkeypatch.setattr("app.graphrag.service.data_service_runner.shutil.which", lambda _: None)
    service.run_default_pipeline(plan)

    def fake_runner(request_path):
        return {
            "status": "completed",
            "request_path": str(request_path),
            "compat_state": {"state_db": str(service.layout.graphrag_state_dir / "graphrag.db")},
        }

    monkeypatch.setattr("app.graphrag.service.run_data_service_execution_request", fake_runner)

    client = TestClient(app)
    response = client.post("/api/v1/knowledge/graphrag/execute", json={"workspace": str(workspace)})

    assert response.status_code == 200
    assert response.json()["status"] == "completed"
