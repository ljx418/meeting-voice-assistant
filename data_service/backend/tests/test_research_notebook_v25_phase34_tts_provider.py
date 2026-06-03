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
    "TTS_VOICES",
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


def test_phase34_provider_disabled_keeps_audio_not_ready_without_binary(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    workspace_id = _create_workspace(client, "RN V25 Phase34 TTS Disabled")
    source_id = _import_text_source(client, workspace_id, title="Audio Source", content="Audio overview requires a configured TTS provider.")

    audio = client.post(f"/api/workspaces/{workspace_id}/artifacts/audio", json={"source_ids": [source_id]})
    assert audio.status_code == 200
    artifact = audio.json()["data"]["artifact"]
    assert artifact["artifact_available"] is False
    assert artifact["error"]["code"] == "AUDIO_OVERVIEW_NOT_READY"
    assert "binary" not in artifact
    _assert_no_internal_paths(audio.json())


def test_phase34_local_espeak_real_audio_e2e_persists_binary_descriptor(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    monkeypatch.setenv("TTS_PROVIDER", "local")
    monkeypatch.setenv("TTS_DEFAULT_VOICE", "en")
    workspace_id = _create_workspace(client, "RN V25 Phase34 TTS Real")
    source_id = _import_text_source(
        client,
        workspace_id,
        title="Audio Source",
        content="This source proves phase thirty four creates a real local audio overview with evidence.",
    )

    health = client.post("/api/tts/provider/health")
    assert health.status_code == 200
    assert health.json()["available"] is True
    assert health.json()["provider"] == "local"

    audio = client.post(f"/api/workspaces/{workspace_id}/artifacts/audio", json={"source_ids": [source_id], "language": "en-US", "voice_id": "en"})
    assert audio.status_code == 200
    payload = audio.json()
    artifact = payload["data"]["artifact"]
    assert artifact["artifact_type"] == "audio_overview"
    assert artifact["status"] == "ready", artifact
    assert artifact["artifact_available"] is True
    assert artifact["script_available"] is True
    assert artifact["audio_available"] is True
    assert artifact["script"]
    assert artifact["script"][0]["evidence_refs"]
    assert artifact["voice_metadata"]["engine"] == "espeak-ng"
    assert artifact["binary"]["mime_type"] == "audio/wav"
    assert artifact["binary"]["size_bytes"] > 1000
    assert len(artifact["binary"]["sha256"]) == 64
    assert artifact["binary"]["duration_ms"] > 0
    assert artifact["binary"]["ref"].startswith(f"artifact://{workspace_id}/{artifact['artifact_id']}?binary=audio")
    _assert_no_internal_paths(payload)

    artifact_id = artifact["artifact_id"]
    workspace_root = Path(__import__("os").environ["DATA_SERVICE_WORKSPACE_ROOT"]) / workspace_id
    binary_path = workspace_root / "research_notebook" / "artifacts" / "binaries" / f"{artifact_id}.wav"
    assert binary_path.exists()
    assert binary_path.stat().st_size == artifact["binary"]["size_bytes"]

    readback = client.get(f"/api/workspaces/{workspace_id}/artifacts/{artifact_id}")
    assert readback.status_code == 200
    assert readback.json()["data"]["artifact"]["binary"]["sha256"] == artifact["binary"]["sha256"]
    status = client.get(f"/api/workspaces/{workspace_id}/artifacts/{artifact_id}/status")
    assert status.status_code == 200
    assert status.json()["data"]["status"] == "ready"
    download = client.get(f"/api/workspaces/{workspace_id}/artifacts/{artifact_id}/download", params={"format": "wav"})
    assert download.status_code == 200
    descriptor = download.json()
    assert descriptor["format"] == "wav"
    assert descriptor["mime_type"] == "audio/wav"
    assert descriptor["size_bytes"] == binary_path.stat().st_size
    assert descriptor["sha256"] == artifact["binary"]["sha256"]
    assert descriptor["duration_ms"] > 0
    assert descriptor["url"].startswith(f"artifact://{workspace_id}/{artifact_id}?binary=audio")
    _assert_no_internal_paths(readback.json())
    _assert_no_internal_paths(descriptor)


def test_phase34_script_only_is_not_audio_ready_for_unimplemented_external_provider(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    monkeypatch.setenv("TTS_PROVIDER", "azure")
    monkeypatch.setenv("TTS_API_KEY", "secret-value")
    workspace_id = _create_workspace(client, "RN V25 Phase34 External")
    source_id = _import_text_source(client, workspace_id, title="Audio Source", content="External providers are not accepted in this local phase.")

    audio = client.post(f"/api/workspaces/{workspace_id}/artifacts/audio", json={"source_ids": [source_id]})
    assert audio.status_code == 200
    artifact = audio.json()["data"]["artifact"]
    assert artifact["status"] == "error"
    assert artifact["script_available"] is True
    assert artifact["audio_available"] is False
    assert artifact["error"]["code"] == "PROVIDER_UNSUPPORTED"
    assert "binary" not in artifact
    _assert_no_internal_paths(audio.json())
