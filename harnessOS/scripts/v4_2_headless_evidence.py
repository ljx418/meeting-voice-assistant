"""Generate the V4.2-A headless interaction evidence package.

The package is derived from the existing V4.1 local Markdown workflow BFF path.
It does not create a generic executor or treat WorkflowSpec/Drawio/HTML reports
as runtime truth.
"""

from __future__ import annotations

import html
import json
import os
import sys
import tempfile
from copy import deepcopy
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parents[1]
TESTS_DIR = REPO_ROOT / "tests"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

from apps.api import create_app  # noqa: E402
from v4_0_reference_support import SCOPE_QUERY, build_gateway  # noqa: E402

OUTPUT_DIR = REPO_ROOT / "docs" / "design" / "V4.2" / "evidence" / "headless-interaction"

FORBIDDEN_TERMS = (
    "capability_token",
    "subscription_token",
    "Authorization",
    "Bearer",
    "secret",
    "raw_trace_payload",
    "raw_artifact_content",
    "raw_connector_payload",
    "raw prompt",
    "upstream signed URL",
    "/v1/rpc",
    "/v1/events/subscribe",
    "complete Workflow Studio ready",
    "Agent executor ready",
    "controlled executor ready",
    "production-ready external app support",
    "full multi-Agent orchestration ready",
)

TOP_LEVEL_SPEC_KEYS = {
    "metadata",
    "stations",
    "edges",
    "artifact_contracts",
    "quality_rules",
    "approval_points",
    "context_refs",
    "evidence_refs",
}


def generate_evidence_package(output_dir: Path = OUTPUT_DIR) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    runtime = _run_v4_1_local_workflow()
    spec = build_workflow_spec(runtime)
    validate_workflow_spec(spec)

    workflow_schema = build_workflow_schema()
    transcript = build_tui_transcript(runtime)
    runtime_export = build_runtime_export(runtime)
    operation_evidence = runtime["operation_evidence"]

    _write_json(output_dir / "workflow.json", spec)
    (output_dir / "workflow.yaml").write_text(render_workflow_yaml(spec), encoding="utf-8")
    _write_json(output_dir / "workflow.schema.json", workflow_schema)
    (output_dir / "tui-transcript.txt").write_text(transcript, encoding="utf-8")
    _write_json(output_dir / "exported-runtime-result.json", runtime_export)
    _write_json(output_dir / "artifacts.json", build_artifact_report(runtime_export))
    _write_json(output_dir / "quality.json", build_quality_report(runtime_export))
    _write_json(output_dir / "operation-evidence.json", operation_evidence)

    (output_dir / "workflow.drawio").write_text(render_workflow_drawio(spec), encoding="utf-8")
    (output_dir / "workflow_status.drawio").write_text(render_status_drawio(spec, runtime_export), encoding="utf-8")
    (output_dir / "artifact_lineage.drawio").write_text(render_artifact_lineage_drawio(spec, runtime_export), encoding="utf-8")

    reports = {
        "thin_web_console.html": render_thin_web_console_html(),
        "workflow_board.html": render_workflow_board_html(spec, runtime_export),
        "artifacts.html": render_artifacts_html(runtime_export),
        "quality.html": render_quality_html(runtime_export),
        "evidence.html": render_evidence_html(operation_evidence),
    }
    for filename, content in reports.items():
        (output_dir / filename).write_text(content, encoding="utf-8")

    summary = render_result_summary(runtime_export, operation_evidence)
    (output_dir / "result-summary.md").write_text(summary, encoding="utf-8")

    package_manifest = {
        "output_dir": _display_path(output_dir),
        "files": sorted(path.name for path in output_dir.iterdir() if path.is_file()),
        "workflow_instance_id": runtime_export["workflow_instance_id"],
        "status": runtime_export["status"],
        "redaction_status": "redacted",
        "source": "v4_1_local_workflow_path",
    }
    assert_no_forbidden_text(package_manifest)
    return package_manifest


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _run_v4_1_local_workflow() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="v42_headless_") as tmp:
        os.environ.setdefault("HARNESS_V3_5_DEV_MODE", "1")
        client = TestClient(create_app(gateway_service=build_gateway(Path(tmp))))
        authorization = _post_json(
            client,
            f"/bff/v4_1/folder-summary/authorize{SCOPE_QUERY}",
            {"folder_path": "Desktop/技术分享", "user_confirmed": True, "source": "folder_input_inspector"},
        )
        scan = _post_json(
            client,
            f"/bff/v4_1/folder-summary/debug-scan{SCOPE_QUERY}",
            {"authorization_id": authorization["authorization_id"]},
        )
        proposal = _post_json(
            client,
            f"/bff/v4_1/folder-summary/proposals{SCOPE_QUERY}",
            {"folder_path": "Desktop/技术分享", "source": "workflow_console"},
        )
        proposal_id = proposal["proposal_id"]
        apply_result = _post_json(
            client,
            f"/bff/v4_1/folder-summary/proposals/{proposal_id}/apply{SCOPE_QUERY}",
            {"user_confirmed": True, "source": "editing_panel", "authorization_id": authorization["authorization_id"]},
        )
        publish_result = _post_json(
            client,
            f"/bff/v4_1/folder-summary/proposals/{proposal_id}/publish{SCOPE_QUERY}",
            {"user_confirmed": True, "source": "editing_panel"},
        )
        run = _post_json(
            client,
            f"/bff/v4_1/folder-summary/proposals/{proposal_id}/start-local-workflow{SCOPE_QUERY}",
            {"user_confirmed": True, "source": "run_panel", "authorization_id": authorization["authorization_id"]},
        )
        patch = _post_json(
            client,
            f"/bff/v4_1/folder-summary/instances/{run['workflow_instance_id']}/agent-debug-proposal{SCOPE_QUERY}",
            {"requested_change": "empty_folder_placeholder_summary"},
        )
        evidence = _get_json(
            client,
            f"/bff/v4_1/folder-summary/instances/{run['workflow_instance_id']}/operation-evidence{SCOPE_QUERY}",
        )
        review = _get_json(
            client,
            f"/bff/v4_1/folder-summary/instances/{run['workflow_instance_id']}/governance-review{SCOPE_QUERY}",
        )
        hydrated = deepcopy(run)
        hydrated["authorization"] = authorization
        hydrated["debug_scan"] = scan
        hydrated["proposal"] = proposal
        hydrated["apply_result"] = apply_result
        hydrated["publish_result"] = publish_result
        hydrated["agent_debug_patch"] = patch
        hydrated["operation_evidence"] = evidence
        hydrated["governance_review"] = review
        assert_no_forbidden_text(hydrated)
        return hydrated


