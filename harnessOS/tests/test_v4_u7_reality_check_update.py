import json
from pathlib import Path

from core.workflows.v4_u5e_local_document_workflow import FakeLLMProviderAdapter
from core.workflows.v4_u7_real_multi_agent_runtime import run_serial_video_runtime, write_u7_evidence_package
from scripts.v4_unified_reality_check_audit import audit_ux08


def test_ux08_audit_prefers_u7_provider_evidence(tmp_path: Path, monkeypatch) -> None:
    import scripts.v4_unified_reality_check_audit as audit

    repo = tmp_path
    evidence_dir = repo / "docs/design/V4.x/evidence/real-multi-agent/UX-08-serial-video"
    result = run_serial_video_runtime(provider_adapter=FakeLLMProviderAdapter())
    result["real_provider_backed"] = True
    result["provider"]["provider"] = "minimax"
    write_u7_evidence_package(result, evidence_dir)
    monkeypatch.setattr(audit, "REPO_ROOT", repo)

    ux = audit_ux08(set(), {})

    assert ux.status == "PASS"
    assert ux.evidence_scope == "real_runtime"
    assert ux.runtime_backed is True
    assert ux.deterministic_only is False
    assert ux.false_green_risk == "MEDIUM"
    assert not ux.missing_evidence


def test_u7_runtime_result_does_not_include_artifact_content_in_json(tmp_path: Path) -> None:
    result = run_serial_video_runtime(provider_adapter=FakeLLMProviderAdapter())
    write_u7_evidence_package(result, tmp_path)

    data = json.loads((tmp_path / "runtime-result.json").read_text(encoding="utf-8"))
    assert all("content" not in artifact for artifact in data["artifacts"])
