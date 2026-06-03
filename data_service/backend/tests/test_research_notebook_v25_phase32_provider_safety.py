from fastapi.testclient import TestClient

from app.main import app
from data_service.research_notebook.providers.errors import PROVIDER_ERROR_CODES
from data_service.research_notebook.providers.redaction import redact_public_value
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


def _assert_provider_error(payload: dict, code: str):
    assert payload["available"] is False
    assert payload["status"] == "unavailable"
    assert payload["capability"]
    assert payload["provider_detail"]["available"] is False
    assert payload["error"]["code"] == code
    assert payload["error"]["code"] in PROVIDER_ERROR_CODES
    assert isinstance(payload["error"]["retryable"], bool)
    _assert_no_internal_paths(payload)


def test_phase32_provider_health_no_provider_contracts(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)

    ocr = client.post("/api/ocr/provider/health").json()
    tts = client.post("/api/tts/provider/health").json()
    pptx = client.post("/api/pptx/provider/health").json()

    _assert_provider_error(ocr, "PROVIDER_NOT_CONFIGURED")
    _assert_provider_error(tts, "PROVIDER_NOT_CONFIGURED")
    _assert_provider_error(pptx, "EXPORTER_NOT_CONFIGURED")
    assert ocr["unsupported_reason"] == "no_provider_configured"
    assert tts["unsupported_reason"] == "no_provider_configured"
    assert pptx["unsupported_reason"] == "exporter_not_configured"


def test_phase32_provider_health_failure_mode_matrix(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)

    cases = [
        ("OCR_PROVIDER", "bad-ocr", None, False, "/api/ocr/provider/health", "PROVIDER_UNSUPPORTED"),
        ("OCR_PROVIDER", "azure", None, False, "/api/ocr/provider/health", "PROVIDER_MISSING_CREDENTIAL"),
        ("OCR_PROVIDER", "azure", ("OCR_SIMULATE_ERROR", "auth_failed"), True, "/api/ocr/provider/health", "PROVIDER_AUTH_FAILED"),
        ("OCR_PROVIDER", "azure", ("OCR_SIMULATE_ERROR", "timeout"), True, "/api/ocr/provider/health", "PROVIDER_TIMEOUT"),
        ("TTS_PROVIDER", "azure", ("TTS_SIMULATE_ERROR", "quota_exceeded"), True, "/api/tts/provider/health", "PROVIDER_QUOTA_EXCEEDED"),
        ("TTS_PROVIDER", "azure", ("TTS_SIMULATE_ERROR", "bad_response"), True, "/api/tts/provider/health", "PROVIDER_BAD_RESPONSE"),
        ("TTS_PROVIDER", "azure", ("TTS_SIMULATE_ERROR", "execution_failed"), True, "/api/tts/provider/health", "PROVIDER_EXECUTION_FAILED"),
        ("TTS_PROVIDER", "azure", ("TTS_SIMULATE_ERROR", "output_invalid"), True, "/api/tts/provider/health", "PROVIDER_OUTPUT_INVALID"),
        ("PPTX_PROVIDER", "bad-exporter", None, False, "/api/pptx/provider/health", "EXPORTER_UNSUPPORTED"),
    ]

    for provider_env, provider, simulated, set_key, route, expected_code in cases:
        for name in PROVIDER_ENV:
            monkeypatch.delenv(name, raising=False)
        monkeypatch.setenv(provider_env, provider)
        if set_key and provider_env in {"OCR_PROVIDER", "TTS_PROVIDER"}:
            monkeypatch.setenv(provider_env.replace("_PROVIDER", "_API_KEY"), "secret-value")
        if simulated:
            monkeypatch.setenv(simulated[0], simulated[1])
        payload = client.post(route).json()
        _assert_provider_error(payload, expected_code)


def test_phase32_redaction_checker_covers_secrets_paths_and_tracebacks():
    payload = {
        "api_key": "sk-test-secret",
        "endpoint": "https://example.com/open",
        "message": "token=abc123SECRET path /Users/Zhuanz/Desktop/workspace/data_service file:///tmp/raw",
        "nested": {
            "Authorization": "Bearer abc123SECRET",
            "raw_traceback": "Traceback /private/tmp/provider.py",
        },
    }

    redacted = redact_public_value(payload)
    assert redacted["api_key"] == "[redacted]"
    assert redacted["nested"]["Authorization"] == "[redacted]"
    assert redacted["nested"]["raw_traceback"] == "[redacted]"
    text = str(redacted)
    assert "abc123SECRET" not in text
    assert "/Users" not in text
    assert "file://" not in text
    assert "/private/tmp" not in text


def test_phase32_pptx_provider_does_not_create_fake_exporter_availability(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    workspace_id = _create_workspace(client, "RN V25 Phase32 PPTX")
    source_id = _import_text_source(client, workspace_id, title="Slides Source", content="Slides need evidence and no fake PPTX export.")
    slides = client.post(
        f"/api/workspaces/{workspace_id}/artifacts/slides",
        json={"source_ids": [source_id], "topic": "No Fake Export", "slide_count": 2},
    ).json()["data"]["artifact"]

    monkeypatch.setenv("PPTX_PROVIDER", "local")
    health = client.post("/api/pptx/provider/health").json()
    _assert_provider_error(health, "EXPORTER_NOT_CONFIGURED")

    manifest = client.get(f"/api/workspaces/{workspace_id}/capabilities").json()["data"]["manifest"]
    assert manifest["capabilities"]["pptx_export"] is False

    export = client.post(f"/api/workspaces/{workspace_id}/artifacts/slides/export", json={"artifact_id": slides["artifact_id"]})
    assert export.status_code == 200
    assert export.json()["error"]["code"] == "SLIDE_OUTLINE_ONLY"
    _assert_no_internal_paths(export.json())


def test_phase32_provider_failure_contracts_do_not_break_fallback_artifacts(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    workspace_id = _create_workspace(client, "RN V25 Phase32 Fallback")
    source_id = _import_text_source(client, workspace_id, title="Audio Source", content="Audio remains unavailable without a working provider.")

    monkeypatch.setenv("TTS_PROVIDER", "azure")
    monkeypatch.setenv("TTS_API_KEY", "secret-value")
    monkeypatch.setenv("TTS_SIMULATE_ERROR", "timeout")
    health = client.post("/api/tts/provider/health").json()
    _assert_provider_error(health, "PROVIDER_TIMEOUT")

    audio = client.post(f"/api/workspaces/{workspace_id}/artifacts/audio", json={"source_ids": [source_id]})
    assert audio.status_code == 200
    artifact = audio.json()["data"]["artifact"]
    assert artifact["artifact_available"] is False
    assert artifact["error"]["code"] == "AUDIO_OVERVIEW_NOT_READY"
    _assert_no_internal_paths(audio.json())