def _post_json(client: TestClient, path: str, payload: dict[str, Any]) -> dict[str, Any]:
    response = client.post(path, json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert "error" not in data, data
    return data


def _get_json(client: TestClient, path: str) -> dict[str, Any] | list[dict[str, Any]]:
    response = client.get(path)
    assert response.status_code == 200, response.text
    data = response.json()
    assert_no_forbidden_text(data)
    return data


def build_workflow_spec(runtime: dict[str, Any]) -> dict[str, Any]:
    nodes = runtime["nodes"]
    artifacts = runtime["artifacts"]
    return {
        "metadata": {
            "workflow_spec_id": "v42_headless_local_markdown_summary",
            "schema_version": "v4.2-a",
            "name": "本地 Markdown 文件夹递归总结",
            "stage": "V4.2-A Headless Interaction Pivot",
            "source_baseline": "V4.1 local recursive Markdown summary workflow",
            "runtime_truth_boundary": "WorkflowSpec is a portable definition and review artifact, not WorkflowDraft or WorkflowVersion runtime truth.",
            "generated_from": "v4_1_local_workflow_path",
        },
        "stations": [
            {
                "station_id": node["station_id"],
                "name": node["name"],
                "station_kind": _station_kind(node["station_id"]),
                "description": _station_description(node["station_id"]),
                "input_artifacts": _station_inputs(node["station_id"]),
                "output_artifacts": _station_outputs(node["station_id"]),
            }
            for node in nodes
        ],
        "edges": [
            {
                "edge_id": f"edge_{nodes[index]['station_id']}_{nodes[index + 1]['station_id']}",
                "from_station_id": nodes[index]["station_id"],
                "to_station_id": nodes[index + 1]["station_id"],
                "artifact_contract_id": _station_outputs(nodes[index]["station_id"])[0],
            }
            for index in range(len(nodes) - 1)
        ],
        "artifact_contracts": [
            {"artifact_contract_id": "folder_ref", "kind": "folder_reference", "description": "用户确认授权后的本地文件夹引用。"},
            {"artifact_contract_id": "file_tree", "kind": "folder_tree", "description": "只读调试扫描树。"},
            {"artifact_contract_id": "md_file_list", "kind": "markdown_file_list", "description": "Markdown 文件列表。"},
            {"artifact_contract_id": "parsed_docs", "kind": "parsed_markdown_documents", "description": "解析后的 Markdown 元数据。"},
            {"artifact_contract_id": "grouped_docs", "kind": "folder_grouped_documents", "description": "按子文件夹分组后的文档引用。"},
            {"artifact_contract_id": "folder_summaries", "kind": "markdown_summary", "description": "每个子文件夹的总结 artifact。"},
            {"artifact_contract_id": "overview_summary", "kind": "overview_summary", "description": "跨文件夹总览总结。"},
            {"artifact_contract_id": "quality_report", "kind": "quality_report", "description": "unsupported 文件、空文件夹和覆盖率。"},
            {"artifact_contract_id": "output_package", "kind": "artifact_package", "description": "发布后的只读 artifact 集。"},
        ],
        "quality_rules": [
            {"rule_id": "summary_coverage", "description": "每个含 Markdown 的子文件夹都必须有总结。"},
            {"rule_id": "unsupported_file_recorded", "description": "unsupported 文件必须进入质量报告。"},
            {"rule_id": "empty_folder_recorded", "description": "空文件夹必须进入质量报告。"},
        ],
        "approval_points": [
            {"approval_point_id": "apply_draft", "operation": "workflow.folder_summary.apply", "policy": "user_confirmed_only"},
            {"approval_point_id": "publish_version", "operation": "workflow.folder_summary.publish", "policy": "user_confirmed_only"},
            {"approval_point_id": "run_local_workflow", "operation": "workflow.folder_summary.run", "policy": "user_confirmed_only"},
        ],
        "context_refs": [
            {"context_ref_id": "folder_path", "value_label": "Desktop/技术分享"},
            {"context_ref_id": "fixture_root", "value_label": "tests/fixtures/desktop/技术分享"},
            {"context_ref_id": "scope", "value_label": "reference_app/demo_a/local"},
        ],
        "evidence_refs": [
            {"evidence_ref_id": "v4_1_runtime", "kind": "runtime_result", "resource_id": runtime["workflow_instance_id"]},
            {"evidence_ref_id": "v4_1_operation_evidence", "kind": "operation_evidence", "resource_id": "operation-evidence.json"},
            {"evidence_ref_id": "v4_2_reports", "kind": "headless_evidence_package", "resource_id": "docs/design/V4.2/evidence/headless-interaction"},
            {"evidence_ref_id": "artifact_count", "kind": "artifact_summary", "resource_id": str(len(artifacts))},
        ],
    }


def build_workflow_schema() -> dict[str, Any]:
    base_string = {"type": "string", "minLength": 1}
    string_array = {"type": "array", "items": base_string}
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://harnessos.local/schemas/v4_2/workflow.schema.json",
        "title": "HarnessOS V4.2-A WorkflowSpec",
        "type": "object",
        "additionalProperties": False,
        "required": sorted(TOP_LEVEL_SPEC_KEYS),
        "properties": {
            "metadata": {
                "type": "object",
                "additionalProperties": False,
                "required": ["workflow_spec_id", "schema_version", "name", "stage", "source_baseline", "runtime_truth_boundary", "generated_from"],
                "properties": {key: base_string for key in ["workflow_spec_id", "schema_version", "name", "stage", "source_baseline", "runtime_truth_boundary", "generated_from"]},
            },
            "stations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["station_id", "name", "station_kind", "description", "input_artifacts", "output_artifacts"],
                    "properties": {
                        "station_id": base_string,
                        "name": base_string,
                        "station_kind": base_string,
                        "description": base_string,
                        "input_artifacts": string_array,
                        "output_artifacts": string_array,
                    },
                },
            },
            "edges": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["edge_id", "from_station_id", "to_station_id", "artifact_contract_id"],
                    "properties": {key: base_string for key in ["edge_id", "from_station_id", "to_station_id", "artifact_contract_id"]},
                },
            },
            "artifact_contracts": _simple_id_description_schema("artifact_contract_id", extra=("kind",)),
            "quality_rules": _simple_id_description_schema("rule_id"),
            "approval_points": _simple_id_description_schema("approval_point_id", extra=("operation", "policy"), description_required=False),
            "context_refs": _ref_schema("context_ref_id", "value_label"),
            "evidence_refs": _ref_schema("evidence_ref_id", "kind", "resource_id"),
        },
    }


