"""MCP tools for V2.1 DevWiki code assets."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .code_assets.devwiki.persistence import devwiki_artifact_refs
from .code_assets.devwiki.service import (
    CodebaseDevWikiService,
    public_devwiki_index_payload,
    public_devwiki_page_payload,
)
from .code_assets.envelope import v2_error_envelope, v2_success_envelope


DEVWIKI_TOOL_NAMES = {
    "knowledge_devwiki_build",
    "knowledge_devwiki_read",
}


DEVWIKI_TOOL_SPECS = [
    {
        "name": "knowledge_devwiki_build",
        "description": "Build V2.1 DevWiki pages from accepted V2.0 codebase artifacts",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_id": {"type": "string"},
                "codebase_id": {"type": "string"},
                "snapshot_id": {"type": "string"},
            },
            "required": ["workspace_id", "codebase_id"],
        },
    },
    {
        "name": "knowledge_devwiki_read",
        "description": "List or read V2.1 DevWiki pages",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_id": {"type": "string"},
                "codebase_id": {"type": "string"},
                "page_slug": {"type": "string"},
            },
            "required": ["workspace_id", "codebase_id"],
        },
    },
]


def handle_devwiki_tool(
    name: str,
    arguments: dict[str, Any],
    *,
    blocked: Callable[..., dict[str, Any]],
    envelope: Callable[..., dict[str, Any]],
    ensure_workspace_meta: Callable[..., dict[str, Any]],
    resolve_workspace: Callable[[str | None, str | None], Path],
) -> dict[str, Any]:
    if name not in DEVWIKI_TOOL_NAMES:
        raise ValueError(f"Unknown DevWiki tool: {name}")
    workspace_path = resolve_workspace(arguments.get("workspace_id"), None)
    meta = ensure_workspace_meta(workspace_path)
    workspace_id = str(meta["workspace_id"])
    codebase_id = str(arguments.get("codebase_id") or "").strip()
    if not codebase_id:
        return blocked(
            workspace_id=workspace_id,
            message="codebase_id is required",
            next_actions=["knowledge_codebase_list"],
            code="invalid_codebase_id",
        )
    service = CodebaseDevWikiService(workspace_path, workspace_id=workspace_id)
    snapshot_id = str(arguments.get("snapshot_id") or "").strip() or None
    try:
        if name == "knowledge_devwiki_build":
            result = service.build_devwiki(codebase_id, snapshot_id=snapshot_id)
            index = public_devwiki_index_payload(result["index"])
            refs = index.get("artifact_refs", devwiki_artifact_refs(codebase_id))
            data = {"devwiki": index}
            return envelope(
                workspace_id=workspace_id,
                artifact_refs=refs,
                next_actions=["knowledge_devwiki_read"],
                data=_with_v2(
                    workspace_id=workspace_id,
                    codebase_id=codebase_id,
                    snapshot_id=str(index["snapshot_id"]),
                    data=data,
                    artifact_refs=refs,
                    next_actions=["knowledge_devwiki_read"],
                ),
            )
        page_slug = str(arguments.get("page_slug") or "").strip()
        if page_slug:
            page = service.read_page(codebase_id, page_slug)
            refs = page.get("artifact_refs", devwiki_artifact_refs(codebase_id, page_slug))
            data = {"page": public_devwiki_page_payload(page)}
            return envelope(
                workspace_id=workspace_id,
                artifact_refs=refs,
                data=_with_v2(
                    workspace_id=workspace_id,
                    codebase_id=codebase_id,
                    snapshot_id=str(page["snapshot_id"]),
                    data=data,
                    artifact_refs=refs,
                    unresolved=page.get("needs_review", []),
                ),
            )
        index = service.list_pages(codebase_id)
        refs = index.get("artifact_refs", devwiki_artifact_refs(codebase_id))
        data = {"devwiki": public_devwiki_index_payload(index)}
        return envelope(
            workspace_id=workspace_id,
            artifact_refs=refs,
            data=_with_v2(
                workspace_id=workspace_id,
                codebase_id=codebase_id,
                snapshot_id=str(index["snapshot_id"]),
                data=data,
                artifact_refs=refs,
            ),
        )
    except FileNotFoundError as exc:
        return _blocked_v2(
            envelope,
            workspace_id=workspace_id,
            codebase_id=codebase_id,
            snapshot_id=snapshot_id,
            code=_devwiki_error_code(str(exc)),
            message=_devwiki_error_message(str(exc)),
            next_actions=["knowledge_project_overview", "knowledge_devwiki_build"],
        )
    except ValueError as exc:
        return _blocked_v2(
            envelope,
            workspace_id=workspace_id,
            codebase_id=codebase_id,
            snapshot_id=snapshot_id,
            code=str(exc),
            message=str(exc),
            next_actions=["knowledge_codebase_describe"],
        )


def _with_v2(
    *,
    workspace_id: str,
    data: dict[str, Any],
    codebase_id: str | None = None,
    snapshot_id: str | None = None,
    artifact_refs: list[dict[str, Any]] | None = None,
    warnings: list[Any] | None = None,
    unresolved: list[Any] | None = None,
    next_actions: list[str] | None = None,
) -> dict[str, Any]:
    payload = dict(data)
    payload["v2"] = v2_success_envelope(
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        snapshot_id=snapshot_id,
        data=data,
        artifact_refs=artifact_refs,
        warnings=warnings,
        unresolved=unresolved,
        next_actions=next_actions,
    )
    return payload


def _blocked_v2(
    envelope: Callable[..., dict[str, Any]],
    *,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str | None,
    code: str,
    message: str,
    next_actions: list[str] | None = None,
) -> dict[str, Any]:
    return envelope(
        workspace_id=workspace_id,
        status="blocked",
        warnings=[message],
        next_actions=next_actions,
        data={
            "error": {"code": code, "message": message, "retryable": False},
            "v2": v2_error_envelope(
                workspace_id=workspace_id,
                codebase_id=codebase_id,
                snapshot_id=snapshot_id,
                code=code,
                message=message,
                next_actions=next_actions,
            ),
        },
    )


def _devwiki_error_code(error: str) -> str:
    if "SNAPSHOT_NOT_FOUND" in error:
        return "SNAPSHOT_NOT_FOUND"
    if "V20_ARTIFACT_MISSING" in error:
        return "V20_ARTIFACT_MISSING"
    if "DEVWIKI_PAGE_NOT_FOUND" in error:
        return "DEVWIKI_PAGE_NOT_FOUND"
    if "DEVWIKI_NOT_FOUND" in error:
        return "DEVWIKI_NOT_FOUND"
    return "DEVWIKI_ERROR"


def _devwiki_error_message(error: str) -> str:
    code = _devwiki_error_code(error)
    if code == "SNAPSHOT_NOT_FOUND":
        return "No codebase snapshot exists; create one before building DevWiki"
    if code == "V20_ARTIFACT_MISSING":
        return "Required V2.0 artifact is missing; build V2.0 artifacts before DevWiki"
    if code == "DEVWIKI_PAGE_NOT_FOUND":
        return "DevWiki page not found"
    if code == "DEVWIKI_NOT_FOUND":
        return "DevWiki has not been built"
    return error or "DevWiki request failed"
