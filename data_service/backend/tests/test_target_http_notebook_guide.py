from fastapi.testclient import TestClient

from app.main import app
from test_target_http_source_preview import _assert_no_internal_paths, _create_workspace, _import_text_source


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


def test_v14d_notebook_guide_empty_state(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    workspace_id = _create_workspace(client, "RN V1.4 Guide Empty")

    response = client.get(f"/api/workspaces/{workspace_id}/guide")
    assert response.status_code == 200
    payload = response.json()
    guide = payload["data"]["guide"]
    assert guide["guide_available"] is False
    assert guide["source_count"] == 0
    assert guide["unavailable_reason"] == "no_sources"
    assert guide["overview"] == ""
    assert guide["key_topics"] == []
    assert guide["suggested_questions"] == []
    _assert_no_internal_paths(payload)


def test_v14d_notebook_guide_uses_registry_sources_and_evidence_refs(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    workspace_id = _create_workspace(client, "RN V1.4 Guide")
    source_id = _import_text_source(
        client,
        workspace_id,
        title="数字人行业资料",
        content="AI digital humans use speech synthesis.\n\nEnterprise adoption needs risk controls.",
    )
    from data_service.ai_provider_contract import AIProviderContractError

    def fake_ai_complete_json(*, system_prompt, user_prompt):
        raise AIProviderContractError("missing_api_key", "test forces deterministic fallback")

    monkeypatch.setattr("app.api.v1.data_service.ai_complete_json", fake_ai_complete_json)

    response = client.get(f"/api/workspaces/{workspace_id}/guide")
    assert response.status_code == 200
    payload = response.json()
    guide = payload["data"]["guide"]
    assert guide["guide_available"] is True
    assert guide["source_count"] == 1
    assert "当前 Notebook 已导入 1 个来源" in guide["overview"]
    assert guide["key_topics"]
    assert guide["suggested_questions"]
    assert guide["suggested_questions"][0].startswith("数字人行业资料")
    assert guide["evidence_refs"][0]["source_id"] == source_id
    assert guide["evidence_refs"][0]["unit_id"].startswith("unit_")
    assert guide["evidence_refs"][0]["evidence_id"].startswith("ev_")
    assert guide["generation_metadata"]["fallback_mode"] is True
    _assert_no_internal_paths(payload)


def test_v15b_notebook_guide_uses_ai_provider_and_topic_evidence_refs(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    workspace_id = _create_workspace(client, "RN V1.5 AI Guide")
    source_id = _import_text_source(
        client,
        workspace_id,
        title="AI 数字人资料",
        content=(
            "AI 数字人产业正在从展示型应用走向营销、客服和培训等场景。\n\n"
            "企业落地需要关注语音合成、形象渲染、知识库接入和合规治理。"
        ),
    )

    def fake_ai_complete_json(*, system_prompt, user_prompt):
        assert "Notebook Guide" in system_prompt
        assert "evidence_context" in user_prompt
        return (
            {
                "overview": "这些资料说明 AI 数字人正在进入企业营销、客服和培训场景。",
                "key_topics": [
                    {"title": "落地场景", "summary": "资料聚焦营销、客服和培训。", "evidence_ref_indexes": [0]},
                    {"title": "技术链路", "summary": "资料提到语音合成、渲染和知识库接入。", "evidence_ref_indexes": [0]},
                    {"title": "治理要求", "summary": "资料强调合规治理。", "evidence_ref_indexes": [0]},
                ],
                "suggested_questions": ["数字人有哪些场景？", "需要哪些技术？", "有哪些治理要求？"],
            },
            {
                "provider": "openai_compatible",
                "provider_name": "minimax",
                "model": "MiniMax-M2.7",
                "latency_ms": 12,
                "response_schema": "openai_chat_completions",
            },
        )

    monkeypatch.setattr("app.api.v1.data_service.ai_complete_json", fake_ai_complete_json)

    response = client.get(f"/api/workspaces/{workspace_id}/guide")

    assert response.status_code == 200
    payload = response.json()
    guide = payload["data"]["guide"]
    assert guide["guide_available"] is True
    assert guide["overview"].startswith("这些资料说明 AI 数字人")
    assert len(guide["key_topics"]) >= 3
    assert len(guide["suggested_questions"]) >= 3
    assert guide["generation_metadata"]["provider_name"] == "minimax"
    assert guide["generation_metadata"]["model"] == "MiniMax-M2.7"
    assert guide["generation_metadata"]["prompt_version"].startswith("v1_5_b")
    assert guide["generation_metadata"]["fallback_mode"] is False
    assert guide["generation_metadata"]["evidence_ref_count"] >= 1
    for topic in guide["key_topics"]:
        assert topic["evidence_refs"]
        assert topic["evidence_refs"][0]["source_id"] == source_id
    _assert_no_internal_paths(payload)


def test_v15b_notebook_guide_ai_schema_mismatch_falls_back(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    workspace_id = _create_workspace(client, "RN V1.5 AI Guide Fallback")
    _import_text_source(
        client,
        workspace_id,
        title="AI 数字人资料",
        content="AI digital humans require evidence-backed governance.",
    )

    from data_service.ai_provider_contract import AIProviderContractError

    def fake_ai_complete_json(*, system_prompt, user_prompt):
        raise AIProviderContractError("response_schema_mismatch", "bad guide json")

    monkeypatch.setattr("app.api.v1.data_service.ai_complete_json", fake_ai_complete_json)

    response = client.get(f"/api/workspaces/{workspace_id}/guide")

    assert response.status_code == 200
    guide = response.json()["data"]["guide"]
    assert guide["guide_available"] is True
    assert guide["generation_metadata"]["fallback_mode"] is True
    assert guide["generation_metadata"]["error_code"] == "response_schema_mismatch"
    assert guide["unavailable_reason"] == "response_schema_mismatch"


def test_v14d_notebook_guide_route_is_in_openapi_schema():
    schema = app.openapi()
    assert "/api/workspaces/{workspace_id}/guide" in schema["paths"]