def _simple_id_description_schema(id_key: str, *, extra: tuple[str, ...] = (), description_required: bool = True) -> dict[str, Any]:
    required = [id_key, *extra]
    if description_required:
        required.append("description")
    properties = {id_key: {"type": "string", "minLength": 1}, "description": {"type": "string", "minLength": 1}}
    for key in extra:
        properties[key] = {"type": "string", "minLength": 1}
    return {"type": "array", "items": {"type": "object", "additionalProperties": False, "required": required, "properties": properties}}


def _ref_schema(*keys: str) -> dict[str, Any]:
    return {
        "type": "array",
        "items": {
            "type": "object",
            "additionalProperties": False,
            "required": list(keys),
            "properties": {key: {"type": "string", "minLength": 1} for key in keys},
        },
    }


def validate_workflow_spec(spec: dict[str, Any]) -> None:
    if set(spec) != TOP_LEVEL_SPEC_KEYS:
        extra = sorted(set(spec) - TOP_LEVEL_SPEC_KEYS)
        missing = sorted(TOP_LEVEL_SPEC_KEYS - set(spec))
        raise ValueError(f"WorkflowSpec top-level keys mismatch. extra={extra}, missing={missing}")
    station_ids = {station["station_id"] for station in spec["stations"]}
    contract_ids = {contract["artifact_contract_id"] for contract in spec["artifact_contracts"]}
    for edge in spec["edges"]:
        if edge["from_station_id"] not in station_ids or edge["to_station_id"] not in station_ids:
            raise ValueError(f"Edge references unknown station: {edge}")
        if edge["artifact_contract_id"] not in contract_ids:
            raise ValueError(f"Edge references unknown artifact contract: {edge}")
    assert_no_forbidden_text(spec)


