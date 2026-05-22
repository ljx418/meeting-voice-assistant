from urllib.parse import quote

from fastapi.testclient import TestClient

from app.main import app
from test_target_http_source_preview import _assert_no_internal_paths, _create_workspace, _import_text_source


def _trace_payload(client: TestClient, workspace_id: str, source_id: str):
    response = client.get(f"/api/workspaces/{workspace_id}/sources/{source_id}/trace")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert set(payload) >= {"status", "data", "warnings", "next_actions"}
    return payload, payload["data"]["trace"]


def test_source_trace_accepts_registry_source_id_for_created_text_source(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "RN Source Trace")
    source_id = _import_text_source(client, workspace_id, title="Trace source", content="Trace provenance should resolve.")

    payload, trace = _trace_payload(client, workspace_id, source_id)

    assert trace["source_id"] == source_id
    assert trace["title"] == "Trace source"
    assert trace["trace_available"] is True
    assert trace["summary"] or trace["provenance"]
    assert trace["artifact_refs"] == [{"type": "source", "source_id": source_id, "artifact_ref": f"source://{source_id}"}]
    assert any(item["label"] == "Registry source" and item["value"] == source_id for item in trace["provenance"])
    _assert_no_internal_paths(payload)


def test_source_trace_error_semantics_for_invalid_and_unknown_ids(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_a = _create_workspace(client, "RN Source Trace A")
    workspace_b = _create_workspace(client, "RN Source Trace B")
    source_id = _import_text_source(client, workspace_a)

    unknown = client.get(f"/api/workspaces/{workspace_a}/sources/src_0000000000000000/trace")
    assert unknown.status_code == 404
    assert "SOURCE_NOT_FOUND" in unknown.json()["detail"]

    cross_workspace = client.get(f"/api/workspaces/{workspace_b}/sources/{source_id}/trace")
    assert cross_workspace.status_code == 404
    assert "SOURCE_NOT_FOUND" in cross_workspace.json()["detail"]

    for invalid_id in [
        f"source://{source_id}",
        "source-src-architecture-notes",
        "architecture-notes",
        "/tmp/source.md",
    ]:
        response = client.get(f"/api/workspaces/{workspace_a}/sources/{quote(invalid_id, safe='')}/trace")
        assert response.status_code == 422
        assert "VALIDATION_ERROR" in response.json()["detail"]


def test_source_trace_routes_exposed_without_compatibility_feature_route():
    routes = {(route.methods and next(iter(route.methods)), route.path) for route in app.routes if hasattr(route, "methods")}
    assert ("GET", "/api/workspaces/{workspace_id}/sources/{source_id}/trace") in routes
    compatibility_trace_routes = sorted(path for _method, path in routes if path.startswith("/api/v1/knowledge") and "trace" in path)
    assert compatibility_trace_routes == ["/api/v1/knowledge/source/trace"]
