from fastapi.testclient import TestClient

from app.main import app
from data_service import DataService


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

    distill_response = client.post("/api/v1/knowledge/distill", json={"workspace": str(workspace), "limit": 5})
    assert distill_response.status_code == 200
    distill_payload = distill_response.json()
    assert distill_payload["manifest"]["source_count"] == 1
    assert distill_payload["units"]
    assert distill_payload["source_profiles"]
    assert distill_payload["provenance_overview"]["available_source_count"] == 1
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

    missing_distill_response = client.post(
        "/api/v1/knowledge/distill",
        json={"workspace": str(workspace), "source_id": "missing-source", "limit": 5},
    )
    assert missing_distill_response.status_code == 404

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