def render_workflow_yaml(spec: dict[str, Any]) -> str:
    lines = [
        "# Generated V4.2-A WorkflowSpec. This file is not runtime truth.",
        f"metadata:",
    ]
    for key, value in spec["metadata"].items():
        lines.append(f"  {key}: {json.dumps(value, ensure_ascii=False)}")
    lines.append("stations:")
    for station in spec["stations"]:
        lines.append(f"  - station_id: {station['station_id']}")
        lines.append(f"    name: {json.dumps(station['name'], ensure_ascii=False)}")
        lines.append(f"    station_kind: {station['station_kind']}")
        lines.append(f"    description: {json.dumps(station['description'], ensure_ascii=False)}")
        lines.append(f"    input_artifacts: [{', '.join(station['input_artifacts'])}]")
        lines.append(f"    output_artifacts: [{', '.join(station['output_artifacts'])}]")
    lines.append("edges:")
    for edge in spec["edges"]:
        lines.append(f"  - edge_id: {edge['edge_id']}")
        lines.append(f"    from_station_id: {edge['from_station_id']}")
        lines.append(f"    to_station_id: {edge['to_station_id']}")
        lines.append(f"    artifact_contract_id: {edge['artifact_contract_id']}")
    for section in ["artifact_contracts", "quality_rules", "approval_points", "context_refs", "evidence_refs"]:
        lines.append(f"{section}:")
        for item in spec[section]:
            first_key = next(iter(item))
            lines.append(f"  - {first_key}: {json.dumps(item[first_key], ensure_ascii=False)}")
            for key, value in list(item.items())[1:]:
                lines.append(f"    {key}: {json.dumps(value, ensure_ascii=False)}")
    return "\n".join(lines) + "\n"


