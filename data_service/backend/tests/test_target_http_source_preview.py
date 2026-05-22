from pathlib import Path
from urllib.parse import quote

from fastapi.testclient import TestClient

from app.main import app


FORBIDDEN_KEYS = {
    "workspace_path",
    "root_path",
    "filesystem_path",
    "source_path",
    "original_path",
    "artifact_physical_path",
    "workspace_layout",
    "artifact_layout",
    "internal_path",
    "debug_paths",
    "path",
    "paths",
    "cache_path",
    "artifact_path",
    "physical_path",
}
FORBIDDEN_TEXT = ("/Users", "file://", "cache_path", "artifact_path", "physical_path", "/tmp/", "C:\\\\")


def _assert_no_internal_paths(payload):
    def walk(value):
        if isinstance(value, dict):
            for key, item in value.items():
                assert key not in FORBIDDEN_KEYS
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)
        elif isinstance(value, str):
            for fragment in FORBIDDEN_TEXT:
                assert fragment not in value

    walk(payload)


def _create_workspace(client: TestClient, name: str) -> str:
    response = client.post("/api/workspaces", json={"name": name})
    assert response.status_code == 200
    return response.json()["workspace_id"]


def _import_text_source(client: TestClient, workspace_id: str, *, title="Architecture notes", content="Queues absorb burst traffic.") -> str:
    response = client.post(
        f"/api/workspaces/{workspace_id}/sources",
        json={"texts": [{"title": title, "content": content, "metadata": {"kind": "text"}}]},
    )
    assert response.status_code == 200
    return response.json()["data"]["sources"][0]["source_id"]


def test_v11be_capability_manifest_source_preview_contract(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "RN Preview Capabilities")

    response = client.get(f"/api/workspaces/{workspace_id}/capabilities")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert set(payload) >= {"status", "data", "warnings", "next_actions"}
    manifest = payload["data"]["manifest"]

    assert manifest["workspace_id"] == workspace_id
    assert manifest["schema_version"] == "v1.1-document-units"
    assert manifest["capabilities"] == {
        "source_preview": True,
        "document_units": True,
        "evidence_spans": True,
        "source_level_preview": True,
        "unit_level_navigation": True,
        "precise_span_highlight": True,
        "citation_backjump": True,
    }
    assert manifest["supported_source_types"] == [{"source_type": "text", "preview": "unit", "locators": []}]
    _assert_no_internal_paths(payload)


def test_v11be_source_preview_success_for_registry_text_source(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "RN Preview Text")
    source_id = _import_text_source(client, workspace_id, content="Queues absorb burst traffic and protect workers.")

    response = client.get(f"/api/workspaces/{workspace_id}/sources/{source_id}/preview")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    preview = payload["data"]["preview"]

    assert preview["source_id"] == source_id
    assert preview["title"] == "Architecture notes"
    assert preview["source_type"] == "text"
    assert preview["preview_available"] is True
    assert preview["content_type"] == "text/plain"
    assert "Queues absorb burst traffic" in preview["text_preview"]
    assert preview["artifact_refs"] == [{"type": "source", "source_id": source_id, "artifact_ref": f"source://{source_id}"}]
    assert preview["preview_truncated"] is False
    assert preview["preview_size_bytes"] >= len("Queues absorb burst traffic")
    assert preview["max_preview_size_bytes"] == 50000
    assert "units" not in preview
    assert "unit_id" not in preview
    assert "evidence_id" not in preview
    assert "locator" not in preview
    _assert_no_internal_paths(payload)


def test_v11be_source_preview_rejects_unknown_artifact_ref_and_slug_source_ids(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "RN Preview Reject")
    source_id = _import_text_source(client, workspace_id)

    unknown = client.get(f"/api/workspaces/{workspace_id}/sources/src_0000000000000000/preview")
    assert unknown.status_code == 404
    assert "SOURCE_NOT_FOUND" in unknown.json()["detail"]

    artifact_ref = quote(f"source://{source_id}", safe="")
    artifact = client.get(f"/api/workspaces/{workspace_id}/sources/{artifact_ref}/preview")
    assert artifact.status_code in {404, 422}
    if artifact.status_code == 422:
        assert "VALIDATION_ERROR" in artifact.json()["detail"]

    slug = client.get(f"/api/workspaces/{workspace_id}/sources/source-src-architecture-notes/preview")
    assert slug.status_code == 422
    assert "VALIDATION_ERROR" in slug.json()["detail"]


def test_v11be_source_preview_unsupported_type_and_truncation(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    source_root = tmp_path / "sources"
    source_root.mkdir()
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_SOURCE_ROOTS", str(source_root))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "RN Preview Unsupported")

    video = source_root / "clip.mp4"
    video.write_bytes(b"not really a video")
    imported_video = client.post(f"/api/workspaces/{workspace_id}/sources", json={"paths": [str(video)]})
    assert imported_video.status_code == 200
    video_source_id = imported_video.json()["data"]["sources"][0]["source_id"]
    unsupported = client.get(f"/api/workspaces/{workspace_id}/sources/{video_source_id}/preview")
    assert unsupported.status_code == 200
    unsupported_preview = unsupported.json()["data"]["preview"]
    assert unsupported_preview["preview_available"] is False
    assert unsupported_preview["content_type"] == "text/plain"
    assert unsupported_preview["unsupported_reason"] == "source_type_not_supported"
    _assert_no_internal_paths(unsupported.json())

    long_text = "x" * 50123
    text_source_id = _import_text_source(client, workspace_id, title="Long text", content=long_text)
    long_response = client.get(f"/api/workspaces/{workspace_id}/sources/{text_source_id}/preview")
    assert long_response.status_code == 200
    long_preview = long_response.json()["data"]["preview"]
    assert long_preview["preview_available"] is True
    assert long_preview["preview_truncated"] is True
    assert long_preview["preview_size_bytes"] == len(long_text)
    assert long_preview["max_preview_size_bytes"] == 50000
    assert len(long_preview["text_preview"].encode("utf-8")) == 50000
    _assert_no_internal_paths(long_response.json())


def test_v11be_no_compatibility_knowledge_route_added_for_source_preview():
    routes = {(method, route.path) for route in app.routes for method in getattr(route, "methods", set())}
    assert ("GET", "/api/workspaces/{workspace_id}/capabilities") in routes
    assert ("GET", "/api/workspaces/{workspace_id}/sources/{source_id}/preview") in routes
    assert all("/api/v1/knowledge" not in path or "preview" not in path for _, path in routes)
