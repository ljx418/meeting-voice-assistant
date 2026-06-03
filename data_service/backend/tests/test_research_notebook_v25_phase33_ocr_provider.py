import base64
import os
import subprocess
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from test_target_http_source_preview import _assert_no_internal_paths, _create_workspace


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


def _png_fixture(tmp_path: Path, text: str) -> bytes:
    fixture = tmp_path / "phase33-ocr-fixture.png"
    subprocess.run(
        [
            "pango-view",
            "--no-display",
            "--font=Sans Bold 38",
            "--dpi=150",
            "--background=white",
            "--foreground=black",
            "--margin=40",
            "--output",
            str(fixture),
            "--text",
            text,
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert fixture.exists()
    assert fixture.stat().st_size > 0
    return fixture.read_bytes()


def _import_image_source(client: TestClient, workspace_id: str, image_bytes: bytes) -> str:
    response = client.post(
        f"/api/workspaces/{workspace_id}/sources",
        json={
            "files": [
                {
                    "title": "Phase 33 OCR image",
                    "file_name": "phase33-ocr-fixture.png",
                    "content_base64": base64.b64encode(image_bytes).decode("ascii"),
                    "content_type": "image/png",
                    "source_type": "image",
                }
            ]
        },
    )
    assert response.status_code == 200
    payload = response.json()
    _assert_no_internal_paths(payload)
    source = payload["data"]["sources"][0]
    assert source["source_type"] == "image"
    return source["source_id"]


def test_phase33_provider_disabled_keeps_ocr_required_without_fake_artifact(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    workspace_id = _create_workspace(client, "RN V25 Phase33 OCR Disabled")
    source_id = _import_image_source(client, workspace_id, _png_fixture(tmp_path, "PHASE THIRTY THREE OCR REAL IMAGE"))

    response = client.post(f"/api/workspaces/{workspace_id}/sources/{source_id}/ocr")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "blocked"
    assert payload["data"]["error"]["code"] == "OCR_REQUIRED"
    assert "artifact" not in payload["data"]
    _assert_no_internal_paths(payload)


def test_phase33_tesseract_real_image_ocr_e2e_persists_artifact(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    monkeypatch.setenv("OCR_PROVIDER", "tesseract")
    workspace_id = _create_workspace(client, "RN V25 Phase33 OCR Real")
    source_id = _import_image_source(client, workspace_id, _png_fixture(tmp_path, "PHASE THIRTY THREE OCR REAL IMAGE"))

    health = client.post("/api/ocr/provider/health")
    assert health.status_code == 200
    assert health.json()["available"] is True
    assert health.json()["provider"] == "tesseract"

    response = client.post(f"/api/workspaces/{workspace_id}/sources/{source_id}/ocr")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    artifact = payload["data"]["artifact"]
    assert artifact["artifact_type"] == "ocr"
    assert artifact["status"] == "ready"
    assert artifact["artifact_available"] is True
    assert artifact["provider"]["name"] == "tesseract"
    assert artifact["pages"]
    block = artifact["pages"][0]["blocks"][0]
    recognized = block["text"].upper()
    assert "PHASE" in recognized
    assert "OCR" in recognized
    assert "IMAGE" in recognized
    assert block["confidence"] > 0
    assert block["confidence_band"] in {"low", "medium", "high"}
    assert block["locator"]["page"] == 1
    assert block["evidence_refs"][0]["locator"].startswith(f"source://{source_id}#page=1&block=0")
    assert artifact["generation_metadata"]["fallback_mode"] is False
    assert artifact["generation_metadata"]["provider"] == "tesseract"
    assert artifact["summary"]
    _assert_no_internal_paths(payload)

    artifact_id = artifact["artifact_id"]
    readback = client.get(f"/api/workspaces/{workspace_id}/artifacts/{artifact_id}")
    assert readback.status_code == 200
    assert readback.json()["data"]["artifact"]["artifact_id"] == artifact_id
    status = client.get(f"/api/workspaces/{workspace_id}/sources/{source_id}/ocr/status")
    assert status.status_code == 200
    assert status.json()["data"]["status"] == "ready"
    assert status.json()["data"]["artifact_id"] == artifact_id

    workspace_root = Path(os.environ["DATA_SERVICE_WORKSPACE_ROOT"]) / workspace_id
    stored = workspace_root / "research_notebook" / "artifacts" / f"{artifact_id}.json"
    assert stored.exists()
    stored_text = stored.read_text(encoding="utf-8")
    assert "PHASE" in stored_text.upper()
    assert "/Users/" not in str(readback.json())
    _assert_no_internal_paths(readback.json())


def test_phase33_pdf_rasterizer_path_is_structured_and_not_embedded_text_success(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    monkeypatch.setenv("OCR_PROVIDER", "tesseract")
    workspace_id = _create_workspace(client, "RN V25 Phase33 PDF")
    fake_pdf = b"%PDF-1.4\n1 0 obj << /Type /Catalog >> endobj\n%%EOF\n"
    response = client.post(
        f"/api/workspaces/{workspace_id}/sources",
        json={
            "files": [
                {
                    "title": "Broken scanned PDF",
                    "file_name": "broken-scanned.pdf",
                    "content_base64": base64.b64encode(fake_pdf).decode("ascii"),
                    "content_type": "application/pdf",
                    "source_type": "pdf",
                }
            ]
        },
    )
    assert response.status_code == 200
    source_id = response.json()["data"]["sources"][0]["source_id"]

    ocr = client.post(f"/api/workspaces/{workspace_id}/sources/{source_id}/ocr")
    assert ocr.status_code == 200
    artifact = ocr.json()["data"]["artifact"]
    assert artifact["status"] == "error"
    assert artifact["error"]["code"] == "PDF_RASTERIZER_UNAVAILABLE"
    assert artifact["artifact_available"] is False
    assert not artifact["pages"]
    _assert_no_internal_paths(ocr.json())
