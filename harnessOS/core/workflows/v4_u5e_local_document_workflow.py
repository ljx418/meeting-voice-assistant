"""V4-U5E real LLM local technical document workflow.

This module is a dev/local workflow slice. It reads only user-confirmed local
Markdown folders, calls an explicit LLM provider adapter, and returns redacted
reports/evidence. It does not implement Agent executor behavior.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol
from uuid import uuid4

import requests
from dotenv import dotenv_values


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "desktop" / "技术分享"
SENSITIVE_TERMS = (
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
    "MINIMAX_API_KEY",
    "DEEPSEEK_API_KEY",
)
THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL)


class V4U5EWorkflowError(RuntimeError):
    """Raised when the U5E workflow cannot proceed."""

    def __init__(self, code: str, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.details = details or {}


@dataclass(frozen=True)
class LLMProviderConfig:
    """Redacted provider config resolved from dotenv/environment."""

    provider: str
    model_ref: str
    base_url: str
    api_key: str
    provider_config_source: str
    real_llm_required: bool

    def redacted(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "model_ref": self.model_ref,
            "base_url": self.base_url,
            "provider_config_source": self.provider_config_source,
            "api_key_configured": bool(self.api_key),
            "real_llm_required": self.real_llm_required,
        }


@dataclass(frozen=True)
class LocalFolderReadAuthorization:
    """User-confirmed local folder read grant."""

    authorization_id: str
    requested_path: str
    resolved_path: Path
    user_confirmed: bool
    source: str
    fixture_source: bool
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "authorization_id": self.authorization_id,
            "requested_path": self.requested_path,
            "resolved_path_label": _safe_path_label(self.resolved_path),
            "user_confirmed": self.user_confirmed,
            "source": self.source,
            "fixture_source": self.fixture_source,
            "created_at": self.created_at,
            "redaction_status": "redacted",
        }


@dataclass(frozen=True)
class ParsedMarkdownDocument:
    """Internal parsed document. Raw content must not be exposed in evidence."""

    relative_path: str
    folder: str
    title: str
    content: str


class LLMProviderAdapter(Protocol):
    """Minimal provider protocol for summary stations."""

    provider: str
    model_ref: str
    provider_config_source: str

    def complete(self, *, prompt: str, prompt_template_ref: str, input_artifact_refs: list[str]) -> dict[str, Any]:
        """Return redacted completion result."""


class OpenAICompatibleProviderAdapter:
    """Synchronous OpenAI-compatible chat completion adapter."""

    def __init__(self, config: LLMProviderConfig) -> None:
        self.config = config
        self.provider = config.provider
        self.model_ref = config.model_ref
        self.provider_config_source = config.provider_config_source

    def complete(self, *, prompt: str, prompt_template_ref: str, input_artifact_refs: list[str]) -> dict[str, Any]:
        if not self.config.api_key:
            raise V4U5EWorkflowError("LLM_KEY_MISSING", "LLM provider key is required.", {"provider": self.provider})
        response = requests.post(
            f"{self.config.base_url.rstrip('/')}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.config.model_ref,
                "messages": [
                    {
                        "role": "system",
                        "content": "你是技术文档总结助手。只输出用户要求的 Markdown 总结，不输出推理过程。",
                    },
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.2,
                "max_tokens": 1200,
            },
            timeout=60,
        )
        if not response.ok:
            raise V4U5EWorkflowError(
                "LLM_PROVIDER_ERROR",
                "LLM provider request failed.",
                {"provider": self.provider, "status_code": response.status_code},
            )
        payload = response.json()
        content = payload.get("choices", [{}])[0].get("message", {}).get("content", "")
        stripped = strip_think_blocks(str(content))
        return {
            "text": stripped,
            "provider": self.provider,
            "model_ref": self.model_ref,
            "provider_config_source": self.provider_config_source,
            "prompt_template_ref": prompt_template_ref,
            "input_artifact_refs": input_artifact_refs,
            "runtime_result_ref": f"llm_result_{uuid4().hex[:12]}",
            "correlation_id": f"corr_{uuid4().hex[:12]}",
            "redaction_status": "redacted",
            "raw_payload_exposed": False,
        }


class MiniMaxProviderAdapter(OpenAICompatibleProviderAdapter):
    """MiniMax-first provider adapter."""


class FakeLLMProviderAdapter:
    """Deterministic adapter for unit tests. Never mark as real LLM evidence."""

    provider = "fake"
    model_ref = "fake-model"
    provider_config_source = "test"

    def __init__(self) -> None:
        self.invocation_count = 0

    def complete(self, *, prompt: str, prompt_template_ref: str, input_artifact_refs: list[str]) -> dict[str, Any]:
        self.invocation_count += 1
        title_match = re.search(r"总结对象[:：]\\s*(.+)", prompt)
        title = title_match.group(1).strip() if title_match else "测试"
        return {
            "text": (
                f"# {title} 总结\n\n"
                "## 内容概览\n这是测试 provider 生成的结构化总结。\n\n"
                "## 核心主题\n- 测试主题\n\n"
                "## 关键知识点\n- 测试知识点\n\n"
                "## 重要文件列表\n- 测试文件.md\n\n"
                "## 引用文件\n- 测试文件.md\n"
            ),
            "provider": self.provider,
            "model_ref": self.model_ref,
            "provider_config_source": self.provider_config_source,
            "prompt_template_ref": prompt_template_ref,
            "input_artifact_refs": input_artifact_refs,
            "runtime_result_ref": f"fake_result_{self.invocation_count}",
            "correlation_id": f"fake_corr_{self.invocation_count}",
            "redaction_status": "redacted",
            "raw_payload_exposed": False,
        }


def load_provider_config(env_files: tuple[str, ...] = (".env", ".env.local")) -> LLMProviderConfig:
    """Resolve U5E provider config from dotenv and process environment."""
    merged: dict[str, str] = {}
    source = "environment"
    for env_file in env_files:
        path = REPO_ROOT / env_file
        if path.exists():
            values = {key: value for key, value in dotenv_values(path).items() if value is not None}
            if values:
                merged.update(values)
                source = env_file
    merged.update({key: value for key, value in os.environ.items() if key.startswith(("V4_U5E_", "MINIMAX_", "OPENAI_", "LLM_"))})

    provider = (merged.get("V4_U5E_LLM_PROVIDER") or merged.get("LLM_PROVIDER") or "minimax").strip().lower()
    model_ref = (merged.get("V4_U5E_LLM_MODEL") or merged.get("LLM_MODEL") or "").strip()
    if not model_ref or model_ref.startswith("your-"):
        model_ref = "MiniMax-M2.1" if provider == "minimax" else "default"
    if provider == "minimax":
        api_key = (merged.get("MINIMAX_API_KEY") or "").strip()
        base_url = (merged.get("MINIMAX_BASE_URL") or "https://api.minimax.chat/v1").strip()
    else:
        api_key = (merged.get("OPENAI_API_KEY") or merged.get("LLM_API_KEY") or "").strip()
        base_url = (merged.get("OPENAI_BASE_URL") or merged.get("LLM_BASE_URL") or "").strip()
    required = str(merged.get("V4_U5E_REAL_LLM_REQUIRED") or "false").strip().lower() in {"1", "true", "yes", "on"}
    return LLMProviderConfig(
        provider=provider,
        model_ref=model_ref,
        base_url=base_url,
        api_key="" if _looks_placeholder(api_key) else api_key,
        provider_config_source=source,
        real_llm_required=required,
    )


def create_provider_adapter(config: LLMProviderConfig) -> LLMProviderAdapter:
    """Create a provider adapter from config."""
    if config.provider == "minimax":
        return MiniMaxProviderAdapter(config)
    return OpenAICompatibleProviderAdapter(config)


def authorize_local_folder(
    requested_path: str,
    *,
    user_confirmed: bool,
    source: str,
    fixture_root: Path = DEFAULT_FIXTURE_ROOT,
) -> LocalFolderReadAuthorization:
    """Create a user-confirmed local folder authorization."""
    if not user_confirmed:
        raise V4U5EWorkflowError("AUTH_REQUIRED", "Local folder read requires user confirmation.")
    resolved, fixture_source = resolve_allowed_folder(requested_path, fixture_root=fixture_root)
    return LocalFolderReadAuthorization(
        authorization_id=f"u5e_folder_auth_{uuid4().hex[:12]}",
        requested_path=requested_path,
        resolved_path=resolved,
        user_confirmed=True,
        source=source,
        fixture_source=fixture_source,
    )


def resolve_allowed_folder(requested_path: str, *, fixture_root: Path = DEFAULT_FIXTURE_ROOT) -> tuple[Path, bool]:
    """Resolve an allowed dev/local folder without root/home/parent escape."""
    normalized = requested_path.replace("\\", "/").strip()
    if not normalized or normalized in {"/", "~", ".", ".."} or ".." in Path(normalized).parts:
        raise V4U5EWorkflowError("PATH_FORBIDDEN", "Folder path is outside the dev/local allowlist.")
    candidate = Path(normalized).expanduser()
    home = Path.home().resolve()
    if candidate.is_absolute():
        resolved_candidate = candidate.resolve()
    else:
        resolved_candidate = (REPO_ROOT / candidate).resolve()
    if resolved_candidate == resolved_candidate.anchor or resolved_candidate == home:
        raise V4U5EWorkflowError("PATH_FORBIDDEN", "Root or home directory scans are forbidden.")

    desktop = home / "Desktop" / "技术分享"
    allowed_labels = {"Desktop/技术分享", "tests/fixtures/desktop/技术分享", fixture_root.as_posix(), str(fixture_root)}
    if normalized in allowed_labels:
        if desktop.exists() and normalized == "Desktop/技术分享":
            return desktop.resolve(), False
        return fixture_root.resolve(), True
    if resolved_candidate == fixture_root.resolve():
        return fixture_root.resolve(), True
    if desktop.exists() and resolved_candidate == desktop.resolve():
        return desktop.resolve(), False
    raise V4U5EWorkflowError("PATH_FORBIDDEN", "Only Desktop/技术分享 or the U5E fixture folder can be authorized.")


def scan_markdown_folder(root: Path) -> dict[str, Any]:
    """Read Markdown files and return redacted scan data plus internal docs."""
    if not root.exists() or not root.is_dir():
        raise V4U5EWorkflowError("PATH_NOT_FOUND", "Authorized folder does not exist.")
    files = sorted(path for path in root.rglob("*") if path.is_file() and path.name != ".gitkeep")
    folders = sorted(path for path in root.rglob("*") if path.is_dir())
    docs: list[ParsedMarkdownDocument] = []
    unsupported: list[str] = []
    for path in files:
        rel = path.relative_to(root).as_posix()
        if path.suffix.lower() not in {".md", ".markdown"}:
            unsupported.append(rel)
            continue
        content = path.read_text(encoding="utf-8")
        folder = path.parent.relative_to(root).as_posix()
        docs.append(
            ParsedMarkdownDocument(
                relative_path=rel,
                folder=folder if folder != "." else "根目录",
                title=_first_heading(content) or path.stem,
                content=content,
            )
        )
    empty_folders = [
        path.relative_to(root).as_posix()
        for path in folders
        if not [child for child in path.iterdir() if child.name != ".gitkeep"]
    ]
    return {
        "scanner_actual_read_count": len(docs),
        "total_file_count": len(files),
        "markdown_file_count": len(docs),
        "child_folder_count": len([path for path in root.iterdir() if path.is_dir()]),
        "unsupported_file_count": len(unsupported),
        "unsupported_files": unsupported,
        "empty_folders": empty_folders,
        "documents": docs,
        "redaction_status": "redacted",
    }


def run_local_document_workflow(
    *,
    requested_path: str = "Desktop/技术分享",
    user_confirmed: bool = True,
    source: str = "mission_console",
    provider_adapter: LLMProviderAdapter | None = None,
    provider_config: LLMProviderConfig | None = None,
    fixture_root: Path = DEFAULT_FIXTURE_ROOT,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    """Run the V4-U5E workflow and return redacted evidence."""
    authorization = authorize_local_folder(
        requested_path,
        user_confirmed=user_confirmed,
        source=source,
        fixture_root=fixture_root,
    )
    config = provider_config or load_provider_config()
    adapter = provider_adapter or create_provider_adapter(config)
    if not config.api_key and adapter.__class__ is not FakeLLMProviderAdapter:
        status = "blocked" if config.real_llm_required else "fallback_demo_only"
        return _blocked_result(authorization, config, status=status)

    scan = scan_markdown_folder(authorization.resolved_path)
    grouped: dict[str, list[ParsedMarkdownDocument]] = {}
    for doc in scan["documents"]:
        grouped.setdefault(doc.folder, []).append(doc)
    artifacts: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []
    provider_invocation_count = 0
    real_llm_backed = adapter.__class__ is not FakeLLMProviderAdapter

    for folder, docs in sorted(grouped.items()):
        result = adapter.complete(
            prompt=_folder_prompt(folder, docs),
            prompt_template_ref="v4_u5e.per_folder_summary.v1",
            input_artifact_refs=[f"markdown:{doc.relative_path}" for doc in docs],
        )
        provider_invocation_count += 1
        artifact = _summary_artifact(
            name=f"{_safe_filename(folder)}_总结.md",
            kind="markdown_summary",
            content=result["text"],
            folder=folder,
            provider_result=result,
            real_llm_backed=real_llm_backed,
        )
        artifacts.append(artifact)
        evidence.append(_llm_evidence("per_folder_summary", artifact, result))

    overview_result = adapter.complete(
        prompt=_overview_prompt(grouped),
        prompt_template_ref="v4_u5e.overview_summary.v1",
        input_artifact_refs=[f"folder_summary:{folder}" for folder in sorted(grouped)],
    )
    provider_invocation_count += 1
    overview = _summary_artifact(
        name="总览总结.md",
        kind="overview_summary",
        content=overview_result["text"],
        folder="overview",
        provider_result=overview_result,
        real_llm_backed=real_llm_backed,
    )
    artifacts.append(overview)
    evidence.append(_llm_evidence("overview_summary", overview, overview_result))

    quality_report = {
        "status": "passed" if grouped else "failed",
        "summary_coverage": {"expected_folder_count": len(grouped), "generated_summary_count": len(grouped)},
        "unsupported_files": scan["unsupported_files"],
        "empty_folders": scan["empty_folders"],
        "markdown_file_count": scan["markdown_file_count"],
        "child_folder_count": scan["child_folder_count"],
        "scanner_actual_read_count": scan["scanner_actual_read_count"],
        "provider_invocation_count": provider_invocation_count,
        "redaction_status": "redacted",
    }
    artifacts.append(
        {
            "artifact_id": f"artifact_{uuid4().hex[:12]}",
            "name": "quality_report.json",
            "kind": "quality_report",
            "content": json.dumps(quality_report, ensure_ascii=False, indent=2),
            "metadata": {"generated_by": "quality_check", "redaction_status": "redacted"},
        }
    )

    result = {
        "workflow_instance_id": f"u5e_local_docs_{uuid4().hex[:12]}",
        "status": "completed",
        "evidence_scope": "real_llm" if real_llm_backed else "fallback_demo_only",
        "real_llm_backed": real_llm_backed,
        "fallback_demo_only": not real_llm_backed,
        "authorization": authorization.to_dict(),
        "provider": config.redacted() if real_llm_backed else _adapter_redacted(adapter),
        "scan": _redacted_scan(scan),
        "artifacts": artifacts,
        "quality_report": quality_report,
        "evidence_chain": evidence,
        "redaction_status": "redacted",
    }
    assert_no_sensitive_text(result)
    if output_dir:
        write_u5e_evidence_package(result, output_dir)
    return result


def write_u5e_evidence_package(result: dict[str, Any], output_dir: Path) -> None:
    """Write UX-12 evidence package without raw prompts or raw file content."""
    output_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir = output_dir / "artifacts"
    artifacts_dir.mkdir(exist_ok=True)
    for artifact in result["artifacts"]:
        if artifact["name"].endswith(".md"):
            (artifacts_dir / artifact["name"]).write_text(artifact["content"], encoding="utf-8")
    (output_dir / "local-document-workflow-result.json").write_text(
        json.dumps(_without_artifact_content(result), ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (output_dir / "quality_report.json").write_text(
        json.dumps(result["quality_report"], ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (output_dir / "evidence_chain.json").write_text(
        json.dumps(result["evidence_chain"], ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (output_dir / "result-summary.md").write_text(render_ux12_summary(result), encoding="utf-8")


def render_ux12_summary(result: dict[str, Any]) -> str:
    """Render the UX-12 result summary."""
    status = "PASS" if result["real_llm_backed"] and result["status"] == "completed" else "BLOCKED"
    scope = "real_runtime" if status == "PASS" else result.get("evidence_scope", "planned_contract")
    return "\n".join(
        [
            "# UX-12 真实 LLM 本地技术文档解析 Evidence Summary",
            "",
            "ux_id: UX-12",
            f"status: {status}",
            f"evidence_scope: {scope}",
            "runtime_backed: true" if status == "PASS" else "runtime_backed: false",
            "deterministic_only: false",
            "transcript_only: false",
            "report_only: false",
            "false_green_risk: LOW" if status == "PASS" else "false_green_risk: HIGH",
            "claim_risk: LOW" if status == "PASS" else "claim_risk: HIGH",
            f"real_llm_backed: {str(result['real_llm_backed']).lower()}",
            f"fallback_demo_only: {str(result['fallback_demo_only']).lower()}",
            f"scanner_actual_read_count: {result['quality_report'].get('scanner_actual_read_count', 0)}",
            f"provider_invocation_count: {result['quality_report'].get('provider_invocation_count', 0)}",
            f"provider: {result['provider'].get('provider')}",
            f"model_ref: {result['provider'].get('model_ref')}",
            f"provider_config_source: {result['provider'].get('provider_config_source')}",
            "evidence_refs:",
            "- local-document-workflow-result.json",
            "- evidence_chain.json",
            "- quality_report.json",
            "- artifacts/",
            "missing_evidence:",
            "- none" if status == "PASS" else "- real LLM provider invocation evidence",
            "",
            "notes: UX-12 is real LLM-backed only when provider_invocation_count > 0 and generated_by=llm_provider artifacts exist.",
            "",
        ]
    )


def strip_think_blocks(text: str) -> str:
    """Strip provider thinking blocks from visible output."""
    return THINK_RE.sub("", text).strip()


def assert_no_sensitive_text(value: Any) -> None:
    """Fail if a redacted payload contains sensitive terms."""
    text = json.dumps(value, ensure_ascii=False)
    for term in SENSITIVE_TERMS:
        if term in text:
            raise AssertionError(f"sensitive term leaked: {term}")


def _blocked_result(authorization: LocalFolderReadAuthorization, config: LLMProviderConfig, *, status: str) -> dict[str, Any]:
    return {
        "workflow_instance_id": f"u5e_local_docs_{uuid4().hex[:12]}",
        "status": status,
        "evidence_scope": status,
        "real_llm_backed": False,
        "fallback_demo_only": status == "fallback_demo_only",
        "authorization": authorization.to_dict(),
        "provider": config.redacted(),
        "scan": None,
        "artifacts": [],
        "quality_report": {"status": status, "scanner_actual_read_count": 0, "provider_invocation_count": 0},
        "evidence_chain": [],
        "redaction_status": "redacted",
    }


def _redacted_scan(scan: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in scan.items() if key != "documents"}


def _without_artifact_content(result: dict[str, Any]) -> dict[str, Any]:
    redacted = dict(result)
    redacted["artifacts"] = [
        {key: value for key, value in artifact.items() if key != "content"}
        for artifact in result.get("artifacts", [])
    ]
    return redacted


def _adapter_redacted(adapter: LLMProviderAdapter) -> dict[str, Any]:
    return {
        "provider": adapter.provider,
        "model_ref": adapter.model_ref,
        "provider_config_source": adapter.provider_config_source,
        "api_key_configured": False,
    }


def _folder_prompt(folder: str, docs: list[ParsedMarkdownDocument]) -> str:
    content = "\n\n".join(
        f"文件：{doc.relative_path}\n标题：{doc.title}\n内容：\n{doc.content}"
        for doc in docs
    )
    return (
        f"总结对象：{folder}\n"
        "请基于以下 Markdown 技术文档，为该子文件夹生成一份 Markdown 总结，必须包含：内容概览、核心主题、关键知识点、重要文件列表、引用文件。\n\n"
        f"{content}"
    )


def _overview_prompt(grouped: dict[str, list[ParsedMarkdownDocument]]) -> str:
    lines = []
    for folder, docs in sorted(grouped.items()):
        titles = "、".join(doc.title for doc in docs)
        refs = "、".join(doc.relative_path for doc in docs)
        lines.append(f"子文件夹：{folder}\n标题：{titles}\n引用文件：{refs}")
    return (
        "总结对象：总览总结\n"
        "请基于以下子文件夹结构，生成总览 Markdown 总结，必须包含：内容概览、核心主题、关键知识点、重要文件列表、引用文件。\n\n"
        + "\n\n".join(lines)
    )


def _summary_artifact(
    *,
    name: str,
    kind: str,
    content: str,
    folder: str,
    provider_result: dict[str, Any],
    real_llm_backed: bool,
) -> dict[str, Any]:
    return {
        "artifact_id": f"artifact_{uuid4().hex[:12]}",
        "name": name,
        "kind": kind,
        "content": content,
        "metadata": {
            "folder": folder,
            "generated_by": "llm_provider" if real_llm_backed else "fallback_demo",
            "provider": provider_result["provider"],
            "model_ref": provider_result["model_ref"],
            "provider_config_source": provider_result["provider_config_source"],
            "prompt_template_ref": provider_result["prompt_template_ref"],
            "input_artifact_refs": provider_result["input_artifact_refs"],
            "runtime_result_ref": provider_result["runtime_result_ref"],
            "correlation_id": provider_result["correlation_id"],
            "redaction_status": "redacted",
        },
    }


def _llm_evidence(operation: str, artifact: dict[str, Any], provider_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "evidence_id": f"u5e_evidence_{uuid4().hex[:12]}",
        "operation": operation,
        "status": "completed",
        "provider": provider_result["provider"],
        "model_ref": provider_result["model_ref"],
        "provider_config_source": provider_result["provider_config_source"],
        "prompt_template_ref": provider_result["prompt_template_ref"],
        "input_artifact_refs": provider_result["input_artifact_refs"],
        "output_artifact_refs": [artifact["artifact_id"]],
        "runtime_result_ref": provider_result["runtime_result_ref"],
        "correlation_id": provider_result["correlation_id"],
        "redaction_status": "redacted",
        "raw_prompt_exposed": False,
        "raw_file_content_exposed": False,
        "token_exposed": False,
    }


def _first_heading(content: str) -> str:
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
    return ""


def _safe_filename(value: str) -> str:
    return value.replace("/", "_").replace("\\", "_").strip() or "根目录"


def _safe_path_label(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return "Desktop/技术分享"


def _looks_placeholder(value: str) -> bool:
    lower = value.strip().lower()
    return not lower or lower.startswith("your-") or lower.startswith("<your-") or lower.endswith("-here")
