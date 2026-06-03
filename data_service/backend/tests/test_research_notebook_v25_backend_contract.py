from fastapi.testclient import TestClient

from app.main import app
from data_service.url_source_contract import URLSourceImportError, URLSourceText
from test_target_http_source_preview import _assert_no_internal_paths, _create_workspace, _import_text_source


def _setup_client(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    for name in ["OCR_PROVIDER", "OCR_API_KEY", "OCR_ENDPOINT", "TTS_PROVIDER", "TTS_API_KEY", "TTS_ENDPOINT", "PPTX_PROVIDER"]:
        monkeypatch.delenv(name, raising=False)
    return TestClient(app)


def test_v25_url_block_reason_private_and_metadata_urls(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    workspace_id = _create_workspace(client, "RN V25 URL Guard")

    cases = [
        ("http://10.0.0.1/internal", "ssrf", 400),
        ("http://172.16.0.1/internal", "private_ip", 400),
        ("http://192.168.1.1/internal", "private_ip", 400),
        ("http://169.254.169.254/metadata", "ssrf", 400),
    ]
    for url, block_reason, status_code in cases:
        response = client.post(f"/api/workspaces/{workspace_id}/sources", json={"urls": [{"title": block_reason, "url": url}]})
        assert response.status_code == status_code
        payload = response.json()
        source = payload["data"]["source"]
        assert source["source_type"] == "url"
        assert source["import_state"] == "blocked"
        assert source["block_reason"] == block_reason
        assert payload["data"]["block_reason"] == block_reason
        _assert_no_internal_paths(payload)


def test_v25_url_redirect_block_is_reported_as_blocked_source(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    workspace_id = _create_workspace(client, "RN V25 Redirect Guard")

    def fake_redirect(url: str, *, title=None, **kwargs):  # noqa: ANN001
        raise URLSourceImportError("ssrf_blocked", "Redirect resolves to a blocked network address.", block_reason="ssrf")

    monkeypatch.setattr("app.api.v1.data_service.fetch_url_source_text", fake_redirect)
    response = client.post(f"/api/workspaces/{workspace_id}/sources", json={"urls": [{"title": "Redirect", "url": "https://example.com/redirect"}]})

    assert response.status_code == 400
    payload = response.json()
    source = payload["data"]["source"]
    assert source["block_reason"] == "ssrf"
    detail = client.get(f"/api/workspaces/{workspace_id}/sources/{source['source_id']}")
    assert detail.status_code == 200
    assert detail.json()["data"]["source"]["import_state"] == "blocked"
    _assert_no_internal_paths(payload)


def test_v25_normal_url_still_imports_ready_source(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    workspace_id = _create_workspace(client, "RN V25 URL Ready")

    def fake_url_text(url: str, *, title=None, **kwargs):  # noqa: ANN001
        return URLSourceText(
            url=url,
            final_url="https://example.com/final",
            title=title or "Public URL",
            content="# Public URL\n\nSource URL: https://example.com/final\n\nPublic source text for evidence-backed artifacts.",
            content_type="text/html",
            fetched_at="2026-06-02T00:00:00Z",
        )

    monkeypatch.setattr("app.api.v1.data_service.fetch_url_source_text", fake_url_text)
    response = client.post(f"/api/workspaces/{workspace_id}/sources", json={"urls": [{"title": "Public", "url": "https://example.com"}]})

    assert response.status_code == 200
    source = response.json()["data"]["sources"][0]
    assert source["source_type"] == "url"
    assert source["import_state"] == "ready"
    assert source["url"] == "https://example.com"
    assert source["final_url"] == "https://example.com/final"
    _assert_no_internal_paths(response.json())


def test_v25_provider_health_and_capabilities_are_provider_gated(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    workspace_id = _create_workspace(client, "RN V25 Capabilities")

    ocr = client.post("/api/ocr/provider/health")
    tts = client.post("/api/tts/provider/health")
    assert ocr.status_code == 200
    assert tts.status_code == 200
    assert ocr.json()["available"] is False
    assert ocr.json()["unsupported_reason"] == "no_provider_configured"
    assert tts.json()["available"] is False
    assert tts.json()["unsupported_reason"] == "no_provider_configured"

    manifest = client.get(f"/api/workspaces/{workspace_id}/capabilities").json()["data"]["manifest"]
    assert manifest["capabilities"]["ocr"] is False
    assert manifest["capabilities"]["audio_overview"] is False
    assert manifest["capabilities"]["slide_outline"] is True
    assert manifest["capabilities"]["pptx_export"] is False
    _assert_no_internal_paths(manifest)


def test_v25_artifacts_slides_mindmap_compare_persist_and_download(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    workspace_id = _create_workspace(client, "RN V25 Artifacts")
    source_a = _import_text_source(client, workspace_id, title="Source A", content="Alpha source discusses queues and evidence governance.")
    source_b = _import_text_source(client, workspace_id, title="Source B", content="Beta source discusses queues and slide outlines.")

    slides_response = client.post(f"/api/workspaces/{workspace_id}/artifacts/slides", json={"source_ids": [source_a, source_b], "topic": "Queue Overview", "slide_count": 3})
    assert slides_response.status_code == 200
    slides = slides_response.json()["data"]["artifact"]
    assert slides["type"] == "slides"
    assert slides["artifact_available"] is True
    assert len(slides["slides"]) == 3
    assert all(slide["evidence_refs"] for slide in slides["slides"])

    artifact_id = slides["artifact_id"]
    read_response = client.get(f"/api/workspaces/{workspace_id}/artifacts/{artifact_id}")
    assert read_response.status_code == 200
    assert read_response.json()["data"]["artifact"]["artifact_id"] == artifact_id
    status_response = client.get(f"/api/workspaces/{workspace_id}/artifacts/{artifact_id}/status")
    assert status_response.status_code == 200
    assert status_response.json()["data"]["status"] == "ready"
    md_download = client.get(f"/api/workspaces/{workspace_id}/artifacts/{artifact_id}/download", params={"format": "md"})
    assert md_download.status_code == 200
    assert md_download.json()["format"] == "md"
    pptx_export = client.post(f"/api/workspaces/{workspace_id}/artifacts/slides/export", json={"artifact_id": artifact_id})
    assert pptx_export.status_code == 200
    assert pptx_export.json()["error"]["code"] == "SLIDE_OUTLINE_ONLY"

    mindmap = client.post(f"/api/workspaces/{workspace_id}/artifacts/mindmap", json={"source_ids": [source_a, source_b], "topic": "Evidence Map"})
    assert mindmap.status_code == 200
    assert mindmap.json()["data"]["artifact"]["root_node"]["children"]

    compare = client.post(f"/api/workspaces/{workspace_id}/artifacts/compare", json={"source_ids": [source_a, source_b]})
    assert compare.status_code == 200
    comparison = compare.json()["data"]["artifact"]["result"]["source_pairs"][0]
    assert comparison["similarities"][0]["evidence_refs"]
    assert comparison["differences"][0]["evidence_a"]
    assert comparison["differences"][0]["evidence_b"]

    listing = client.get(f"/api/workspaces/{workspace_id}/artifacts")
    assert listing.status_code == 200
    assert listing.json()["data"]["count"] >= 3
    _assert_no_internal_paths(slides_response.json())
    _assert_no_internal_paths(mindmap.json())
    _assert_no_internal_paths(compare.json())


def test_v25_audio_and_ocr_return_stable_not_ready_without_provider(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    workspace_id = _create_workspace(client, "RN V25 Provider Missing")
    source_id = _import_text_source(client, workspace_id, title="Audio Source", content="Audio overview requires a TTS provider.")

    audio = client.post(f"/api/workspaces/{workspace_id}/artifacts/audio", json={"source_ids": [source_id]})
    assert audio.status_code == 200
    artifact = audio.json()["data"]["artifact"]
    assert artifact["artifact_available"] is False
    assert artifact["error"]["code"] == "AUDIO_OVERVIEW_NOT_READY"

    ocr = client.post(f"/api/workspaces/{workspace_id}/sources/{source_id}/ocr")
    assert ocr.status_code == 200
    assert ocr.json()["status"] == "blocked"
    assert ocr.json()["data"]["error"]["code"] == "OCR_REQUIRED"
    _assert_no_internal_paths(audio.json())
    _assert_no_internal_paths(ocr.json())
