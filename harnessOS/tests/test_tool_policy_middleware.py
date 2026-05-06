from __future__ import annotations

import asyncio
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from apps.gateway.policies import PolicyEvaluator
from apps.gateway.protocol import RpcRequest
from apps.gateway.runtime import GatewayRuntimePool
from apps.gateway.service import GatewayService
from apps.gateway.storage import GatewaySessionStore
from core.engine.query import QueryContext, _execute_tool_call
from core.engine.tools.base import BaseTool, ToolRegistry, ToolResult
from tools import get_builtin_tools


def _tool_by_name(name: str):
    return {tool.name: tool for tool in get_builtin_tools(policy_evaluator=PolicyEvaluator())}[name]


def test_langchain_tool_policy_blocks_mutating_tool_without_approval(tmp_path, monkeypatch):
    monkeypatch.setenv("WORKSPACE_ROOT", str(tmp_path))
    tool = _tool_by_name("workspace_write_file")

    output = tool.func(file_path="blocked.txt", content="secret")

    assert "Tool execution blocked pending approval" in output
    assert not (tmp_path / "blocked.txt").exists()


def test_langchain_tool_policy_ignores_caller_controlled_approved_flag(tmp_path, monkeypatch):
    monkeypatch.setenv("WORKSPACE_ROOT", str(tmp_path))
    tool = _tool_by_name("workspace_write_file")

    output = tool.func(file_path="allowed.txt", content="ok", approved=True)

    assert "Tool execution blocked pending approval" in output
    assert not (tmp_path / "allowed.txt").exists()


def test_langchain_tool_policy_allows_mutating_tool_with_approved_approval_id(tmp_path, monkeypatch):
    monkeypatch.setenv("WORKSPACE_ROOT", str(tmp_path))
    tools = get_builtin_tools(
        policy_evaluator=PolicyEvaluator(),
        approval_checker=lambda approval_id, expected: (
            approval_id == "appr_ok"
            and expected["tool_name"] == "workspace_write_file"
            and expected["tool_input"]["file_path"] == "approved.txt"
        ),
    )
    tool = {item.name: item for item in tools}["workspace_write_file"]

    output = tool.func(file_path="approved.txt", content="ok", approval_id="appr_ok")

    assert "Successfully wrote" in output
    assert (tmp_path / "approved.txt").read_text(encoding="utf-8") == "ok"


def test_langchain_tool_policy_rejects_approval_id_for_different_input(tmp_path, monkeypatch):
    monkeypatch.setenv("WORKSPACE_ROOT", str(tmp_path))
    tools = get_builtin_tools(
        policy_evaluator=PolicyEvaluator(),
        approval_checker=lambda approval_id, expected: (
            approval_id == "appr_ok"
            and expected["tool_input"]["file_path"] == "approved.txt"
        ),
    )
    tool = {item.name: item for item in tools}["workspace_write_file"]

    output = tool.func(file_path="other.txt", content="ok", approval_id="appr_ok")

    assert "Tool execution blocked pending approval" in output
    assert not (tmp_path / "other.txt").exists()


def test_langchain_tool_policy_allows_read_only_tool(tmp_path, monkeypatch):
    monkeypatch.setenv("WORKSPACE_ROOT", str(tmp_path))
    (tmp_path / "readme.txt").write_text("hello", encoding="utf-8")
    tool = _tool_by_name("workspace_read_file")

    assert tool.func(file_path="readme.txt") == "hello"


class WriteInput(BaseModel):
    file_path: str
    content: str


class EngineWriteTool(BaseTool):
    name = "workspace_write_file"
    description = "write"
    input_model = WriteInput

    def __init__(self) -> None:
        self.executed = False

    async def execute(self, arguments: WriteInput, context) -> ToolResult:
        self.executed = True
        return ToolResult(output="wrote")


class LargeOutputInput(BaseModel):
    size: int


class LargeOutputTool(BaseTool):
    name = "large_output"
    description = "large output"
    input_model = LargeOutputInput

    async def execute(self, arguments: LargeOutputInput, context) -> ToolResult:
        del context
        return ToolResult(output="x" * arguments.size)

    def is_read_only(self, arguments: LargeOutputInput) -> bool:
        del arguments
        return True