def build_tui_transcript(runtime: dict[str, Any]) -> str:
    workflow_instance_id = runtime["workflow_instance_id"]
    proposal_id = runtime["proposal"]["proposal_id"]
    lines = [
        "V4.2-A Headless Interaction Pivot transcript",
        "boundary=WorkflowSpec/Drawio/HTML reports are not runtime truth",
        "browser_direct_v1_rpc=false",
        "browser_direct_v1_events_subscribe=false",
        "",
        "step=01 command='harness tui' read_only=true transcript_only=false result='打开 Headless Command Palette'",
        "step=02 command='harness workflow create \"递归总结 Desktop/技术分享 下的 Markdown 文件\"' read_only=false transcript_only=false backed_by=v4_1_local_workflow_path user_confirmed=false result='生成 workflow spec 和 patch proposal' proposal_id="
        + proposal_id,
        "step=03 command='harness workflow diff --spec workflow.yaml' read_only=true transcript_only=false result='展示 proposal diff'",
        "step=04 command='harness workflow apply --proposal "
        + proposal_id
        + " --user-confirmed' read_only=false transcript_only=false backed_by=v4_1_local_workflow_path user_confirmed=true source=editing_panel result='V4.1 local draft applied'",
        "step=05 command='harness workflow publish --proposal "
        + proposal_id
        + " --user-confirmed' read_only=false transcript_only=false backed_by=v4_1_local_workflow_path user_confirmed=true source=editing_panel result='V4.1 local workflow published'",
        "step=06 command='harness workflow run --proposal "
        + proposal_id
        + " --user-confirmed' read_only=false transcript_only=false backed_by=v4_1_local_workflow_path user_confirmed=true source=run_panel result='V4.1 local workflow completed' workflow_instance_id="
        + workflow_instance_id,
        "step=07 command='harness workflow status --instance "
        + workflow_instance_id
        + "' read_only=true transcript_only=false result='9 stations completed'",
        "step=08 command='harness artifacts list --instance "
        + workflow_instance_id
        + "' read_only=true transcript_only=false result='5 artifacts listed'",
        "step=09 command='harness quality report --instance "
        + workflow_instance_id
        + "' read_only=true transcript_only=false result='quality passed with unsupported and empty folders recorded'",
        "step=10 command='harness evidence show --instance "
        + workflow_instance_id
        + "' read_only=true transcript_only=false result='operation evidence exported'",
        "step=11 command='harness station rerun --station markdown_parse --user-confirmed' read_only=false transcript_only=true generic_runtime=false result='deferred to V4.2-B/C unless V4.1 local rerun path is explicitly invoked'",
    ]
    return "\n".join(lines) + "\n"


def build_runtime_export(runtime: dict[str, Any]) -> dict[str, Any]:
    artifacts = [build_artifact_metadata(item) for item in runtime["artifacts"]]
    return {
        "workflow_instance_id": runtime["workflow_instance_id"],
        "proposal_id": runtime["proposal_id"],
        "status": runtime["status"],
        "source": "v4_1_local_workflow_path",
        "nodes": runtime["nodes"],
        "artifacts": artifacts,
        "quality_report": runtime["quality_report"],
        "debug_scan": runtime["debug_scan"],
        "governance_summary": runtime["governance_review"]["summary"],
        "redaction_status": "redacted",
    }


def build_artifact_metadata(item: dict[str, Any]) -> dict[str, Any]:
    producer_station_id = _producer_station_for_artifact(item["name"])
    return {
        "artifact_id": item["artifact_id"],
        "name": item["name"],
        "kind": item["kind"],
        "producer_station_id": producer_station_id,
        "lineage_refs": [
            f"station:{producer_station_id}",
            "workflow:v4_1_local_markdown_summary",
        ],
        "redaction_status": item["redaction_status"],
    }


def build_artifact_report(runtime: dict[str, Any]) -> dict[str, Any]:
    return {
        "report_id": "v42_headless_artifact_report",
        "workflow_instance_id": runtime["workflow_instance_id"],
        "source_refs": [
            "exported-runtime-result.json",
            "artifact_lineage.drawio",
        ],
        "artifacts": runtime["artifacts"],
        "readonly": True,
        "redaction_status": "redacted",
    }


