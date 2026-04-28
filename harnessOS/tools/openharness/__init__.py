"""Built-in tool registration."""

from examples.open_harness.src.openharness.tools.ask_user_question_tool import AskUserQuestionTool
from examples.open_harness.src.openharness.tools.agent_tool import AgentTool
from examples.open_harness.src.openharness.tools.bash_tool import BashTool
from examples.open_harness.src.openharness.tools.base import BaseTool, ToolExecutionContext, ToolRegistry, ToolResult
from examples.open_harness.src.openharness.tools.brief_tool import BriefTool
from examples.open_harness.src.openharness.tools.config_tool import ConfigTool
from examples.open_harness.src.openharness.tools.cron_create_tool import CronCreateTool
from examples.open_harness.src.openharness.tools.cron_delete_tool import CronDeleteTool
from examples.open_harness.src.openharness.tools.cron_list_tool import CronListTool
from examples.open_harness.src.openharness.tools.cron_toggle_tool import CronToggleTool
from examples.open_harness.src.openharness.tools.enter_plan_mode_tool import EnterPlanModeTool
from examples.open_harness.src.openharness.tools.enter_worktree_tool import EnterWorktreeTool
from examples.open_harness.src.openharness.tools.exit_plan_mode_tool import ExitPlanModeTool
from examples.open_harness.src.openharness.tools.exit_worktree_tool import ExitWorktreeTool
from examples.open_harness.src.openharness.tools.file_edit_tool import FileEditTool
from examples.open_harness.src.openharness.tools.file_read_tool import FileReadTool
from examples.open_harness.src.openharness.tools.file_write_tool import FileWriteTool
from examples.open_harness.src.openharness.tools.glob_tool import GlobTool
from examples.open_harness.src.openharness.tools.grep_tool import GrepTool
from examples.open_harness.src.openharness.tools.list_mcp_resources_tool import ListMcpResourcesTool
from examples.open_harness.src.openharness.tools.lsp_tool import LspTool
from examples.open_harness.src.openharness.tools.mcp_auth_tool import McpAuthTool
from examples.open_harness.src.openharness.tools.mcp_tool import McpToolAdapter
from examples.open_harness.src.openharness.tools.notebook_edit_tool import NotebookEditTool
from examples.open_harness.src.openharness.tools.read_mcp_resource_tool import ReadMcpResourceTool
from examples.open_harness.src.openharness.tools.remote_trigger_tool import RemoteTriggerTool
from examples.open_harness.src.openharness.tools.send_message_tool import SendMessageTool
from examples.open_harness.src.openharness.tools.skill_tool import SkillTool
from examples.open_harness.src.openharness.tools.sleep_tool import SleepTool
from examples.open_harness.src.openharness.tools.task_create_tool import TaskCreateTool
from examples.open_harness.src.openharness.tools.task_get_tool import TaskGetTool
from examples.open_harness.src.openharness.tools.task_list_tool import TaskListTool
from examples.open_harness.src.openharness.tools.task_output_tool import TaskOutputTool
from examples.open_harness.src.openharness.tools.task_stop_tool import TaskStopTool
from examples.open_harness.src.openharness.tools.task_update_tool import TaskUpdateTool
from examples.open_harness.src.openharness.tools.team_create_tool import TeamCreateTool
from examples.open_harness.src.openharness.tools.team_delete_tool import TeamDeleteTool
from examples.open_harness.src.openharness.tools.todo_write_tool import TodoWriteTool
from examples.open_harness.src.openharness.tools.tool_search_tool import ToolSearchTool
from examples.open_harness.src.openharness.tools.web_fetch_tool import WebFetchTool
from examples.open_harness.src.openharness.tools.web_search_tool import WebSearchTool


def create_default_tool_registry(mcp_manager=None) -> ToolRegistry:
    """Return the default built-in tool registry."""
    registry = ToolRegistry()
    for tool in (
        BashTool(),
        AskUserQuestionTool(),
        FileReadTool(),
        FileWriteTool(),
        FileEditTool(),
        NotebookEditTool(),
        LspTool(),
        McpAuthTool(),
        GlobTool(),
        GrepTool(),
        SkillTool(),
        ToolSearchTool(),
        WebFetchTool(),
        WebSearchTool(),
        ConfigTool(),
        BriefTool(),
        SleepTool(),
        EnterWorktreeTool(),
        ExitWorktreeTool(),
        TodoWriteTool(),
        EnterPlanModeTool(),
        ExitPlanModeTool(),
        CronCreateTool(),
        CronListTool(),
        CronDeleteTool(),
        CronToggleTool(),
        RemoteTriggerTool(),
        TaskCreateTool(),
        TaskGetTool(),
        TaskListTool(),
        TaskStopTool(),
        TaskOutputTool(),
        TaskUpdateTool(),
        AgentTool(),
        SendMessageTool(),
        TeamCreateTool(),
        TeamDeleteTool(),
    ):
        registry.register(tool)
    if mcp_manager is not None:
        registry.register(ListMcpResourcesTool(mcp_manager))
        registry.register(ReadMcpResourceTool(mcp_manager))
        for tool_info in mcp_manager.list_tools():
            registry.register(McpToolAdapter(mcp_manager, tool_info))
    return registry


__all__ = [
    "BaseTool",
    "ToolExecutionContext",
    "ToolRegistry",
    "ToolResult",
    "create_default_tool_registry",
]