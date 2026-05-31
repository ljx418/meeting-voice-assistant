from fastapi.testclient import TestClient

from app.main import app
from test_target_http_source_preview import _assert_no_internal_paths, _create_workspace, _import_text_source


def _setup_client(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    return TestClient(app)


def test_v14f_studio_artifact_requires_evidence(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    workspace_id = _create_workspace(client, "RN Studio Empty")

    response = client.post(f"/api/workspaces/{workspace_id}/studio/artifacts", json={"artifact_type": "study_guide"})

    assert response.status_code == 200
    payload = response.json()
    artifact = payload["data"]["artifact"]
    assert artifact["artifact_available"] is False
    assert artifact["unsupported_reason"] == "no_evidence"
    assert artifact["evidence_refs"] == []
    _assert_no_internal_paths(payload)


def test_v14f_studio_artifacts_return_evidence_refs_for_lightweight_outputs(tmp_path, monkeypatch):
    import app.api.v1.data_service as data_service_api

    def _force_fallback(*_args, **_kwargs):
        from data_service.ai_provider_contract import AIProviderContractError

        raise AIProviderContractError("missing_api_key", "test fallback")

    monkeypatch.setattr(data_service_api, "ai_complete_json", _force_fallback)
    client = _setup_client(tmp_path, monkeypatch)
    workspace_id = _create_workspace(client, "RN Studio Outputs")
    source_id = _import_text_source(
        client,
        workspace_id,
        title="Digital Human Notes",
        content="Digital humans need speech synthesis, rendering, and evidence-backed governance.",
    )

    for artifact_type in ["notes", "study_guide", "briefing_doc", "faq"]:
        response = client.post(f"/api/workspaces/{workspace_id}/studio/artifacts", json={"artifact_type": artifact_type})

        assert response.status_code == 200
        payload = response.json()
        artifact = payload["data"]["artifact"]
        assert artifact["artifact_type"] == artifact_type
        assert artifact["artifact_available"] is True
        assert artifact["sections"]
        assert artifact["evidence_refs"]
        assert artifact["generation_metadata"]["fallback_mode"] is True
        assert artifact["evidence_refs"][0]["source_id"] == source_id
        assert artifact["evidence_refs"][0]["unit_id"].startswith("unit_")
        assert artifact["evidence_refs"][0]["evidence_id"].startswith("ev_")
        assert artifact["sections"][0]["evidence_refs"]
        _assert_no_internal_paths(payload)


def test_v14f_studio_artifact_rejects_unknown_type(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    workspace_id = _create_workspace(client, "RN Studio Unknown")

    response = client.post(f"/api/workspaces/{workspace_id}/studio/artifacts", json={"artifact_type": "podcast"})

    assert response.status_code == 422
    assert "VALIDATION_ERROR" in response.json()["detail"]


def test_v15c_studio_artifact_uses_ai_provider_and_section_evidence_refs(tmp_path, monkeypatch):
    import app.api.v1.data_service as data_service_api

    def _fake_ai_complete_json(*, system_prompt, user_prompt):
        assert "Studio 输出" in system_prompt
        assert "evidence_context" in user_prompt
        return (
            {
                "summary": "AI 数字人资料可沉淀为带引用的学习导读。",
                "sections": [
                    {"title": "学习目标", "content": "理解数字人的技术、产业和治理要点。", "evidence_ref_indexes": [0]},
                    {"title": "核心主题", "content": "数字人需要模型、渲染和证据治理共同支撑。", "evidence_ref_indexes": [0]},
                    {"title": "建议追问", "content": "哪些证据支持数字人落地路径？", "evidence_ref_indexes": [0]},
                ],
            },
            {
                "provider": "openai_compatible",
                "provider_name": "minimax",
                "model": "MiniMax-M2.7",
                "latency_ms": 12,
                "response_schema": "openai_chat_completions",
            },
        )

    monkeypatch.setattr(data_service_api, "ai_complete_json", _fake_ai_complete_json)
    client = _setup_client(tmp_path, monkeypatch)
    workspace_id = _create_workspace(client, "RN Studio AI Outputs")
    source_id = _import_text_source(
        client,
        workspace_id,
        title="Digital Human Studio",
        content="AI digital humans require source-grounded notes, study guides, briefing docs, and FAQ outputs.",
    )

    response = client.post(f"/api/workspaces/{workspace_id}/studio/artifacts", json={"artifact_type": "study_guide"})

    assert response.status_code == 200
    payload = response.json()
    artifact = payload["data"]["artifact"]
    assert artifact["artifact_available"] is True
    assert artifact["generation_metadata"]["fallback_mode"] is False
    assert artifact["generation_metadata"]["provider_name"] == "minimax"
    assert artifact["generation_metadata"]["prompt_version"] == "v1_5_c_ai_studio_2026_05_31"
    assert artifact["evidence_refs"][0]["source_id"] == source_id
    assert len(artifact["sections"]) >= 3
    assert all(section["evidence_refs"] for section in artifact["sections"])
    _assert_no_internal_paths(payload)


def test_v15c_studio_artifact_ai_schema_mismatch_falls_back(tmp_path, monkeypatch):
    import app.api.v1.data_service as data_service_api

    def _bad_ai_complete_json(*_args, **_kwargs):
        return ({"summary": "missing sections"}, {"provider_name": "minimax"})

    monkeypatch.setattr(data_service_api, "ai_complete_json", _bad_ai_complete_json)
    client = _setup_client(tmp_path, monkeypatch)
    workspace_id = _create_workspace(client, "RN Studio AI Fallback")
    _import_text_source(
        client,
        workspace_id,
        title="Digital Human Fallback",
        content="Digital humans require grounded Studio outputs.",
    )

    response = client.post(f"/api/workspaces/{workspace_id}/studio/artifacts", json={"artifact_type": "briefing_doc"})

    assert response.status_code == 200
    payload = response.json()
    artifact = payload["data"]["artifact"]
    assert artifact["artifact_available"] is True
    assert artifact["generation_metadata"]["fallback_mode"] is True
    assert artifact["generation_metadata"]["error_code"] == "response_schema_mismatch"
    assert artifact["sections"][0]["evidence_refs"]
    _assert_no_internal_paths(payload)


def test_v15c_studio_artifact_normalizes_missing_section_evidence_refs(tmp_path, monkeypatch):
    import app.api.v1.data_service as data_service_api

    def _ai_without_indexes(*_args, **_kwargs):
        return (
            {
                "summary": "AI 数字人资料可以生成 FAQ。",
                "sections": [
                    {"title": "数字人是什么？", "content": "数字人资料覆盖行业、技术和治理。"},
                    {"title": "有什么风险？", "content": "资料提到合规和内容溯源风险。"},
                    {"title": "资料未覆盖什么？", "content": "资料未覆盖时应继续补源。"},
                ],
            },
            {
                "provider": "openai_compatible",
                "provider_name": "minimax",
                "model": "MiniMax-M2.7",
                "latency_ms": 12,
                "response_schema": "openai_chat_completions",
            },
        )

    monkeypatch.setattr(data_service_api, "ai_complete_json", _ai_without_indexes)
    client = _setup_client(tmp_path, monkeypatch)
    workspace_id = _create_workspace(client, "RN Studio AI Normalize")
    _import_text_source(
        client,
        workspace_id,
        title="Digital Human FAQ",
        content="Digital humans require source-grounded FAQ outputs with traceable citations.",
    )

    response = client.post(f"/api/workspaces/{workspace_id}/studio/artifacts", json={"artifact_type": "faq"})

    assert response.status_code == 200
    payload = response.json()
    artifact = payload["data"]["artifact"]
    assert artifact["generation_metadata"]["fallback_mode"] is False
    assert len(artifact["sections"]) >= 3
    assert all(section["evidence_refs"] for section in artifact["sections"])
    _assert_no_internal_paths(payload)
