import hashlib
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


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_phase41_descriptor_only_contract_for_markdown_audio_and_pptx(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    for name in PROVIDER_ENV:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("TTS_PROVIDER", "local")
    monkeypatch.setenv("TTS_DEFAULT_VOICE", "en")
    monkeypatch.setenv("PPTX_PROVIDER", "local")
    monkeypatch.setenv("PPTX_EXPORTER_ENABLED", "1")
    client = TestClient(app)
    workspace_id = _create_workspace(client, "RN V25 Phase41 Download Contract")
    source_id = _import_text_source(
        client,
        workspace_id,
        title="Download Contract Source",
        content="Phase forty one validates descriptor-only artifact downloads with evidence-backed source text.",
    )

    slides_response = client.post(
        f"/api/workspaces/{workspace_id}/artifacts/slides",
        json={"source_ids": [source_id], "topic": "Descriptor Contract", "slide_count": 2},
    )
    assert slides_response.status_code == 200
    slides = slides_response.json()["data"]["artifact"]
    md = client.get(f"/api/workspaces/{workspace_id}/artifacts/{slides['artifact_id']}/download", params={"format": "md"})
    assert md.status_code == 200
    md_descriptor = md.json()
    assert md_descriptor["format"] == "md"
    assert md_descriptor["url"].startswith(f"artifact://{workspace_id}/{slides['artifact_id']}?format=md")
    assert "content" not in md_descriptor
    _assert_no_internal_paths(md_descriptor)

    audio_response = client.post(f"/api/workspaces/{workspace_id}/artifacts/audio", json={"source_ids": [source_id], "voice_id": "en"})
    assert audio_response.status_code == 200
    audio = audio_response.json()["data"]["artifact"]
    assert audio["status"] == "ready"

    workspace_root = Path(__import__("os").environ["DATA_SERVICE_WORKSPACE_ROOT"]) / workspace_id
    audio_path = workspace_root / "research_notebook" / "artifacts" / "binaries" / f"{audio['artifact_id']}.wav"
    assert audio_path.exists()
    wav = client.get(f"/api/workspaces/{workspace_id}/artifacts/{audio['artifact_id']}/download", params={"format": "wav"})
    assert wav.status_code == 200
    wav_descriptor = wav.json()
    assert wav_descriptor["format"] == "wav"
    assert wav_descriptor["mime_type"] == "audio/wav"
    assert wav_descriptor["size_bytes"] == audio_path.stat().st_size
    assert wav_descriptor["sha256"] == _sha256(audio_path)
    assert wav_descriptor["duration_ms"] > 0
    assert wav_descriptor["url"].startswith(f"artifact://{workspace_id}/{audio['artifact_id']}?binary=audio")
    _assert_no_internal_paths(wav_descriptor)

    export = client.post(f"/api/workspaces/{workspace_id}/artifacts/slides/export", json={"artifact_id": slides["artifact_id"]})
    assert export.status_code == 200
    pptx = export.json()
    assert pptx["status"] == "ready"
    pptx_path = workspace_root / "research_notebook" / "artifacts" / "binaries" / f"{pptx['artifact_id']}.pptx"
    assert pptx_path.exists()
    pptx_download = client.get(f"/api/workspaces/{workspace_id}/artifacts/{pptx['artifact_id']}/download", params={"format": "pptx"})
    assert pptx_download.status_code == 200
    pptx_descriptor = pptx_download.json()
    assert pptx_descriptor["format"] == "pptx"
    assert pptx_descriptor["mime_type"] == "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    assert pptx_descriptor["size_bytes"] == pptx_path.stat().st_size
    assert pptx_descriptor["sha256"] == _sha256(pptx_path)
    assert pptx_descriptor["url"].startswith(f"artifact://{workspace_id}/{pptx['artifact_id']}?binary=pptx")
    _assert_no_internal_paths(pptx_descriptor)


def test_phase41_download_errors_are_structured_and_do_not_stream(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    workspace_id = _create_workspace(client, "RN V25 Phase41 Download Errors")
    source_id = _import_text_source(client, workspace_id, title="Download Error Source", content="Unsupported format returns structured errors.")
    slides = client.post(f"/api/workspaces/{workspace_id}/artifacts/slides", json={"source_ids": [source_id], "slide_count": 1}).json()["data"]["artifact"]

    missing = client.get(f"/api/workspaces/{workspace_id}/artifacts/art_missing/download", params={"format": "json"})
    assert missing.status_code == 404
    assert missing.json()["detail"]["error"]["code"] == "not_found"
    _assert_no_internal_paths(missing.json())

    unsupported = client.get(f"/api/workspaces/{workspace_id}/artifacts/{slides['artifact_id']}/download", params={"format": "exe"})
    assert unsupported.status_code == 200
    payload = unsupported.json()
    assert payload["error"]["code"] == "UNSUPPORTED_ARTIFACT_FORMAT"
    assert payload["format"] == "exe"
    assert "md" in payload["supported_formats"]
    assert "url" not in payload
    _assert_no_internal_paths(payload)
