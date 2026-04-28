"""Tool execution policy guard helpers."""

from __future__ import annotations

from typing import Any, Callable, Optional


ApprovalChecker = Callable[[str], bool]


def guarded_tool_func(
    *,
    tool_name: str,
    func: Callable[..., str],
    policy_evaluator: Any,
    approval_checker: Optional[ApprovalChecker] = None,
) -> Callable[..., str]:
    """Wrap a callable tool with execution-time policy enforcement."""

    def guarded(*args: Any, **kwargs: Any) -> str:
        approval_id = _optional_text(kwargs.pop("approval_id", None))
        approved_flag = bool(kwargs.pop("approved", False))
        tool_input = dict(kwargs) if kwargs else _positional_input(args)
        decision = policy_evaluator.evaluate_tool(tool_name, tool_input)
        if decision.requires_approval and not _is_approved(
            approval_id=approval_id,
            approved_flag=approved_flag,
            approval_checker=approval_checker,
        ):
            return _blocked_message(tool_name, decision, approval_id=approval_id)
        return func(*args, **kwargs)

    return guarded


def should_block_tool(
    *,
    tool_name: str,
    tool_input: Any,
    policy_evaluator: Any,
    approval_checker: Optional[ApprovalChecker] = None,
) -> tuple[bool, str, dict[str, Any]]:
    """Return whether a concrete tool invocation should be blocked."""
    approval_id = None
    approved_flag = False
    if isinstance(tool_input, dict):
        approval_id = _optional_text(tool_input.get("approval_id"))
        approved_flag = bool(tool_input.get("approved", False))
    decision = policy_evaluator.evaluate_tool(tool_name, tool_input)
    if decision.requires_approval and not _is_approved(
        approval_id=approval_id,
        approved_flag=approved_flag,
        approval_checker=approval_checker,
    ):
        return True, _blocked_message(tool_name, decision, approval_id=approval_id), decision.model_dump()
    return False, "", decision.model_dump()


def _is_approved(
    *,
    approval_id: Optional[str],
    approved_flag: bool,
    approval_checker: Optional[ApprovalChecker],
) -> bool:
    if approved_flag:
        return True
    if approval_id and approval_checker is not None:
        try:
            return bool(approval_checker(approval_id))
        except Exception:
            return False
    return False


def _blocked_message(tool_name: str, decision: Any, *, approval_id: Optional[str]) -> str:
    suffix = f" Approval ID: {approval_id}" if approval_id else ""
    return (
        f"Tool execution blocked pending approval. Tool: {tool_name}. "
        f"Action: {decision.action}. Risk: {decision.risk_level}. "
        f"Reason: {decision.reason}.{suffix}"
    )


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
