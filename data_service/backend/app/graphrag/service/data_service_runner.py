"""Bridge runner for delegated data_service -> app.graphrag execution."""

from __future__ import annotations

import asyncio
import json
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict

try:
    from ..core.microsoft.adapter import MicrosoftGraphRAGAdapter
except Exception:  # pragma: no cover - standalone extraction keeps compat fallback only
    MicrosoftGraphRAGAdapter = None

from .data_service_bridge import materialize_workspace_graph_state


def run_data_service_execution_request(request_path: Path) -> Dict[str, Any]:
    """Execute one delegated GraphRAG request from data_service."""
    request_path = Path(request_path).resolve()
    request_payload = json.loads(request_path.read_text(encoding="utf-8"))
    workspace = Path(request_payload["workspace"]).resolve()
    graphrag_workspace = workspace / "graphrag"

    contract_path = Path(request_payload["input_contract_path"]).resolve()
    contract_payload = json.loads(contract_path.read_text(encoding="utf-8"))

    cli_health = check_graphrag_cli_health()
    if not cli_health["available"]:
        return _compat_result(
            workspace,
            contract_payload,
            request_path,
            cli_health=cli_health,
            reason="graphrag_cli_not_found",
        )
    if not cli_health["healthy"]:
        return _compat_result(
            workspace,
            contract_payload,
            request_path,
            cli_health=cli_health,
            reason="graphrag_cli_broken",
        )
    if MicrosoftGraphRAGAdapter is None:
        return _compat_result(
            workspace,
            contract_payload,
            request_path,
            cli_health=cli_health,
            reason="microsoft_graphrag_adapter_missing",
        )

    adapter = MicrosoftGraphRAGAdapter(session_id="data_service", workspace=graphrag_workspace)
    return _run_coro_sync(_execute_request(adapter, request_payload, request_path, workspace, contract_payload))


def _compat_result(
    workspace: Path,
    contract_payload: Dict[str, Any],
    request_path: Path,
    *,
    cli_health: Dict[str, Any],
    reason: str,
) -> Dict[str, Any]:
    compat_stats = materialize_workspace_graph_state(
        workspace,
        contract_payload,
        execution_owner="app.graphrag",
    )
    return {
        "status": "completed",
        "execution_mode": "app_graphrag_compat_materializer",
        "reason": reason,
        "workspace": str(workspace),
        "request_path": str(request_path),
        "cli_health": cli_health,
        "compat_state": compat_stats,
    }


def check_graphrag_cli_health() -> Dict[str, Any]:
    """Return a small, explicit health payload for the native GraphRAG CLI."""
    cli_path = shutil.which("graphrag")
    if cli_path is None:
        return {
            "available": False,
            "healthy": False,
            "reason": "graphrag_cli_not_found",
        }
    try:
        result = subprocess.run(
            [cli_path, "--help"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "available": True,
            "healthy": False,
            "reason": "graphrag_cli_healthcheck_timeout",
            "path": cli_path,
            "stdout": (exc.stdout or "")[-4000:] if isinstance(exc.stdout, str) else "",
            "stderr": (exc.stderr or "")[-4000:] if isinstance(exc.stderr, str) else "",
        }
    except OSError as exc:
        return {
            "available": True,
            "healthy": False,
            "reason": "graphrag_cli_healthcheck_error",
            "path": cli_path,
            "error": str(exc),
        }

    return {
        "available": True,
        "healthy": result.returncode == 0,
        "reason": "ok" if result.returncode == 0 else "graphrag_cli_healthcheck_failed",
        "path": cli_path,
        "returncode": result.returncode,
        "stdout": (result.stdout or "")[-4000:],
        "stderr": (result.stderr or "")[-4000:],
    }


def _run_coro_sync(coro):
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(asyncio.run, coro)
        return future.result()


async def _execute_request(
    adapter: MicrosoftGraphRAGAdapter,
    request_payload: Dict[str, Any],
    request_path: Path,
    workspace: Path,
    contract_payload: Dict[str, Any],
) -> Dict[str, Any]:
    returncode, stdout, stderr = await adapter._execute_command(
        "index",
        "--root",
        str(adapter.workspace),
    )
    if returncode != 0:
        compat_stats = materialize_workspace_graph_state(
            workspace,
            contract_payload,
            execution_owner="app.graphrag",
        )
        return {
            "status": "completed",
            "execution_mode": "app_graphrag_compat_after_cli_failure",
            "reason": "graphrag_index_failed",
            "workspace": str(workspace),
            "request_path": str(request_path),
            "cli_error": {
                "returncode": returncode,
                "stdout": stdout[-4000:],
                "stderr": stderr[-4000:],
            },
            "compat_state": compat_stats,
        }

    compat_stats = materialize_workspace_graph_state(
        workspace,
        contract_payload,
        execution_owner="app.graphrag",
    )
    return {
        "status": "completed",
        "workspace": str(workspace),
        "request_path": str(request_path),
        "returncode": returncode,
        "compat_state": compat_stats,
    }
