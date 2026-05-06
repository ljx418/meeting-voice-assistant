import time

from fastapi.testclient import TestClient

from app.config import config
from app.main import app
from data_service import DataService


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
    assert workspace["bound_paths"] == [str(source_root.resolve())]

    list_response = client.post("/api/v1/knowledge/workspaces/list", json={"limit": 10})
    assert list_response.status_code == 200
    list_payload = list_response.json()
    assert any(item["workspace_id"] == "research-vault" for item in list_payload["data"]["items"])

    describe_empty_response = client.post(
        "/api/v1/knowledge/workspaces/describe",
        json={"workspace_id": "research-vault"},
    )
    assert describe_empty_response.status_code == 200
    assert describe_empty_response.json()["data"]["source_summary"]["source_count"] == 0

    import_response = client.post(
        "/api/v1/knowledge/sources/import",
        json={"workspace": workspace["workspace_path"], "paths": [str(source_file)], "metadata": {"from": "api-test"}},
    )
    assert import_response.status_code == 200
    import_payload = import_response.json()
    imported = import_payload["data"]["sources"][0]
    assert imported["ingest_status"] == "pending"
    assert imported["original_path"] == str(source_file.resolve())

    sources_response = client.post(
        "/api/v1/knowledge/sources/list",
        json={"workspace": workspace["workspace_path"], "limit": 20},
    )
    assert sources_response.status_code == 200
    sources_payload = sources_response.json()
    assert sources_payload["data"]["items"][0]["source_id"] == imported["source_id"]
    assert sources_payload["data"]["items"][0]["status"] == "active"

    describe_response = client.post(
        "/api/v1/knowledge/workspaces/describe",
        json={"workspace": workspace["workspace_path"]},
    )
    assert describe_response.status_code == 200
    assert describe_response.json()["data"]["source_summary"]["source_count"] == 1

    remove_response = client.post(
        "/api/v1/knowledge/sources/remove",
        json={"workspace": workspace["workspace_path"], "source_id": imported["source_id"], "reason": "test"},
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
    workspace = created["data"]["workspace"]["workspace_path"]
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
    workspace = created.json()["data"]["workspace"]["workspace_path"]

    initial_scan = client.post(
        "/api/v1/knowledge/directories/scan",
        json={"workspace": workspace, "limit": 20},
    )
    assert initial_scan.status_code == 200
    initial_payload = initial_scan.json()["data"]
    assert initial_payload["summary"]["new_count"] == 1
    assert initial_payload["summary"]["pending_count"] == 1

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
