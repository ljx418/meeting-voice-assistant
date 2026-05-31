from urllib.parse import quote

from fastapi.testclient import TestClient

from app.main import app
from test_target_http_source_preview import _assert_no_internal_paths, _create_workspace, _import_text_source, _patch_pdf_extractor


def _setup_client(tmp_path, monkeypatch):
    import app.api.v1.data_service as data_service_api
    from data_service.ai_provider_contract import AIProviderContractError

    def _force_query_fallback(*_args, **_kwargs):
        raise AIProviderContractError("missing_api_key", "test fallback")

    monkeypatch.setattr(data_service_api, "ai_complete_json", _force_query_fallback)
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    return TestClient(app)


def _setup_path_client(tmp_path, monkeypatch):
    import app.api.v1.data_service as data_service_api
    from data_service.ai_provider_contract import AIProviderContractError

    def _force_query_fallback(*_args, **_kwargs):
        raise AIProviderContractError("missing_api_key", "test fallback")

    monkeypatch.setattr(data_service_api, "ai_complete_json", _force_query_fallback)
    root = tmp_path / "managed"
    source_root = tmp_path / "sources"
    source_root.mkdir()
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_SOURCE_ROOTS", str(source_root))
    return TestClient(app), source_root


def _first_unit(client: TestClient, workspace_id: str, source_id: str) -> dict:
    response = client.get(f"/api/workspaces/{workspace_id}/sources/{source_id}/units")
    assert response.status_code == 200
    return response.json()["data"]["units"]["items"][0]


def _first_query_evidence(client: TestClient, workspace_id: str, query: str = "queue backpressure") -> dict:
    response = client.post(f"/api/workspaces/{workspace_id}/query", json={"query": query, "top_k": 4})
    assert response.status_code == 200
    payload = response.json()
    assert payload["evidence"]
    _assert_no_internal_paths(payload)
    return payload["evidence"][0]


