from fastapi.testclient import TestClient

from app.main import app
from test_target_http_source_preview import _assert_no_internal_paths, _create_workspace


def _setup_client(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    return TestClient(app)


def test_v13f_agent_workflow_draft_for_registered_folder_summary_template(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    workspace_id = _create_workspace(client, "RN V1.3 Agent Draft")

    response = client.post(
        f"/api/workspaces/{workspace_id}/agent-workflows/draft",
        json={"user_goal": "递归总结 Desktop/技术分享，每个子文件夹生成一份总结。"},
    )

    assert response.status_code == 200
    payload = response.json()
    data = payload["data"]
    assert data["task"]["status"] == "awaiting_approval"
    assert data["workflow"]["template_id"] == "folder_summary_v1"
    assert data["workflow"]["status"] == "draft"
    assert data["workflow"]["draft_parameters"] == {
        "authorized_root_hint": "Desktop/技术分享",
        "include_extensions": [".md", ".txt"],
        "exclude_globs": ["**/*.tmp"],
        "follow_symlinks": False,
        "requires_user_confirmation": True,
    }
    assert [step["status"] for step in data["workflow"]["steps"]] == ["pending"] * 7
    assert payload["next_actions"] == ["review_workflow_draft", "confirm_folder_permission_before_run"]
    _assert_no_internal_paths(payload)


def test_v13f_agent_workflow_draft_rejects_unregistered_goal(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    workspace_id = _create_workspace(client, "RN V1.3 Agent Guardrail")

    response = client.post(
        f"/api/workspaces/{workspace_id}/agent-workflows/draft",
        json={"user_goal": "帮我自由调用工具整理所有文件。"},
    )

    assert response.status_code == 422
    assert "registered folder_summary_v1 template" in response.json()["detail"]


def test_v13f_agent_workflow_draft_route_exposed_without_knowledge_feature_route():
    routes = {(method, route.path) for route in app.routes for method in getattr(route, "methods", set())}
    assert ("POST", "/api/workspaces/{workspace_id}/agent-workflows/draft") in routes
    assert all("/api/v1/knowledge" not in path or "agent-workflows" not in path for _, path in routes)
