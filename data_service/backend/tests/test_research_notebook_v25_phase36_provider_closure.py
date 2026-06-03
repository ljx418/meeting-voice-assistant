import base64
import zipfile
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from test_research_notebook_v25_phase33_ocr_provider import _png_fixture
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
    "TTS_DEFAULT_VOICE",
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


def _import_image_source(client: TestClient, workspace_id: str, image_bytes: bytes) -> str:
    response = client.post(
        f"/api/workspaces/{workspace_id}/sources",
        json={
            "files": [
                {
                    "title": "Closure OCR image",
                    "file_name": "closure-ocr.png",
                    "content_base64": base64.b64encode(image_bytes).decode("ascii"),
                    "content_type": "image/png",
                    "source_type": "image",
                }
            ]
        },
    )
    assert response.status_code == 200
    _assert_no_internal_paths(response.json())
    return response.json()["data"]["sources"][0]["source_id"]


def test_phase36_provider_enabled_closure_matrix_real_artifacts(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    monkeypatch.setenv("OCR_PROVIDER", "tesseract")
    monkeypatch.setenv("TTS_PROVIDER", "local")
    monkeypatch.setenv("TTS_DEFAULT_VOICE", "en")
    monkeypatch.setenv("PPTX_PROVIDER", "local")
    monkeypatch.setenv("PPTX_EXPORTER_ENABLED", "1")
    workspace_id = _create_workspace(client, "RN V25 Phase36 Enabled Closure")

    for route in ["/api/ocr/provider/health", "/api/tts/provider/health", "/api/pptx/provider/health"]:
        health = client.post(route)
        assert health.status_code == 200
        assert health.json()["available"] is True
        _assert_no_internal_paths(health.json())

    image_source_id = _import_image_source(client, workspace_id, _png_fixture(tmp_path, "PHASE THIRTY SIX OCR CLOSURE IMAGE"))
    text_source_id = _import_text_source(
        client,
        workspace_id,
        title="Closure source",
        content="Phase thirty six validates OCR, audio, and PPTX provider-backed artifacts with real source evidence.",
    )

    ocr = client.post(f"/api/workspaces/{workspace_id}/sources/{image_source_id}/ocr")
    assert ocr.status_code == 200
    ocr_artifact = ocr.json()["data"]["artifact"]
    assert ocr_artifact["status"] == "ready"
    assert ocr_artifact["pages"][0]["blocks"][0]["text"]
    _assert_no_internal_paths(ocr.json())

    audio = client.post(f"/api/workspaces/{workspace_id}/artifacts/audio", json={"source_ids": [text_source_id], "voice_id": "en"})
    assert audio.status_code == 200
    audio_artifact = audio.json()["data"]["artifact"]
    assert audio_artifact["status"] == "ready"
    assert audio_artifact["audio_available"] is True
    assert audio_artifact["binary"]["duration_ms"] > 0
    _assert_no_internal_paths(audio.json())

    slides = client.post(
        f"/api/workspaces/{workspace_id}/artifacts/slides",
        json={"source_ids": [text_source_id], "topic": "Provider Closure", "slide_count": 2},
    )
    assert slides.status_code == 200
    slides_artifact = slides.json()["data"]["artifact"]
    assert len(slides_artifact["slides"]) == 2

    pptx = client.post(f"/api/workspaces/{workspace_id}/artifacts/slides/export", json={"artifact_id": slides_artifact["artifact_id"]})
    assert pptx.status_code == 200
    pptx_artifact = pptx.json()
    assert pptx_artifact["status"] == "ready"
    assert pptx_artifact["slide_count"] == 2
    _assert_no_internal_paths(pptx_artifact)

    workspace_root = Path(__import__("os").environ["DATA_SERVICE_WORKSPACE_ROOT"]) / workspace_id
    pptx_path = workspace_root / "research_notebook" / "artifacts" / "binaries" / f"{pptx_artifact['artifact_id']}.pptx"
    with zipfile.ZipFile(pptx_path) as package:
        names = set(package.namelist())
    assert "ppt/presentation.xml" in names
    assert sorted(name for name in names if name.startswith("ppt/slides/slide") and name.endswith(".xml")) == [
        "ppt/slides/slide1.xml",
        "ppt/slides/slide2.xml",
    ]

    listing = client.get(f"/api/workspaces/{workspace_id}/artifacts")
    assert listing.status_code == 200
    types = {item["artifact_type"] for item in listing.json()["data"]["items"]}
    assert {"ocr", "audio_overview", "slides", "pptx_export"}.issubset(types)
    _assert_no_internal_paths(listing.json())


def test_phase36_provider_disabled_closure_matrix_stable_fallbacks(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    workspace_id = _create_workspace(client, "RN V25 Phase36 Disabled Closure")
    image_source_id = _import_image_source(client, workspace_id, _png_fixture(tmp_path, "PHASE THIRTY SIX DISABLED OCR"))
    text_source_id = _import_text_source(client, workspace_id, title="Disabled source", content="Disabled provider closure keeps fallbacks stable.")

    assert client.post("/api/ocr/provider/health").json()["available"] is False
    assert client.post("/api/tts/provider/health").json()["available"] is False
    assert client.post("/api/pptx/provider/health").json()["available"] is False

    ocr = client.post(f"/api/workspaces/{workspace_id}/sources/{image_source_id}/ocr")
    assert ocr.status_code == 200
    assert ocr.json()["data"]["error"]["code"] == "OCR_REQUIRED"

    audio = client.post(f"/api/workspaces/{workspace_id}/artifacts/audio", json={"source_ids": [text_source_id]})
    assert audio.status_code == 200
    assert audio.json()["data"]["artifact"]["error"]["code"] == "AUDIO_OVERVIEW_NOT_READY"

    slides = client.post(f"/api/workspaces/{workspace_id}/artifacts/slides", json={"source_ids": [text_source_id], "slide_count": 1}).json()["data"]["artifact"]
    pptx = client.post(f"/api/workspaces/{workspace_id}/artifacts/slides/export", json={"artifact_id": slides["artifact_id"]})
    assert pptx.status_code == 200
    assert pptx.json()["error"]["code"] == "SLIDE_OUTLINE_ONLY"
    _assert_no_internal_paths(ocr.json())
    _assert_no_internal_paths(audio.json())
    _assert_no_internal_paths(pptx.json())
