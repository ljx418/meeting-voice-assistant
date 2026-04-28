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


def test_langchain_tool_policy_allows_mutating_tool_with_approved_flag(tmp_path, monkeypatch):
    monkeypatch.setenv("WORKSPACE_ROOT", str(tmp_path))
    tool = _tool_by_name("workspace_write_file")

    output = tool.func(file_path="allowed.txt", content="ok", approved=True)

    assert "Successfully wrote" in output
    assert (tmp_path / "allowed.txt").read_text(encoding="utf-8") == "ok"


def test_langchain_tool_policy_allows_mutating_tool_with_approved_approval_id(tmp_path, monkeypatch):
    monkeypatch.setenv("WORKSPACE_ROOT", str(tmp_path))
    tools = get_builtin_tools(
        policy_evaluator=PolicyEvaluator(),
        approval_checker=lambda approval_id: approval_id == "appr_ok",
    )
    tool = {item.name: item for item in tools}["workspace_write_file"]

    output = tool.func(file_path="approved.txt", content="ok", approval_id="appr_ok")

    assert "Successfully wrote" in output
    assert (tmp_path / "approved.txt").read_text(encoding="utf-8") == "ok"


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