@dataclass
class AllowAllPermissions:
    def evaluate(self, *args: Any, **kwargs: Any):
        return type("Decision", (), {"allowed": True, "requires_confirmation": False, "reason": ""})()


def test_engine_tool_policy_blocks_before_tool_execute(tmp_path):
    async def run():
        tool = EngineWriteTool()
        registry = ToolRegistry()
        registry.register(tool)
        context = QueryContext(
            api_client=object(),
            tool_registry=registry,
            permission_checker=AllowAllPermissions(),
            cwd=tmp_path,
            model="fake",
            system_prompt="",
            max_tokens=100,
            tool_metadata={"policy_evaluator": PolicyEvaluator()},
        )

        result = await _execute_tool_call(
            context,
            "workspace_write_file",
            "tool_1",
            {"file_path": "blocked.txt", "content": "no"},
        )

        assert result.is_error is True
        assert "Tool execution blocked pending approval" in result.content
        assert tool.executed is False

    asyncio.run(run())


def test_engine_spills_large_tool_result_to_file(tmp_path):
    async def run():
        registry = ToolRegistry()
        registry.register(LargeOutputTool())
        context = QueryContext(
            api_client=object(),
            tool_registry=registry,
            permission_checker=AllowAllPermissions(),
            cwd=tmp_path,
            model="fake",
            system_prompt="",
            max_tokens=100,
            tool_metadata={"tool_result_spill_threshold_chars": 100},
        )

        result = await _execute_tool_call(
            context,
            "large_output",
            "tool_large",
            {"size": 240},
        )

        assert result.is_error is False
        assert "Tool result was too large" in result.content
        assert "Path:" in result.content
        assert len(result.content) < 5000
        spill = result.metadata["spilled_tool_result"]
        spill_path = Path(spill["path"])
        assert spill_path == tmp_path / ".harnessos" / "tool-results" / "large_output-tool_large.txt"
        assert spill_path.read_text(encoding="utf-8") == "x" * 240

    asyncio.run(run())


def test_engine_tool_policy_auto_creates_approval_and_reject_blocks_retry(tmp_path):
    async def run():
        service = GatewayService(
            GatewayRuntimePool(
                agent_factory=lambda _model: object(),
                runtime_backend="simple",
                store=GatewaySessionStore(tmp_path / "sessions"),
            )
        )
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        session_id = started.result["session_id"]
        trace_id = service.trace_store.new_trace_id()
        turn_id = "turn_tool_auto"

        tool = EngineWriteTool()
        registry = ToolRegistry()
        registry.register(tool)
        context = QueryContext(
            api_client=object(),
            tool_registry=registry,
            permission_checker=AllowAllPermissions(),
            cwd=tmp_path,
            model="fake",
            system_prompt="",
            max_tokens=100,
            tool_metadata={
                "session_id": session_id,
                "turn_id": turn_id,
                "trace_id": trace_id,
                "user_input": "write blocked.txt",
                "policy_evaluator": service.policy_evaluator,
                "approval_checker": service.runtime_pool._is_approval_approved,
                "approval_requester": lambda tool_name, tool_input, decision: service.runtime_pool._request_tool_approval(
                    session_id=session_id,
                    turn_id=turn_id,
                    trace_id=trace_id,
                    user_input="write blocked.txt",
                    tool_name=tool_name,
                    tool_input=tool_input,
                    decision=decision,
                ),
            },
        )

        result = await _execute_tool_call(
            context,
            "workspace_write_file",
            "tool_1",
            {"file_path": "blocked.txt", "content": "no"},
        )

        assert result.is_error is True
        assert "Approval ID: appr_" in result.content
        assert tool.executed is False
        approval_id = result.metadata["approval"]["approval_id"]
        assert result.metadata["retry_context"]["approval_id"] == approval_id

        rejected = await service.handle_rpc(
            RpcRequest(id="2", method="approval.reject", params={"approval_id": approval_id, "reason": "not allowed"})
        )
        assert rejected.error is None
        assert rejected.result["approval"]["status"] == "rejected"

        retried = await service.handle_rpc(
            RpcRequest(id="3", method="turn.retry", params={"session_id": session_id, "approval_id": approval_id})
        )
        assert retried.error is not None
        assert retried.error.code == "INVALID_PARAMS"
        assert "approval is not approved: rejected" in retried.error.message
        assert tool.executed is False

    asyncio.run(run())


