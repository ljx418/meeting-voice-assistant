"""V2.6 lightweight architecture inventory extractors.

These extractors intentionally collect deterministic hints only. They do not
claim full TypeScript semantics, runtime topology, or complete schema validity.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from data_service.mcp_common import now


SCHEMA_VERSION = "v2.6"
LANGUAGE_EXTENSIONS = {".js", ".jsx", ".ts", ".tsx", ".vue"}
CONFIG_FILENAMES = {
    "package.json",
    "pyproject.toml",
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "compose.yml",
    "compose.yaml",
    ".env.example",
    ".env.sample",
    ".env.template",
}
CONFIG_SUFFIXES = (".toml", ".json", ".yaml", ".yml")
CI_PATH_PARTS = (".github/workflows/", ".gitlab-ci.yml")
SCHEMA_HINT_SUFFIXES = (".sql", ".prisma", ".graphql", ".proto")
SECRET_HINTS = ("secret", "token", "api_key", "apikey", "password", "authorization", "credential", "private_key")
IMPORT_RE = re.compile(r"^\s*import\s+(?:[^'\"]+\s+from\s+)?[\"']([^\"']+)[\"']", re.MULTILINE)
REQUIRE_RE = re.compile(r"require\([\"']([^\"']+)[\"']\)")
EXPORT_RE = re.compile(r"^\s*export\s+(?:default\s+)?(?:class|function|const|let|var|interface|type)?\s*([A-Za-z0-9_$]*)", re.MULTILINE)
API_RE = re.compile(r"\b(fetch|axios\.(?:get|post|put|patch|delete)|useFetch)\s*\(")
ROUTE_RE = re.compile(r"\b(path|route|router|href|to)\s*[:=]\s*[\"']([^\"']+)[\"']")


def build_architecture_inventory(
    *,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    root: Path,
    files: list[dict[str, Any]],
    source_artifact_refs: list[dict[str, str]],
) -> dict[str, list[dict[str, Any]]]:
    included = [item for item in files if item.get("included") and isinstance(item.get("path"), str)]
    language_facts: list[dict[str, Any]] = []
    config_inventory: list[dict[str, Any]] = []
    deployment_inventory: list[dict[str, Any]] = []
    schema_inventory: list[dict[str, Any]] = []

    for item in included:
        rel = str(item["path"])
        path = root / rel
        suffix = Path(rel).suffix.lower()
        name = Path(rel).name
        text = _read_text(path)
        if text is None:
            continue
        if suffix in LANGUAGE_EXTENSIONS:
            language_facts.extend(_language_facts(workspace_id, codebase_id, snapshot_id, rel, text, source_artifact_refs))
        if _is_config_file(rel):
            config_inventory.extend(_config_items(workspace_id, codebase_id, snapshot_id, rel, text, source_artifact_refs))
        if _is_deployment_file(rel, name):
            deployment_inventory.extend(_deployment_items(workspace_id, codebase_id, snapshot_id, rel, text, source_artifact_refs))
        if _is_schema_file(rel, text):
            schema_inventory.extend(_schema_items(workspace_id, codebase_id, snapshot_id, rel, text, source_artifact_refs))

    return {
        "language_facts": _dedupe(language_facts, "fact_id"),
        "config_inventory": _dedupe(config_inventory, "item_id"),
        "deployment_inventory": _dedupe(deployment_inventory, "deployment_id"),
        "schema_inventory": _dedupe(schema_inventory, "schema_id"),
    }


def public_inventory_payload(items: list[dict[str, Any]], *, item_key: str, limit: int = 50) -> dict[str, Any]:
    counts: dict[str, int] = {}
    needs_review_count = 0
    for item in items:
        item_type = str(item.get(item_key) or item.get("fact_type") or item.get("schema_type") or "unknown")
        counts[item_type] = counts.get(item_type, 0) + 1
        if item.get("needs_review"):
            needs_review_count += 1
    return {
        "counts": dict(sorted(counts.items())),
        "total": len(items),
        "needs_review_count": needs_review_count,
        "sample": items[: max(1, min(limit, 50))],
        "truncated": len(items) > max(1, min(limit, 50)),
    }


def _language_facts(workspace_id: str, codebase_id: str, snapshot_id: str, rel: str, text: str, refs: list[dict[str, str]]) -> list[dict[str, Any]]:
    facts: list[dict[str, Any]] = []
    language = _language_for_path(rel)
    for imported in sorted(set([*IMPORT_RE.findall(text), *REQUIRE_RE.findall(text)])):
        facts.append(_fact(workspace_id, codebase_id, snapshot_id, rel, "import", imported, language, refs, confidence=0.82))
    for exported in sorted({match for match in EXPORT_RE.findall(text) if match}):
        facts.append(_fact(workspace_id, codebase_id, snapshot_id, rel, "export", exported, language, refs, confidence=0.72, needs_review=True))
    for match in API_RE.finditer(text):
        facts.append(_fact(workspace_id, codebase_id, snapshot_id, rel, "api_client_hint", match.group(1), language, refs, line=_line_of(text, match.start()), confidence=0.68, needs_review=True))
    if rel.endswith(".vue"):
        facts.append(_fact(workspace_id, codebase_id, snapshot_id, rel, "frontend_entrypoint", Path(rel).stem, language, refs, confidence=0.75, needs_review=True))
    for route_match in ROUTE_RE.finditer(text):
        target = route_match.group(2)
        if target.startswith(("/", "http", "#")):
            facts.append(_fact(workspace_id, codebase_id, snapshot_id, rel, "route_hint", target, language, refs, line=_line_of(text, route_match.start()), confidence=0.62, needs_review=True))
    return facts


def _config_items(workspace_id: str, codebase_id: str, snapshot_id: str, rel: str, text: str, refs: list[dict[str, str]]) -> list[dict[str, Any]]:
    name = Path(rel).name
    if name == "package.json":
        return _package_json_items(workspace_id, codebase_id, snapshot_id, rel, text, refs)
    if name == "pyproject.toml":
        return _pyproject_items(workspace_id, codebase_id, snapshot_id, rel, text, refs)
    if name.lower().startswith(".env"):
        return _env_example_items(workspace_id, codebase_id, snapshot_id, rel, text, refs)
    if "openapi" in rel.lower() or "swagger" in rel.lower():
        return [_config_item(workspace_id, codebase_id, snapshot_id, rel, "openapi_like_schema", "file", "openapi-like file detected", refs, confidence=0.7, needs_review=True)]
    return [_config_item(workspace_id, codebase_id, snapshot_id, rel, _config_type(rel), "file", "configuration file detected", refs, confidence=0.65, needs_review=True)]


def _package_json_items(workspace_id: str, codebase_id: str, snapshot_id: str, rel: str, text: str, refs: list[dict[str, str]]) -> list[dict[str, Any]]:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return [_config_item(workspace_id, codebase_id, snapshot_id, rel, "package_manifest", "parse_error", "json parse failed", refs, confidence=0.3, needs_review=True)]
    items: list[dict[str, Any]] = []
    for key in ("name", "type", "main", "module", "private"):
        if key in payload:
            items.append(_config_item(workspace_id, codebase_id, snapshot_id, rel, "package_manifest", key, _summarize_value(key, payload[key]), refs))
    for key, value in sorted(payload.items()):
        if _is_sensitive_key(str(key)):
            items.append(_config_item(workspace_id, codebase_id, snapshot_id, rel, "package_manifest", str(key), _summarize_value(str(key), value), refs, confidence=0.7, needs_review=True))
    for section in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
        deps = payload.get(section)
        if isinstance(deps, dict):
            items.append(_config_item(workspace_id, codebase_id, snapshot_id, rel, "package_manifest", section, f"{len(deps)} dependencies", refs))
    scripts = payload.get("scripts")
    if isinstance(scripts, dict):
        for script_name, script_value in sorted(scripts.items()):
            items.append(_config_item(workspace_id, codebase_id, snapshot_id, rel, "package_manifest", f"scripts.{script_name}", _summarize_value(script_name, script_value), refs, confidence=0.76))
    return items


def _pyproject_items(workspace_id: str, codebase_id: str, snapshot_id: str, rel: str, text: str, refs: list[dict[str, str]]) -> list[dict[str, Any]]:
    items = []
    for key in ("name", "version", "description", "requires-python"):
        match = re.search(rf"^\s*{re.escape(key)}\s*=\s*(.+)$", text, flags=re.MULTILINE)
        if match:
            items.append(_config_item(workspace_id, codebase_id, snapshot_id, rel, "python_project_config", key, _summarize_value(key, match.group(1).strip()), refs))
    if re.search(r"^\s*dependencies\s*=", text, flags=re.MULTILINE):
        items.append(_config_item(workspace_id, codebase_id, snapshot_id, rel, "python_project_config", "dependencies", "dependencies declared", refs))
    for section in re.findall(r"^\s*\[([^\]]+)\]", text, flags=re.MULTILINE):
        if section.startswith("tool.") or section.startswith("project"):
            items.append(_config_item(workspace_id, codebase_id, snapshot_id, rel, "python_project_config", f"section.{section}", "section present", refs, confidence=0.72))
    return items or [_config_item(workspace_id, codebase_id, snapshot_id, rel, "python_project_config", "file", "pyproject detected", refs, confidence=0.65, needs_review=True)]


def _env_example_items(workspace_id: str, codebase_id: str, snapshot_id: str, rel: str, text: str, refs: list[dict[str, str]]) -> list[dict[str, Any]]:
    items = []
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#") or "=" not in line:
            continue
        key = line.split("=", 1)[0].strip()
        if key:
            items.append(_config_item(workspace_id, codebase_id, snapshot_id, rel, "env_example", key, "[redacted-env-value]", refs, confidence=0.7, needs_review=_is_sensitive_key(key), redacted=True))
    return items


def _deployment_items(workspace_id: str, codebase_id: str, snapshot_id: str, rel: str, text: str, refs: list[dict[str, str]]) -> list[dict[str, Any]]:
    lower = rel.lower()
    items: list[dict[str, Any]] = []
    if Path(rel).name == "package.json":
        items.extend(_package_script_deployments(workspace_id, codebase_id, snapshot_id, rel, text, refs))
    if Path(rel).name == "Dockerfile" or lower.endswith("/dockerfile"):
        base = _first_match(text, r"^\s*FROM\s+([^\s]+)", "unknown")
        ports = re.findall(r"^\s*EXPOSE\s+(.+)$", text, flags=re.MULTILINE)
        items.append(_deployment_item(workspace_id, codebase_id, snapshot_id, rel, "dockerfile", "Dockerfile", base, "container_image", ports, [], refs))
    if any(token in lower for token in ("compose.yml", "compose.yaml", "docker-compose")):
        service_names = re.findall(r"^\s{2}([A-Za-z0-9_.-]+):\s*$", text, flags=re.MULTILINE)
        for service_name in service_names[:50]:
            items.append(_deployment_item(workspace_id, codebase_id, snapshot_id, rel, "docker_compose", service_name, "compose_service", service_name, re.findall(r"['\"]?([0-9]{2,5}):[0-9]{2,5}['\"]?", text), [], refs, confidence=0.68, needs_review=True))
    if ".github/workflows/" in rel:
        items.append(_deployment_item(workspace_id, codebase_id, snapshot_id, rel, "github_actions", Path(rel).stem, "ci_workflow", "github_actions", [], [], refs, confidence=0.72, needs_review=True))
    if lower.endswith((".yaml", ".yml")) and re.search(r"^\s*kind\s*:\s*(Deployment|Service|Ingress|StatefulSet|DaemonSet)", text, flags=re.MULTILINE):
        kind = _first_match(text, r"^\s*kind\s*:\s*([A-Za-z0-9_-]+)", "kubernetes")
        name = _first_match(text, r"^\s*name\s*:\s*([A-Za-z0-9_.-]+)", Path(rel).stem)
        items.append(_deployment_item(workspace_id, codebase_id, snapshot_id, rel, "kubernetes", name, kind, "kubernetes_manifest", re.findall(r"containerPort\s*:\s*([0-9]+)", text), [], refs, confidence=0.7, needs_review=True))
    return items


def _package_script_deployments(workspace_id: str, codebase_id: str, snapshot_id: str, rel: str, text: str, refs: list[dict[str, str]]) -> list[dict[str, Any]]:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return []
    scripts = payload.get("scripts")
    if not isinstance(scripts, dict):
        return []
    items: list[dict[str, Any]] = []
    for name, command in sorted(scripts.items()):
        if not isinstance(command, str):
            continue
        runtime_hint = "node_script"
        ports = re.findall(r"(?:--port\s+|PORT=)([0-9]{2,5})", command)
        if any(token in name.lower() for token in ("dev", "start", "serve", "preview", "build")):
            items.append(_deployment_item(workspace_id, codebase_id, snapshot_id, rel, "package_script", name, runtime_hint, command[:80], ports, [], refs, confidence=0.62, needs_review=True))
    return items


def _schema_items(workspace_id: str, codebase_id: str, snapshot_id: str, rel: str, text: str, refs: list[dict[str, str]]) -> list[dict[str, Any]]:
    lower = rel.lower()
    schema_type = "schema_like_file"
    signals: list[str] = []
    if "openapi" in lower or "swagger" in lower or re.search(r"^\s*openapi\s*:", text, flags=re.MULTILINE):
        schema_type = "openapi_like_schema"
        signals.append("openapi_hint")
    if "$schema" in text or re.search(r'"properties"\s*:', text):
        schema_type = "json_schema_hint"
        signals.append("json_schema_hint")
    if lower.endswith(".sql"):
        schema_type = "database_schema_hint"
        signals.extend(re.findall(r"\b(CREATE\s+TABLE|ALTER\s+TABLE|CREATE\s+INDEX)\b", text, flags=re.IGNORECASE)[:5])
    if lower.endswith(".prisma"):
        schema_type = "database_schema_hint"
        signals.extend(re.findall(r"^\s*(model|enum)\s+([A-Za-z0-9_]+)", text, flags=re.MULTILINE)[:5])
    if lower.endswith((".graphql", ".proto")):
        schema_type = "api_schema_hint"
        signals.append(Path(rel).suffix.lower().lstrip("."))
    if not signals:
        signals = ["schema-like file detected"]
    return [_schema_item(workspace_id, codebase_id, snapshot_id, rel, schema_type, Path(rel).stem, signals, refs)]


def _fact(workspace_id: str, codebase_id: str, snapshot_id: str, rel: str, fact_type: str, name: str, language: str, refs: list[dict[str, str]], *, line: int | None = None, confidence: float = 0.8, needs_review: bool = False) -> dict[str, Any]:
    line_no = line or _first_line_hint(rel)
    return {
        "schema_version": SCHEMA_VERSION,
        "fact_id": _stable_id("lang", rel, fact_type, name),
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "fact_type": fact_type,
        "language": language,
        "path": rel,
        "name": name,
        "signals": [fact_type],
        "evidence": [_evidence(rel, line_no)],
        "confidence": confidence,
        "needs_review": needs_review,
        "source_artifact_refs": refs,
        "created_at": now(),
    }


def _config_item(workspace_id: str, codebase_id: str, snapshot_id: str, rel: str, item_type: str, key: str, value_summary: str, refs: list[dict[str, str]], *, confidence: float = 0.8, needs_review: bool = False, redacted: bool | None = None) -> dict[str, Any]:
    is_redacted = bool(redacted) or _is_sensitive_key(key) or _contains_secret(value_summary)
    return {
        "schema_version": SCHEMA_VERSION,
        "item_id": _stable_id("config", rel, item_type, key),
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "item_type": item_type,
        "path": rel,
        "key": key,
        "value_summary": "[redacted]" if is_redacted else value_summary,
        "signals": [item_type, key],
        "evidence": [_evidence(rel, _line_hint_for_key(key))],
        "confidence": confidence,
        "needs_review": needs_review or is_redacted,
        "source_artifact_refs": refs,
        "redaction": {"applied": True, "redaction_count": 1 if is_redacted else 0},
        "created_at": now(),
    }


def _deployment_item(workspace_id: str, codebase_id: str, snapshot_id: str, rel: str, deployment_type: str, name: str, runtime_hint: str, service_hint: str, ports: list[str], dependencies: list[str], refs: list[dict[str, str]], *, confidence: float = 0.8, needs_review: bool = False) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "deployment_id": _stable_id("deployment", rel, deployment_type, name),
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "deployment_type": deployment_type,
        "path": rel,
        "name": name,
        "runtime_hint": runtime_hint,
        "service_hint": service_hint,
        "ports": sorted(set(str(port) for port in ports))[:20],
        "dependencies": dependencies[:50],
        "evidence": [_evidence(rel, 1)],
        "confidence": confidence,
        "needs_review": needs_review,
        "source_artifact_refs": refs,
        "created_at": now(),
    }


def _schema_item(workspace_id: str, codebase_id: str, snapshot_id: str, rel: str, schema_type: str, name: str, signals: list[Any], refs: list[dict[str, str]]) -> dict[str, Any]:
    clean_signals = [str(signal) for signal in signals]
    return {
        "schema_version": SCHEMA_VERSION,
        "schema_id": _stable_id("schema", rel, schema_type, name),
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "schema_type": schema_type,
        "path": rel,
        "name": name,
        "signals": clean_signals,
        "evidence": [_evidence(rel, 1)],
        "confidence": 0.66,
        "needs_review": True,
        "source_artifact_refs": refs,
        "created_at": now(),
    }


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return None
    except OSError:
        return None


def _is_config_file(rel: str) -> bool:
    lower = rel.lower()
    name = Path(rel).name
    return name in CONFIG_FILENAMES or any(part in lower for part in CI_PATH_PARTS) or ("openapi" in lower or "swagger" in lower) or lower.endswith(CONFIG_SUFFIXES) and any(token in lower for token in ("config", "settings", "schema"))


def _is_deployment_file(rel: str, name: str) -> bool:
    lower = rel.lower()
    return name in {"Dockerfile", "package.json"} or any(token in lower for token in ("docker-compose", "compose.yaml", "compose.yml", ".github/workflows/", "deployment.yaml", "deployment.yml", "k8s", "kubernetes"))


def _is_schema_file(rel: str, text: str) -> bool:
    lower = rel.lower()
    return lower.endswith(SCHEMA_HINT_SUFFIXES) or "openapi" in lower or "swagger" in lower or "$schema" in text or re.search(r"^\s*openapi\s*:", text, flags=re.MULTILINE) is not None


def _config_type(rel: str) -> str:
    lower = rel.lower()
    if "docker" in lower:
        return "container_config"
    if ".github/workflows/" in lower:
        return "ci_workflow"
    if lower.endswith((".yaml", ".yml")) and ("compose" in lower):
        return "compose_config"
    return "unknown_config"


def _language_for_path(rel: str) -> str:
    suffix = Path(rel).suffix.lower()
    return {".ts": "typescript", ".tsx": "typescript", ".js": "javascript", ".jsx": "javascript", ".vue": "vue"}.get(suffix, "unknown")


def _summarize_value(key: str, value: Any) -> str:
    if _is_sensitive_key(key):
        return "[redacted]"
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        return "[redacted]" if _contains_secret(value) else value[:120]
    if isinstance(value, list):
        return f"{len(value)} items"
    if isinstance(value, dict):
        return f"{len(value)} keys"
    return type(value).__name__


def _contains_secret(value: str) -> bool:
    lower = value.lower()
    return any(hint in lower for hint in SECRET_HINTS)


def _is_sensitive_key(key: str) -> bool:
    lower = key.lower()
    return any(hint in lower for hint in SECRET_HINTS)


def _stable_id(prefix: str, *parts: str) -> str:
    raw = ":".join(parts)
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}:{digest}"


def _evidence(path: str, line: int) -> dict[str, Any]:
    return {"path": path, "line_range": [max(1, line), max(1, line)]}


def _line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _line_hint_for_key(key: str) -> int:
    return 1 if not key else 1


def _first_line_hint(_rel: str) -> int:
    return 1


def _first_match(text: str, pattern: str, default: str) -> str:
    match = re.search(pattern, text, flags=re.MULTILINE)
    return match.group(1) if match else default


def _dedupe(items: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    deduped: dict[str, dict[str, Any]] = {}
    for item in items:
        item_id = str(item.get(key) or "")
        if item_id and item_id not in deduped:
            deduped[item_id] = item
    return [deduped[item_id] for item_id in sorted(deduped)]
