from fastapi.testclient import TestClient

from app.main import app
from test_target_http_source_preview import _assert_no_internal_paths, _create_workspace, _import_text_source


def _setup_client(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    return TestClient(app)


def test_v16e_research_refuses_without_sources(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    workspace_id = _create_workspace(client, "RN V1.6-E No Sources")

    response = client.post(f"/api/workspaces/{workspace_id}/research", json={"question": "数字人监管风险有哪些？"})

    assert response.status_code == 200
    payload = response.json()
    report = payload["data"]["research"]
    assert report["research_available"] is False
    assert report["coverage_status"] == "no_sources"
    assert report["answer_basis"] == "source_grounded_refusal"
    assert report["supported_conclusions"] == []
    assert report["suggested_source_actions"]
    _assert_no_internal_paths(payload)


def test_v16e_research_returns_resolvable_evidence_refs(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    workspace_id = _create_workspace(client, "RN V1.6-E Research")
    source_id = _import_text_source(
        client,
        workspace_id,
        title="数字人监管风险",
        content=(
            "数字人应用需要标注 AI 生成身份，并建立肖像授权、内容审核和证据留存机制。\n\n"
            "企业在客服和培训场景使用数字人时，应记录来源依据以支持合规审计。"
        ),
    )

    response = client.post(f"/api/workspaces/{workspace_id}/research", json={"question": "肖像授权 内容审核 证据留存", "top_k": 4})

    assert response.status_code == 200
    payload = response.json()
    report = payload["data"]["research"]
    assert report["research_available"] is True
    assert report["coverage_status"] == "source_supported"
    assert report["supported_conclusions"]
    assert "conflicts" in report
    assert "missing_evidence" in report
    evidence = report["supported_conclusions"][0]["evidence_refs"][0]
    assert evidence["source_id"] == source_id
    assert evidence["unit_id"].startswith("unit_")
    assert evidence["evidence_id"].startswith("ev_")

    unit = client.get(f"/api/workspaces/{workspace_id}/sources/{source_id}/units/{evidence['unit_id']}")
    assert unit.status_code == 200
    span = client.get(
        f"/api/workspaces/{workspace_id}/sources/{source_id}/units/{evidence['unit_id']}/evidence/{evidence['evidence_id']}"
    )
    assert span.status_code == 200
    assert span.json()["data"]["evidence_span"]["evidence_id"] == evidence["evidence_id"]
    _assert_no_internal_paths(payload)


def test_v19_research_labels_structured_conflicts(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    workspace_id = _create_workspace(client, "RN V1.9 Conflict Labeling")
    optimistic_source_id = _import_text_source(
        client,
        workspace_id,
        title="数字人商业化乐观口径",
        content=(
            "本资料认为，数字人项目 Alpha 在 2026 年已经实现规模化商业化。\n\n"
            "资料给出的判断依据是：该项目已经覆盖多个品牌营销场景，并且在直播、客服和培训中形成可复制交付流程。"
        ),
    )
    conservative_source_id = _import_text_source(
        client,
        workspace_id,
        title="数字人商业化保守口径",
        content=(
            "本资料认为，数字人项目 Alpha 在 2026 年尚未实现规模化商业化。\n\n"
            "资料给出的判断依据是：该项目仍处于试点阶段，客户复购和交付成本尚不稳定，监管审核流程也会影响推广速度。"
        ),
    )

    response = client.post(
        f"/api/workspaces/{workspace_id}/research",
        json={"question": "数字人项目 Alpha 在 2026 年是否已经实现规模化商业化？请列出来源之间的分歧。", "top_k": 8},
    )

    assert response.status_code == 200
    payload = response.json()
    report = payload["data"]["research"]
    assert report["research_available"] is True
    conflict = report["conflicts"][0]
    assert conflict["topic"] == "数字人项目 Alpha 2026 年规模化商业化状态"
    assert len(conflict["positions"]) == 2
    claims = [position["claim"] for position in conflict["positions"]]
    assert any("已经实现规模化商业化" in claim for claim in claims)
    assert any("尚未实现规模化商业化" in claim for claim in claims)
    source_ids = {
        position["evidence_refs"][0]["source_id"]
        for position in conflict["positions"]
        if position["evidence_refs"]
    }
    assert source_ids == {optimistic_source_id, conservative_source_id}
    for position in conflict["positions"]:
        evidence = position["evidence_refs"][0]
        unit = client.get(f"/api/workspaces/{workspace_id}/sources/{evidence['source_id']}/units/{evidence['unit_id']}")
        assert unit.status_code == 200
        span = client.get(
            f"/api/workspaces/{workspace_id}/sources/{evidence['source_id']}/units/{evidence['unit_id']}/evidence/{evidence['evidence_id']}"
        )
        assert span.status_code == 200
    _assert_no_internal_paths(payload)


def test_v19_research_does_not_label_non_conflicting_conclusions(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    workspace_id = _create_workspace(client, "RN V1.9 No Conflict")
    _import_text_source(
        client,
        workspace_id,
        title="数字人合规资料",
        content=(
            "数字人应用需要标注 AI 生成身份，并建立肖像授权、内容审核和证据留存机制。\n\n"
            "企业在客服和培训场景使用数字人时，应记录来源依据以支持合规审计。"
        ),
    )

    response = client.post(f"/api/workspaces/{workspace_id}/research", json={"question": "肖像授权 内容审核 证据留存", "top_k": 4})

    assert response.status_code == 200
    payload = response.json()
    report = payload["data"]["research"]
    assert report["research_available"] is True
    assert report["supported_conclusions"]
    assert report["conflicts"] == []
    _assert_no_internal_paths(payload)
