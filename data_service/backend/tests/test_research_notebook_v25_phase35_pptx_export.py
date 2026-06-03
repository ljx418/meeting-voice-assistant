import zipfile
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from test_target_http_source_preview import _assert_no_internal_paths, _create_workspace, _import_text_source


PROVIDER_ENV = [
    "OCR_PROVIDER",
    "OCR_API_KEY",
    "OCR_ENDPOINT",
    "OCR_SIMULATE_ERROR",
    "TTS_PROVIDER",
    "TTS_API_KEY",
    "TTS_ENDPOINT",
    "TTS_SIMULATE_ERROR",
    "PPTX_PROVIDER",
    "PPTX_SIMULATE_ERROR",
    "PPTX_EXPORTER_ENABLED",
]


def _setup_client(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    for name in PROVIDER_ENV:
        monkeypatch.delenv(name, raising=False)
    return TestClient(app)


def _slides_artifact(client: TestClient, workspace_id: str, slide_count: int = 3) -> dict:
    source_a = _import_text_source(client, workspace_id, title="Slide Source A", content="Alpha source supports a real PowerPoint export with evidence.")
    source_b = _import_text_source(client, workspace_id, title="Slide Source B", content="Beta source keeps slide count and lineage stable.")
    response = client.post(
        f"/api/workspaces/{workspace_id}/artifacts/slides",
        json={"source_ids": [source_a, source_b], "topic": "Phase 35 PPTX Export", "slide_count": slide_count},
    )
    assert response.status_code == 200
    artifact = response.json()["data"]["artifact"]
    assert artifact["artifact_type"] == "slides"
    assert len(artifact["slides"]) == slide_count
    return artifact


def test_phase35_exporter_disabled_keeps_slide_outline_only_without_binary(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    workspace_id = _create_workspace(client, "RN V25 Phase35 PPTX Disabled")
    slides = _slides_artifact(client, workspace_id, slide_count=2)

    export = client.post(f"/api/workspaces/{workspace_id}/artifacts/slides/export", json={"artifact_id": slides["artifact_id"]})
    assert export.status_code == 200
    assert export.json()["error"]["code"] == "SLIDE_OUTLINE_ONLY"
    _assert_no_internal_paths(export.json())


def test_phase35_local_pptx_export_e2e_writes_openxml_package(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    monkeypatch.setenv("PPTX_PROVIDER", "local")
    monkeypatch.setenv("PPTX_EXPORTER_ENABLED", "1")
    workspace_id = _create_workspace(client, "RN V25 Phase35 PPTX Real")
    slides = _slides_artifact(client, workspace_id, slide_count=3)

    health = client.post("/api/pptx/provider/health")
    assert health.status_code == 200
    assert health.json()["available"] is True
    assert health.json()["provider"] == "local"

    export = client.post(f"/api/workspaces/{workspace_id}/artifacts/slides/export", json={"artifact_id": slides["artifact_id"]})
    assert export.status_code == 200
    artifact = export.json()
    assert artifact["artifact_type"] == "pptx_export"
    assert artifact["status"] == "ready"
    assert artifact["artifact_available"] is True
    assert artifact["source_slides_artifact_id"] == slides["artifact_id"]
    assert artifact["slide_count"] == 3
    assert artifact["binary"]["mime_type"] == "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    assert artifact["binary"]["size_bytes"] > 0
    assert len(artifact["binary"]["sha256"]) == 64
    assert artifact["binary"]["ref"].startswith(f"artifact://{workspace_id}/{artifact['artifact_id']}?binary=pptx")
    assert artifact["evidence_refs"]
    _assert_no_internal_paths(artifact)

    workspace_root = Path(__import__("os").environ["DATA_SERVICE_WORKSPACE_ROOT"]) / workspace_id
    pptx_path = workspace_root / "research_notebook" / "artifacts" / "binaries" / f"{artifact['artifact_id']}.pptx"
    assert pptx_path.exists()
    assert pptx_path.stat().st_size == artifact["binary"]["size_bytes"]
    assert not pptx_path.read_bytes().startswith(b"{")
    with zipfile.ZipFile(pptx_path) as package:
        names = set(package.namelist())
    assert "[Content_Types].xml" in names
    assert "ppt/presentation.xml" in names
    slide_names = sorted(name for name in names if name.startswith("ppt/slides/slide") and name.endswith(".xml"))
    assert slide_names == ["ppt/slides/slide1.xml", "ppt/slides/slide2.xml", "ppt/slides/slide3.xml"]

    readback = client.get(f"/api/workspaces/{workspace_id}/artifacts/{artifact['artifact_id']}")
    assert readback.status_code == 200
    assert readback.json()["data"]["artifact"]["binary"]["sha256"] == artifact["binary"]["sha256"]
    status = client.get(f"/api/workspaces/{workspace_id}/artifacts/{artifact['artifact_id']}/status")
    assert status.status_code == 200
    assert status.json()["data"]["status"] == "ready"
    download = client.get(f"/api/workspaces/{workspace_id}/artifacts/{artifact['artifact_id']}/download", params={"format": "pptx"})
    assert download.status_code == 200
    descriptor = download.json()
    assert descriptor["format"] == "pptx"
    assert descriptor["size_bytes"] == pptx_path.stat().st_size
    assert descriptor["sha256"] == artifact["binary"]["sha256"]
    assert descriptor["url"].startswith(f"artifact://{workspace_id}/{artifact['artifact_id']}?binary=pptx")
    _assert_no_internal_paths(readback.json())
    _assert_no_internal_paths(descriptor)