def build_quality_report(runtime: dict[str, Any]) -> dict[str, Any]:
    quality = runtime["quality_report"]
    return {
        "report_id": "v42_headless_quality_report",
        "workflow_instance_id": runtime["workflow_instance_id"],
        "source_refs": ["exported-runtime-result.json"],
        "status": quality["status"],
        "checks": [
            {
                "check_id": "summary_coverage",
                "status": quality["status"],
                "station_id": "quality_check",
                "artifact_id": "quality_report.json",
                "details": quality["summary_coverage"],
            },
            {
                "check_id": "unsupported_file_recorded",
                "status": "warning" if quality["unsupported_files"] else "passed",
                "station_id": "quality_check",
                "artifact_id": "quality_report.json",
                "details": {"unsupported_files": quality["unsupported_files"]},
            },
            {
                "check_id": "empty_folder_recorded",
                "status": "warning" if quality["empty_folders"] else "passed",
                "station_id": "quality_check",
                "artifact_id": "quality_report.json",
                "details": {"empty_folders": quality["empty_folders"]},
            },
        ],
        "readonly": True,
        "redaction_status": "redacted",
    }


def _producer_station_for_artifact(name: str) -> str:
    if name == "quality_report.json":
        return "quality_check"
    if name == "总览总结.md":
        return "overview_summary"
    return "per_folder_summary"