def test_engine_tool_policy_allows_execution_with_turn_approval_id(tmp_path):
    async def run():
        service = GatewayService(
            GatewayRuntimePool(
                agent_factory=lambda _model: object(),
                runtime_backend="simple",
                store=GatewaySessionStore(tmp_path / "sessions"),
            )
        )
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        session_id = started.result["session_id"]
        trace_id = service.trace_store.new_trace_id()
        turn_id = "turn_tool_approved"

        requested = service.runtime_pool._request_tool_approval(
            session_id=session_id,
            turn_id=turn_id,
            trace_id=trace_id,
            user_input="write approved.txt",
            tool_name="workspace_write_file",
            tool_input={"file_path": "approved.txt", "content": "ok"},
            decision=service.policy_evaluator.evaluate_tool(
                "workspace_write_file",
                {"file_path": "approved.txt", "content": "ok"},
            ).model_dump(),
        )
        approval_id = requested["approval"]["approval_id"]
        await service.handle_rpc(RpcRequest(id="2", method="approval.approve", params={"approval_id": approval_id}))

        tool = EngineWriteTool()
        registry = ToolRegistry()
        registry.register(tool)
        context = QueryContext(
            api_client=object(),
            tool_registry=registry,
            permission_checker=AllowAllPermissions(),
            cwd=tmp_path,
            model="fake",
            system_prompt="",
            max_tokens=100,
            tool_metadata={
                "session_id": session_id,
                "turn_id": turn_id,
                "trace_id": trace_id,
                "policy_evaluator": service.policy_evaluator,
                "approval_checker": service.runtime_pool._is_approval_approved,
                "approval_id": approval_id,
            },
        )

        result = await _execute_tool_call(
            context,
            "workspace_write_file",
            "tool_1",
            {"file_path": "approved.txt", "content": "ok"},
        )

        assert result.is_error is False
        assert result.content == "wrote"
        assert tool.executed is True

    asyncio.run(run())


def test_engine_tool_policy_rejects_approval_id_for_different_tool_input(tmp_path):
    async def run():
        service = GatewayService(
            GatewayRuntimePool(
                agent_factory=lambda _model: object(),
                runtime_backend="simple",
                store=GatewaySessionStore(tmp_path / "sessions"),
            )
        )
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        session_id = started.result["session_id"]
        trace_id = service.trace_store.new_trace_id()

        requested = service.runtime_pool._request_tool_approval(
            session_id=session_id,
            turn_id="turn_tool_approved",
            trace_id=trace_id,
            user_input="write approved.txt",
            tool_name="workspace_write_file",
            tool_input={"file_path": "approved.txt", "content": "ok"},
            decision=service.policy_evaluator.evaluate_tool(
                "workspace_write_file",
                {"file_path": "approved.txt", "content": "ok"},
            ).model_dump(),
        )
        approval_id = requested["approval"]["approval_id"]
        await service.handle_rpc(RpcRequest(id="2", method="approval.approve", params={"approval_id": approval_id}))

        tool = EngineWriteTool()
        registry = ToolRegistry()
        registry.register(tool)
        context = QueryContext(
            api_client=object(),
            tool_registry=registry,
            permission_checker=AllowAllPermissions(),
            cwd=tmp_path,
            model="fake",
            system_prompt="",
            max_tokens=100,
            tool_metadata={
                "policy_evaluator": service.policy_evaluator,
                "approval_checker": service.runtime_pool._is_approval_approved,
                "approval_id": approval_id,
            },
        )

        result = await _execute_tool_call(
            context,
            "workspace_write_file",
            "tool_1",
            {"file_path": "other.txt", "content": "ok"},
        )

        assert result.is_error is True
        assert "Tool execution blocked pending approval" in result.content
        assert tool.executed is False

    asyncio.run(run())