def test_v11dbe_evidence_span_route_and_manifest_contract(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    workspace_id = _create_workspace(client, "RN Evidence Capabilities")

    manifest_response = client.get(f"/api/workspaces/{workspace_id}/capabilities")
    assert manifest_response.status_code == 200
    capabilities = manifest_response.json()["data"]["manifest"]["capabilities"]
    assert capabilities["evidence_spans"] is True
    assert capabilities["precise_span_highlight"] is True
    assert capabilities["citation_backjump"] is True

    routes = {(method, route.path) for route in app.routes for method in getattr(route, "methods", set())}
    assert ("GET", "/api/workspaces/{workspace_id}/sources/{source_id}/units/{unit_id}/evidence/{evidence_id}") in routes
    assert all("/api/v1/knowledge" not in path or "evidence" not in path for _, path in routes)


def test_v11dbe_workspace_query_returns_resolvable_evidence_span(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    workspace_id = _create_workspace(client, "RN Evidence Query")
    source_id = _import_text_source(
        client,
        workspace_id,
        content="Queue backpressure protects workers.\n\nRetry-safe operation state keeps builds observable.",
    )

    evidence = _first_query_evidence(client, workspace_id)
    assert evidence["source_id"] == source_id
    assert evidence["unit_id"].startswith("unit_")
    assert evidence["evidence_id"].startswith("ev_")
    assert evidence["snippet"]

    span_response = client.get(
        f"/api/workspaces/{workspace_id}/sources/{source_id}/units/{evidence['unit_id']}/evidence/{evidence['evidence_id']}"
    )
    assert span_response.status_code == 200
    payload = span_response.json()
    span = payload["data"]["evidence_span"]
    assert span["evidence_id"] == evidence["evidence_id"]
    assert span["source_id"] == source_id
    assert span["unit_id"] == evidence["unit_id"]
    assert span["offset_basis"] == "normalized_text"
    assert span["offset_range"] == "half_open"
    assert span["text_basis"] == "document_unit_text"
    assert span["start_offset"] == 0
    assert span["end_offset"] > span["start_offset"]
    assert span["snippet"].startswith("Queue backpressure")
    assert span["preview_available"] is True
    _assert_no_internal_paths(payload)


def test_v14e_workspace_query_refuses_without_sources(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    workspace_id = _create_workspace(client, "RN Source Grounded No Sources")

    response = client.post(f"/api/workspaces/{workspace_id}/query", json={"query": "What is covered?"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["coverage_status"] == "no_sources"
    assert payload["answer_basis"] == "source_grounded_refusal"
    assert payload["no_evidence"] is True
    assert payload["evidence"] == []
    assert payload["suggested_source_actions"]
    assert "没有可用来源" in payload["answer"]
    _assert_no_internal_paths(payload)


def test_v14e_workspace_query_refuses_when_sources_do_not_cover_question(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    workspace_id = _create_workspace(client, "RN Source Grounded Insufficient")
    _import_text_source(client, workspace_id, content="Queue backpressure protects workers.")

    response = client.post(f"/api/workspaces/{workspace_id}/query", json={"query": "quantum chip revenue forecast", "top_k": 4})

    assert response.status_code == 200
    payload = response.json()
    assert payload["coverage_status"] == "insufficient_evidence"
    assert payload["answer_basis"] == "source_grounded_refusal"
    assert payload["unsupported_reason"] == "insufficient_evidence"
    assert payload["no_evidence"] is True
    assert payload["evidence"] == []
    assert "当前资料未覆盖" in payload["answer"]
    assert payload["suggested_source_actions"]
    _assert_no_internal_paths(payload)


def test_v15d_workspace_query_uses_ai_provider_for_source_grounded_answer(tmp_path, monkeypatch):
    import app.api.v1.data_service as data_service_api

    def _fake_ai_complete_json(*, system_prompt, user_prompt):
        assert "来源约束问答" in system_prompt
        assert "evidence_context" in user_prompt
        return (
            {
                "answer": "基于来源，数字人企业应用包括企业数字员工和虚拟主播等场景。",
                "answer_basis": "source_supported",
                "key_claims": [{"claim": "数字人企业应用包含企业数字员工。", "evidence_ref_indexes": [0]}],
            },
            {
                "provider": "openai_compatible",
                "provider_name": "minimax",
                "model": "MiniMax-M2.7",
                "latency_ms": 20,
                "response_schema": "openai_chat_completions",
            },
        )

    client = _setup_client(tmp_path, monkeypatch)
    monkeypatch.setattr(data_service_api, "ai_complete_json", _fake_ai_complete_json)
    workspace_id = _create_workspace(client, "RN V1.5 QA")
    _import_text_source(
        client,
        workspace_id,
        content="AI 数字人企业应用包括企业数字员工、虚拟主播和客服助手。",
    )

    response = client.post(f"/api/workspaces/{workspace_id}/query", json={"query": "数字人企业应用", "top_k": 4})

    assert response.status_code == 200
    payload = response.json()
    assert payload["coverage_status"] == "source_supported"
    assert payload["answer_basis"] == "source_supported"
    assert payload["generation_metadata"]["fallback_mode"] is False
    assert payload["generation_metadata"]["prompt_version"] == "v1_5_d_source_grounded_qa_2026_05_27"
    assert payload["key_claims"][0]["evidence_refs"]
    assert payload["evidence_refs"]
    _assert_no_internal_paths(payload)


def test_v15d_workspace_query_ai_schema_mismatch_falls_back_without_losing_evidence(tmp_path, monkeypatch):
    import app.api.v1.data_service as data_service_api

    def _bad_ai_complete_json(*_args, **_kwargs):
        return ({"answer": "missing claims"}, {"provider_name": "minimax"})

    client = _setup_client(tmp_path, monkeypatch)
    monkeypatch.setattr(data_service_api, "ai_complete_json", _bad_ai_complete_json)
    workspace_id = _create_workspace(client, "RN V1.5 QA Fallback")
    _import_text_source(client, workspace_id, content="AI 数字人企业应用包括企业数字员工。")

    response = client.post(f"/api/workspaces/{workspace_id}/query", json={"query": "数字人企业应用", "top_k": 4})

    assert response.status_code == 200
    payload = response.json()
    assert payload["coverage_status"] == "source_supported"
    assert payload["generation_metadata"]["fallback_mode"] is True
    assert payload["generation_metadata"]["error_code"] == "response_schema_mismatch"
    assert payload["evidence_refs"]
    _assert_no_internal_paths(payload)


def test_v14c_workspace_query_returns_resolvable_pdf_evidence_span(tmp_path, monkeypatch):
    client, source_root = _setup_path_client(tmp_path, monkeypatch)
    _patch_pdf_extractor(
        monkeypatch,
        [
            "AI digital humans use speech synthesis and real-time rendering.",
            "Enterprise deployments require evidence-backed risk controls.",
        ],
    )
    workspace_id = _create_workspace(client, "RN V1.4 PDF Evidence")
    pdf = source_root / "digital-human.pdf"
    pdf.write_bytes(b"%PDF-1.7\nfake text pdf fixture\n")
    imported = client.post(f"/api/workspaces/{workspace_id}/sources", json={"paths": [str(pdf)]})
    assert imported.status_code == 200
    source_id = imported.json()["data"]["sources"][0]["source_id"]

    evidence = _first_query_evidence(client, workspace_id, query="speech synthesis rendering")
    assert evidence["source_id"] == source_id
    assert evidence["unit_id"].startswith("unit_")
    assert evidence["evidence_id"].startswith("ev_")
    assert evidence["locator"]["page_no"] == 1

    span_response = client.get(
        f"/api/workspaces/{workspace_id}/sources/{source_id}/units/{evidence['unit_id']}/evidence/{evidence['evidence_id']}"
    )
    assert span_response.status_code == 200
    payload = span_response.json()
    span = payload["data"]["evidence_span"]
    assert span["source_id"] == source_id
    assert span["unit_id"] == evidence["unit_id"]
    assert span["evidence_id"] == evidence["evidence_id"]
    assert span["locator"]["page_no"] == 1
    assert span["offset_basis"] == "normalized_text"
    assert span["offset_range"] == "half_open"
    assert span["text_basis"] == "document_unit_text"
    assert "AI digital humans" in span["snippet"]
    _assert_no_internal_paths(payload)


def test_v11dbe_evidence_span_error_semantics(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    workspace_id = _create_workspace(client, "RN Evidence Errors")
    source_a = _import_text_source(client, workspace_id, title="A", content="Queue backpressure protects workers.")
    source_b = _import_text_source(client, workspace_id, title="B", content="Different source unit.")
    unit_a = _first_unit(client, workspace_id, source_a)
    unit_b = _first_unit(client, workspace_id, source_b)
    evidence = _first_query_evidence(client, workspace_id, query="queue")

    unknown = client.get(
        f"/api/workspaces/{workspace_id}/sources/{source_a}/units/{unit_a['unit_id']}/evidence/ev_0000000000000000"
    )
    assert unknown.status_code == 404
    assert "EVIDENCE_NOT_FOUND" in unknown.json()["detail"]

    cross_unit = client.get(
        f"/api/workspaces/{workspace_id}/sources/{source_b}/units/{unit_b['unit_id']}/evidence/{evidence['evidence_id']}"
    )
    assert cross_unit.status_code == 404
    assert "EVIDENCE_NOT_FOUND" in cross_unit.json()["detail"]

    artifact_ref = quote(f"unit:{source_a}:{unit_a['unit_id']}:{evidence['evidence_id']}", safe="")
    artifact = client.get(f"/api/workspaces/{workspace_id}/sources/{source_a}/units/{unit_a['unit_id']}/evidence/{artifact_ref}")
    assert artifact.status_code == 422
    assert "VALIDATION_ERROR" in artifact.json()["detail"]

    slug = client.get(f"/api/workspaces/{workspace_id}/sources/{source_a}/units/{unit_a['unit_id']}/evidence/source-src-architecture-notes")
    assert slug.status_code == 422
    assert "VALIDATION_ERROR" in slug.json()["detail"]


def test_v11dbe_query_evidence_uses_registry_source_and_backend_unit_id(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    workspace_id = _create_workspace(client, "RN Evidence Query Shape")
    source_id = _import_text_source(client, workspace_id, content="Operation polling exposes retry-safe build state.")
    unit = _first_unit(client, workspace_id, source_id)
    evidence = _first_query_evidence(client, workspace_id, query="operation polling")

    assert evidence["source_id"] == source_id
    assert evidence["unit_id"] == unit["unit_id"]
    assert evidence["evidence_id"].startswith("ev_")
    assert "source_ref" not in evidence
    assert "artifact_ref" not in evidence
