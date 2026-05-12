import json
import sys
import zipfile
from pathlib import Path

import pytest

from data_service import (
    ArtifactLayout,
    DataService,
    DistilledUnit,
    DistilledUnitKind,
    EngineTarget,
    GraphExecutionOwner,
    GraphRAGWorkspaceAdapter,
    LLMWikiEngineAdapter,
    QueryMode,
)
from data_service.adapters import AdapterResult
from data_service.models import AuthorityLevel


def _write_minimal_docx(path: Path, paragraphs: list[str]) -> None:
    document_body = "".join(
        f"<w:p><w:r><w:t>{text}</w:t></w:r></w:p>"
        for text in paragraphs
    )
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("[Content_Types].xml", "<Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\"/>")
        archive.writestr("_rels/.rels", "")
        archive.writestr(
            "word/document.xml",
            (
                "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
                "<w:document xmlns:w=\"http://schemas.openxmlformats.org/wordprocessingml/2006/main\">"
                f"<w:body>{document_body}</w:body></w:document>"
            ),
        )


def test_artifact_layout_from_workspace(tmp_path):
    workspace = tmp_path / "workspace"
    layout = ArtifactLayout.from_workspace(workspace)

    assert layout.raw_dir == (workspace / "llmwiki" / "raw").resolve()
    assert layout.readable_dir == (workspace / "llmwiki" / "readable").resolve()
    assert layout.normalized_dir == (workspace / "llmwiki" / "normalized").resolve()
    assert layout.distill_dir == (workspace / "distill").resolve()
    assert layout.distill_sources_dir == (workspace / "distill" / "sources").resolve()
    assert layout.distill_units_dir == (workspace / "distill" / "units").resolve()
    assert layout.distill_manifest == (workspace / "distill" / "manifest.json").resolve()
    assert layout.distill_schema == (workspace / "distill" / "schema.json").resolve()
    assert layout.graphrag_input_dir == (workspace / "graphrag" / "input").resolve()
    assert layout.graphrag_state_dir == (workspace / "graphrag" / "state").resolve()
    assert layout.graphrag_execution_owner == (workspace / "graphrag" / "cache" / "execution_owner.json").resolve()
    assert layout.graphrag_execution_request == (workspace / "graphrag" / "cache" / "execution_request.json").resolve()
    assert layout.summary_dir == (workspace / "summary").resolve()
    assert layout.summary_md == (workspace / "summary" / "summary.md").resolve()
    assert layout.summary_json == (workspace / "summary" / "summary.json").resolve()
    assert layout.quality_dir == (workspace / "quality").resolve()
    assert layout.quality_feedback_jsonl == (workspace / "quality" / "feedback.jsonl").resolve()
    assert layout.quality_correction_rules_json == (workspace / "quality" / "correction_rules.json").resolve()
    assert layout.quality_correction_plan_json == (workspace / "quality" / "correction_plan.json").resolve()


def test_data_service_builds_single_ingest_dual_engine_plan(tmp_path):
    workspace = tmp_path / "workspace"
    doc_a = tmp_path / "a.md"
    doc_b = tmp_path / "b.json"
    doc_a.write_text("# A\n", encoding="utf-8")
    doc_b.write_text('{"title":"B"}', encoding="utf-8")
    service = DataService(workspace)

    plan = service.build_ingest_plan([str(doc_a), str(doc_b)])

    assert plan.targets == [EngineTarget.LLMWIKI, EngineTarget.GRAPHRAG]
    assert plan.graphrag_execution_owner == GraphExecutionOwner.APP_GRAPHRAG
    assert plan.stages == [
        "row",
        "extract",
        "normalize",
        "distill",
        "llmwiki_compile",
        "graphrag_index",
        "summary",
    ]
    assert plan.distill_policy["graphrag_prefers_distill"] is True
    assert len(plan.sources) == 2


def test_data_service_directory_ingest_skips_symlink_outside_source_root(tmp_path):
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    inside = source_dir / "inside.md"
    inside.write_text("# Inside\n", encoding="utf-8")
    outside = tmp_path / "outside.md"
    outside.write_text("# Secret\n", encoding="utf-8")
    link = source_dir / "linked-secret.md"
    try:
        link.symlink_to(outside)
    except OSError as exc:
        pytest.skip(f"symlink unavailable: {exc}")

    service = DataService(tmp_path / "workspace")
    plan = service.build_ingest_plan([str(source_dir)])

    assert [Path(source.path) for source in plan.sources] == [inside.resolve()]


def test_data_service_expands_directory_paths(tmp_path):
    workspace = tmp_path / "workspace"
    source_dir = tmp_path / "row" / "deepseek_split"
    source_dir.mkdir(parents=True)
    (source_dir / "a.json").write_text('{"title":"A"}', encoding="utf-8")
    (source_dir / "b.md").write_text("# B\n", encoding="utf-8")
    (source_dir / ".hidden.json").write_text('{"title":"hidden"}', encoding="utf-8")

    service = DataService(workspace)
    plan = service.build_ingest_plan([str(source_dir)])

    assert [Path(source.path).name for source in plan.sources] == ["a.json", "b.md"]


def test_data_service_writes_summary_files(tmp_path):
    workspace = tmp_path / "workspace"
    service = DataService(workspace)
    plan = service.build_ingest_plan(["/tmp/notes.md"])

    service.write_summary_files(plan)

    assert service.layout.summary_dir.exists()
    assert service.layout.summary_md.exists()
    assert service.layout.summary_json.exists()
    markdown = service.layout.summary_md.read_text(encoding="utf-8")
    assert "data_service" in markdown
    assert "distill" in markdown
    payload = json.loads(service.layout.summary_json.read_text(encoding="utf-8"))
    assert payload["distill_schema_version"] == DataService.DISTILL_SCHEMA_VERSION
    assert "quality" in payload


def test_data_service_records_quality_feedback_in_workspace(tmp_path):
    workspace = tmp_path / "workspace"
    service = DataService(workspace)

    feedback = service.record_quality_feedback(
        target_type="page",
        target_id="vscode",
        action="rename_suggest",
        label="VSCode",
        suggested_value="VS Code",
        reason="页面标题应使用官方写法",
        metadata={"source": "test"},
    )

    assert feedback["target_type"] == "page"
    assert feedback["target_id"] == "vscode"
    assert feedback["action"] == "rename_suggest"
    assert service.layout.quality_feedback_jsonl.exists()
    assert service.layout.quality_feedback_jsonl.resolve().is_relative_to(workspace.resolve())
    records = service.read_quality_feedback(limit=10)
    assert records["total_count"] == 1
    assert records["summary"]["feedback_count"] == 1
    assert records["summary"]["action_counts"]["rename_suggest"] == 1
    assert records["summary"]["target_type_counts"]["page"] == 1
    filtered = service.read_quality_feedback(limit=10, target_type="source")
    assert filtered["filtered_count"] == 0
    summary_payload = json.loads(service.layout.summary_json.read_text(encoding="utf-8"))
    assert summary_payload["quality"]["manual_feedback"]["feedback_count"] == 1
    assert summary_payload["quality"]["correction_rules"]["rule_count"] == 1


def test_data_service_builds_draft_correction_rules_from_feedback(tmp_path):
    workspace = tmp_path / "workspace"
    service = DataService(workspace)
    service.record_quality_feedback(
        target_type="entity",
        target_id="old-entity",
        action="merge_suggest",
        label="Old Entity",
        suggested_value="Canonical Entity",
        reason="同一实体需要合并",
    )
    service.record_quality_feedback(
        target_type="entity",
        target_id="noise-entity",
        action="mark_noise",
        label="Noise Entity",
        reason="图谱噪音",
    )
    service.record_quality_feedback(
        target_type="page",
        target_id="good-page",
        action="confirm_good",
        label="Good Page",
    )

    payload = service.build_quality_correction_rules()

    assert service.layout.quality_correction_rules_json.exists()
    assert payload["source_feedback_count"] == 3
    assert payload["summary"]["rule_count"] == 2
    assert payload["summary"]["rule_type_counts"] == {"merge": 1, "suppress": 1}
    rules = service.read_quality_correction_rules(limit=10)
    assert rules["total_count"] == 2
    assert {item["rule_type"] for item in rules["items"]} == {"merge", "suppress"}
    merge_rule = next(item for item in rules["items"] if item["rule_type"] == "merge")
    assert merge_rule["status"] == "draft"
    assert merge_rule["proposed_value"] == "Canonical Entity"


def test_data_service_reviews_correction_rule_and_preserves_status_on_rebuild(tmp_path):
    workspace = tmp_path / "workspace"
    service = DataService(workspace)
    service.record_quality_feedback(
        target_type="entity",
        target_id="old-entity",
        action="merge_suggest",
        label="Old Entity",
        suggested_value="Canonical Entity",
        reason="同一实体需要合并",
    )
    rules = service.read_quality_correction_rules(limit=10)
    rule_id = rules["items"][0]["rule_id"]

    reviewed = service.review_quality_correction_rule(
        rule_id=rule_id,
        status="approved",
        reviewer="tester",
        note="确认合并",
    )

    assert reviewed["rule"]["status"] == "approved"
    assert reviewed["rule"]["reviewer"] == "tester"
    assert reviewed["summary"]["status_counts"]["approved"] == 1
    rebuilt = service.build_quality_correction_rules()
    assert rebuilt["rules"][0]["status"] == "approved"
    assert rebuilt["rules"][0]["review_note"] == "确认合并"
    summary_payload = json.loads(service.layout.summary_json.read_text(encoding="utf-8"))
    assert summary_payload["quality"]["correction_rules"]["status_counts"]["approved"] == 1


def test_data_service_revokes_approved_rule_and_removes_it_from_plan(tmp_path):
    workspace = tmp_path / "workspace"
    service = DataService(workspace)
    service.record_quality_feedback(
        target_type="entity",
        target_id="old-entity",
        action="rename_suggest",
        label="Old Entity",
        suggested_value="Canonical Entity",
    )
    rule_id = service.read_quality_correction_rules(limit=10)["items"][0]["rule_id"]
    approved = service.review_quality_correction_rule(rule_id=rule_id, status="approved", reviewer="tester")
    assert approved["correction_plan"]["source_rule_count"] == 1

    revoked = service.review_quality_correction_rule(
        rule_id=rule_id,
        status="revoked",
        reviewer="tester",
        note="误批准，撤回",
    )

    assert revoked["rule"]["status"] == "revoked"
    assert revoked["summary"]["status_counts"]["revoked"] == 1
    plan = service.read_quality_correction_plan()
    assert plan["source_rule_count"] == 0
    assert plan["summary"]["action_count"] == 0
    rebuilt = service.build_quality_correction_rules()
    assert rebuilt["rules"][0]["status"] == "revoked"


