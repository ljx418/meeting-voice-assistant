from fastapi.testclient import TestClient

from app.main import app
from data_service.url_source_contract import URLSourceImportError, URLSourceText


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


def _setup_client(tmp_path, monkeypatch):
    import app.api.v1.data_service as data_service_api
    from data_service.ai_provider_contract import AIProviderContractError

    def _force_query_fallback(*_args, **_kwargs):
        raise AIProviderContractError("missing_api_key", "test fallback")

    monkeypatch.setattr(data_service_api, "ai_complete_json", _force_query_fallback)
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    return TestClient(app)


def _create_workspace(client: TestClient, name: str) -> str:
    response = client.post("/api/workspaces", json={"name": name})
    assert response.status_code == 200
    return response.json()["workspace_id"]


def _fake_url_text(url: str, *, title=None, **kwargs):  # noqa: ANN001
    return URLSourceText(
        url=url,
        final_url=url,
        title=title or "Example URL Source",
        content="# Example URL Source\n\nSource URL: https://example.com/\n\nQueues absorb burst traffic from a public web page.",
        content_type="text/html",
        fetched_at="2026-05-28T00:00:00Z",
    )


def test_v16a_url_source_import_preview_units_and_evidence(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    monkeypatch.setattr("app.api.v1.data_service.fetch_url_source_text", _fake_url_text)
    workspace_id = _create_workspace(client, "RN V16 URL Source")

    import_response = client.post(
        f"/api/workspaces/{workspace_id}/sources",
        json={"urls": [{"title": "Public page", "url": "https://example.com/"}]},
    )
    assert import_response.status_code == 200
    imported = import_response.json()
    source = imported["data"]["sources"][0]
    source_id = source["source_id"]
    assert source["source_type"] == "url"
    _assert_no_internal_paths(imported)

    preview_response = client.get(f"/api/workspaces/{workspace_id}/sources/{source_id}/preview")
    assert preview_response.status_code == 200
    preview = preview_response.json()["data"]["preview"]
    assert preview["source_type"] == "url"
    assert preview["preview_available"] is True
    assert "Queues absorb burst traffic" in preview["text_preview"]
    _assert_no_internal_paths(preview_response.json())

    units_response = client.get(f"/api/workspaces/{workspace_id}/sources/{source_id}/units")
    assert units_response.status_code == 200
    units = units_response.json()["data"]["units"]["items"]
    assert units
    assert units[0]["source_id"] == source_id
    assert any("Queues absorb burst traffic" in unit["text_preview"] for unit in units)

    query_response = client.post(f"/api/workspaces/{workspace_id}/query", json={"query": "Queues absorb burst traffic"})
    assert query_response.status_code == 200
    evidence = query_response.json()["evidence"][0]
    assert evidence["source_id"] == source_id
    assert evidence["unit_id"].startswith("unit_")
    assert evidence["evidence_id"].startswith("ev_")

    span_response = client.get(
        f"/api/workspaces/{workspace_id}/sources/{source_id}/units/{evidence['unit_id']}/evidence/{evidence['evidence_id']}"
    )
    assert span_response.status_code == 200
    span = span_response.json()["data"]["evidence_span"]
    assert span["source_id"] == source_id
    assert span["unit_id"] == evidence["unit_id"]
    assert span["offset_basis"] == "normalized_text"
    assert span["offset_range"] == "half_open"
    assert span["text_basis"] == "document_unit_text"
    _assert_no_internal_paths(span_response.json())


def test_v16a_url_source_import_rejects_unsafe_url(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    workspace_id = _create_workspace(client, "RN V16 URL Unsafe")

    response = client.post(
        f"/api/workspaces/{workspace_id}/sources",
        json={"urls": [{"title": "Localhost", "url": "http://127.0.0.1:8003/"}]},
    )

    assert response.status_code == 400
    payload = response.json()
    source = payload["data"]["source"]
    assert source["source_type"] == "url"
    assert source["import_state"] == "blocked"
    assert source["block_reason"] == "ssrf"
    assert payload["data"]["block_reason"] == "ssrf"
    detail = client.get(f"/api/workspaces/{workspace_id}/sources/{source['source_id']}")
    assert detail.status_code == 200
    assert detail.json()["data"]["source"]["block_reason"] == "ssrf"
    _assert_no_internal_paths(payload)


def test_v16a_url_source_import_returns_stable_extraction_error(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)

    def fake_failed(url: str, *, title=None, **kwargs):  # noqa: ANN001
        raise URLSourceImportError("robots_or_permission_blocked", "URL is blocked by permission or policy.")

    monkeypatch.setattr("app.api.v1.data_service.fetch_url_source_text", fake_failed)
    workspace_id = _create_workspace(client, "RN V16 URL Permission")

    response = client.post(
        f"/api/workspaces/{workspace_id}/sources",
        json={"urls": [{"title": "Blocked", "url": "https://example.com/private"}]},
    )

    assert response.status_code == 403
    payload = response.json()
    assert payload["status"] == "blocked"
    assert payload["data"]["source"]["block_reason"] == "permission_denied"
    assert payload["data"]["source"]["import_state"] == "blocked"
    _assert_no_internal_paths(payload)
