from pathlib import Path
import base64
from types import SimpleNamespace
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


def _import_typed_text_source(
    client: TestClient,
    workspace_id: str,
    *,
    source_type: str,
    title: str,
    content: str,
) -> str:
    response = client.post(
        f"/api/workspaces/{workspace_id}/sources",
        json={"texts": [{"title": title, "content": content, "metadata": {"source_type": source_type}}]},
    )
    assert response.status_code == 200
    return response.json()["data"]["sources"][0]["source_id"]


def _patch_pdf_extractor(monkeypatch, pages: list[str]):
    def fake_extract(self, file_path):
        sections = [
            SimpleNamespace(
                text=text,
                title=f"Page {index + 1}",
                locator={"kind": "pdf_page", "page": index + 1},
                order_index=index,
            )
            for index, text in enumerate(pages)
        ]
        return SimpleNamespace(status="success", sections=sections, error=None)

    monkeypatch.setattr("app.llmwiki.extractors.pdf_pypdf.PdfPypdfExtractor.extract", fake_extract)


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
    expected_core = {
        "source_preview": True,
        "document_units": True,
        "evidence_spans": True,
        "source_level_preview": True,
        "unit_level_navigation": True,
        "precise_span_highlight": True,
        "citation_backjump": True,
        "ocr": False,
        "scanned_pdf_ocr": False,
    }
    assert {key: manifest["capabilities"].get(key) for key in expected_core} == expected_core
    assert manifest["capabilities"]["audio_overview"] is False
    assert manifest["capabilities"]["slide_outline"] is True
    assert manifest["capabilities"]["pptx_export"] is False
    assert manifest["capabilities"]["mindmap"] is True
    assert manifest["capabilities"]["compare"] is True
    assert manifest["supported_source_types"] == [
        {"source_type": "text", "preview": "unit", "locators": []},
        {"source_type": "markdown", "preview": "unit", "locators": ["offset"]},
        {"source_type": "json", "preview": "unit", "locators": ["json_path"]},
        {"source_type": "pdf", "preview": "unit", "locators": ["page_no", "offset"]},
        {"source_type": "url", "preview": "unit", "locators": ["offset"]},
    ]
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


def test_v11s3_source_preview_success_for_markdown_and_json_sources(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "RN S3 Preview")
    markdown_source_id = _import_typed_text_source(
        client,
        workspace_id,
        source_type="markdown",
        title="Markdown source",
        content="# Release notes\n\nQueues absorb burst traffic.",
    )
    json_source_id = _import_typed_text_source(
        client,
        workspace_id,
        source_type="json",
        title="JSON source",
        content='{"summary":"Queues absorb burst traffic","risk":"low"}',
    )

    markdown = client.get(f"/api/workspaces/{workspace_id}/sources/{markdown_source_id}/preview")
    assert markdown.status_code == 200
    markdown_preview = markdown.json()["data"]["preview"]
    assert markdown_preview["source_id"] == markdown_source_id
    assert markdown_preview["source_type"] == "markdown"
    assert markdown_preview["preview_available"] is True
    assert markdown_preview["content_type"] == "text/markdown"
    assert "# Release notes" in markdown_preview["text_preview"]
    assert "units" not in markdown_preview
    _assert_no_internal_paths(markdown.json())

    json_response = client.get(f"/api/workspaces/{workspace_id}/sources/{json_source_id}/preview")
    assert json_response.status_code == 200
    json_preview = json_response.json()["data"]["preview"]
    assert json_preview["source_id"] == json_source_id
    assert json_preview["source_type"] == "json"
    assert json_preview["preview_available"] is True
    assert json_preview["content_type"] == "text/plain"
    assert "Queues absorb burst traffic" in json_preview["text_preview"]
    assert "units" not in json_preview
    _assert_no_internal_paths(json_response.json())


