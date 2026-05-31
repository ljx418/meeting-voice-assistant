from fastapi.testclient import TestClient

from app.main import app
from test_target_http_folder_collections import _setup_client, _write_fixture_tree
from test_target_http_source_preview import _assert_no_internal_paths, _create_workspace


def test_v13c_folder_summary_workflow_dry_run_success(tmp_path, monkeypatch):
    client, source_root = _setup_client(tmp_path, monkeypatch)
    tech = _write_fixture_tree(source_root)
    workspace_id = _create_workspace(client, "RN V1.3 Workflow Runtime")

    response = client.post(
        f"/api/workspaces/{workspace_id}/workflows/folder-summary/runs",
        json={
            "authorized_root": str(tech),
            "permission_grant_id": "grant_runtime",
            "dry_run": True,
            "recursive": True,
            "include_extensions": [".md", ".txt"],
            "follow_symlinks": False,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["next_actions"] == ["review_workflow_run_report", "confirm_extract_before_summary_generation"]
    data = payload["data"]
    workflow = data["workflow"]
    run = data["run"]
    collection = data["collection"]

    assert workflow["template_id"] == "folder_summary_v1"
    assert workflow["status"] == "ready"
    assert workflow["required_permissions"] == ["folder:scan"]
    assert run["workflow_id"] == workflow["workflow_id"]
    assert run["status"] == "completed"
    assert run["dry_run"] is True
    assert run["artifacts"] == []
    assert run["run_report"]["generated_artifact_count"] == 0
    assert run["run_report"]["extracted_file_count"] == 0
    assert run["run_report"]["manifest_file_count"] == len(collection["files"])
    assert {step["name"]: step["status"] for step in workflow["steps"]} == {
        "scan_folder": "completed",
        "extract_text": "skipped",
        "group_by_subfolder": "completed",
        "create_sources": "skipped",
        "summarize_folder": "skipped",
        "generate_index_report": "skipped",
        "write_artifacts": "skipped",
    }
    assert all(step["started_at"] and step["finished_at"] for step in workflow["steps"])
    assert all(step["retry_count"] == 0 for step in workflow["steps"])
    assert all(isinstance(step["artifact_refs"], list) for step in workflow["steps"])
    _assert_no_internal_paths(payload)


def test_v13c_folder_summary_workflow_rejects_non_dry_run_and_unapproved_extensions(tmp_path, monkeypatch):
    client, source_root = _setup_client(tmp_path, monkeypatch)
    tech = _write_fixture_tree(source_root)
    workspace_id = _create_workspace(client, "RN V1.3 Workflow Guardrails")

    non_dry_run = client.post(
        f"/api/workspaces/{workspace_id}/workflows/folder-summary/runs",
        json={"authorized_root": str(tech), "permission_grant_id": "grant_runtime", "dry_run": False},
    )
    assert non_dry_run.status_code == 422
    assert "VALIDATION_ERROR" in non_dry_run.json()["detail"]

    unsupported = client.post(
        f"/api/workspaces/{workspace_id}/workflows/folder-summary/runs",
        json={"authorized_root": str(tech), "permission_grant_id": "grant_runtime", "include_extensions": [".json"]},
    )
    assert unsupported.status_code == 422
    assert "VALIDATION_ERROR" in unsupported.json()["detail"]


def test_v13c_folder_summary_workflow_route_exposed_without_knowledge_feature_route():
    routes = {(method, route.path) for route in app.routes for method in getattr(route, "methods", set())}
    assert ("POST", "/api/workspaces/{workspace_id}/workflows/folder-summary/runs") in routes
    assert all("/api/v1/knowledge" not in path or "folder-summary" not in path for _, path in routes)


def test_v13d_folder_summary_generator_success_after_confirm_extract(tmp_path, monkeypatch):
    client, source_root = _setup_client(tmp_path, monkeypatch)
    tech = _write_fixture_tree(source_root)
    workspace_id = _create_workspace(client, "RN V1.3 Summary Generator")

    response = client.post(
        f"/api/workspaces/{workspace_id}/workflows/folder-summary/runs",
        json={
            "authorized_root": str(tech),
            "permission_grant_id": "grant_summary",
            "dry_run": False,
            "confirm_extract": True,
            "recursive": True,
            "include_extensions": [".md", ".txt"],
            "follow_symlinks": False,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    data = payload["data"]
    run = data["run"]
    workflow = data["workflow"]
    artifacts = run["artifacts"]
    assert run["dry_run"] is False
    assert run["run_report"]["extracted_file_count"] == len(data["collection"]["files"])
    assert run["run_report"]["generated_artifact_count"] == len(artifacts)
    assert len(artifacts) >= 2
    step_status = {step["name"]: step["status"] for step in workflow["steps"]}
    assert step_status["create_sources"] == "completed"
    assert step_status["summarize_folder"] == "completed"
    assert {artifact["status"] for artifact in artifacts} == {"ready"}
    assert artifacts[0]["artifact_type"] == "root_summary"
    assert artifacts[0]["schema_version"] == "v1.3-summary-artifact"
    assert artifacts[0]["coverage"]["evidence_ref_count"] >= 1
    first_ref = artifacts[0]["evidence_refs"][0]
    assert first_ref["evidence_status"] == "source_unit_span"
    assert first_ref["source_id"].startswith("src_")
    assert first_ref["unit_id"].startswith("unit_")
    assert first_ref["evidence_id"].startswith("ev_")
    assert "根目录总览" in artifacts[0]["markdown"]
    _assert_no_internal_paths(payload)

    unit_response = client.get(
        f"/api/workspaces/{workspace_id}/sources/{first_ref['source_id']}/units/{first_ref['unit_id']}"
    )
    assert unit_response.status_code == 200
    evidence_response = client.get(
        f"/api/workspaces/{workspace_id}/sources/{first_ref['source_id']}/units/{first_ref['unit_id']}/evidence/{first_ref['evidence_id']}"
    )
    assert evidence_response.status_code == 200
    span = evidence_response.json()["data"]["evidence_span"]
    assert span["source_id"] == first_ref["source_id"]
    assert span["unit_id"] == first_ref["unit_id"]
    assert span["evidence_id"] == first_ref["evidence_id"]


def test_v13d_folder_summary_generator_requires_confirm_extract(tmp_path, monkeypatch):
    client, source_root = _setup_client(tmp_path, monkeypatch)
    tech = _write_fixture_tree(source_root)
    workspace_id = _create_workspace(client, "RN V1.3 Summary Confirm")

    response = client.post(
        f"/api/workspaces/{workspace_id}/workflows/folder-summary/runs",
        json={"authorized_root": str(tech), "permission_grant_id": "grant_summary", "dry_run": False},
    )

    assert response.status_code == 422
    assert "confirm_extract=true" in response.json()["detail"]