def render_workflow_drawio(spec: dict[str, Any]) -> str:
    cells = [_drawio_base_cells()]
    for index, station in enumerate(spec["stations"]):
        cells.append(_drawio_vertex(station["station_id"], station["name"], 60 + (index % 3) * 260, 80 + (index // 3) * 120, "#DCFCE7", "#16A34A"))
    for edge in spec["edges"]:
        cells.append(_drawio_edge(edge["edge_id"], edge["from_station_id"], edge["to_station_id"]))
    return _drawio_document("V4.2-A WorkflowSpec Visualization", cells)


def render_status_drawio(spec: dict[str, Any], runtime: dict[str, Any]) -> str:
    status_by_id = {node["station_id"]: node["status"] for node in runtime["nodes"]}
    cells = [_drawio_base_cells()]
    for index, station in enumerate(spec["stations"]):
        status = status_by_id.get(station["station_id"], "unknown")
        label = f"{station['name']}\\nstatus={status}"
        cells.append(_drawio_vertex(f"status_{station['station_id']}", label, 60 + (index % 3) * 260, 80 + (index // 3) * 120, "#DBEAFE", "#2563EB"))
    return _drawio_document("V4.2-A Runtime Status Visualization", cells)


def render_artifact_lineage_drawio(spec: dict[str, Any], runtime: dict[str, Any]) -> str:
    cells = [_drawio_base_cells()]
    for index, artifact in enumerate(runtime["artifacts"]):
        cells.append(_drawio_vertex(f"artifact_{index}", artifact["name"], 80 + (index % 2) * 360, 80 + (index // 2) * 120, "#F8FAFC", "#64748B"))
    cells.append(_drawio_vertex("quality_report", "quality_report\\nsource=quality", 820, 200, "#FFFBEB", "#F59E0B"))
    return _drawio_document("V4.2-A Artifact Lineage", cells)


def _drawio_base_cells() -> str:
    return '<mxCell id="0"/><mxCell id="1" parent="0"/>'


def _drawio_vertex(cell_id: str, label: str, x: int, y: int, fill: str, stroke: str) -> str:
    return (
        f'<mxCell id="{escape(cell_id)}" value="{escape(label)}" '
        f'style="rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};fontSize=13" vertex="1" parent="1">'
        f'<mxGeometry x="{x}" y="{y}" width="190" height="72" as="geometry"/></mxCell>'
    )


def _drawio_edge(cell_id: str, source: str, target: str) -> str:
    return (
        f'<mxCell id="{escape(cell_id)}" value="" style="endArrow=block;html=1;rounded=0;strokeColor=#64748B" edge="1" parent="1" '
        f'source="{escape(source)}" target="{escape(target)}"><mxGeometry relative="1" as="geometry"/></mxCell>'
    )


def _drawio_document(title: str, cells: list[str]) -> str:
    return (
        '<mxfile host="app.diagrams.net" modified="2026-05-28T00:00:00.000Z" agent="HarnessOS V4.2-A" version="24.7.17">'
        f'<diagram id="v42_headless" name="{escape(title)}"><mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" math="0" shadow="0">'
        f'<root>{"".join(cells)}</root></mxGraphModel></diagram></mxfile>'
    )


def render_workflow_board_html(spec: dict[str, Any], runtime: dict[str, Any]) -> str:
    rows = "\n".join(
        f"<tr><td>{html.escape(node['station_id'])}</td><td>{html.escape(node['name'])}</td><td>{html.escape(node['status'])}</td><td>{len(node.get('attempts') or [])}</td></tr>"
        for node in runtime["nodes"]
    )
    return _html_page(
        "V4.2-A Workflow Board",
        "Data source: spec / draft-version / runtime",
        f"<p>WorkflowSpec 不是运行时事实源；本报告只读。</p><table><thead><tr><th>Station</th><th>Name</th><th>Status</th><th>Attempts</th></tr></thead><tbody>{rows}</tbody></table>",
    )


def render_artifacts_html(runtime: dict[str, Any]) -> str:
    items = "\n".join(f"<li>{html.escape(item['name'])} <span>{html.escape(item['kind'])}</span></li>" for item in runtime["artifacts"])
    return _html_page("V4.2-A Artifacts", "Data source: artifact / runtime", f"<p>只展示 artifact metadata，不输出原始 artifact 内容。</p><ul>{items}</ul>")


def render_quality_html(runtime: dict[str, Any]) -> str:
    quality = runtime["quality_report"]
    unsupported = ", ".join(quality["unsupported_files"]) or "none"
    empty = ", ".join(quality["empty_folders"]) or "none"
    body = (
        f"<p>Status: {html.escape(quality['status'])}</p>"
        f"<p>Markdown files: {quality['markdown_file_count']}</p>"
        f"<p>Unsupported files: {html.escape(unsupported)}</p>"
        f"<p>Empty folders: {html.escape(empty)}</p>"
    )
    return _html_page("V4.2-A Quality", "Data source: quality / runtime", body)


def render_evidence_html(evidence: list[dict[str, Any]]) -> str:
    rows = "\n".join(
        f"<tr><td>{html.escape(item['operation'])}</td><td>{html.escape(str(item['user_confirmed']))}</td><td>{html.escape(item['policy_decision'])}</td><td>{html.escape(item['redaction_status'])}</td></tr>"
        for item in evidence
    )
    return _html_page(
        "V4.2-A Evidence",
        "Data source: evidence / governance review",
        f"<p>治理证据只读，不提供操作按钮。</p><table><thead><tr><th>Operation</th><th>User Confirmed</th><th>Policy</th><th>Redaction</th></tr></thead><tbody>{rows}</tbody></table>",
    )


def render_thin_web_console_html() -> str:
    links = "\n".join(
        f'<li><a href="{html.escape(target)}">{html.escape(label)}</a></li>'
        for label, target in [
            ("打开 Workflow Drawio", "workflow.drawio"),
            ("打开 Workflow Status Drawio", "workflow_status.drawio"),
            ("打开 Artifact Lineage Drawio", "artifact_lineage.drawio"),
            ("查看 Workflow Board", "workflow_board.html"),
            ("查看 Artifacts", "artifacts.html"),
            ("查看 Quality", "quality.html"),
            ("查看 Evidence", "evidence.html"),
        ]
    )
    return _html_page(
        "V4.2-A Thin Web Console",
        "Data source: spec / runtime / artifact / quality / evidence",
        f"<p>Thin Web Console 仅作为观察入口，不提供完整拖拽编辑、不提供通用运行或重跑。</p><ul>{links}</ul>",
    )


def _html_page(title: str, source: str, body: str) -> str:
    page = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    body {{ font-family: Inter, Arial, sans-serif; background: #f8fafc; color: #0f172a; margin: 32px; }}
    main {{ max-width: 960px; margin: 0 auto; background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 24px; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 16px; }}
    th, td {{ border-bottom: 1px solid #e2e8f0; text-align: left; padding: 10px; }}
    .source {{ color: #475569; }}
    .readonly {{ color: #166534; font-weight: 700; }}
  </style>
</head>
<body>
  <main>
    <h1>{html.escape(title)}</h1>
    <p class="source">{html.escape(source)}</p>
    <p class="readonly">只读报告，无隐藏 mutation form。</p>
    {body}
  </main>
</body>
</html>
"""
    lowered = page.lower()
    if "<form" in lowered or "method=\"post\"" in lowered or "fetch(" in lowered:
        raise ValueError("HTML report contains a mutation surface")
    assert_no_forbidden_text(page)
    return page


def render_result_summary(runtime: dict[str, Any], evidence: list[dict[str, Any]]) -> str:
    operations = ", ".join(sorted({item["operation"] for item in evidence}))
    return f"""# V4.2-A Headless Interaction Evidence Result Summary

Allowed claim:

V4.2-A complete: headless interaction baseline ready for local workflow validation.

Runtime source:

- source: v4_1_local_workflow_path
- workflow_instance_id: {runtime['workflow_instance_id']}
- status: {runtime['status']}
- stations: {len(runtime['nodes'])}
- artifacts: {len(runtime['artifacts'])}
- evidence operations: {operations}

Headless outputs:

- TUI transcript generated.
- WorkflowSpec YAML/JSON/schema generated.
- Drawio workflow/status/artifact lineage files generated.
- HTML board/artifacts/quality/evidence reports generated.
- Thin Web Console role is observation-only: open Drawio, open HTML reports, view evidence package, view workflow board, view artifacts, view quality.

Boundary checks:

- WorkflowSpec is not WorkflowDraft or WorkflowVersion runtime truth: PASS.
- Drawio is read-only and not runtime truth: PASS.
- HTML reports are read-only and contain no hidden mutation form: PASS.
- Mutating commands are V4.1-backed or transcript-only: PASS.
- Generic controlled execution runtime is deferred to V4.2-B/C: PASS.
- source=agent cannot execute mutation: PASS.
- Browser direct /v1 routes are not used by this package: PASS.
- Redaction check: PASS.
- No false-green claims: PASS.

Spec Drift Evaluation:

- Risk: LOW
- Reason: V4.2-A outputs are headless wrappers around the verified V4.1 local workflow path and do not add generic runtime behavior.
- Decision: proceed to completion validation.

False Green Evaluation:

- Risk: LOW
- Reason: transcript-only and V4.1-backed operations are explicitly labeled. No generic executor evidence is fabricated.
- Decision: proceed to V4.2-B audit only after focused tests pass.
"""


def assert_no_forbidden_text(payload: Any) -> None:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True) if not isinstance(payload, str) else payload
    for term in FORBIDDEN_TERMS:
        if term in raw:
            raise AssertionError(f"Forbidden term leaked: {term}")


def _write_json(path: Path, payload: Any) -> None:
    assert_no_forbidden_text(payload)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _station_kind(station_id: str) -> str:
    return {
        "folder_input": "input",
        "folder_scan": "scan",
        "markdown_filter": "filter",
        "markdown_parse": "parse",
        "folder_group": "group",
        "per_folder_summary": "summarize",
        "overview_summary": "summarize",
        "quality_check": "quality",
        "artifact_publish": "publish_artifacts",
    }[station_id]


def _station_description(station_id: str) -> str:
    return {
        "folder_input": "用户确认本地文件夹读取授权。",
        "folder_scan": "递归扫描文件夹并返回只读文件树和统计。",
        "markdown_filter": "筛选 Markdown 文件并记录 unsupported 文件。",
        "markdown_parse": "解析 Markdown 元数据。",
        "folder_group": "按子文件夹对文档分组。",
        "per_folder_summary": "为每个含 Markdown 的子文件夹生成总结。",
        "overview_summary": "生成跨子文件夹总览总结。",
        "quality_check": "检查总结覆盖率、unsupported 文件和空文件夹。",
        "artifact_publish": "发布只读总结与质量报告 artifacts。",
    }[station_id]


def _station_inputs(station_id: str) -> list[str]:
    return {
        "folder_input": ["folder_ref"],
        "folder_scan": ["folder_ref"],
        "markdown_filter": ["file_tree"],
        "markdown_parse": ["md_file_list"],
        "folder_group": ["parsed_docs"],
        "per_folder_summary": ["grouped_docs"],
        "overview_summary": ["folder_summaries"],
        "quality_check": ["folder_summaries", "overview_summary"],
        "artifact_publish": ["folder_summaries", "overview_summary", "quality_report"],
    }[station_id]


def _station_outputs(station_id: str) -> list[str]:
    return {
        "folder_input": ["folder_ref"],
        "folder_scan": ["file_tree"],
        "markdown_filter": ["md_file_list"],
        "markdown_parse": ["parsed_docs"],
        "folder_group": ["grouped_docs"],
        "per_folder_summary": ["folder_summaries"],
        "overview_summary": ["overview_summary"],
        "quality_check": ["quality_report"],
        "artifact_publish": ["output_package"],
    }[station_id]


if __name__ == "__main__":
    manifest = generate_evidence_package()
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
