from data_service.research_notebook.providers.adapter_contract import (
    ArtifactWriteResult,
    ProviderExecutionRequest,
    provider_execution_capability,
    unsupported_execution_result,
)
from data_service.research_notebook.providers.health import provider_health


def test_provider_execution_result_shape_rejects_health_only_external_tts(monkeypatch):
    monkeypatch.setenv("TTS_PROVIDER", "azure")
    monkeypatch.setenv("TTS_API_KEY", "secret-should-not-leak")
    monkeypatch.setenv("TTS_ENDPOINT", "https://tts.example.invalid/private-endpoint")

    health = provider_health("tts")
    capability = provider_execution_capability("tts", "azure", health_payload=health)
    result = unsupported_execution_result("tts", "azure", health_payload=health).to_public()

    assert health["available"] is True
    assert capability.health_known is True
    assert capability.health_available is True
    assert capability.execution_supported is False
    assert result["ok"] is False
    assert result["capability"] == "tts"
    assert result["provider"]["name"] == "azure"
    assert result["provider"]["kind"] == "external"
    assert result["provider"]["health_known"] is True
    assert result["provider"]["execution_supported"] is False
    assert result["error"]["code"] == "PROVIDER_UNSUPPORTED"
    assert result["redacted"] is True
    assert "secret-should-not-leak" not in str(result)
    assert "private-endpoint" not in str(result)


def test_local_tts_execution_support_requires_health_available(monkeypatch):
    monkeypatch.setenv("TTS_PROVIDER", "local")
    monkeypatch.delenv("TTS_API_KEY", raising=False)
    monkeypatch.delenv("TTS_ENDPOINT", raising=False)

    health = provider_health("tts")
    capability = provider_execution_capability("tts", "local", health_payload=health)

    assert capability.health_known is True
    assert capability.health_available == bool(health["available"])
    assert capability.execution_supported == bool(health["available"])
    public = capability.to_public()
    assert public["provider"]["name"] == "local"
    assert public["provider"]["execution_supported"] == bool(health["available"])


def test_unknown_provider_is_not_health_known_and_returns_unsupported(monkeypatch):
    monkeypatch.setenv("OCR_PROVIDER", "unknown-cloud")
    monkeypatch.setenv("OCR_API_KEY", "secret-should-not-leak")

    health = provider_health("ocr")
    capability = provider_execution_capability("ocr", "unknown-cloud", health_payload=health)
    result = unsupported_execution_result("ocr", "unknown-cloud", health_payload=health).to_public()

    assert capability.health_known is False
    assert capability.health_available is False
    assert capability.execution_supported is False
    assert capability.unsupported_reason == "unsupported_provider"
    assert result["error"]["code"] == "PROVIDER_UNSUPPORTED"
    assert "secret-should-not-leak" not in str(result)


def test_provider_execution_request_and_artifact_write_result_public_shape():
    request = ProviderExecutionRequest(
        capability="ocr",
        provider_name="tesseract",
        workspace_id="research-notebook",
        source_id="source_pdf",
        payload={"input_ref": "source://source_pdf"},
    )
    write_result = ArtifactWriteResult(
        ok=True,
        status="ready",
        artifact_id="ocr_123",
        artifact={
            "artifact_id": "ocr_123",
            "binary": {
                "ref": "artifact://research-notebook/ocr_123",
                "local_path": "/Users/example/private/ocr_123.json",
            },
        },
    ).to_public()

    assert request.capability == "ocr"
    assert request.provider_name == "tesseract"
    assert write_result["ok"] is True
    assert write_result["status"] == "ready"
    assert write_result["artifact_id"] == "ocr_123"
    assert write_result["redacted"] is True
    assert "/Users/example" not in str(write_result)
    assert "[redacted]" in str(write_result)
