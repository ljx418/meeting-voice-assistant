import io
import json
import os
import wave
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
    "TTS_MODEL",
    "MINIMAX_API_KEY",
    "MINIMAX_TTS_ENDPOINT",
    "MINIMAX_ENDPOINT",
    "MINIMAX_TTS_MODEL",
    "MINIMAX_TTS_VOICE_ID",
    "DATA_SERVICE_AI_API_KEY",
    "DATA_SERVICE_AI_BASE_URL",
    "DATA_SERVICE_AI_TIMEOUT_MS",
    "PPTX_PROVIDER",
    "PPTX_SIMULATE_ERROR",
    "PPTX_EXPORTER_ENABLED",
]


class _FakeHTTPResponse:
    def __init__(self, payload: dict):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


def _setup_client(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    for name in PROVIDER_ENV:
        monkeypatch.delenv(name, raising=False)
    return TestClient(app)


def _wav_bytes() -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(16000)
        handle.writeframes(b"\x00\x00" * 3200)
    return buffer.getvalue()


def test_phase39_minimax_tts_mocked_provider_writes_real_binary_descriptor(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    monkeypatch.setenv("TTS_PROVIDER", "minimax")
    monkeypatch.setenv("DATA_SERVICE_AI_API_KEY", "secret-should-not-leak")
    monkeypatch.setenv("TTS_ENDPOINT", "https://api.minimax.example/v1/t2a_v2")
    monkeypatch.setenv("MINIMAX_TTS_MODEL", "speech-test")
    monkeypatch.setenv("MINIMAX_TTS_VOICE_ID", "voice-test")

    calls = []

    def fake_urlopen(request, timeout, **_kwargs):
        calls.append((request, timeout))
        assert request.full_url == "https://api.minimax.example/v1/t2a_v2"
        assert request.headers["Authorization"].startswith("Bearer ")
        assert b'"format": "wav"' in request.data
        return _FakeHTTPResponse({"data": {"audio": _wav_bytes().hex()}, "base_resp": {"status_code": 0}})

    monkeypatch.setattr("data_service.research_notebook.providers.tts_minimax.urllib.request.urlopen", fake_urlopen)

    workspace_id = _create_workspace(client, "RN V25 Phase39 Minimax")
    source_id = _import_text_source(
        client,
        workspace_id,
        title="Minimax Audio Source",
        content="This source proves phase thirty nine creates a Minimax audio overview with evidence.",
    )

    health = client.post("/api/tts/provider/health")
    assert health.status_code == 200
    assert health.json()["available"] is True
    assert health.json()["provider"] == "minimax"
    execution = client.post("/api/tts/provider/execution")
    assert execution.status_code == 200
    assert execution.json()["ok"] is True
    assert execution.json()["provider"]["execution_supported"] is True

    audio = client.post(f"/api/workspaces/{workspace_id}/artifacts/audio", json={"source_ids": [source_id], "language": "en-US"})
    assert audio.status_code == 200
    payload = audio.json()
    artifact = payload["data"]["artifact"]
    assert artifact["status"] == "ready"
    assert artifact["artifact_available"] is True
    assert artifact["script_available"] is True
    assert artifact["audio_available"] is True
    assert artifact["provider"]["name"] == "minimax"
    assert artifact["voice_metadata"]["engine"] == "minimax_t2a_v2"
    assert artifact["generation_metadata"]["provider"] == "minimax"
    assert artifact["script"][0]["evidence_refs"]
    assert artifact["binary"]["mime_type"] == "audio/wav"
    assert artifact["binary"]["size_bytes"] > 44
    assert artifact["binary"]["duration_ms"] > 0
    assert len(artifact["binary"]["sha256"]) == 64
    assert calls
    _assert_no_internal_paths(payload)
    assert "secret-should-not-leak" not in str(payload)

    artifact_id = artifact["artifact_id"]
    workspace_root = Path(os.environ["DATA_SERVICE_WORKSPACE_ROOT"]) / workspace_id
    binary_path = workspace_root / "research_notebook" / "artifacts" / "binaries" / f"{artifact_id}.wav"
    assert binary_path.exists()
    assert binary_path.stat().st_size == artifact["binary"]["size_bytes"]


def test_phase39_minimax_missing_key_is_not_fake_audio_ready(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    monkeypatch.setenv("TTS_PROVIDER", "minimax")
    workspace_id = _create_workspace(client, "RN V25 Phase39 Minimax Missing Key")
    source_id = _import_text_source(client, workspace_id, title="Minimax Missing Key", content="No fake audio should be generated.")
    for name in ("TTS_API_KEY", "MINIMAX_API_KEY", "DATA_SERVICE_AI_API_KEY"):
        monkeypatch.setenv(name, "")

    health = client.post("/api/tts/provider/health")
    assert health.status_code == 200
    assert health.json()["available"] is False
    assert health.json()["error"]["code"] == "PROVIDER_MISSING_CREDENTIAL"

    audio = client.post(f"/api/workspaces/{workspace_id}/artifacts/audio", json={"source_ids": [source_id]})
    assert audio.status_code == 200
    artifact = audio.json()["data"]["artifact"]
    assert artifact["status"] == "error"
    assert artifact["artifact_available"] is False
    assert artifact["error"]["code"] == "AUDIO_OVERVIEW_NOT_READY"
    assert "binary" not in artifact
    _assert_no_internal_paths(audio.json())
