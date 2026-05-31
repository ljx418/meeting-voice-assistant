import json

from fastapi.testclient import TestClient

from app.main import app


def _setup_client(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    for key in [
        "DATA_SERVICE_AI_PROVIDER",
        "DATA_SERVICE_AI_PROVIDER_NAME",
        "DATA_SERVICE_AI_BASE_URL",
        "DATA_SERVICE_AI_MODEL",
        "DATA_SERVICE_AI_API_KEY",
    ]:
        monkeypatch.delenv(key, raising=False)
    return TestClient(app)


def test_v15a_ai_provider_health_missing_api_key_is_stable(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    monkeypatch.setenv("DATA_SERVICE_AI_PROVIDER", "openai_compatible")
    monkeypatch.setenv("DATA_SERVICE_AI_PROVIDER_NAME", "minimax")
    monkeypatch.setenv("DATA_SERVICE_AI_BASE_URL", "https://example.invalid/v1")
    monkeypatch.setenv("DATA_SERVICE_AI_MODEL", "minimax-test")

    response = client.get("/api/workspaces/-/ai-provider/health")

    assert response.status_code == 200
    payload = response.json()
    health = payload["data"]["provider_health"]
    assert payload["status"] == "blocked"
    assert health["provider_available"] is False
    assert health["error_code"] == "missing_api_key"
    assert "DATA_SERVICE_AI_API_KEY" in health["message"]
    assert "secret" not in json.dumps(payload).lower()


def test_v15a_ai_provider_health_missing_provider_config_is_stable(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    monkeypatch.setenv("DATA_SERVICE_AI_API_KEY", "secret-provider-key")

    response = client.get("/api/workspaces/-/ai-provider/health")

    assert response.status_code == 200
    payload = response.json()
    health = payload["data"]["provider_health"]
    assert payload["status"] == "blocked"
    assert health["provider_available"] is False
    assert health["error_code"] == "missing_provider_config"
    assert "DATA_SERVICE_AI_PROVIDER" in health["message"]
    assert "secret-provider-key" not in json.dumps(payload)


def test_v15a_ai_provider_health_success_sanitizes_response(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    monkeypatch.setenv("DATA_SERVICE_AI_PROVIDER", "openai_compatible")
    monkeypatch.setenv("DATA_SERVICE_AI_PROVIDER_NAME", "minimax")
    monkeypatch.setenv("DATA_SERVICE_AI_BASE_URL", "https://api.minimax.example/v1")
    monkeypatch.setenv("DATA_SERVICE_AI_MODEL", "minimax-text-test")
    monkeypatch.setenv("DATA_SERVICE_AI_API_KEY", "secret-provider-key")

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return json.dumps(
                {
                    "id": "chatcmpl_test",
                    "choices": [{"message": {"content": '{"status":"ok","message":"ready"}'}}],
                    "usage": {"total_tokens": 12},
                }
            ).encode("utf-8")

    def fake_urlopen(request, timeout, context=None):
        assert request.full_url == "https://api.minimax.example/v1/chat/completions"
        assert request.headers["Authorization"] == "Bearer secret-provider-key"
        assert timeout == 30
        assert context is not None
        return FakeResponse()

    monkeypatch.setattr("data_service.ai_provider_contract.urllib.request.urlopen", fake_urlopen)

    response = client.get("/api/workspaces/-/ai-provider/health")

    assert response.status_code == 200
    payload = response.json()
    health = payload["data"]["provider_health"]
    assert payload["status"] == "ok"
    assert health["provider_available"] is True
    assert health["provider"]["provider"] == "openai_compatible"
    assert health["provider"]["provider_name"] == "minimax"
    assert health["provider"]["model"] == "minimax-text-test"
    assert health["provider"]["api_key_configured"] is True
    assert "choices" in health["raw_response_keys"]
    serialized = json.dumps(payload)
    assert "secret-provider-key" not in serialized
    assert "Authorization" not in serialized


def test_v15a_ai_provider_health_route_is_in_openapi_schema():
    schema = app.openapi()
    assert "/api/workspaces/-/ai-provider/health" in schema["paths"]
