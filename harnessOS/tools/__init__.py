"""
harnessOS tools package.
"""

from typing import Any, Callable, List, Optional

from langchain_core.tools import Tool

from tools.workspace import (
    workspace_ls,
    workspace_read_file,
    workspace_write_file,
)
from tools.knowledge import kb_search, kb_ingest
from tools.artifact import artifact_save
from tools.policy_guard import guarded_tool_func


def get_builtin_tools(
    *,
    policy_evaluator: Any = None,
    approval_checker: Optional[Callable[[str], bool]] = None,
    approval_requester: Optional[Callable[[str, Any, dict[str, Any]], dict[str, Any]]] = None,
) -> List[Tool]:
    """Get all builtin tools for harnessOS.

    Returns:
        List of Tool instances
    """
    def maybe_guard(name: str, func: Callable[..., str]) -> Callable[..., str]:
        if policy_evaluator is None:
            return func
        return guarded_tool_func(
            tool_name=name,
            func=func,
            policy_evaluator=policy_evaluator,
            approval_checker=approval_checker,
            approval_requester=approval_requester,
        )

    return [
        Tool(
            name="workspace_ls",
            description="List files in the workspace directory. Usage: workspace_ls(directory='.')",
            func=maybe_guard("workspace_ls", workspace_ls),
        ),
        Tool(
            name="workspace_read_file",
            description="Read contents of a file in the workspace. Usage: workspace_read_file(file_path='path/to/file.txt')",
            func=maybe_guard("workspace_read_file", workspace_read_file),
        ),
        Tool(
            name="workspace_write_file",
            description="Write content to a file in the workspace. Usage: workspace_write_file(file_path='path/to/file.txt', content='file content')",
            func=maybe_guard("workspace_write_file", workspace_write_file),
        ),
        Tool(
            name="kb_search",
            description="Search the knowledge base for relevant information. Usage: kb_search(query='search terms')",
            func=maybe_guard("kb_search", kb_search),
        ),
        Tool(
            name="kb_ingest",
            description="Ingest a document into the knowledge base. Usage: kb_ingest(document='text content to ingest')",
            func=maybe_guard("kb_ingest", kb_ingest),
        ),
        Tool(
            name="artifact_save",
            description="Save a structured output as an artifact. Usage: artifact_save(name='artifact-name', content='content to save')",
            func=maybe_guard("artifact_save", artifact_save),
        ),
    ]


__all__ = [
    "get_builtin_tools",
    "workspace_ls",
    "workspace_read_file",
    "workspace_write_file",
    "kb_search",
    "kb_ingest",
    "artifact_save",
]