def test_data_service_builds_approved_correction_plan_and_applies_graph_policy(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    service = DataService(workspace)
    service.record_quality_feedback(
        target_type="entity",
        target_id="noise-entity",
        action="mark_noise",
        label="Noise Entity",
        reason="图谱噪音",
    )
    service.record_quality_feedback(
        target_type="entity",
        target_id="old-entity",
        action="rename_suggest",
        label="Old Entity",
        suggested_value="Canonical Entity",
        reason="展示名称不自然",
    )
    service.layout.ensure_directories()
    (service.layout.llmwiki_pages_dir / "old-entity.md").write_text(
        "# Old Entity\n\nOld Entity appears in this page.\n",
        encoding="utf-8",
    )
    rules = service.read_quality_correction_rules(limit=10)["items"]
    for rule in rules:
        service.review_quality_correction_rule(rule_id=rule["rule_id"], status="approved", reviewer="tester")

    def fake_snapshot(workspace_path, *, max_nodes):
        return {
            "nodes": [
                {"id": "noise-entity", "label": "Noise Entity", "name": "Noise Entity", "type": "entity"},
                {"id": "old-entity", "label": "Old Entity", "name": "Old Entity", "type": "entity"},
            ],
            "edges": [{"source": "noise-entity", "target": "old-entity"}],
            "communities": [{"id": "c1", "title": "C1", "entity_ids": ["noise-entity", "old-entity"], "entity_count": 2}],
            "stats": {"entity_count": 2, "relationship_count": 1, "community_count": 1, "document_count": 1},
            "db_path": str(Path(workspace_path) / "graphrag" / "state" / "graphrag.db"),
            "source": "app.graphrag.bridge",
        }

    monkeypatch.setattr("app.graphrag.service.read_workspace_graph_snapshot", fake_snapshot)
    plan = service.build_quality_correction_plan()

    assert service.layout.quality_correction_plan_json.exists()
    assert plan["source_rule_count"] == 2
    assert plan["summary"]["action_counts"] == {"rename_target": 1, "suppress_target": 1}
    assert plan["summary"]["impacted_action_count"] == 2
    assert plan["summary"]["impact_counts"]["graph_nodes"] == 2
    assert plan["summary"]["impact_counts"]["llmwiki_pages"] == 1
    rename_action = next(item for item in plan["actions"] if item["action"] == "rename_target")
    assert rename_action["impact"]["graph_nodes"][0]["name"] == "Old Entity"
    assert rename_action["impact"]["llmwiki_pages"][0]["slug"] == "old-entity"

    graph = service.get_graph_snapshot(max_nodes=20)

    assert [node["name"] for node in graph["nodes"]] == ["Canonical Entity"]
    assert graph["edges"] == []
    assert graph["communities"][0]["entity_ids"] == ["old-entity"]
    assert graph["quality_plan"]["applied_action_count"] == 2
    assert graph["quality_plan"]["suppressed_node_count"] == 1
    assert graph["quality_diagnostics"]["summary"]["top_community_count"] == 1
    assert graph["quality_diagnostics"]["summary"]["isolated_node_count"] == 1


def test_data_service_graph_snapshot_includes_quality_diagnostics(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    service = DataService(workspace)

    def fake_snapshot(workspace_path, *, max_nodes):
        return {
            "nodes": [
                {
                    "id": "central-entity",
                    "label": "Central Entity",
                    "name": "Central Entity",
                    "type": "entity",
                    "node_type": "entity",
                    "document_count": 3,
                    "weighted_count": 3.0,
                },
                {
                    "id": "isolated-entity",
                    "label": "Isolated Entity",
                    "name": "Isolated Entity",
                    "type": "entity",
                    "node_type": "entity",
                    "document_count": 1,
                    "weighted_count": 1.0,
                },
                {
                    "id": "theme-1",
                    "label": "Theme",
                    "name": "Theme",
                    "type": "theme",
                    "node_type": "theme",
                    "document_count": 1,
                    "weighted_count": 1.0,
                },
            ],
            "edges": [{"source": "central-entity", "target": "theme-1", "label": "belongs_to"}],
            "communities": [
                {
                    "id": "community-strong",
                    "title": "Strong Community",
                    "entity_ids": ["central-entity", "theme-1"],
                    "entity_count": 2,
                    "relationship_count": 1,
                    "score": 4.0,
                },
                {
                    "id": "community-weak",
                    "title": "Weak Community",
                    "entity_ids": ["isolated-entity"],
                    "entity_count": 1,
                    "relationship_count": 0,
                    "score": 1.0,
                },
            ],
            "stats": {"entity_count": 2, "theme_count": 1, "relationship_count": 1, "community_count": 2, "document_count": 3},
            "source": "app.graphrag.bridge",
            "db_path": "",
        }

    monkeypatch.setattr("app.graphrag.service.read_workspace_graph_snapshot", fake_snapshot)
    graph = service.get_graph_snapshot(max_nodes=20)
    diagnostics = graph["quality_diagnostics"]

    assert diagnostics["schema_version"] == "1.0"
    assert [item["id"] for item in diagnostics["top_communities"][:2]] == ["community-strong", "community-weak"]
    assert diagnostics["weak_communities"][0]["feedback_target"]["target_type"] == "community"
    assert diagnostics["weak_communities"][0]["feedback_target"]["suggested_action"] == "needs_review"
    assert diagnostics["isolated_nodes"][0]["id"] == "isolated-entity"
    assert diagnostics["isolated_nodes"][0]["feedback_target"]["suggested_action"] == "mark_noise"
    assert diagnostics["low_value_nodes"][0]["id"] == "isolated-entity"


def test_data_service_applies_correction_plan_to_graphrag_query(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    service = DataService(workspace)
    service.record_quality_feedback(
        target_type="entity",
        target_id="noise-entity",
        action="mark_noise",
        label="Noise Entity",
    )
    service.record_quality_feedback(
        target_type="entity",
        target_id="old-entity",
        action="rename_suggest",
        label="Old Entity",
        suggested_value="Canonical Entity",
    )
    for rule in service.read_quality_correction_rules(limit=10)["items"]:
        service.review_quality_correction_rule(rule_id=rule["rule_id"], status="approved")
    service.build_quality_correction_plan()

    def fake_query(workspace_path, query_text, *, top_k):
        return {
            "graph_model_version": DataService.GRAPH_QUERY_MODEL_VERSION,
            "nodes": [
                {"id": "noise-entity", "label": "Noise Entity", "name": "Noise Entity", "type": "entity"},
                {"id": "old-entity", "label": "Old Entity", "name": "Old Entity", "type": "entity"},
            ],
            "edges": [{"source": "noise-entity", "target": "old-entity"}],
            "communities": [],
            "hits": [
                {"title": "Entity: Noise Entity", "snippet": "Noise Entity hit", "source": "noise-entity", "score": 1.0, "meta": {"kind": "entity"}},
                {"title": "Entity: Old Entity", "snippet": "Old Entity hit", "source": "old-entity", "score": 0.9, "meta": {"kind": "entity"}},
            ],
            "units": [],
            "stats": {"entity_count": 2, "relationship_count": 1, "community_count": 0, "document_count": 1},
            "source": "app.graphrag.bridge",
        }

    monkeypatch.setattr("app.graphrag.service.query_workspace_graph", fake_query)
    result = service.query_graphrag("entity", top_k=5)

    assert [node["name"] for node in result.engine_payloads["graphrag"]["nodes"]] == ["Canonical Entity"]
    assert result.engine_payloads["graphrag"]["edges"] == []
    assert [hit.title for hit in result.hits] == ["Entity: Canonical Entity"]
    assert result.hits[0].snippet == "Canonical Entity hit"
    assert result.hits[0].meta["kind"] == "entity"
    assert result.engine_payloads["graphrag"]["quality_plan"]["suppressed_node_count"] == 1
    impact = result.engine_payloads["graphrag"]["quality_plan"]["query_hit_impact"]
    assert impact["suppressed_count"] == 1
    assert impact["rewritten_count"] == 1
    assert impact["suppressed_hits"][0]["title"] == "Entity: Noise Entity"
    assert impact["rewritten_hits"][0]["original_title"] == "Entity: Old Entity"


def test_data_service_applies_correction_plan_to_llmwiki_query(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    service = DataService(workspace)
    service.record_quality_feedback(
        target_type="page",
        target_id="noise-page",
        action="mark_noise",
        label="Noise Page",
    )
    service.record_quality_feedback(
        target_type="page",
        target_id="old-page",
        action="rename_suggest",
        label="Old Page",
        suggested_value="Canonical Page",
    )
    for rule in service.read_quality_correction_rules(limit=10)["items"]:
        service.review_quality_correction_rule(rule_id=rule["rule_id"], status="approved")
    service.build_quality_correction_plan()

    class FakeEngine:
        def __init__(self, config):
            self.config = config

        def search(self, query_text, *, top_k, scope):
            return {
                "pages": [
                    {"title": "Noise Page", "snippet": "Noise Page body", "result_id": "noise-page", "score": 1.0},
                    {"title": "Old Page", "snippet": "Old Page body", "result_id": "old-page", "score": 0.9},
                ],
                "passages": [],
            }

    monkeypatch.setattr("data_service.service.WikiEngine", FakeEngine)
    result = service.query_llmwiki("page", top_k=5)

    assert [hit.title for hit in result.hits] == ["Canonical Page"]
    assert result.hits[0].snippet == "Canonical Page body"
    impact = result.engine_payloads["llmwiki"]["quality_plan"]["query_hit_impact"]
    assert impact["suppressed_count"] == 1
    assert impact["rewritten_count"] == 1


def test_data_service_graph_policy_merges_existing_canonical_and_updates_community(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    service = DataService(workspace)
    service.record_quality_feedback(
        target_type="entity",
        target_id="old-entity",
        action="merge_suggest",
        label="Old Entity",
        suggested_value="Canonical Entity",
    )
    service.record_quality_feedback(
        target_type="community",
        target_id="c1",
        action="rename_suggest",
        label="Noisy Community",
        suggested_value="Canonical Community",
    )
    for rule in service.read_quality_correction_rules(limit=10)["items"]:
        service.review_quality_correction_rule(rule_id=rule["rule_id"], status="approved")

    def fake_snapshot(workspace_path, *, max_nodes):
        return {
            "nodes": [
                {"id": "old-entity", "label": "Old Entity", "name": "Old Entity", "type": "entity", "node_type": "entity"},
                {"id": "canonical-entity", "label": "Canonical Entity", "name": "Canonical Entity", "type": "entity", "node_type": "entity"},
                {"id": "theme-1", "label": "Theme", "name": "Theme", "type": "theme", "node_type": "theme"},
            ],
            "edges": [
                {"source": "old-entity", "target": "theme-1", "label": "rel"},
                {"source": "canonical-entity", "target": "theme-1", "label": "rel"},
            ],
            "communities": [
                {"id": "c1", "title": "Noisy Community", "entity_ids": ["old-entity", "canonical-entity"], "entity_count": 2},
            ],
            "stats": {"entity_count": 2, "theme_count": 1, "relationship_count": 2, "community_count": 1, "document_count": 1},
            "source": "app.graphrag.bridge",
            "db_path": "",
        }

    monkeypatch.setattr("app.graphrag.service.read_workspace_graph_snapshot", fake_snapshot)
    service.build_quality_correction_plan()
    graph = service.get_graph_snapshot(max_nodes=20)

    assert [node["id"] for node in graph["nodes"]] == ["canonical-entity", "theme-1"]
    assert graph["edges"] == [{"source": "canonical-entity", "target": "theme-1", "label": "rel"}]
    assert graph["communities"][0]["title"] == "Canonical Community"
    assert graph["communities"][0]["entity_ids"] == ["canonical-entity"]
    assert graph["stats"]["entity_count"] == 1
    assert graph["stats"]["theme_count"] == 1


def test_data_service_applies_correction_plan_to_llmwiki_page(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    service = DataService(workspace)
    service.record_quality_feedback(
        target_type="page",
        target_id="old-page",
        action="rename_suggest",
        label="Old Page",
        suggested_value="Canonical Page",
    )
    rule = service.read_quality_correction_rules(limit=10)["items"][0]
    service.review_quality_correction_rule(rule_id=rule["rule_id"], status="approved")
    service.build_quality_correction_plan()

    class FakeEngine:
        def __init__(self, config):
            self.config = config

        def read_page(self, slug):
            return {
                "page": {
                    "slug": slug,
                    "title": "Old Page",
                    "summary": "Old Page summary",
                    "body_md": "# Old Page\n\nOld Page body.",
                },
                "sources": [],
                "citations": [],
                "backlinks": [{"slug": "old-page", "title": "Old Page"}],
            }

    monkeypatch.setattr("data_service.service.WikiEngine", FakeEngine)
    page = service.read_llmwiki_page("old-page")

    assert page["page"]["title"] == "Canonical Page"
    assert "Canonical Page body" in page["page"]["body_md"]
    assert page["backlinks"][0]["title"] == "Canonical Page"
    assert page["quality_plan"]["applied_action_count"] == 1


def test_data_service_applies_correction_plan_to_llmwiki_markdown_files(tmp_path):
    workspace = tmp_path / "workspace"
    service = DataService(workspace)
    service.layout.ensure_directories()
    page_path = service.layout.llmwiki_pages_dir / "old-page.md"
    page_path.write_text("# Old Page\n\nOld Page body.\n", encoding="utf-8")
    service.record_quality_feedback(
        target_type="page",
        target_id="old-page",
        action="rename_suggest",
        label="Old Page",
        suggested_value="Canonical Page",
    )
    rule = service.read_quality_correction_rules(limit=10)["items"][0]
    service.review_quality_correction_rule(rule_id=rule["rule_id"], status="approved")
    service.build_quality_correction_plan()

    result = service.apply_quality_plan_to_llmwiki_markdown_files()

    assert result["status"] == "applied"
    assert result["updated_count"] == 1
    rewritten = page_path.read_text(encoding="utf-8")
    assert "# Canonical Page" in rewritten
    assert "Canonical Page body" in rewritten
    assert "Old Page" not in rewritten


def test_data_service_marks_suppressed_llmwiki_markdown_file(tmp_path):
    workspace = tmp_path / "workspace"
    service = DataService(workspace)
    service.layout.ensure_directories()
    page_path = service.layout.llmwiki_pages_dir / "noise-page.md"
    page_path.write_text("# Noise Page\n\nNoise Page body.\n", encoding="utf-8")
    service.record_quality_feedback(
        target_type="page",
        target_id="noise-page",
        action="mark_noise",
        label="Noise Page",
    )
    rule = service.read_quality_correction_rules(limit=10)["items"][0]
    service.review_quality_correction_rule(rule_id=rule["rule_id"], status="approved")
    service.build_quality_correction_plan()

    result = service.apply_quality_plan_to_llmwiki_markdown_files()

    assert result["updated_pages"][0]["quality_suppressed"] is True
    assert page_path.read_text(encoding="utf-8").startswith("<!-- quality_suppressed: true -->")


def test_data_service_marks_merged_llmwiki_topic_and_appends_canonical_signal(tmp_path):
    workspace = tmp_path / "workspace"
    service = DataService(workspace)
    service.layout.ensure_directories()
    old_path = service.layout.llmwiki_pages_dir / "old-topic.md"
    canonical_path = service.layout.llmwiki_pages_dir / "canonical-topic.md"
    old_path.write_text("# Old Topic\n\nOld Topic detail.\n", encoding="utf-8")
    canonical_path.write_text("# Canonical Topic\n\nCanonical Topic detail.\n", encoding="utf-8")
    service.record_quality_feedback(
        target_type="page",
        target_id="old-topic",
        action="merge_suggest",
        label="Old Topic",
        suggested_value="Canonical Topic",
    )
    rule = service.read_quality_correction_rules(limit=10)["items"][0]
    service.review_quality_correction_rule(rule_id=rule["rule_id"], status="approved")
    service.build_quality_correction_plan()

    result = service.apply_quality_plan_to_llmwiki_markdown_files()

    old_body = old_path.read_text(encoding="utf-8")
    canonical_body = canonical_path.read_text(encoding="utf-8")
    assert result["updated_pages"][0]["quality_merged_into"] == "Canonical Topic"
    assert "<!-- quality_merged_into: Canonical Topic -->" in old_body
    assert "This page has been merged into [[Canonical Topic]]" in old_body
    assert "## Merged Topic Signals" in canonical_body
    assert "<!-- quality_merge_source: old-topic -->" in canonical_body
    assert "Old Topic detail." in canonical_body


def test_data_service_builds_distilled_units(tmp_path):
    workspace = tmp_path / "workspace"
    doc = tmp_path / "openclaw.json"
    doc.write_text('{"title":"安装OpenClaw","turns":[{"role":"user","content":"如何安装OpenClaw？"},{"role":"assistant","content":"先安装Python，再运行安装脚本。"}]}', encoding="utf-8")
    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])

    units = service.build_distilled_units(plan)
    service.write_summary_files(plan)

    assert len(units) >= 2
    assert any(unit.kind == DistilledUnitKind.TOPIC_CANDIDATE for unit in units)
    assert any(unit.kind == DistilledUnitKind.CONCLUSION for unit in units)
    assert (service.layout.distill_sources_dir / f"{doc.stem}.json").exists()
    assert (service.layout.distill_units_dir / "distilled_units.jsonl").exists()
    assert service.layout.distill_manifest.exists()
    assert service.layout.distill_schema.exists()
    source_payload = json.loads((service.layout.distill_sources_dir / f"{doc.stem}.json").read_text(encoding="utf-8"))
    assert source_payload["schema_version"] == DataService.DISTILL_SCHEMA_VERSION
    assert source_payload["typed_unit_type_counts"]["concept"] >= 1
    assert source_payload["typed_unit_type_counts"]["claim"] >= 1
    assert all(unit["typed_unit"]["schema_version"] == DataService.TYPED_DISTILL_UNIT_SCHEMA_VERSION for unit in source_payload["units"])
    assert {unit["typed_unit"]["type"] for unit in source_payload["units"]}.issuperset({"concept", "claim"})
    manifest_payload = json.loads(service.layout.distill_manifest.read_text(encoding="utf-8"))
    schema_payload = json.loads(service.layout.distill_schema.read_text(encoding="utf-8"))
    assert manifest_payload["distilled_unit_count"] == len(units)
    assert manifest_payload["typed_unit_schema_version"] == DataService.TYPED_DISTILL_UNIT_SCHEMA_VERSION
    assert manifest_payload["quality"]["typed_unit_type_counts"]["concept"] >= 1
    assert "profile" in manifest_payload["sources"][0]
    assert "unit_kind_counts" in manifest_payload["sources"][0]
    assert "typed_unit_type_counts" in manifest_payload["sources"][0]
    assert schema_payload["legacy_kind_to_typed_unit_type"]["conclusion"] == "claim"
    assert "typed_unit" in schema_payload["unit_fields"]
    assert "profile_debug" in schema_payload["source_record_fields"]


def test_data_service_typed_units_cover_meeting_turns_fixture(tmp_path):
    workspace = tmp_path / "workspace"
    doc = tmp_path / "meeting.json"
    doc.write_text(
        json.dumps(
            {
                "title": "OpenClaw 项目复盘会议",
                "turns": [
                    {"speaker": "Alice", "content": "本次会议确认 OpenClaw 插件需要先完成 MCP 契约验收。"},
                    {"speaker": "Bob", "content": "风险是 GraphRAG 索引失败会影响知识检索。"},
                    {"speaker": "Alice", "content": "下一步先补充端到端测试，然后再更新文档。"},
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])
    units = service.build_distilled_units(plan)

    source_payload = json.loads((service.layout.distill_sources_dir / f"{doc.stem}.json").read_text(encoding="utf-8"))
    typed_counts = source_payload["typed_unit_type_counts"]
    assert typed_counts["meeting_summary"] >= 1
    assert typed_counts["risk"] >= 1
    assert typed_counts["claim"] >= 1
    assert typed_counts["entity_evidence"] >= 1
    assert any(unit.kind == DistilledUnitKind.NOTE for unit in units)
    assert any(unit.kind == DistilledUnitKind.RISK for unit in units)


def test_data_service_typed_units_cover_code_analysis_fixture(tmp_path):
    workspace = tmp_path / "workspace"
    doc = tmp_path / "checkout_code_analysis.json"
    doc.write_text(
        json.dumps(
            {
                "title": "CheckoutService architecture analysis",
                "architecture_notes": [
                    "CheckoutService coordinates payment and inventory through explicit adapters."
                ],
                "symbols": [
                    {"kind": "class", "name": "CheckoutService"},
                    {"kind": "interface", "name": "PaymentGateway"},
                ],
                "dependencies": [
                    {"source": "CheckoutService", "target": "PaymentGateway"},
                ],
                "calls": [
                    {"caller": "CheckoutService.create_order", "callee": "Inventory.reserve"},
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])
    service.build_distilled_units(plan)

    source_payload = json.loads((service.layout.distill_sources_dir / f"{doc.stem}.json").read_text(encoding="utf-8"))
    typed_counts = source_payload["typed_unit_type_counts"]
    assert typed_counts["architecture_note"] >= 1
    assert typed_counts["code_symbol"] >= 2
    assert typed_counts["code_dependency"] >= 1
    assert typed_counts["code_call_edge"] >= 1
    assert source_payload["unit_kind_counts"]["entity_candidate"] >= 2
    assert source_payload["unit_kind_counts"]["relation_candidate"] >= 2

    bundle = service.read_distill_bundle(limit=10, typed_unit_type="code_call_edge")
    assert bundle["units"]
    assert all(unit["typed_unit"]["type"] == "code_call_edge" for unit in bundle["units"])
    schema_payload = json.loads(service.layout.distill_schema.read_text(encoding="utf-8"))
    assert "code_call_edge" in schema_payload["typed_unit_types"]


def test_data_service_builds_more_units_for_dense_source_and_cleans_title_markers(tmp_path):
    workspace = tmp_path / "workspace"
    dense_doc = tmp_path / "AI学习-废弃于20260415.json"
    dense_doc.write_text(
        json.dumps(
            {
                "title": "AI学习-废弃于20260415",
                "turns": [
                    {"role": "user", "content": "如何系统学习 AI Agent、LLM、RAG、MCP？"},
                    {"role": "assistant", "content": "先建立学习路线，然后拆分模型、工具调用、记忆、评估。"},
                    {"role": "user", "content": "投资和宏观政策又如何和 AI 学习结合？"},
                    {"role": "assistant", "content": "可以把 AI 学习、投资、宏观政策拆成不同主题，再建立跨主题知识索引。"},
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    small_doc = tmp_path / "tiny.json"
    small_doc.write_text('{"title":"使用","turns":[{"role":"user","content":"你好"}]}', encoding="utf-8")

    service = DataService(workspace)
    plan = service.build_ingest_plan([str(dense_doc), str(small_doc)])

    units = service.build_distilled_units(plan)
    dense_units = [unit for unit in units if unit.source_id == dense_doc.stem]
    small_units = [unit for unit in units if unit.source_id == small_doc.stem]

    assert len(dense_units) > len(small_units)
    assert all("废弃于" not in " ".join(unit.entities) for unit in dense_units)
    assert any(unit.source_weight > 1.0 for unit in dense_units)


def test_data_service_distill_extracts_risk_example_fact_and_profile(tmp_path):
    workspace = tmp_path / "workspace"
    doc = tmp_path / "openclaw-guide.json"
    doc.write_text(
        json.dumps(
            {
                "title": "OpenClaw 安装说明",
                "turns": [
                    {"role": "user", "content": "如何安装 OpenClaw？"},
                    {"role": "assistant", "content": "先安装 Python，然后运行安装脚本。"},
                    {"role": "assistant", "content": "例如可以先用虚拟环境隔离依赖。"},
                    {"role": "assistant", "content": "注意不要缺少系统依赖，否则会报错。"},
                    {"role": "assistant", "content": "OpenClaw 需要 Python 运行环境。"},
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])

    units = service.build_distilled_units(plan)
    kinds = {unit.kind for unit in units if unit.source_id == doc.stem}

    assert DistilledUnitKind.RISK in kinds
    assert DistilledUnitKind.EXAMPLE in kinds
    assert DistilledUnitKind.FACT_CANDIDATE in kinds

    source_payload = json.loads((service.layout.distill_sources_dir / f"{doc.stem}.json").read_text(encoding="utf-8"))
    assert source_payload["profile"]["risk_count"] >= 1
    assert source_payload["profile"]["example_count"] >= 1
    assert source_payload["profile"]["fact_count"] >= 1
    assert source_payload["unit_kind_counts"]["risk"] >= 1
    assert source_payload["unit_kind_counts"]["example"] >= 1
    assert source_payload["unit_kind_counts"]["fact_candidate"] >= 1


def test_data_service_filters_short_cn_noise_and_numeric_prefixed_themes(tmp_path):
    workspace = tmp_path / "workspace"
    doc = tmp_path / "投资分析.json"
    doc.write_text(
        json.dumps(
            {
                "title": "投资分析",
                "turns": [
                    {"role": "user", "content": "35岁工作调整后，如何继续做投资分析？"},
                    {"role": "assistant", "content": "重点关注宏观政策、资产配置和长期现金流，而不是只看岁工作这种标签。"},
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])

    units = service.build_distilled_units(plan)
    entities = " ".join(" ".join(unit.entities) for unit in units)
    tags = " ".join(" ".join(unit.tags) for unit in units)

    assert "岁工作" not in entities
    assert "分析" not in tags


def test_data_service_theme_cleanup_rejects_table_titles_and_strips_generic_suffixes(tmp_path):
    workspace = tmp_path / "workspace"
    service = DataService(workspace)

    assert service._clean_theme_candidate("国际金价与黄金ETF涨跌逻辑分析") == "国际金价与黄金ETF"
    assert service._clean_theme_candidate("Bose耳机配对问题排查") == "Bose"
    assert service._clean_theme_candidate("Cursor国内使用限制") == "Cursor"
    assert service._clean_theme_candidate("TypeScript中的多态与复态") == "TypeScript"
    assert service._clean_theme_candidate("新能源车1000公里续航发展分析") == "新能源车"
    assert service._clean_theme_candidate("中国养老金5000元以上人数分析") == "中国养老金"
    assert service._clean_theme_candidate("武汉25岁工作35岁被裁退休金计算") == "武汉25岁工作"
    assert service._is_meaningful_theme("国际金价与黄金ETF涨跌逻辑分析") is True
    assert service._is_meaningful_theme("配置微信飞书") is False
    assert service._is_meaningful_theme("User seeks clarification on creample term") is False
    assert service._is_meaningful_theme("公里续航发展") is False
    assert service._is_meaningful_theme("元以上人数") is False
    assert service._is_meaningful_theme("表11试验流程表") is False
    assert service._is_meaningful_theme("表11试验流程表是某个临床试验方案中的流程图") is False


def test_data_service_filters_low_signal_chat_sentences_from_distill(tmp_path):
    workspace = tmp_path / "workspace"
    doc = tmp_path / "chat.json"
    doc.write_text(
        json.dumps(
            {
                "title": "AI 学习",
                "turns": [
                    {"role": "user", "content": "你好"},
                    {"role": "assistant", "content": "好的"},
                    {"role": "user", "content": "如何系统学习 AI Agent？"},
                    {"role": "assistant", "content": "先梳理模型、工具调用和评估。"},
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])

    units = service.build_distilled_units(plan)
    combined = " ".join(unit.text for unit in units if unit.source_id == doc.stem)

    assert "你好" not in combined
    assert "好的" not in combined


def test_data_service_adds_title_fallback_question_for_semantic_title_only_source(tmp_path):
    workspace = tmp_path / "workspace"
    doc = tmp_path / "title_only.json"
    doc.write_text(
        json.dumps(
            {
                "title": "米醋与白醋的区别及用途",
                "turns": [],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])

    units = service.build_distilled_units(plan)
    questions = [unit for unit in units if unit.kind == DistilledUnitKind.QUESTION]
    conclusions = [unit for unit in units if unit.kind == DistilledUnitKind.CONCLUSION]
    entities = [unit.text for unit in units if unit.kind == DistilledUnitKind.ENTITY_CANDIDATE]

    assert any(unit.text == "米醋与白醋的区别及用途" and unit.is_title_derived for unit in questions)
    assert not conclusions
    assert "米醋" in entities
    assert "白醋" in entities

    source_payload = json.loads((service.layout.distill_sources_dir / f"{doc.stem}.json").read_text(encoding="utf-8"))
    assert source_payload["profile_debug"]["title_fallback_question"] == "米醋与白醋的区别及用途"
    assert source_payload["unit_kind_counts"]["question"] >= 1
    assert "米醋" in source_payload["tags"]
    assert "白醋" in source_payload["tags"]


def test_data_service_records_low_signal_diagnostics_for_zero_unit_source(tmp_path):
    workspace = tmp_path / "workspace"
    doc = tmp_path / "low_signal.json"
    doc.write_text(
        json.dumps(
            {
                "title": "记录",
                "turns": [
                    {"role": "user", "content": "你好"},
                    {"role": "assistant", "content": "好的"},
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])

    units = service.build_distilled_units(plan)
    service.write_summary_files(plan)

    assert [unit for unit in units if unit.source_id == doc.stem] == []
    source_payload = json.loads((service.layout.distill_sources_dir / f"{doc.stem}.json").read_text(encoding="utf-8"))
    manifest_payload = json.loads(service.layout.distill_manifest.read_text(encoding="utf-8"))
    summary_payload = json.loads(service.layout.summary_json.read_text(encoding="utf-8"))

    assert source_payload["profile"]["zero_unit"] is True
    assert source_payload["profile_debug"]["low_signal"]["zero_unit"] is True
    assert "no_safe_title_fallback" in source_payload["profile_debug"]["low_signal"]["reasons"]
    assert manifest_payload["quality"]["zero_unit_count"] == 1
    assert manifest_payload["quality"]["zero_unit_sources"][0]["source_id"] == doc.stem
    assert summary_payload["quality"]["distill"]["zero_unit_count"] == 1


def test_data_service_records_title_fallback_low_signal_coverage(tmp_path):
    workspace = tmp_path / "workspace"
    doc = tmp_path / "fallback_covered.json"
    doc.write_text(
        json.dumps(
            {
                "title": "中国核电建设及并网时间数据",
                "turns": [],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])

    units = service.build_distilled_units(plan)
    conclusions = [unit for unit in units if unit.kind == DistilledUnitKind.CONCLUSION]
    source_payload = json.loads((service.layout.distill_sources_dir / f"{doc.stem}.json").read_text(encoding="utf-8"))
    manifest_payload = json.loads(service.layout.distill_manifest.read_text(encoding="utf-8"))

    assert not conclusions
    assert source_payload["profile"]["zero_unit"] is False
    assert source_payload["profile_debug"]["low_signal"]["title_fallbacks"]["fact_candidate"] is True
    assert "title_only_conservatively_covered" in source_payload["profile_debug"]["low_signal"]["reasons"]
    assert manifest_payload["quality"]["zero_unit_count"] == 0
    assert manifest_payload["quality"]["title_fallback_source_counts"]["fact_candidate"] == 1


def test_data_service_conservatively_covers_real_low_signal_titles(tmp_path):
    workspace = tmp_path / "workspace"
    titles = [
        "36岁停止工作确保退休资金充足",
        "管培生实践移植案例",
        "端午节看望老人注意事项",
        "生成两份云南菜评价",
        "车企相关",
        "跨设备智能卡片交互系统专利",
        "User seeks clarification on creample term.",
        "香农极限及其在通信中的应用",
    ]
    docs = []
    for index, title in enumerate(titles):
        doc = tmp_path / f"low_signal_{index}.json"
        doc.write_text(json.dumps({"title": title, "turns": []}, ensure_ascii=False), encoding="utf-8")
        docs.append(str(doc))
    service = DataService(workspace)
    plan = service.build_ingest_plan(docs)

    units = service.build_distilled_units(plan)
    conclusions = [unit for unit in units if unit.kind == DistilledUnitKind.CONCLUSION]
    manifest_payload = json.loads(service.layout.distill_manifest.read_text(encoding="utf-8"))
    source_units = {
        source["title"]: [
            unit for unit in units
            if unit.source_id == source["source_id"]
        ]
        for source in manifest_payload["sources"]
    }

    assert manifest_payload["quality"]["zero_unit_count"] == 0
    assert not conclusions
    assert all(source_units[title] for title in titles)
    assert any(unit.text == "退休资金" for unit in units if unit.kind == DistilledUnitKind.ENTITY_CANDIDATE)
    assert any(unit.text == "creample" for unit in units if unit.kind == DistilledUnitKind.ENTITY_CANDIDATE)
    assert manifest_payload["quality"]["title_fallback_source_count"] >= 7


def test_data_service_prefers_inner_json_title_over_filename(tmp_path):
    workspace = tmp_path / "workspace"
    doc = tmp_path / "weird_filename.json"
    doc.write_text(
        json.dumps(
            {
                "title": "OpenClaw 配置说明",
                "turns": [],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])
    service.build_distilled_units(plan)

    source_payload = json.loads((service.layout.distill_sources_dir / f"{doc.stem}.json").read_text(encoding="utf-8"))
    assert source_payload["title"] == "OpenClaw 配置说明"


def test_data_service_extracts_core_entity_from_title_only_medical_source(tmp_path):
    workspace = tmp_path / "workspace"
    doc = tmp_path / "medical_title_only.json"
    doc.write_text(
        json.dumps(
            {
                "title": "腱鞘炎就诊科室选择建议",
                "turns": [],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])

    units = service.build_distilled_units(plan)
    entities = [unit.text for unit in units if unit.kind == DistilledUnitKind.ENTITY_CANDIDATE]
    questions = [unit.text for unit in units if unit.kind == DistilledUnitKind.QUESTION]

    assert "腱鞘炎" in entities
    assert "腱鞘炎就诊科室选" not in entities
    assert questions == ["腱鞘炎就诊科室选择建议"]


def test_data_service_extracts_core_entity_from_title_only_recommendation_source(tmp_path):
    workspace = tmp_path / "workspace"
    doc = tmp_path / "travel_title_only.json"
    doc.write_text(
        json.dumps(
            {
                "title": "武汉周末小众游推荐",
                "turns": [],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])

    units = service.build_distilled_units(plan)
    questions = [unit.text for unit in units if unit.kind == DistilledUnitKind.QUESTION]
    topics = [unit.text for unit in units if unit.kind == DistilledUnitKind.TOPIC_CANDIDATE]
    notes = [unit.text for unit in units if unit.kind == DistilledUnitKind.NOTE]

    assert questions == ["武汉周末小众游推荐"]
    assert topics
    assert any("武汉" in text and "建议" in text for text in notes)


def test_data_service_extracts_core_entity_from_title_only_duration_source(tmp_path):
    workspace = tmp_path / "workspace"
    doc = tmp_path / "housing_title_only.json"
    doc.write_text(
        json.dumps(
            {
                "title": "中国高层住宅宜居年限分析",
                "turns": [],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])

    units = service.build_distilled_units(plan)
    entities = [unit.text for unit in units if unit.kind == DistilledUnitKind.ENTITY_CANDIDATE]
    questions = [unit.text for unit in units if unit.kind == DistilledUnitKind.QUESTION]

    assert "中国高层住宅" in entities
    assert questions == ["中国高层住宅宜居年限分析"]


def test_data_service_adds_title_derived_fact_for_data_like_title_only_source(tmp_path):
    workspace = tmp_path / "workspace"
    doc = tmp_path / "data_title_only.json"
    doc.write_text(
        json.dumps(
            {
                "title": "中国核电建设及并网时间数据",
                "turns": [],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])

    units = service.build_distilled_units(plan)
    facts = [unit.text for unit in units if unit.kind == DistilledUnitKind.FACT_CANDIDATE]
    topics = [unit.text for unit in units if unit.kind == DistilledUnitKind.TOPIC_CANDIDATE]

    assert any("中国核电" in text and "数据或进展信息" in text for text in facts)
    assert "中国核电" in topics
    assert "投资" not in topics


def test_data_service_adds_title_derived_risk_for_problem_title_only_source(tmp_path):
    workspace = tmp_path / "workspace"
    doc = tmp_path / "risk_title_only.json"
    doc.write_text(
        json.dumps(
            {
                "title": "Bose耳机配对问题排查指南",
                "turns": [],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])

    units = service.build_distilled_units(plan)
    risks = [unit.text for unit in units if unit.kind == DistilledUnitKind.RISK]

    assert any("Bose" in text and "问题排查" in text for text in risks)


def test_data_service_merges_calendar_title_only_entities(tmp_path):
    workspace = tmp_path / "workspace"
    doc = tmp_path / "calendar_title_only.json"
    doc.write_text(
        json.dumps(
            {
                "title": "日历App跨端协作技术专利方案",
                "turns": [],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])

    units = service.build_distilled_units(plan)
    entities = [unit.text for unit in units if unit.kind == DistilledUnitKind.ENTITY_CANDIDATE]
    topics = [unit.text for unit in units if unit.kind == DistilledUnitKind.TOPIC_CANDIDATE]

    assert "日历" in entities
    assert "日历" in topics
    assert "日历App" not in entities
    assert "日历App跨端协作技术专利方案" not in topics
    assert "跨端协作技术专利方案" not in entities


def test_data_service_preserves_mixed_symbol_title_entity(tmp_path):
    workspace = tmp_path / "workspace"
    doc = tmp_path / "s1_title_only.json"
    doc.write_text(
        json.dumps(
            {
                "title": "股市S1含义解析",
                "turns": [],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])

    units = service.build_distilled_units(plan)
    entities = [unit.text for unit in units if unit.kind == DistilledUnitKind.ENTITY_CANDIDATE]
    topics = [unit.text for unit in units if unit.kind == DistilledUnitKind.TOPIC_CANDIDATE]
    questions = [unit.text for unit in units if unit.kind == DistilledUnitKind.QUESTION]

    assert "股市S1" in entities
    assert "股市" not in entities
    assert "股市S1" in topics
    assert "股市" not in topics
    assert questions == ["股市S1含义解析"]


def test_data_service_merges_title_only_market_progress_entity(tmp_path):
    workspace = tmp_path / "workspace"
    doc = tmp_path / "space_company_title_only.json"
    doc.write_text(
        json.dumps(
            {
                "title": "中国民营航天公司上市进展及股东情况",
                "turns": [],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])

    units = service.build_distilled_units(plan)
    entities = [unit.text for unit in units if unit.kind == DistilledUnitKind.ENTITY_CANDIDATE]
    topics = [unit.text for unit in units if unit.kind == DistilledUnitKind.TOPIC_CANDIDATE]
    questions = [unit.text for unit in units if unit.kind == DistilledUnitKind.QUESTION]

    assert "中国民营航天公司" in entities
    assert "中国民营航天公司" in topics
    assert "中国民营航天公司上市" not in entities
    assert "投资" not in topics
    assert questions == ["中国民营航天公司上市进展及股东情况"]


def test_data_service_merges_title_only_product_property_entity(tmp_path):
    workspace = tmp_path / "workspace"
    doc = tmp_path / "product_property_title_only.json"
    doc.write_text(
        json.dumps(
            {
                "title": "小米SU7玻璃防晒性能解析",
                "turns": [],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])

    units = service.build_distilled_units(plan)
    entities = [unit.text for unit in units if unit.kind == DistilledUnitKind.ENTITY_CANDIDATE]
    topics = [unit.text for unit in units if unit.kind == DistilledUnitKind.TOPIC_CANDIDATE]

    assert "小米SU7" in entities
    assert "小米SU7" in topics
    assert "SU7" not in entities
    assert "SU7" not in topics
    assert "小米SU7玻璃防晒性能" not in entities
    assert "玻璃防晒性能" not in entities


def test_data_service_merges_title_only_event_schedule_entity(tmp_path):
    workspace = tmp_path / "workspace"
    doc = tmp_path / "world_cup_title_only.json"
    doc.write_text(
        json.dumps(
            {
                "title": "美加墨世界杯小组赛时间",
                "turns": [],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])

    units = service.build_distilled_units(plan)
    entities = [unit.text for unit in units if unit.kind == DistilledUnitKind.ENTITY_CANDIDATE]
    topics = [unit.text for unit in units if unit.kind == DistilledUnitKind.TOPIC_CANDIDATE]

    assert "美加墨世界杯" in entities
    assert "美加墨世界杯" in topics
    assert "美加墨世界杯小组赛" not in entities


def test_data_service_distill_profile_debug_explains_title_only_candidates(tmp_path):
    workspace = tmp_path / "workspace"
    doc = tmp_path / "debug_title_only.json"
    doc.write_text(
        json.dumps(
            {
                "title": "小米SU7玻璃防晒性能解析",
                "turns": [],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])

    service.build_distilled_units(plan)
    source_payload = json.loads((service.layout.distill_sources_dir / f"{doc.stem}.json").read_text(encoding="utf-8"))

    assert source_payload["profile_debug"]["title_only_excerpt"] is True
    assert "小米SU7" in source_payload["profile_debug"]["entity_candidates"]
    assert "小米SU7" in source_payload["profile_debug"]["theme_labels"]
    normalization = source_payload["profile_debug"]["title_normalization"]
    assert normalization["raw_title"] == "小米SU7玻璃防晒性能解析"
    assert "小米SU7" in normalization["normalized_entities"]
    assert "玻璃防晒性能" in normalization["dropped_fragments"]


def test_data_service_merges_installed_tool_title_to_tool_entity(tmp_path):
    workspace = tmp_path / "workspace"
    doc = tmp_path / "installed_tool_title_only.json"
    doc.write_text(
        json.dumps(
            {
                "title": "已安装VSCode选项验证",
                "turns": [],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])

    units = service.build_distilled_units(plan)
    entities = [unit.text for unit in units if unit.kind == DistilledUnitKind.ENTITY_CANDIDATE]
    topics = [unit.text for unit in units if unit.kind == DistilledUnitKind.TOPIC_CANDIDATE]

    assert "VSCode" in entities
    assert "VSCode" in topics
    assert "已安装VSCode选项验证" not in entities
    assert "已安装VSCode选项验证" not in topics
    source_payload = json.loads((service.layout.distill_sources_dir / f"{doc.stem}.json").read_text(encoding="utf-8"))
    normalization = source_payload["profile_debug"]["title_normalization"]
    assert normalization["dropped_fragments"] == ["已安装", "选项验证"]
    assert "install_status_removed" in normalization["rules_applied"]
    assert "functional_suffix_removed" in normalization["rules_applied"]


def test_data_service_merges_language_concept_title_to_language_entity(tmp_path):
    workspace = tmp_path / "workspace"
    doc = tmp_path / "typescript_title_only.json"
    doc.write_text(
        json.dumps(
            {
                "title": "TypeScript中的多态与复态解析",
                "turns": [],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])

    units = service.build_distilled_units(plan)
    entities = [unit.text for unit in units if unit.kind == DistilledUnitKind.ENTITY_CANDIDATE]
    topics = [unit.text for unit in units if unit.kind == DistilledUnitKind.TOPIC_CANDIDATE]

    assert "TypeScript" in entities
    assert "TypeScript" in topics
    assert "中的多态与复态" not in entities
    assert "中的多态与复态" not in topics
    source_payload = json.loads((service.layout.distill_sources_dir / f"{doc.stem}.json").read_text(encoding="utf-8"))
    normalization = source_payload["profile_debug"]["title_normalization"]
    assert "中的多态与复态" in normalization["dropped_fragments"]
    assert "latin_prefix_kept" in normalization["rules_applied"]


def test_data_service_merges_code_example_title_to_language_entity(tmp_path):
    workspace = tmp_path / "workspace"
    doc = tmp_path / "python_code_title_only.json"
    doc.write_text(
        json.dumps(
            {
                "title": "鸿蒙手机Python自动化测试代码示例",
                "turns": [],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])

    units = service.build_distilled_units(plan)
    entities = [unit.text for unit in units if unit.kind == DistilledUnitKind.ENTITY_CANDIDATE]
    topics = [unit.text for unit in units if unit.kind == DistilledUnitKind.TOPIC_CANDIDATE]

    assert "Python" in entities
    assert "Python" in topics
    assert "鸿蒙手机Python自动化测试代码示例" not in entities
    assert "鸿蒙手机Python自动化测试代码示例" not in topics
    assert "鸿蒙手机Python自动化测试" not in entities
    assert "鸿蒙手机Python自动化测试" not in topics
    source_payload = json.loads((service.layout.distill_sources_dir / f"{doc.stem}.json").read_text(encoding="utf-8"))
    normalization = source_payload["profile_debug"]["title_normalization"]
    assert "自动化测试代码示例" in normalization["dropped_fragments"]
    assert "latin_core_kept" in normalization["rules_applied"]


def test_data_service_merges_company_background_title_to_company_entity(tmp_path):
    workspace = tmp_path / "workspace"
    doc = tmp_path / "company_background_title_only.json"
    doc.write_text(
        json.dumps(
            {
                "title": "超聚变公司股权结构及背景介绍",
                "turns": [],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])

    units = service.build_distilled_units(plan)
    entities = [unit.text for unit in units if unit.kind == DistilledUnitKind.ENTITY_CANDIDATE]
    topics = [unit.text for unit in units if unit.kind == DistilledUnitKind.TOPIC_CANDIDATE]

    assert "超聚变公司" in entities
    assert "超聚变公司" in topics
    assert "背景介绍" not in entities
    assert "背景介绍" not in topics
    source_payload = json.loads((service.layout.distill_sources_dir / f"{doc.stem}.json").read_text(encoding="utf-8"))
    normalization = source_payload["profile_debug"]["title_normalization"]
    assert "股权结构" in normalization["dropped_fragments"]
    assert "背景介绍" in normalization["dropped_fragments"]
    assert "functional_suffix_removed" in normalization["rules_applied"]


def test_data_service_run_pipeline_skips_missing_adapters(tmp_path):
    service = DataService(tmp_path / "workspace")
    plan = service.build_ingest_plan(["/tmp/notes.md"])

    results = service.run_pipeline(plan)

    assert [result.engine for result in results] == ["llmwiki", "graphrag"]
    assert all(result.status == "skipped" for result in results)


def test_data_service_run_pipeline_calls_adapters(tmp_path):
    service = DataService(tmp_path / "workspace")
    plan = service.build_ingest_plan(["/tmp/notes.md"])
    units = [
        DistilledUnit(
            unit_id="u1",
            source_id="s1",
            kind=DistilledUnitKind.CONCLUSION,
            authority=AuthorityLevel.PRIMARY_DOC,
            text="OpenClaw requires Python.",
            normalized_text="OpenClaw requires Python.",
        )
    ]

    class FakeLLMWikiAdapter:
        def compile(self, plan, units):
            return AdapterResult(engine="llmwiki", status="success", artifacts=["page.md"], meta={"unit_count": len(units)})

    class FakeGraphRAGAdapter:
        def index(self, plan, units):
            return AdapterResult(engine="graphrag", status="success", artifacts=["graph.json"], meta={"unit_count": len(units)})

    results = service.run_pipeline(
        plan,
        distilled_units=units,
        llmwiki_adapter=FakeLLMWikiAdapter(),
        graphrag_adapter=FakeGraphRAGAdapter(),
    )

    assert [result.status for result in results] == ["success", "success"]
    assert results[0].artifacts == ["page.md"]
    assert results[1].artifacts == ["graph.json"]


def test_graphrag_workspace_adapter_stages_distilled_inputs(tmp_path):
    service = DataService(tmp_path / "workspace")
    notes_path = tmp_path / "notes.md"
    notes_path.write_text("# Notes\n", encoding="utf-8")
    plan = service.build_ingest_plan([str(notes_path)], include_llmwiki=False, include_graphrag=True)
    plan.sources[0].source_id = "source-a"
    units = [
        DistilledUnit(
            unit_id="u1",
            source_id="source-a",
            kind=DistilledUnitKind.CONCLUSION,
            authority=AuthorityLevel.PRIMARY_DOC,
            text="OpenClaw requires Python.",
            normalized_text="OpenClaw requires Python.",
        )
    ]

    result = GraphRAGWorkspaceAdapter().index(plan, units)

    assert result.status == "indexed"
    assert any(path.endswith("distilled_units.jsonl") for path in result.artifacts)
    assert any(path.endswith("index_manifest.json") for path in result.artifacts)
    assert any(path.endswith("graphrag.db") for path in result.artifacts)
    bundle = plan.layout.graphrag_input_dir / "distilled_units.jsonl"
    db_path = plan.layout.graphrag_state_dir / "graphrag.db"
    assert bundle.exists()
    assert db_path.exists()
    assert "OpenClaw requires Python." in bundle.read_text(encoding="utf-8")


def test_graphrag_workspace_adapter_runs_app_graphrag_fallback(tmp_path, monkeypatch):
    service = DataService(tmp_path / "workspace")
    notes_path = tmp_path / "notes.md"
    notes_path.write_text("# Notes\n", encoding="utf-8")
    plan = service.build_ingest_plan(
        [str(notes_path)],
        include_llmwiki=False,
        include_graphrag=True,
        graphrag_execution_owner=GraphExecutionOwner.APP_GRAPHRAG,
    )
    plan.sources[0].source_id = "source-a"
    units = [
        DistilledUnit(
            unit_id="u1",
            source_id="source-a",
            kind=DistilledUnitKind.CONCLUSION,
            authority=AuthorityLevel.PRIMARY_DOC,
            text="OpenClaw requires Python.",
            normalized_text="OpenClaw requires Python.",
        )
    ]

    monkeypatch.setattr("app.graphrag.service.data_service_runner.shutil.which", lambda _: None)
    result = GraphRAGWorkspaceAdapter(execution_owner=GraphExecutionOwner.APP_GRAPHRAG).index(plan, units)

    assert result.status == "indexed"
    assert result.meta["execution_owner"] == GraphExecutionOwner.APP_GRAPHRAG.value
    assert result.meta["execution_mode"] == "app_graphrag"
    assert result.meta["execution_result"]["execution_mode"] == "app_graphrag_compat_materializer"
    assert result.meta["execution_result"]["reason"] == "graphrag_cli_not_found"
    assert result.meta["execution_result"]["cli_health"]["healthy"] is False
    assert service.layout.graphrag_execution_owner.exists()
    assert service.layout.graphrag_execution_request.exists()
    owner_payload = json.loads(service.layout.graphrag_execution_owner.read_text(encoding="utf-8"))
    request_payload = json.loads(service.layout.graphrag_execution_request.read_text(encoding="utf-8"))
    assert owner_payload["execution_owner"] == GraphExecutionOwner.APP_GRAPHRAG.value
    assert owner_payload["status"] == "indexed_via_app_graphrag"
    assert request_payload["status"] == "ready_for_app_graphrag_runner"
    assert (service.layout.graphrag_state_dir / "graphrag.db").exists()


def test_graphrag_workspace_adapter_reports_broken_native_cli(tmp_path, monkeypatch):
    service = DataService(tmp_path / "workspace")
    notes_path = tmp_path / "notes.md"
    notes_path.write_text("# Notes\n", encoding="utf-8")
    plan = service.build_ingest_plan(
        [str(notes_path)],
        include_llmwiki=False,
        include_graphrag=True,
        graphrag_execution_owner=GraphExecutionOwner.APP_GRAPHRAG,
    )
    plan.sources[0].source_id = "source-a"
    units = [
        DistilledUnit(
            unit_id="u1",
            source_id="source-a",
            kind=DistilledUnitKind.CONCLUSION,
            authority=AuthorityLevel.PRIMARY_DOC,
            text="OpenClaw requires Python.",
            normalized_text="OpenClaw requires Python.",
        )
    ]

    class BrokenCliResult:
        returncode = 2
        stdout = ""
        stderr = "can't open file '/tmp/graphrag_patched.py'"

    monkeypatch.setattr("app.graphrag.service.data_service_runner.shutil.which", lambda _: "/usr/local/bin/graphrag")
    monkeypatch.setattr("app.graphrag.service.data_service_runner.subprocess.run", lambda *_, **__: BrokenCliResult())

    result = GraphRAGWorkspaceAdapter(execution_owner=GraphExecutionOwner.APP_GRAPHRAG).index(plan, units)

    execution_result = result.meta["execution_result"]
    assert result.status == "indexed"
    assert execution_result["execution_mode"] == "app_graphrag_compat_materializer"
    assert execution_result["reason"] == "graphrag_cli_broken"
    assert execution_result["cli_health"]["available"] is True
    assert execution_result["cli_health"]["healthy"] is False
    assert execution_result["cli_health"]["returncode"] == 2
    assert "graphrag_patched.py" in execution_result["cli_health"]["stderr"]
    assert (service.layout.graphrag_state_dir / "graphrag.db").exists()


def test_graphrag_cli_health_check_reports_healthy_cli(monkeypatch):
    from app.graphrag.service.data_service_runner import check_graphrag_cli_health

    class HealthyCliResult:
        returncode = 0
        stdout = "Usage: graphrag [OPTIONS] COMMAND [ARGS]..."
        stderr = ""

    monkeypatch.setattr("app.graphrag.service.data_service_runner.shutil.which", lambda _: "/usr/local/bin/graphrag")
    monkeypatch.setattr("app.graphrag.service.data_service_runner.subprocess.run", lambda *_, **__: HealthyCliResult())

    health = check_graphrag_cli_health()

    assert health == {
        "available": True,
        "healthy": True,
        "reason": "ok",
        "path": "/usr/local/bin/graphrag",
        "returncode": 0,
        "stdout": "Usage: graphrag [OPTIONS] COMMAND [ARGS]...",
        "stderr": "",
    }


def test_graphrag_workspace_adapter_filters_noise_and_creates_themes(tmp_path):
    service = DataService(tmp_path / "workspace")
    notes_path = tmp_path / "AI学习-废弃于20260415.md"
    notes_path.write_text("# AI学习-废弃于20260415\n\nOpenClaw 与 ComfyUI 的 Agent 工作流。\n", encoding="utf-8")
    plan = service.build_ingest_plan([str(notes_path)], include_llmwiki=False, include_graphrag=True)
    plan.sources[0].source_id = "source-ai"
    units = [
        DistilledUnit(
            unit_id="u1",
            source_id="source-ai",
            kind=DistilledUnitKind.TOPIC_CANDIDATE,
            authority=AuthorityLevel.SECONDARY_CHAT,
            text="AI学习",
            normalized_text="AI学习",
            source_weight=2.4,
            source_density_score=2.8,
            tags=["AI学习", "废弃于", "OpenClaw"],
            entities=["OpenClaw", "废弃于"],
        ),
        DistilledUnit(
            unit_id="u2",
            source_id="source-ai",
            kind=DistilledUnitKind.CONCLUSION,
            authority=AuthorityLevel.SECONDARY_CHAT,
            text="OpenClaw 与 ComfyUI 的 Agent 工作流。",
            normalized_text="OpenClaw 与 ComfyUI 的 Agent 工作流。",
            source_weight=2.4,
            source_density_score=2.8,
            tags=["AI学习", "ComfyUI"],
            entities=["OpenClaw", "ComfyUI"],
        ),
    ]

    GraphRAGWorkspaceAdapter().index(plan, units)

    graph = service.get_graph_snapshot(max_nodes=20)
    node_names = [node["name"] for node in graph["nodes"]]

    assert "废弃于" not in node_names
    assert any(node["type"] == "theme" for node in graph["nodes"])
    assert any(community["title"] == "AI学习" for community in graph["communities"])


def test_graphrag_workspace_adapter_filters_cn_noise_fragments(tmp_path):
    service = DataService(tmp_path / "workspace")
    notes_path = tmp_path / "macro.md"
    notes_path.write_text("# 宏观政策\n\n35岁工作和点分析不应该进入主题。\n", encoding="utf-8")
    plan = service.build_ingest_plan([str(notes_path)], include_llmwiki=False, include_graphrag=True)
    plan.sources[0].source_id = "source-macro"
    units = [
        DistilledUnit(
            unit_id="u1",
            source_id="source-macro",
            kind=DistilledUnitKind.TOPIC_CANDIDATE,
            authority=AuthorityLevel.SECONDARY_CHAT,
            text="宏观政策",
            normalized_text="宏观政策",
            tags=["宏观政策", "点分析", "35岁工作"],
            entities=["35岁工作", "点分析", "宏观政策"],
        ),
    ]

    GraphRAGWorkspaceAdapter().index(plan, units)
    graph = service.get_graph_snapshot(max_nodes=20)
    node_names = [node["name"] for node in graph["nodes"]]

    assert "35岁工作" not in node_names
    assert "点分析" not in node_names
    assert "宏观政策" in node_names


def test_graphrag_workspace_adapter_does_not_promote_tags_into_entities_or_themes(tmp_path):
    service = DataService(tmp_path / "workspace")
    notes_path = tmp_path / "gold.md"
    notes_path.write_text("# 黄金ETF\n\n国际金价与黄金 ETF 观察。\n", encoding="utf-8")
    plan = service.build_ingest_plan([str(notes_path)], include_llmwiki=False, include_graphrag=True)
    plan.sources[0].source_id = "source-gold"
    units = [
        DistilledUnit(
            unit_id="u1",
            source_id="source-gold",
            kind=DistilledUnitKind.CONCLUSION,
            authority=AuthorityLevel.SECONDARY_CHAT,
            text="国际金价与黄金 ETF 观察。",
            normalized_text="国际金价与黄金 ETF 观察。",
            tags=["国际金价与黄金ETF涨跌逻辑分析", "配置说明"],
            entities=["黄金ETF"],
        ),
        DistilledUnit(
            unit_id="u2",
            source_id="source-gold",
            kind=DistilledUnitKind.TOPIC_CANDIDATE,
            authority=AuthorityLevel.SECONDARY_CHAT,
            text="国际金价与黄金ETF",
            normalized_text="国际金价与黄金ETF",
            tags=["国际金价与黄金ETF涨跌逻辑分析", "搭建指南"],
            entities=[],
        ),
    ]

    GraphRAGWorkspaceAdapter().index(plan, units)

    graph = service.get_graph_snapshot(max_nodes=20)
    node_names = [node["name"] for node in graph["nodes"]]

    assert "黄金ETF" in node_names
    assert "国际金价与黄金ETF" in node_names
    assert "国际金价与黄金ETF涨跌逻辑分析" not in node_names
    assert "配置说明" not in node_names
    assert "搭建指南" not in node_names


def test_data_service_run_default_pipeline(tmp_path):
    workspace = tmp_path / "workspace"
    doc = tmp_path / "notes.md"
    doc.write_text("# OpenClaw\n\nOpenClaw setup notes.\n", encoding="utf-8")
    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])

    results = service.run_default_pipeline(plan)

    assert [result.engine for result in results] == ["llmwiki", "graphrag"]
    assert results[0].status in {"success", "partial"}
    assert results[1].status == "indexed"
    assert (workspace / "summary" / "summary.md").exists()


def test_data_service_phasee_docx_yaml_run_default_pipeline(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    docx_path = docs_dir / "openclaw_governance.docx"
    yaml_path = docs_dir / "service_contract.yaml"
    _write_minimal_docx(
        docx_path,
        [
            "OpenClaw 治理方案",
            "MCP 出门验证必须覆盖 workspace source build distill graph 查询链路。",
            "风险是外部接口出现隐藏性变更。",
        ],
    )
    yaml_path.write_text(
        "\n".join(
            [
                "title: Data Service PhaseE Contract",
                "capabilities:",
                "  - docx ingestion",
                "  - yaml structured parsing",
                "acceptance:",
                "  llmwiki: true",
                "  graphrag: true",
            ]
        ),
        encoding="utf-8",
    )
    service = DataService(workspace)
    plan = service.build_ingest_plan([str(docs_dir)], graphrag_execution_owner=GraphExecutionOwner.APP_GRAPHRAG)

    monkeypatch.setattr("app.graphrag.service.data_service_runner.shutil.which", lambda _: None)
    results = service.run_default_pipeline(plan)

    assert {Path(source.path).suffix.lower() for source in plan.sources} == {".docx", ".yaml"}
    assert [result.engine for result in results] == ["llmwiki", "graphrag"]
    assert results[0].status == "success"
    assert results[1].status == "indexed"
    assert results[0].meta["success"] == 2
    assert len(list(service.layout.llmwiki_pages_dir.glob("*.md"))) >= 2
    assert service.layout.graphrag_execution_request.exists()
    bundle = service.read_distill_bundle(limit=50)
    bundle_text = "\n".join(unit["text"] for unit in bundle["units"])
    assert "OpenClaw" in bundle_text
    assert "docx ingestion" in bundle_text
    manifest = json.loads(service.layout.distill_manifest.read_text(encoding="utf-8"))
    assert manifest["source_count"] == 2
    assert manifest["quality"]["format_counts"] == {"docx": 1, "yaml": 1}
    assert manifest["quality"]["extractor_counts"]["DocxExtractor"] == 1
    assert manifest["quality"]["extractor_counts"]["YamlExtractor"] == 1
    assert manifest["quality"]["format_issue_sources"] == []
    assert {source["source_format"] for source in manifest["sources"]} == {"docx", "yaml"}
    assert all(source["extractor_available"] is True for source in manifest["sources"])
    assert {profile["source_format"] for profile in bundle["source_profiles"]} == {"docx", "yaml"}
    assert {profile["extractor_name"] for profile in bundle["source_profiles"]} == {"DocxExtractor", "YamlExtractor"}

    summary_bundle = service.read_summary_bundle()
    assert summary_bundle["quality"]["distill"]["format_counts"] == {"docx": 1, "yaml": 1}
    assert summary_bundle["quality"]["distill"]["format_issue_sources"] == []


def test_data_service_run_default_pipeline_with_app_graphrag_owner(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    doc = tmp_path / "notes.md"
    doc.write_text("# OpenClaw\n\nOpenClaw setup notes.\n", encoding="utf-8")
    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)], graphrag_execution_owner=GraphExecutionOwner.APP_GRAPHRAG)

    monkeypatch.setattr("app.graphrag.service.data_service_runner.shutil.which", lambda _: None)
    results = service.run_default_pipeline(plan)

    assert [result.engine for result in results] == ["llmwiki", "graphrag"]
    assert results[1].status == "indexed"
    assert results[1].meta["execution_owner"] == GraphExecutionOwner.APP_GRAPHRAG.value
    assert results[1].meta["execution_result"]["execution_mode"] == "app_graphrag_compat_materializer"
    assert service.layout.graphrag_execution_owner.exists()
    assert service.layout.graphrag_execution_request.exists()
    audit = service.read_boundary_audit()
    graph_index_row = next(item for item in audit["capability_migration_table"] if item["capability"] == "graph_index_execution")
    assert graph_index_row["current_owner"] == GraphExecutionOwner.APP_GRAPHRAG.value
    assert graph_index_row["status"] == "done"


def test_data_service_run_graphrag_execution_request(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    doc = tmp_path / "notes.md"
    doc.write_text("# OpenClaw\n\nOpenClaw setup notes.\n", encoding="utf-8")
    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)], graphrag_execution_owner=GraphExecutionOwner.APP_GRAPHRAG)

    monkeypatch.setattr("app.graphrag.service.data_service_runner.shutil.which", lambda _: None)
    service.run_default_pipeline(plan)

    def fake_runner(request_path):
        return {
            "status": "completed",
            "request_path": str(request_path),
            "compat_state": {
                "state_db": str(service.layout.graphrag_state_dir / "graphrag.db"),
            },
        }

    monkeypatch.setattr("app.graphrag.service.run_data_service_execution_request", fake_runner)
    result = service.run_graphrag_execution_request()

    assert result["status"] == "completed"
    owner_payload = json.loads(service.layout.graphrag_execution_owner.read_text(encoding="utf-8"))
    assert owner_payload["status"] == "indexed_via_app_graphrag"


def test_data_service_get_graph_snapshot_prefers_app_graphrag_bridge(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    service = DataService(workspace)
    service.layout.ensure_directories()
    service.layout.graphrag_execution_owner.write_text(
        json.dumps(
            {
                "execution_owner": GraphExecutionOwner.APP_GRAPHRAG.value,
                "status": "indexed_via_app_graphrag",
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    def fake_snapshot(workspace_path, *, max_nodes):
        return {
            "graph_model_version": DataService.GRAPH_QUERY_MODEL_VERSION,
            "nodes": [{"id": "n1", "label": "Bridge", "name": "Bridge", "type": "entity", "node_type": "entity", "size": 10, "count": 1, "weighted_count": 1.0, "document_count": 1, "community_id": None, "metrics": {}, "attributes": {}}],
            "edges": [],
            "communities": [],
            "stats": {"entity_count": 1, "theme_count": 0, "relationship_count": 0, "community_count": 0, "document_count": 1},
            "db_path": str(Path(workspace_path) / "graphrag" / "state" / "graphrag.db"),
            "source": "app.graphrag.bridge",
        }

    monkeypatch.setattr("app.graphrag.service.read_workspace_graph_snapshot", fake_snapshot)
    graph = service.get_graph_snapshot(max_nodes=20)
    assert graph["source"] == "app.graphrag.bridge"
    assert graph["nodes"][0]["label"] == "Bridge"


def test_data_service_query_graphrag_prefers_app_graphrag_bridge(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    service = DataService(workspace)
    service.layout.ensure_directories()
    service.layout.graphrag_execution_owner.write_text(
        json.dumps(
            {
                "execution_owner": GraphExecutionOwner.APP_GRAPHRAG.value,
                "status": "indexed_via_app_graphrag",
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    def fake_query(workspace_path, query_text, *, top_k):
        return {
            "graph_model_version": DataService.GRAPH_QUERY_MODEL_VERSION,
            "nodes": [{"id": "n1", "label": "Bridge", "name": "Bridge", "type": "entity", "node_type": "entity", "size": 10, "score": 1.0, "weighted_count": 1.0, "document_count": 1, "metrics": {}, "attributes": {}}],
            "edges": [],
            "communities": [],
            "hits": [{"title": "Entity: Bridge", "snippet": "bridge hit", "source": "n1", "score": 1.0, "kind": "entity", "meta": {"kind": "entity"}}],
            "units": [],
            "stats": {"entity_count": 1, "theme_count": 0, "relationship_count": 0, "community_count": 0, "document_count": 1},
            "source": "app.graphrag.bridge",
        }

    monkeypatch.setattr("app.graphrag.service.query_workspace_graph", fake_query)
    result = service.query_graphrag("Bridge", top_k=5)
    assert result.engine_payloads["graphrag"]["source"] == "app.graphrag.bridge"
    assert result.hits[0].title == "Entity: Bridge"


def test_data_service_query_graphrag_and_hybrid(tmp_path):
    workspace = tmp_path / "workspace"
    doc = tmp_path / "notes.md"
    doc.write_text("# OpenClaw\n\nOpenClaw requires Python and ClaudeCode.\n", encoding="utf-8")
    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])
    service.run_default_pipeline(plan)

    graphrag = service.query("OpenClaw", mode=QueryMode.GRAPHRAG, top_k=5)
    hybrid = service.query("OpenClaw", mode=QueryMode.HYBRID, top_k=5)

    assert graphrag.mode == QueryMode.GRAPHRAG
    assert graphrag.hits
    assert "GraphRAG matched" in graphrag.answer
    assert graphrag.engine_payloads["graphrag"]["graph_model_version"] == DataService.GRAPH_QUERY_MODEL_VERSION
    assert graphrag.engine_payloads["graphrag"]["source"] == "app.graphrag.bridge"
    assert "nodes" in graphrag.engine_payloads["graphrag"]
    assert "edges" in graphrag.engine_payloads["graphrag"]
    if graphrag.engine_payloads["graphrag"]["nodes"]:
        first_node = graphrag.engine_payloads["graphrag"]["nodes"][0]
        assert {"id", "label", "type", "node_type", "metrics"}.issubset(first_node.keys())
    if graphrag.engine_payloads["graphrag"]["edges"]:
        first_edge = graphrag.engine_payloads["graphrag"]["edges"][0]
        assert {"id", "source", "target", "relation", "attributes"}.issubset(first_edge.keys())
    assert hybrid.mode == QueryMode.HYBRID
    assert hybrid.hits


def test_data_service_summary_bundle_and_graph_snapshot(tmp_path):
    workspace = tmp_path / "workspace"
    doc = tmp_path / "notes.md"
    doc.write_text("# ComfyUI\n\nComfyUI integrates with OpenClaw.\n", encoding="utf-8")
    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])
    service.run_default_pipeline(plan)

    summary_bundle = service.read_summary_bundle()
    graph_snapshot = service.get_graph_snapshot(max_nodes=20)

    assert summary_bundle["workspace"] == str(workspace.resolve())
    assert "summary_markdown" in summary_bundle
    assert "summary_json" in summary_bundle
    assert "quality" in summary_bundle
    assert "llmwiki_pages" in summary_bundle
    assert graph_snapshot["graph_model_version"] == DataService.GRAPH_QUERY_MODEL_VERSION
    assert graph_snapshot["source"] == "app.graphrag.bridge"
    assert graph_snapshot["stats"]["entity_count"] >= 1
    assert "communities" in graph_snapshot
    assert summary_bundle["quality"]["distill"]["schema_version"] == DataService.DISTILL_SCHEMA_VERSION
    assert "unit_kind_counts" in summary_bundle["quality"]["distill"]
    assert summary_bundle["quality"]["distill"]["typed_unit_schema_version"] == DataService.TYPED_DISTILL_UNIT_SCHEMA_VERSION
    assert "typed_unit_type_counts" in summary_bundle["quality"]["distill"]
    assert summary_bundle["quality"]["llmwiki"]["page_count"] >= 1
    assert "top_communities" in summary_bundle["quality"]["graphrag"]
    if graph_snapshot["nodes"]:
        first_node = graph_snapshot["nodes"][0]
        assert {"id", "label", "type", "node_type", "metrics", "attributes"}.issubset(first_node.keys())
    if graph_snapshot["edges"]:
        first_edge = graph_snapshot["edges"][0]
        assert {"id", "source", "target", "relation", "attributes"}.issubset(first_edge.keys())
    if graph_snapshot["communities"]:
        first_community = graph_snapshot["communities"][0]
        assert {"id", "title", "stats", "attributes"}.issubset(first_community.keys())


def test_data_service_distill_bundle_preview(tmp_path):
    workspace = tmp_path / "workspace"
    doc = tmp_path / "notes.json"
    doc.write_text(
        json.dumps(
            {
                "title": "OpenClaw 配置说明",
                "turns": [
                    {"role": "user", "content": "怎么配置 OpenClaw？"},
                    {"role": "assistant", "content": "先安装 Python，再配置 API Key。"},
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])
    service.build_distilled_units(plan)

    bundle = service.read_distill_bundle(limit=5)
    source_bundle = service.read_distill_bundle(source_id=doc.stem, limit=5)

    assert bundle["schema_version"] == DataService.DISTILL_SCHEMA_VERSION
    assert bundle["manifest"]["source_count"] == 1
    assert bundle["units"]
    assert all("typed_unit" in unit for unit in bundle["units"])
    assert bundle["provenance_overview"]["typed_unit_type_counts"]
    assert bundle["source"] is None
    assert bundle["source_profiles"]
    assert bundle["provenance_overview"]["available_source_count"] == 1
    assert source_bundle["source"] is not None
    assert source_bundle["source"]["source_id"] == doc.stem
    assert source_bundle["source"]["record"]["schema_version"] == DataService.DISTILL_SCHEMA_VERSION
    assert "profile_debug" in source_bundle["source"]
    assert "provenance_summary" in source_bundle["source"]
    assert "units_by_kind" in source_bundle["source"]
    assert "top_units" in source_bundle["source"]
    assert source_bundle["source"]["provenance_summary"]["typed_unit_type_counts"]
    assert source_bundle["source_profiles"][0]["typed_unit_type_counts"]
    assert source_bundle["source"]["profile_debug"]["summary_sentences"]
    assert source_bundle["source"]["provenance_summary"]["path_count"] >= 1
    assert source_bundle["units"]


def test_data_service_distill_bundle_recovers_from_sources_dir_when_manifest_missing(tmp_path):
    workspace = tmp_path / "workspace"
    doc = tmp_path / "notes.json"
    doc.write_text(
        json.dumps(
            {
                "title": "OpenClaw 配置说明",
                "turns": [
                    {"role": "user", "content": "怎么配置 OpenClaw？"},
                    {"role": "assistant", "content": "先安装 Python，再配置 API Key。"},
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])
    service.build_distilled_units(plan)

    service.layout.distill_manifest.unlink()
    bundle = service.read_distill_bundle(limit=5)

    assert bundle["sources"]
    assert bundle["available_source_count"] == 1
    assert bundle["manifest"]["recovered_from_sources_dir"] is True


def test_data_service_distill_bundle_supports_filters(tmp_path):
    workspace = tmp_path / "workspace"
    doc = tmp_path / "notes.json"
    doc.write_text(
        json.dumps(
            {
                "title": "OpenClaw 配置说明",
                "turns": [
                    {"role": "user", "content": "怎么配置 OpenClaw？"},
                    {"role": "assistant", "content": "先安装 Python，再配置 API Key。"},
                    {"role": "assistant", "content": "注意不要缺少系统依赖。"},
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])
    service.build_distilled_units(plan)

    kind_bundle = service.read_distill_bundle(limit=10, kind="conclusion")
    assert kind_bundle["units"]
    assert all(unit["kind"] == "conclusion" for unit in kind_bundle["units"])

    typed_bundle = service.read_distill_bundle(limit=10, typed_unit_type="claim")
    assert typed_bundle["units"]
    assert typed_bundle["filters"]["typed_unit_type"] == "claim"
    assert all(unit["typed_unit"]["type"] == "claim" for unit in typed_bundle["units"])

    importance_bundle = service.read_distill_bundle(limit=10, min_importance=0.7)
    assert importance_bundle["units"]
    assert all(float(unit["importance"]) >= 0.7 for unit in importance_bundle["units"])

    enriched_bundle = service.read_distill_bundle(limit=10, llm_enriched_only=True)
    assert enriched_bundle["filters"]["llm_enriched_only"] is True
    assert all(bool(unit.get("is_llm_enriched", False)) for unit in enriched_bundle["units"])

    authority_bundle = service.read_distill_bundle(limit=10, authority="SECONDARY_CHAT")
    assert authority_bundle["units"]
    assert all(unit["authority"] == "SECONDARY_CHAT" for unit in authority_bundle["units"])

    weighted_bundle = service.read_distill_bundle(limit=10, min_source_weight=1.1)
    assert weighted_bundle["units"]
    assert all(float(unit["source_weight"]) >= 1.1 for unit in weighted_bundle["units"])

    dense_bundle = service.read_distill_bundle(limit=10, min_source_density=1.0)
    assert dense_bundle["units"]
    assert all(float(unit["source_density_score"]) >= 1.0 for unit in dense_bundle["units"])


def test_data_service_cli_distill_command(tmp_path, monkeypatch, capsys):
    workspace = tmp_path / "workspace"
    doc = tmp_path / "notes.md"
    doc.write_text("# OpenClaw\n\nOpenClaw requires Python.\n", encoding="utf-8")
    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])
    service.build_distilled_units(plan)

    from data_service.__main__ import main

    monkeypatch.setattr(
        sys,
        "argv",
        ["data_service", "distill", "--workspace", str(workspace), "--limit", "3", "--typed-type", "concept"],
    )

    exit_code = main()
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["workspace"] == str(workspace.resolve())
    assert payload["units"]
    assert payload["filters"]["typed_unit_type"] == "concept"
    assert all(unit["typed_unit"]["type"] == "concept" for unit in payload["units"])
    assert payload["filters"]["kind"] is None
    assert payload["source_profiles"]
    assert payload["provenance_overview"]["available_source_count"] == 1


def test_data_service_builds_explicit_engine_handoffs(tmp_path):
    workspace = tmp_path / "workspace"
    doc = tmp_path / "notes.json"
    doc.write_text(
        json.dumps(
            {
                "title": "OpenClaw 配置说明",
                "turns": [
                    {"role": "user", "content": "怎么配置 OpenClaw？"},
                    {"role": "assistant", "content": "先安装 Python，再配置 API Key。"},
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])
    units = service.build_distilled_units(plan)

    llmwiki_handoff = service.build_llmwiki_handoff(plan, units)
    graphrag_handoff = service.build_graphrag_handoff(plan, units)

    assert llmwiki_handoff["contract_version"] == DataService.ENGINE_INPUT_CONTRACT_VERSION
    assert graphrag_handoff["contract_version"] == DataService.ENGINE_INPUT_CONTRACT_VERSION
    assert "entity_candidate" not in llmwiki_handoff["allowed_unit_kinds"]
    assert "relation_candidate" in graphrag_handoff["allowed_unit_kinds"]
    assert all("normalized_text" not in unit for unit in llmwiki_handoff["units"])
    assert all("relations" not in unit for unit in llmwiki_handoff["units"])
    assert any("normalized_text" in unit for unit in graphrag_handoff["units"])
    assert all(unit["typed_unit"]["schema_version"] == DataService.TYPED_DISTILL_UNIT_SCHEMA_VERSION for unit in llmwiki_handoff["units"])
    assert all(unit["typed_unit"]["schema_version"] == DataService.TYPED_DISTILL_UNIT_SCHEMA_VERSION for unit in graphrag_handoff["units"])
    assert all(set(unit.keys()) <= {
        "unit_id", "source_id", "kind", "typed_unit", "authority", "text", "importance", "confidence",
        "source_weight", "source_density_score", "is_title_derived", "is_llm_enriched",
        "tags", "entities", "provenance",
    } for unit in llmwiki_handoff["units"])


def test_default_adapters_write_input_contracts(tmp_path):
    workspace = tmp_path / "workspace"
    doc = tmp_path / "notes.md"
    doc.write_text("# OpenClaw\n\nOpenClaw requires Python.\n", encoding="utf-8")
    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])
    units = service.build_distilled_units(plan)

    llmwiki_result = service.run_pipeline(
        plan,
        distilled_units=units,
        llmwiki_adapter=LLMWikiEngineAdapter(),
        graphrag_adapter=GraphRAGWorkspaceAdapter(),
    )

    assert any(path.endswith("llmwiki/state/input_contract.json") for path in llmwiki_result[0].artifacts)
    assert any(path.endswith("graphrag/cache/input_contract.json") for path in llmwiki_result[1].artifacts)
    llmwiki_contract = json.loads((service.layout.llmwiki_state_dir / "input_contract.json").read_text(encoding="utf-8"))
    graphrag_contract = json.loads((service.layout.graphrag_cache_dir / "input_contract.json").read_text(encoding="utf-8"))
    assert llmwiki_contract["engine"] == "llmwiki"
    assert graphrag_contract["engine"] == "graphrag"


def test_data_service_boundary_audit_reports_current_split(tmp_path):
    workspace = tmp_path / "workspace"
    doc = tmp_path / "notes.md"
    doc.write_text("# OpenClaw\n\nOpenClaw requires Python.\n", encoding="utf-8")
    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])
    service.run_default_pipeline(plan)

    audit = service.read_boundary_audit()

    assert audit["contracts"]["llmwiki_input_contract"]["exists"] is True
    assert audit["contracts"]["graphrag_input_contract"]["exists"] is True
    assert audit["contracts"]["graphrag_execution_owner"]["exists"] is True
    assert audit["contracts"]["typed_unit_contract"]["schema_version"] == DataService.TYPED_DISTILL_UNIT_SCHEMA_VERSION
    assert audit["contracts"]["typed_unit_contract"]["legacy_kind_to_typed_unit_type"]["conclusion"] == "claim"
    assert audit["contracts"]["typed_unit_contract"]["typed_unit_type_counts"]
    assert "index" in audit["graphrag_codebase"]["api_modules"]
    assert "query" in audit["graphrag_codebase"]["api_modules"]
    assert any(item["area"] == "indexing" for item in audit["overlap_areas"])
    assert "distill_contract" in audit["data_service"]["owns_now"]
    assert any(item["capability"] == "graph_index_execution" for item in audit["capability_migration_table"])
    graph_index_row = next(item for item in audit["capability_migration_table"] if item["capability"] == "graph_index_execution")
    assert graph_index_row["target_owner"] == "app.graphrag"
    assert graph_index_row["current_owner"] == GraphExecutionOwner.APP_GRAPHRAG.value
    assert graph_index_row["status"] == "done"
    query_model_row = next(item for item in audit["capability_migration_table"] if item["capability"] == "graph_query_model")
    assert query_model_row["current_owner"] == "app.graphrag.service"
    assert query_model_row["status"] == "done"
    community_row = next(item for item in audit["capability_migration_table"] if item["capability"] == "community_snapshot_assembly")
    assert community_row["current_owner"] == "app.graphrag.service"
    assert community_row["status"] == "done"
    assert graph_index_row["current_owner"] == GraphExecutionOwner.APP_GRAPHRAG.value
    assert graph_index_row["status"] == "done"
    assert audit["graph_execution_runtime"]["execution_owner"] == GraphExecutionOwner.APP_GRAPHRAG.value


def test_data_service_reset_workspace_preserves_row_content(tmp_path):
    root = tmp_path / "knowledge"
    workspace = root / "workspace"
    row_dir = root / "row" / "deepseek_split"
    row_dir.mkdir(parents=True)
    source_path = row_dir / "a.json"
    source_path.write_text('{"title":"ComfyUI"}', encoding="utf-8")

    service = DataService(workspace)
    plan = service.build_ingest_plan([str(source_path)])
    service.run_default_pipeline(plan)

    assert service.layout.llmwiki_dir.exists()
    assert service.layout.graphrag_dir.exists()

    result = service.reset_workspace("Delete")

    assert result["row_preserved"] is True
    assert source_path.exists()
    assert source_path.read_text(encoding="utf-8") == '{"title":"ComfyUI"}'
    assert service.layout.llmwiki_dir.exists()
    assert service.layout.graphrag_dir.exists()
    assert list(service.layout.llmwiki_pages_dir.glob("*.md")) == []
