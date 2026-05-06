"""Tool execution policy guard helpers."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Callable, Optional


ApprovalChecker = Callable[..., bool]
ApprovalRequester = Callable[[str, Any, dict[str, Any]], dict[str, Any]]


def guarded_tool_func(
    *,
    tool_name: str,
    func: Callable[..., str],
    policy_evaluator: Any,
    approval_checker: Optional[ApprovalChecker] = None,
    approval_requester: Optional[ApprovalRequester] = None,
) -> Callable[..., str]:
    """Wrap a callable tool with execution-time policy enforcement."""

    def guarded(*args: Any, **kwargs: Any) -> str:
        approval_id = _optional_text(kwargs.pop("approval_id", None))
        kwargs.pop("approved", None)
        tool_input = dict(kwargs) if kwargs else _positional_input(args)
        decision = policy_evaluator.evaluate_tool(tool_name, tool_input)
        if decision.requires_approval and not _is_approved(
            approval_id=approval_id,
            approval_checker=approval_checker,
            tool_name=tool_name,
            tool_input=tool_input,
            decision=decision.model_dump(),
        ):
            requested = _request_approval(
                approval_requester=approval_requester,
                tool_name=tool_name,
                tool_input=tool_input,
                decision=decision.model_dump(),
            )
            return _blocked_message(
                tool_name,
                decision,
                approval_id=approval_id or _approval_id_from_request(requested),
            )
        return func(*args, **kwargs)

    return guarded


def should_block_tool(
    *,
    tool_name: str,
    tool_input: Any,
    policy_evaluator: Any,
    approval_checker: Optional[ApprovalChecker] = None,
    approval_requester: Optional[ApprovalRequester] = None,
    default_approval_id: Optional[str] = None,
    binding_context: Optional[dict[str, Any]] = None,
) -> tuple[bool, str, dict[str, Any]]:
    """Return whether a concrete tool invocation should be blocked."""
    approval_id = None
    if isinstance(tool_input, dict):
        approval_id = _optional_text(tool_input.get("approval_id"))
    if approval_id is None:
        approval_id = default_approval_id
    decision = policy_evaluator.evaluate_tool(tool_name, tool_input)
    decision_payload = decision.model_dump()
    if decision.requires_approval and not _is_approved(
        approval_id=approval_id,
        approval_checker=approval_checker,
            tool_name=tool_name,
            tool_input=tool_input,
            decision=decision_payload,
            binding_context=binding_context,
        ):
        requested = _request_approval(
            approval_requester=approval_requester,
            tool_name=tool_name,
            tool_input=tool_input,
            decision=decision_payload,
        )
        if requested:
            decision_payload["approval"] = requested.get("approval")
            decision_payload["retry_context"] = requested.get("retry_context")
        return (
            True,
            _blocked_message(tool_name, decision, approval_id=approval_id or _approval_id_from_request(requested)),
            decision_payload,
        )
    return False, "", decision_payload


def _is_approved(
    *,
    approval_id: Optional[str],
    approval_checker: Optional[ApprovalChecker],
    tool_name: str,
    tool_input: Any,
    decision: dict[str, Any],
    binding_context: Optional[dict[str, Any]] = None,
) -> bool:
    if approval_id and approval_checker is not None:
        expected = {
            "tool_name": tool_name,
            "tool_input": tool_input,
            "tool_input_hash": tool_input_hash(tool_input),
            "action": decision.get("action"),
        }
        if binding_context:
            expected.update(
                {
                    key: value
                    for key, value in binding_context.items()
                    if key in {"session_id", "turn_id", "source_turn_id", "trace_id"} and value
                }
            )
        try:
            return bool(approval_checker(approval_id, expected))
        except Exception:
            return False
    return False


def tool_input_hash(tool_input: Any) -> str:
    """Return a stable hash for binding approvals to tool inputs."""
    try:
        payload = json.dumps(tool_input, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    except TypeError:
        payload = repr(tool_input)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _blocked_message(tool_name: str, decision: Any, *, approval_id: Optional[str]) -> str:
    suffix = f" Approval ID: {approval_id}" if approval_id else ""
    return (
        f"Tool execution blocked pending approval. Tool: {tool_name}. "
        f"Action: {decision.action}. Risk: {decision.risk_level}. "
        f"Reason: {decision.reason}.{suffix}"
    )


def _request_approval(
    *,
    approval_requester: Optional[ApprovalRequester],
    tool_name: str,
    tool_input: Any,
    decision: dict[str, Any],
) -> dict[str, Any]:
    if approval_requester is None:
        return {}
    try:
        requested = approval_requester(tool_name, tool_input, decision)
    except Exception:
        return {}
    return requested if isinstance(requested, dict) else {}


def _approval_id_from_request(requested: dict[str, Any]) -> Optional[str]:
    approval = requested.get("approval")
    if isinstance(approval, dict):
        value = approval.get("approval_id")
        if isinstance(value, str) and value.strip():
            return value
    value = requested.get("approval_id")
    if isinstance(value, str) and value.strip():
        return value
    return None


def _optional_text(value: Any) -> Optional[str]:
    if isinstance(value, str) and value.strip():
        return value
    return None


def _positional_input(args: tuple[Any, ...]) -> Any:
    if len(args) == 1:
        return args[0]
    if args:
        return list(args)
    return {}
