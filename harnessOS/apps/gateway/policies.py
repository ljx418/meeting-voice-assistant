"""Policy evaluation for gateway-side governance decisions."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any, Optional


@dataclass(frozen=True)
class PolicyDecision:
    """Result of evaluating one requested operation."""

    requires_approval: bool
    action: str = "none"
    risk_level: str = "low"
    reason: str = "No policy matched."
    matched_rule: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def model_dump(self) -> dict[str, Any]:
        """Return a JSON-serializable decision payload."""
        return asdict(self)


class PolicyEvaluator:
    """Small deterministic policy engine for Phase 2 governance."""

    _READ_ONLY_TOOLS = {
        "workspace_ls",
        "workspace_read_file",
        "kb_search",
    }
    _APPROVAL_TOOLS = {
        "workspace_write_file": ("workspace.write", "high"),
        "workspace_mkdir": ("workspace.mkdir", "medium"),
        "kb_ingest": ("knowledge.ingest", "medium"),
        "artifact_save": ("artifact.write", "medium"),
    }
    _WRITE_INTENT_RE = re.compile(
        r"(写入|写到|写文件|保存到|保存为|创建文件|覆盖|修改文件|新增文件|"
        r"write\s+(?:a\s+)?file|save\s+(?:to|as)|create\s+(?:a\s+)?file|overwrite|modify\s+(?:a\s+)?file)",
        re.IGNORECASE,
    )
    _DESTRUCTIVE_INTENT_RE = re.compile(
        r"(删除|移除|清空|delete|remove|wipe|truncate)",
        re.IGNORECASE,
    )
    _OUTBOUND_INTENT_RE = re.compile(
        r"(发送给|发送到|发给|发布到|发布至|推送到|推送给|"
        r"send\s+to|publish\s+to|post\s+to|push\s+to)",
        re.IGNORECASE,
    )
    _READ_INTENT_RE = re.compile(
        r"(读取|查看|列出|检索|搜索|分析会议|会议分析|生成会议纪要|read|list|search|analy[sz]e)",
        re.IGNORECASE,
    )

    def evaluate_user_input(self, user_input: str, *, domain: Optional[str] = None) -> PolicyDecision:
        """Evaluate the natural-language turn before model/tool execution."""
        normalized = user_input.strip()
        if not normalized:
            return PolicyDecision(False)

        if self._DESTRUCTIVE_INTENT_RE.search(normalized):
            return PolicyDecision(
                requires_approval=True,
                action="workspace.delete",
                risk_level="high",
                reason="The request appears to delete or remove local content.",
                matched_rule="destructive_intent",
                metadata={"domain": domain},
            )
        if self._OUTBOUND_INTENT_RE.search(normalized):
            return PolicyDecision(
                requires_approval=True,
                action="external.send_or_publish",
                risk_level="high",
                reason="The request appears to send or publish content outside the local session.",
                matched_rule="outbound_intent",
                metadata={"domain": domain},
            )
        if self._WRITE_INTENT_RE.search(normalized):
            return PolicyDecision(
                requires_approval=True,
                action="workspace.write",
                risk_level="high",
                reason="The request appears to write or overwrite a local file.",
                matched_rule="write_intent",
                metadata={"domain": domain},
            )
        if self._READ_INTENT_RE.search(normalized):
            return PolicyDecision(
                requires_approval=False,
                action="read_only",
                risk_level="low",
                reason="The request appears to be read-only or analytical.",
                matched_rule="read_only_intent",
                metadata={"domain": domain},
            )
        return PolicyDecision(False, metadata={"domain": domain})

    def evaluate_tool(self, tool_name: str, tool_input: Any = None) -> PolicyDecision:
        """Evaluate a concrete tool operation."""
        if tool_name in self._READ_ONLY_TOOLS:
            return PolicyDecision(
                requires_approval=False,
                action="read_only",
                risk_level="low",
                reason=f"Tool {tool_name} is classified as read-only.",
                matched_rule="read_only_tool",
                metadata={"tool_name": tool_name, "tool_input": tool_input},
            )
        if tool_name in self._APPROVAL_TOOLS:
            action, risk_level = self._APPROVAL_TOOLS[tool_name]
            return PolicyDecision(
                requires_approval=True,
                action=action,
                risk_level=risk_level,
                reason=f"Tool {tool_name} mutates local project state.",
                matched_rule="approval_tool",
                metadata={"tool_name": tool_name, "tool_input": tool_input},
            )
        lowered = tool_name.lower()
        if any(token in lowered for token in ("write", "save", "mkdir", "delete", "send", "publish")):
            return PolicyDecision(
                requires_approval=True,
                action=f"tool.{lowered}",
                risk_level="high",
                reason=f"Tool {tool_name} matches a write/send/publish policy pattern.",
                matched_rule="tool_name_pattern",
                metadata={"tool_name": tool_name, "tool_input": tool_input},
            )
        return PolicyDecision(
            requires_approval=False,
            action="unknown_tool",
            risk_level="low",
            reason=f"Tool {tool_name} did not match an approval policy.",
            metadata={"tool_name": tool_name, "tool_input": tool_input},
        )
