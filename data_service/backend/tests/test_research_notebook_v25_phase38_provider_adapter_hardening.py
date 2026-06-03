from fastapi.testclient import TestClient

from app.main import app
from test_research_notebook_v25_phase32_provider_safety import PROVIDER_ENV
from test_target_http_source_preview import _assert_no_internal_paths


def _setup_client(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    for name in PROVIDER_ENV:
        monkeypatch.delenv(name, raising=False)
    return TestClient(app)


def test_phase38_health_known_external_tts_is_not_execution_supported(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    monkeypatch.setenv("TTS_PROVIDER", "azure")
    monkeypatch.setenv("TTS_API_KEY", "secret-should-not-leak")
    monkeypatch.setenv("TTS_ENDPOINT", "https://tts.example.invalid/private")

    health = client.post("/api/tts/provider/health")
    assert health.status_code == 200
    assert health.json()["available"] is True
    assert health.json()["provider"] == "azure"

    execution = client.post("/api/tts/provider/execution")
    assert execution.status_code == 200
    payload = execution.json()
    assert payload["ok"] is False
    assert payload["status"] == "unavailable"
    assert payload["capability"] == "tts"
    assert payload["provider"]["name"] == "azure"
    assert payload["provider"]["kind"] == "external"
    assert payload["provider"]["health_known"] is True
    assert payload["provider"]["health_available"] is True
    assert payload["provider"]["execution_supported"] is False
    assert payload["error"]["code"] == "PROVIDER_UNSUPPORTED"
    assert "secret-should-not-leak" not in str(payload)
    assert "private" not in str(payload)
    _assert_no_internal_paths(payload)


def test_phase38_unknown_ocr_provider_does_not_fallback_to_tesseract(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    monkeypatch.setenv("OCR_PROVIDER", "unknown-cloud")
    monkeypatch.setenv("OCR_API_KEY", "secret-should-not-leak")

    health = client.post("/api/ocr/provider/health")
    assert health.status_code == 200
    assert health.json()["available"] is False
    assert health.json()["provider"] == "unknown-cloud"
    assert health.json()["error"]["code"] == "PROVIDER_UNSUPPORTED"

    execution = client.post("/api/ocr/provider/execution")
    assert execution.status_code == 200
    payload = execution.json()
    assert payload["ok"] is False
    assert payload["provider"]["name"] == "unknown-cloud"
    assert payload["provider"]["health_known"] is False
    assert payload["provider"]["execution_supported"] is False
    assert payload["error"]["code"] == "PROVIDER_UNSUPPORTED"
    assert payload["provider"]["name"] != "tesseract"
    assert "secret-should-not-leak" not in str(payload)
    _assert_no_internal_paths(payload)


def test_phase38_local_execution_status_tracks_local_prerequisite_health(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    monkeypatch.setenv("OCR_PROVIDER", "tesseract")

    health = client.post("/api/ocr/provider/health").json()
    execution = client.post("/api/ocr/provider/execution")
    assert execution.status_code == 200
    payload = execution.json()
    assert payload["capability"] == "ocr"
    assert payload["provider"]["name"] == "tesseract"
    assert payload["provider"]["health_known"] is True
    assert payload["provider"]["health_available"] == bool(health["available"])
    assert payload["provider"]["execution_supported"] == bool(health["available"])
    if health["available"]:
        assert payload["ok"] is True
        assert payload["status"] == "available"
        assert payload["error"] is None
    else:
        assert payload["ok"] is False
        assert payload["error"]["code"] == "PROVIDER_UNSUPPORTED"
    _assert_no_internal_paths(payload)
