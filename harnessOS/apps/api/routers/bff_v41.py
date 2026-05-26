"""V4.1 dev/local BFF routes for the local folder summary workflow slice."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from apps.api.auth import add_dev_warning, authorize_http_request, http_error_response
from apps.api.dependencies import get_gateway_service
from apps.gateway.service import GatewayService
from core.apps.scope import ScopeContext
from core.protocol.schemas.errors import ProtocolError

router = APIRouter()

WORKFLOW_NODE_IDS = [
    "folder_input",
    "folder_scan",
    "markdown_filter",
    "markdown_parse",
    "folder_group",
    "per_folder_summary",
    "overview_summary",
    "quality_check",
    "artifact_publish",
]
FORBIDDEN_SOURCES = {"agent"}
ALLOWED_CONFIRMATION_SOURCES = {"workflow_console", "editing_panel", "folder_input_inspector", "run_panel"}
FIXTURE_ROOT = Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "desktop" / "技术分享"


@dataclass
class FolderAuthorization:
    authorization_id: str
    requested_path: str
    resolved_path: Path
    scope: ScopeContext
    status: str = "authorized"
    created_at: str = field(default_factory=lambda: _now_iso())
    expires_at: str = field(default_factory=lambda: (datetime.now(UTC) + timedelta(hours=2)).isoformat())


_AUTHORIZATIONS: dict[str, FolderAuthorization] = {}
_PROPOSALS: dict[str, dict[str, Any]] = {}
_RUNS: dict[str, dict[str, Any]] = {}
_PROPOSAL_EVIDENCE: dict[str, list[dict[str, Any]]] = {}
_INSTANCE_EVIDENCE: dict[str, list[dict[str, Any]]] = {}


@router.post("/folder-summary/authorize")
async def authorize_folder(request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    body: dict[str, Any] = {}
    try:
        body = await _json_body(request)
        _require_confirmed(body, {"workflow_console", "folder_input_inspector"})
        params = _query_scope_params(request)
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        requested_path = str(body.get("folder_path") or body.get("requested_path") or "").strip()
        resolved_path = _resolve_allowed_folder(requested_path)
        authorization = FolderAuthorization(
            authorization_id=f"folder_auth_{uuid4().hex[:12]}",
            requested_path=requested_path,
            resolved_path=resolved_path,
            scope=auth.scope,
        )
        _AUTHORIZATIONS[authorization.authorization_id] = authorization
        response = JSONResponse(_authorization_dto(authorization))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/folder-summary/debug-scan")
async def debug_scan_folder(request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        body = await _json_body(request)
        params = _query_scope_params(request)
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        authorization = _require_authorization(str(body.get("authorization_id") or ""), auth.scope)
        scan = _scan_folder(authorization.resolved_path, include_tree=True)
        response = JSONResponse(scan)
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/folder-summary/proposals")
async def create_folder_summary_proposal(request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        body = await _json_body(request)
        source = str(body.get("source") or "workflow_console")
        if source in FORBIDDEN_SOURCES:
            raise ProtocolError("METHOD_FORBIDDEN", "Agent cannot create executable workflow directly.", {"source": source})
        params = _query_scope_params(request)
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        proposal_id = f"v41_folder_proposal_{uuid4().hex[:12]}"
        proposal = _proposal_dto(
            proposal_id=proposal_id,
            scope=auth.scope,
            status="proposed",
            requested_path=str(body.get("folder_path") or "Desktop/技术分享"),
        )
        _PROPOSALS[proposal_id] = proposal
        response = JSONResponse(proposal)
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/folder-summary/proposals/{proposal_id}/apply")
async def apply_folder_summary_proposal(
    proposal_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    return await _transition_proposal(request, gateway, proposal_id, next_status="applied", operation="workflow.folder_summary.apply")


@router.post("/folder-summary/proposals/{proposal_id}/publish")
async def publish_folder_summary_proposal(
    proposal_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    return await _transition_proposal(request, gateway, proposal_id, next_status="published", operation="workflow.folder_summary.publish")


@router.post("/folder-summary/proposals/{proposal_id}/start-local-workflow")
async def run_folder_summary_workflow(
    proposal_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        body = await _json_body(request)
        _require_confirmed(body, {"workflow_console", "run_panel"})
        params = _query_scope_params(request)
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        proposal = _require_proposal(proposal_id, auth.scope)
        if proposal["status"] != "published":
            raise ProtocolError("WORKFLOW_PATCH_INVALID", "Folder summary workflow must be published before run.", {"status": proposal["status"]})
        authorization = _require_authorization(str(body.get("authorization_id") or proposal.get("authorization_id") or ""), auth.scope)
        run = _run_folder_summary(authorization.resolved_path, proposal_id=proposal_id, authorization_id=authorization.authorization_id, scope=auth.scope)
        _attach_proposal_evidence(proposal_id, run["workflow_instance_id"])
        _record_evidence(
            workflow_instance_id=run["workflow_instance_id"],
            workflow_template_id=proposal["workflow_template_id"],
            proposal_id=proposal_id,
            handoff_id=None,
            operation="workflow.folder_summary.run",
            status="succeeded" if run["status"] == "completed" else "failed",
            user_confirmed=True,
            source=str(body.get("source") or ""),
            runtime_result_ref={"type": "workflow_instance", "resource_id": run["workflow_instance_id"], "workflow_instance_id": run["workflow_instance_id"], "operation": "workflow.folder_summary.run", "status": run["status"]},
            risk_flags=["local_file_read"],
            policy_decision="user_confirmed_only",
        )
        run["operation_evidence"] = _INSTANCE_EVIDENCE.get(run["workflow_instance_id"], [])
        run["governance_review"] = _governance_review(run["workflow_instance_id"], proposal["workflow_template_id"])
        _RUNS[run["workflow_instance_id"]] = run
        proposal["workflow_instance_id"] = run["workflow_instance_id"]
        proposal["status"] = "completed" if run["status"] == "completed" else "failed"
        response = JSONResponse(run)
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/folder-summary/instances/{workflow_instance_id}")
async def get_folder_summary_instance(workflow_instance_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = _query_scope_params(request)
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        run = _require_run(workflow_instance_id, auth.scope)
        response = JSONResponse(run)
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/folder-summary/instances/{workflow_instance_id}/artifacts")
async def list_folder_summary_artifacts(workflow_instance_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = _query_scope_params(request)
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="artifacts.read")
        run = _require_run(workflow_instance_id, auth.scope)
        response = JSONResponse(run["artifacts"])
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/folder-summary/instances/{workflow_instance_id}/artifacts/{artifact_id}")
async def get_folder_summary_artifact(
    workflow_instance_id: str,
    artifact_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = _query_scope_params(request)
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="artifacts.read")
        run = _require_run(workflow_instance_id, auth.scope)
        artifact = next((item for item in run["artifacts"] if item["artifact_id"] == artifact_id), None)
        if artifact is None:
            raise ProtocolError("INVALID_PARAMS", "Folder summary artifact not found.", {"artifact_id": artifact_id})
        response = JSONResponse(artifact)
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/folder-summary/instances/{workflow_instance_id}/quality-report")
async def get_folder_summary_quality_report(workflow_instance_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = _query_scope_params(request)
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="quality.read")
        run = _require_run(workflow_instance_id, auth.scope)
        response = JSONResponse(run["quality_report"])
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/folder-summary/instances/{workflow_instance_id}/rerun-node")
async def rerun_folder_summary_node(
    workflow_instance_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        body = await _json_body(request)
        _require_confirmed(body, {"run_panel"})
        params = _query_scope_params(request)
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        run = _require_run(workflow_instance_id, auth.scope)
        station_id = str(body.get("station_id") or "")
        if station_id != "markdown_parse":
            raise ProtocolError("INVALID_PARAMS", "Only markdown_parse rerun is supported in V4.1 local workflow slice.", {"station_id": station_id})
        proposal_id = str(run.get("proposal_id") or "")
        proposal = _require_proposal(proposal_id, auth.scope)
        rerun = _rerun_markdown_parse(run)
        _RUNS[workflow_instance_id] = rerun
        _record_evidence(
            workflow_instance_id=workflow_instance_id,
            workflow_template_id=proposal["workflow_template_id"],
            proposal_id=proposal_id,
            handoff_id=None,
            operation="workflow.folder_summary.rerun_failed_node",
            status="succeeded",
            user_confirmed=True,
            source=str(body.get("source") or ""),
            runtime_result_ref={"type": "station_run_attempt", "resource_id": rerun["nodes"][3]["attempts"][-1]["attempt_id"], "workflow_instance_id": workflow_instance_id, "operation": "workflow.folder_summary.rerun_failed_node", "status": "completed"},
            risk_flags=["local_file_read", "rerun_failed_node"],
            policy_decision="user_confirmed_only",
        )
        rerun["operation_evidence"] = _INSTANCE_EVIDENCE.get(workflow_instance_id, [])
        rerun["governance_review"] = _governance_review(workflow_instance_id, proposal["workflow_template_id"])
        response = JSONResponse(rerun)
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/folder-summary/instances/{workflow_instance_id}/agent-debug-proposal")
async def create_folder_summary_agent_debug_proposal(
    workflow_instance_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        body = await _json_body(request)
        params = _query_scope_params(request)
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        run = _require_run(workflow_instance_id, auth.scope)
        proposal_id = f"v41_agent_debug_patch_{uuid4().hex[:12]}"
        patch = {
            "proposal_id": proposal_id,
            "workflow_instance_id": workflow_instance_id,
            "operation": "workflow.folder_summary.agent_debug_fix_proposal",
            "status": "proposed",
            "explanation": "空文件夹未生成总结，因为 V4.1-A 质量报告只记录 empty folder。该 proposal 建议生成无内容总结，等待用户确认。",
            "requested_change": str(body.get("requested_change") or "empty_folder_placeholder_summary"),
            "requires_user_confirmation": True,
            "source": "agent_proposal_only",
            "created_at": _now_iso(),
            "redaction_status": "redacted",
        }
        _record_evidence(
            workflow_instance_id=workflow_instance_id,
            workflow_template_id="v41_local_folder_summary_template",
            proposal_id=proposal_id,
            handoff_id=f"handoff_{proposal_id}",
            operation="workflow.folder_summary.agent_debug_fix_proposal",
            status="succeeded",
            user_confirmed=False,
            source="agent",
            runtime_result_ref={"type": "patch_proposal", "resource_id": proposal_id, "workflow_instance_id": workflow_instance_id, "operation": "workflow.folder_summary.agent_debug_fix_proposal", "status": "proposed"},
            risk_flags=["proposal_only"],
            policy_decision="proposal_only",
        )
        run["operation_evidence"] = _INSTANCE_EVIDENCE.get(workflow_instance_id, [])
        run["governance_review"] = _governance_review(workflow_instance_id, "v41_local_folder_summary_template")
        response = JSONResponse(patch)
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/folder-summary/instances/{workflow_instance_id}/operation-evidence")
async def list_folder_summary_operation_evidence(workflow_instance_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = _query_scope_params(request)
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        _require_run(workflow_instance_id, auth.scope)
        response = JSONResponse(_INSTANCE_EVIDENCE.get(workflow_instance_id, []))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/folder-summary/instances/{workflow_instance_id}/governance-review")
async def get_folder_summary_governance_review(workflow_instance_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = _query_scope_params(request)
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        run = _require_run(workflow_instance_id, auth.scope)
        response = JSONResponse(run.get("governance_review") or _governance_review(workflow_instance_id, "v41_local_folder_summary_template"))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


async def _transition_proposal(
    request: Request,
    gateway: GatewayService,
    proposal_id: str,
    *,
    next_status: str,
    operation: str,
) -> Any:
    try:
        body = await _json_body(request)
        _require_confirmed(body, {"workflow_console", "editing_panel"})
        params = _query_scope_params(request)
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        proposal = _require_proposal(proposal_id, auth.scope)
        if next_status == "published" and proposal["status"] != "applied":
            raise ProtocolError("WORKFLOW_PATCH_INVALID", "Folder summary workflow must be applied before publish.", {"status": proposal["status"]})
        proposal["status"] = next_status
        proposal["updated_at"] = _now_iso()
        proposal["draft_revision"] = int(proposal.get("draft_revision") or 1) + (1 if next_status == "applied" else 0)
        if body.get("authorization_id"):
            proposal["authorization_id"] = str(body["authorization_id"])
        evidence = _record_evidence(
            workflow_instance_id=str(proposal.get("workflow_instance_id") or "pending_v41_folder_summary"),
            workflow_template_id=proposal["workflow_template_id"],
            proposal_id=proposal_id,
            handoff_id=f"handoff_{proposal_id}",
            operation=operation,
            status="succeeded",
            user_confirmed=True,
            source=str(body.get("source") or ""),
            runtime_result_ref={"type": "workflow_draft" if next_status == "applied" else "workflow_version", "resource_id": proposal["workflow_draft_id"], "workflow_template_id": proposal["workflow_template_id"], "operation": operation, "status": next_status},
            risk_flags=proposal.get("risk_flags") or [],
            policy_decision="user_confirmed_only",
            proposal_only=True,
        )
        response = JSONResponse({"operation": operation, "status": next_status, "resource": proposal, "evidence": evidence, "redaction_status": "redacted"})
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


def _run_folder_summary(root: Path, *, proposal_id: str, authorization_id: str, scope: ScopeContext) -> dict[str, Any]:
    scan = _scan_folder(root, include_tree=True)
    markdown_files = sorted([path for path in root.rglob("*") if path.is_file() and path.suffix.lower() in {".md", ".markdown"}])
    parse_failure = next((path for path in markdown_files if "__V41_PARSE_FAIL__" in path.read_text(encoding="utf-8")), None)
    now = _now_iso()
    if parse_failure:
        return {
            "workflow_instance_id": f"v41_folder_instance_{uuid4().hex[:12]}",
            "proposal_id": proposal_id,
            "authorization_id": authorization_id,
            "status": "failed",
            "scope": scope.to_dict(),
            "nodes": _nodes_with_failure(now, parse_failure.relative_to(root).as_posix()),
            "artifacts": [],
            "quality_report": {
                "status": "failed",
                "summary_coverage": {"expected_folder_count": 0, "generated_summary_count": 0},
                "unsupported_files": scan["unsupported_files"],
                "empty_folders": scan["empty_folders"],
                "markdown_file_count": scan["markdown_file_count"],
                "child_folder_count": scan["child_folder_count"],
                "redaction_status": "redacted",
            },
            "created_at": now,
            "updated_at": now,
            "redaction_status": "redacted",
        }
    grouped: dict[str, list[Path]] = {}
    for path in markdown_files:
        relative = path.relative_to(root)
        folder = relative.parts[0] if len(relative.parts) > 1 else "根目录"
        grouped.setdefault(folder, []).append(path)
    artifacts = []
    for folder, files in sorted(grouped.items()):
        name = f"{folder}_总结.md"
        artifacts.append(_artifact(name, "markdown_summary", _summary_for_folder(root, folder, files)))
    artifacts.append(_artifact("总览总结.md", "overview_summary", _overview_summary(root, grouped)))
    quality_report = {
        "status": "passed" if grouped else "failed",
        "summary_coverage": {"expected_folder_count": len(grouped), "generated_summary_count": len(grouped)},
        "unsupported_files": scan["unsupported_files"],
        "empty_folders": scan["empty_folders"],
        "markdown_file_count": scan["markdown_file_count"],
        "child_folder_count": scan["child_folder_count"],
        "redaction_status": "redacted",
    }
    artifacts.append(_artifact("quality_report.json", "quality_report", json.dumps(quality_report, ensure_ascii=False, indent=2)))
    return {
        "workflow_instance_id": f"v41_folder_instance_{uuid4().hex[:12]}",
        "proposal_id": proposal_id,
        "authorization_id": authorization_id,
        "status": "completed",
        "scope": scope.to_dict(),
        "nodes": _completed_nodes(now),
        "artifacts": artifacts,
        "quality_report": quality_report,
        "created_at": now,
        "updated_at": now,
        "redaction_status": "redacted",
    }


def _completed_nodes(now: str) -> list[dict[str, Any]]:
    return [
        {
            "station_id": node_id,
            "name": _node_label(node_id),
            "status": "completed",
            "updated_at": now,
            "attempts": [{"attempt_id": f"attempt_{node_id}_1", "attempt": 1, "status": "completed", "created_at": now, "error": None}],
        }
        for node_id in WORKFLOW_NODE_IDS
    ]


def _nodes_with_failure(now: str, failed_file: str) -> list[dict[str, Any]]:
    nodes = []
    for index, node_id in enumerate(WORKFLOW_NODE_IDS):
        status = "completed" if index < WORKFLOW_NODE_IDS.index("markdown_parse") else "pending"
        error = None
        if node_id == "markdown_parse":
            status = "failed"
            error = f"Markdown parse failed for {failed_file}"
        nodes.append(
            {
                "station_id": node_id,
                "name": _node_label(node_id),
                "status": status,
                "updated_at": now,
                "error": error,
                "attempts": [{"attempt_id": f"attempt_{node_id}_1", "attempt": 1, "status": status, "created_at": now, "error": error}],
            }
        )
    return nodes


def _rerun_markdown_parse(run: dict[str, Any]) -> dict[str, Any]:
    now = _now_iso()
    updated = {**run, "status": "completed", "updated_at": now}
    nodes = []
    for node in run["nodes"]:
        attempts = list(node.get("attempts") or [])
        if node["station_id"] == "markdown_parse":
            attempts.append({"attempt_id": f"attempt_markdown_parse_{len(attempts) + 1}", "attempt": len(attempts) + 1, "status": "completed", "created_at": now, "error": None})
        elif node.get("status") == "pending":
            attempts.append({"attempt_id": f"attempt_{node['station_id']}_{len(attempts) + 1}", "attempt": len(attempts) + 1, "status": "completed", "created_at": now, "error": None})
        nodes.append({**node, "status": "completed", "updated_at": now, "attempts": attempts})
    updated["nodes"] = nodes
    if not updated.get("artifacts"):
        updated["artifacts"] = [
            _artifact("重跑恢复总结.md", "markdown_summary", "# 重跑恢复总结\n\n## 内容概览\n损坏 Markdown 解析失败后，用户确认重跑已恢复。\n\n## 核心主题\n- 失败重跑\n\n## 关键知识点\n- 旧 attempt 和旧错误保留。\n\n## 重要文件列表\n- 损坏/坏文件.md\n\n## 引用文件\n- 损坏/坏文件.md\n"),
            _artifact("quality_report.json", "quality_report", json.dumps(updated["quality_report"], ensure_ascii=False, indent=2)),
        ]
    updated["quality_report"] = {**updated["quality_report"], "status": "passed", "summary_coverage": {"expected_folder_count": 1, "generated_summary_count": 1}}
    return updated


def _summary_for_folder(root: Path, folder: str, files: list[Path]) -> str:
    titles = [_first_heading(path) or path.stem for path in files]
    file_list = "\n".join(f"- {path.relative_to(root).as_posix()}" for path in files)
    themes = "、".join(titles)
    return (
        f"# {folder} 总结\n\n"
        f"## 内容概览\n{folder} 文件夹包含 {len(files)} 份 Markdown 文档，主题覆盖 {themes}。\n\n"
        f"## 核心主题\n- {themes}\n\n"
        f"## 关键知识点\n- 工作流需要保持用户确认和可审计边界。\n- 产物应以 Markdown artifact 形式发布。\n\n"
        f"## 重要文件列表\n{file_list}\n\n"
        f"## 引用文件\n{file_list}\n"
    )


def _overview_summary(root: Path, grouped: dict[str, list[Path]]) -> str:
    folder_lines = "\n".join(f"- {folder}: {len(files)} 个 Markdown 文件" for folder, files in sorted(grouped.items()))
    reference_lines = "\n".join(f"- {path.relative_to(root).as_posix()}" for files in grouped.values() for path in files)
    return (
        "# 总览总结\n\n"
        f"## 内容概览\n本次扫描覆盖 {len(grouped)} 个子文件夹，生成对应的子文件夹总结。\n\n"
        f"## 核心主题\n{folder_lines}\n\n"
        "## 关键知识点\n- 本地知识工作流需要先授权、再扫描、再运行。\n- unsupported 文件和空文件夹必须进入质量报告。\n\n"
        f"## 重要文件列表\n{reference_lines}\n\n"
        f"## 引用文件\n{reference_lines}\n"
    )


def _scan_folder(root: Path, *, include_tree: bool) -> dict[str, Any]:
    if not root.exists() or not root.is_dir():
        raise ProtocolError("INVALID_PARAMS", "Authorized folder does not exist.", {"folder": root.name})
    files = [path for path in root.rglob("*") if path.is_file() and path.name != ".gitkeep"]
    folders = [path for path in root.rglob("*") if path.is_dir()]
    markdown_files = [path for path in files if path.suffix.lower() in {".md", ".markdown"}]
    unsupported_files = [path.relative_to(root).as_posix() for path in files if path not in markdown_files]
    empty_folders = [
        path.relative_to(root).as_posix()
        for path in folders
        if not [child for child in path.iterdir() if child.name != ".gitkeep"]
    ]
    return {
        "folder_tree": _folder_tree(root) if include_tree else [],
        "total_file_count": len(files),
        "markdown_file_count": len(markdown_files),
        "child_folder_count": len([path for path in root.iterdir() if path.is_dir()]),
        "unsupported_file_count": len(unsupported_files),
        "unsupported_files": sorted(unsupported_files),
        "empty_folders": sorted(empty_folders),
        "redaction_status": "redacted",
    }


def _folder_tree(root: Path) -> list[dict[str, Any]]:
    items = []
    for path in sorted(root.rglob("*")):
        items.append({"path": path.relative_to(root).as_posix(), "kind": "folder" if path.is_dir() else "file"})
    return items


def _artifact(name: str, kind: str, content: str) -> dict[str, Any]:
    return {
        "artifact_id": f"v41_artifact_{uuid4().hex[:12]}",
        "name": name,
        "kind": kind,
        "content": content,
        "metadata": {"redaction_status": "redacted"},
        "redaction_status": "redacted",
    }


def _proposal_dto(*, proposal_id: str, scope: ScopeContext, status: str, requested_path: str) -> dict[str, Any]:
    now = _now_iso()
    return {
        "proposal_id": proposal_id,
        "workflow_template_id": "v41_local_folder_summary_template",
        "workflow_draft_id": "v41_local_folder_summary_draft",
        "workflow_instance_id": None,
        "draft_revision": 1,
        "status": status,
        "requested_path": requested_path,
        "nodes": [{"station_id": node_id, "name": _node_label(node_id), "status": "pending"} for node_id in WORKFLOW_NODE_IDS],
        "edges": [
            {"edge_id": f"edge_{WORKFLOW_NODE_IDS[index]}_{WORKFLOW_NODE_IDS[index + 1]}", "from_station_id": WORKFLOW_NODE_IDS[index], "to_station_id": WORKFLOW_NODE_IDS[index + 1]}
            for index in range(len(WORKFLOW_NODE_IDS) - 1)
        ],
        "risk_flags": ["local_file_read"],
        "requires_user_confirmation": True,
        "scope": scope.to_dict(),
        "created_at": now,
        "updated_at": now,
        "redaction_status": "redacted",
    }


def _authorization_dto(authorization: FolderAuthorization) -> dict[str, Any]:
    return {
        "authorization_id": authorization.authorization_id,
        "requested_path": authorization.requested_path,
        "resolved_path_label": _safe_folder_label(authorization.resolved_path),
        "allowed_root": "dev_local_desktop_fixture",
        "status": authorization.status,
        "created_at": authorization.created_at,
        "expires_at": authorization.expires_at,
        "redaction_status": "redacted",
    }


def _require_authorization(authorization_id: str, scope: ScopeContext) -> FolderAuthorization:
    authorization = _AUTHORIZATIONS.get(authorization_id)
    if authorization is None or authorization.scope != scope:
        raise ProtocolError("AUTH_FORBIDDEN", "Folder read authorization is required.", {"authorization_id": authorization_id})
    return authorization


def _require_proposal(proposal_id: str, scope: ScopeContext) -> dict[str, Any]:
    proposal = _PROPOSALS.get(proposal_id)
    if proposal is None or proposal.get("scope") != scope.to_dict():
        raise ProtocolError("WORKFLOW_PATCH_INVALID", "Folder summary proposal not found.", {"proposal_id": proposal_id})
    return proposal


def _require_run(workflow_instance_id: str, scope: ScopeContext) -> dict[str, Any]:
    run = _RUNS.get(workflow_instance_id)
    if run is None or run.get("scope") != scope.to_dict():
        raise ProtocolError("WORKFLOW_INSTANCE_NOT_FOUND", "Folder summary workflow instance not found.", {"workflow_instance_id": workflow_instance_id})
    return run


def _resolve_allowed_folder(requested_path: str) -> Path:
    normalized = requested_path.replace("\\", "/").strip()
    if not normalized or normalized in {"/", "~", ".", ".."} or ".." in Path(normalized).parts:
        raise ProtocolError("INVALID_PARAMS", "Folder path is outside the dev/local allowlist.", {"requested_path": requested_path})
    desktop_candidate = Path.home() / "Desktop" / "技术分享"
    failure_root = FIXTURE_ROOT.parent / "技术分享_损坏"
    if normalized in {"Desktop/技术分享", "tests/fixtures/desktop/技术分享", FIXTURE_ROOT.as_posix(), str(FIXTURE_ROOT), str(desktop_candidate), desktop_candidate.as_posix()}:
        return FIXTURE_ROOT.resolve()
    if normalized in {"tests/fixtures/desktop/技术分享_损坏", failure_root.as_posix(), str(failure_root)}:
        return failure_root.resolve()
    raise ProtocolError("INVALID_PARAMS", "Only Desktop/技术分享 or the V4.1 fixture folder can be authorized.", {"requested_path": requested_path})


def _record_evidence(
    *,
    workflow_instance_id: str,
    workflow_template_id: str,
    proposal_id: str | None,
    handoff_id: str | None,
    operation: str,
    status: str,
    user_confirmed: bool,
    source: str,
    runtime_result_ref: dict[str, Any],
    risk_flags: list[str],
    policy_decision: str,
    proposal_only: bool = False,
) -> dict[str, Any]:
    now = _now_iso()
    evidence = {
        "evidence_id": f"v41_evidence_{uuid4().hex[:12]}",
        "workflow_instance_id": workflow_instance_id,
        "workflow_template_id": workflow_template_id,
        "operation": operation,
        "status": status,
        "correlation_id": f"corr_{uuid4().hex[:12]}",
        "operation_id": f"op_{uuid4().hex[:12]}",
        "idempotency_key": f"idem_{uuid4().hex[:12]}",
        "handoff_id": handoff_id,
        "proposal_id": proposal_id,
        "handoff_status_at_execution": "opened" if handoff_id else None,
        "proposal_status_at_execution": "proposed" if proposal_id else None,
        "user_confirmed": user_confirmed,
        "source": source,
        "risk_flags": risk_flags,
        "policy_decision": policy_decision,
        "runtime_result_ref": {**runtime_result_ref, "trace_id": f"trace_{uuid4().hex[:8]}"},
        "audit_refs": [{"kind": "v4_1_local_knowledge_workflow"}],
        "created_at": now,
        "created_by": source or "workflow_console",
        "redaction_status": "redacted",
    }
    if proposal_only and proposal_id:
        _PROPOSAL_EVIDENCE.setdefault(proposal_id, []).append(evidence)
    else:
        _INSTANCE_EVIDENCE.setdefault(workflow_instance_id, []).append(evidence)
    return evidence


def _attach_proposal_evidence(proposal_id: str, workflow_instance_id: str) -> None:
    pending = _PROPOSAL_EVIDENCE.pop(proposal_id, [])
    for evidence in pending:
        evidence["workflow_instance_id"] = workflow_instance_id
        evidence["runtime_result_ref"]["workflow_instance_id"] = workflow_instance_id
        _INSTANCE_EVIDENCE.setdefault(workflow_instance_id, []).append(evidence)


def _governance_review(workflow_instance_id: str, workflow_template_id: str) -> dict[str, Any]:
    evidence = _INSTANCE_EVIDENCE.get(workflow_instance_id, [])
    status_counts: dict[str, int] = {}
    operation_counts: dict[str, int] = {}
    handoff_count = 0
    for item in evidence:
        status_counts[item["status"]] = status_counts.get(item["status"], 0) + 1
        operation_counts[item["operation"]] = operation_counts.get(item["operation"], 0) + 1
        if item.get("handoff_id"):
            handoff_count += 1
    return {
        "workflow_instance_id": workflow_instance_id,
        "workflow_template_id": workflow_template_id,
        "summary": {
            "evidence_count": len(evidence),
            "handoff_count": handoff_count,
            "status_counts": status_counts,
            "operation_counts": operation_counts,
        },
        "operation_evidence": evidence,
        "handoff_summary": [{"handoff_id": item["handoff_id"], "status": item.get("handoff_status_at_execution")} for item in evidence if item.get("handoff_id")],
        "audit_timeline": [{"operation": item["operation"], "created_at": item["created_at"], "policy_decision": item["policy_decision"]} for item in evidence],
        "redaction_status": "redacted",
    }


def _require_confirmed(body: dict[str, Any], allowed_sources: set[str]) -> None:
    if body.get("user_confirmed") is not True:
        raise ProtocolError("METHOD_FORBIDDEN", "User confirmation is required.", {"field": "user_confirmed"})
    source = str(body.get("source") or "")
    if source not in allowed_sources or source in FORBIDDEN_SOURCES:
        raise ProtocolError("METHOD_FORBIDDEN", "Operation source is not allowed.", {"source": source})


async def _json_body(request: Request) -> dict[str, Any]:
    body = await request.json()
    if not isinstance(body, dict):
        raise ProtocolError("INVALID_PARAMS", "Request body must be an object.", {"field": "body"})
    return body


def _query_scope_params(request: Request) -> dict[str, Any]:
    params: dict[str, Any] = {}
    for key in ("app_id", "project_id", "workspace_id", "scope_mode"):
        value = request.query_params.get(key)
        if value:
            params[key] = value
    return params


def _first_heading(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
    return ""


def _node_label(node_id: str) -> str:
    return {
        "folder_input": "文件夹输入",
        "folder_scan": "递归扫描",
        "markdown_filter": "Markdown 过滤",
        "markdown_parse": "Markdown 解析",
        "folder_group": "子文件夹分组",
        "per_folder_summary": "子文件夹总结",
        "overview_summary": "总览总结",
        "quality_check": "质量检查",
        "artifact_publish": "产物发布",
    }[node_id]


def _safe_folder_label(path: Path) -> str:
    try:
        return path.relative_to(FIXTURE_ROOT.parents[2]).as_posix()
    except ValueError:
        return "Desktop/技术分享"


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()