def test_engine_tool_policy_rejects_approval_id_for_different_session(tmp_path):
    async def run():
        service = GatewayService(
            GatewayRuntimePool(
                agent_factory=lambda _model: object(),
                runtime_backend="simple",
                store=GatewaySessionStore(tmp_path / "sessions"),
            )
        )
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        session_id = started.result["session_id"]
        trace_id = service.trace_store.new_trace_id()

        requested = service.runtime_pool._request_tool_approval(
            session_id=session_id,
            turn_id="turn_tool_approved",
            trace_id=trace_id,
            user_input="write approved.txt",
            tool_name="workspace_write_file",
            tool_input={"file_path": "approved.txt", "content": "ok"},
            decision=service.policy_evaluator.evaluate_tool(
                "workspace_write_file",
                {"file_path": "approved.txt", "content": "ok"},
            ).model_dump(),
        )
        approval_id = requested["approval"]["approval_id"]
        await service.handle_rpc(RpcRequest(id="2", method="approval.approve", params={"approval_id": approval_id}))

        tool = EngineWriteTool()
        registry = ToolRegistry()
        registry.register(tool)
        context = QueryContext(
            api_client=object(),
            tool_registry=registry,
            permission_checker=AllowAllPermissions(),
            cwd=tmp_path,
            model="fake",
            system_prompt="",
            max_tokens=100,
            tool_metadata={
                "session_id": "sess_other",
                "turn_id": "turn_tool_approved",
                "trace_id": trace_id,
                "policy_evaluator": service.policy_evaluator,
                "approval_checker": service.runtime_pool._is_approval_approved,
                "approval_id": approval_id,
            },
        )

        result = await _execute_tool_call(
            context,
            "workspace_write_file",
            "tool_1",
            {"file_path": "approved.txt", "content": "ok"},
        )

        assert result.is_error is True
        assert "Tool execution blocked pending approval" in result.content
        assert tool.executed is False

    asyncio.run(run())


def test_engine_tool_policy_allows_retry_turn_with_source_turn_binding(tmp_path):
    async def run():
        service = GatewayService(
            GatewayRuntimePool(
                agent_factory=lambda _model: object(),
                runtime_backend="simple",
                store=GatewaySessionStore(tmp_path / "sessions"),
            )
        )
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        session_id = started.result["session_id"]
        trace_id = service.trace_store.new_trace_id()
        source_turn_id = "turn_source"

        requested = service.runtime_pool._request_tool_approval(
            session_id=session_id,
            turn_id=source_turn_id,
            trace_id=trace_id,
            user_input="write approved.txt",
            tool_name="workspace_write_file",
            tool_input={"file_path": "approved.txt", "content": "ok"},
            decision=service.policy_evaluator.evaluate_tool(
                "workspace_write_file",
                {"file_path": "approved.txt", "content": "ok"},
            ).model_dump(),
        )
        approval_id = requested["approval"]["approval_id"]
        await service.handle_rpc(RpcRequest(id="2", method="approval.approve", params={"approval_id": approval_id}))

        tool = EngineWriteTool()
        registry = ToolRegistry()
        registry.register(tool)
        context = QueryContext(
            api_client=object(),
            tool_registry=registry,
            permission_checker=AllowAllPermissions(),
            cwd=tmp_path,
            model="fake",
            system_prompt="",
            max_tokens=100,
            tool_metadata={
                "session_id": session_id,
                "turn_id": "turn_retry",
                "source_turn_id": source_turn_id,
                "trace_id": trace_id,
                "policy_evaluator": service.policy_evaluator,
                "approval_checker": service.runtime_pool._is_approval_approved,
                "approval_id": approval_id,
            },
        )

        result = await _execute_tool_call(
            context,
            "workspace_write_file",
            "tool_1",
            {"file_path": "approved.txt", "content": "ok"},
        )

        assert result.is_error is False
        assert tool.executed is True

    asyncio.run(run())