def test_v14c_source_preview_success_for_text_pdf_source(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    source_root = tmp_path / "sources"
    source_root.mkdir()
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_SOURCE_ROOTS", str(source_root))
    _patch_pdf_extractor(
        monkeypatch,
        [
            "AI digital humans use speech synthesis and real-time rendering.",
            "Enterprise deployments require evidence-backed risk controls.",
        ],
    )

    client = TestClient(app)
    workspace_id = _create_workspace(client, "RN V1.4 PDF Preview")
    pdf = source_root / "digital-human.pdf"
    pdf.write_bytes(b"%PDF-1.7\nfake text pdf fixture\n")
    imported = client.post(f"/api/workspaces/{workspace_id}/sources", json={"paths": [str(pdf)]})
    assert imported.status_code == 200
    source_id = imported.json()["data"]["sources"][0]["source_id"]

    response = client.get(f"/api/workspaces/{workspace_id}/sources/{source_id}/preview")
    assert response.status_code == 200
    payload = response.json()
    preview = payload["data"]["preview"]
    assert preview["source_id"] == source_id
    assert preview["source_type"] == "pdf"
    assert preview["preview_available"] is True
    assert preview["content_type"] == "text/plain"
    assert "AI digital humans use speech synthesis" in preview["text_preview"]
    assert "Enterprise deployments require evidence-backed risk controls" in preview["text_preview"]
    assert preview["artifact_refs"] == [{"type": "source", "source_id": source_id, "artifact_ref": f"source://{source_id}"}]
    assert preview["preview_truncated"] is False
    assert "units" not in preview
    _assert_no_internal_paths(payload)


def test_v14c_source_preview_success_for_browser_uploaded_pdf_source(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    _patch_pdf_extractor(monkeypatch, ["Browser uploaded PDF text is extractable."])

    client = TestClient(app)
    workspace_id = _create_workspace(client, "RN V1.4 Browser PDF Upload")
    response = client.post(
        f"/api/workspaces/{workspace_id}/sources",
        json={
            "files": [
                {
                    "title": "Browser PDF",
                    "file_name": "browser-upload.pdf",
                    "content_type": "application/pdf",
                    "source_type": "pdf",
                    "content_base64": base64.b64encode(b"%PDF-1.7 browser upload").decode("ascii"),
                    "metadata": {"upload_surface": "browser"},
                }
            ]
        },
    )
    assert response.status_code == 200
    source = response.json()["data"]["sources"][0]
    assert source["title"] == "Browser PDF"
    assert source["metadata"]["browser_file_import"] is True
    assert source["metadata"]["file_name"] == "browser-upload.pdf"
    assert source["metadata"]["file_upload_contract"] == "base64_file_content"
    _assert_no_internal_paths(response.json())

    preview = client.get(f"/api/workspaces/{workspace_id}/sources/{source['source_id']}/preview")
    assert preview.status_code == 200
    preview_payload = preview.json()["data"]["preview"]
    assert preview_payload["source_type"] == "pdf"
    assert preview_payload["preview_available"] is True
    assert "Browser uploaded PDF text is extractable" in preview_payload["text_preview"]
    _assert_no_internal_paths(preview.json())


def test_v16c_scanned_pdf_returns_ocr_required_without_claiming_ocr_ready(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    def fake_extract(self, file_path):
        return SimpleNamespace(status="unsupported", sections=[], error="scanned_or_unsupported_pdf")

    monkeypatch.setattr("app.llmwiki.extractors.pdf_pypdf.PdfPypdfExtractor.extract", fake_extract)

    client = TestClient(app)
    workspace_id = _create_workspace(client, "RN V1.6 OCR Required")
    response = client.post(
        f"/api/workspaces/{workspace_id}/sources",
        json={
            "files": [
                {
                    "title": "Scanned PDF",
                    "file_name": "scanned.pdf",
                    "content_type": "application/pdf",
                    "source_type": "pdf",
                    "content_base64": base64.b64encode(b"%PDF-1.7 scanned image only").decode("ascii"),
                    "metadata": {"upload_surface": "browser"},
                }
            ]
        },
    )
    assert response.status_code == 200
    source = response.json()["data"]["sources"][0]

    capabilities = client.get(f"/api/workspaces/{workspace_id}/capabilities").json()["data"]["manifest"]["capabilities"]
    assert capabilities["ocr"] is False
    assert capabilities["scanned_pdf_ocr"] is False

    preview = client.get(f"/api/workspaces/{workspace_id}/sources/{source['source_id']}/preview")
    assert preview.status_code == 200
    preview_payload = preview.json()["data"]["preview"]
    assert preview_payload["source_type"] == "pdf"
    assert preview_payload["preview_available"] is False
    assert preview_payload["unsupported_reason"] == "ocr_required"
    _assert_no_internal_paths(preview.json())

    units = client.get(f"/api/workspaces/{workspace_id}/sources/{source['source_id']}/units")
    assert units.status_code == 200
    units_payload = units.json()["data"]["units"]
    assert units_payload["items"] == []
    assert units_payload["unsupported_reason"] == "ocr_required"
    _assert_no_internal_paths(units.json())


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
