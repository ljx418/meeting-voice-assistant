"""Built-in tool registration."""

from harnessOS.openharness.tools.ask_user_question_tool import AskUserQuestionTool
from harnessOS.openharness.tools.agent_tool import AgentTool
from harnessOS.openharness.tools.bash_tool import BashTool
from harnessOS.openharness.tools.base import BaseTool, ToolExecutionContext, ToolRegistry, ToolResult
from harnessOS.openharness.tools.brief_tool import BriefTool
from harnessOS.openharness.tools.config_tool import ConfigTool
from harnessOS.openharness.tools.cron_create_tool import CronCreateTool
from harnessOS.openharness.tools.cron_delete_tool import CronDeleteTool
from harnessOS.openharness.tools.cron_list_tool import CronListTool
from harnessOS.openharness.tools.cron_toggle_tool import CronToggleTool
from harnessOS.openharness.tools.enter_plan_mode_tool import EnterPlanModeTool
from harnessOS.openharness.tools.enter_worktree_tool import EnterWorktreeTool
from harnessOS.openharness.tools.exit_plan_mode_tool import ExitPlanModeTool
from harnessOS.openharness.tools.exit_worktree_tool import ExitWorktreeTool
from harnessOS.openharness.tools.file_edit_tool import FileEditTool
from harnessOS.openharness.tools.file_read_tool import FileReadTool
from harnessOS.openharness.tools.file_write_tool import FileWriteTool
from harnessOS.openharness.tools.glob_tool import GlobTool
from harnessOS.openharness.tools.grep_tool import GrepTool
from harnessOS.openharness.tools.list_mcp_resources_tool import ListMcpResourcesTool
from harnessOS.openharness.tools.lsp_tool import LspTool
from harnessOS.openharness.tools.mcp_auth_tool import McpAuthTool
from harnessOS.openharness.tools.mcp_tool import McpToolAdapter
from harnessOS.openharness.tools.notebook_edit_tool import NotebookEditTool
from harnessOS.openharness.tools.read_mcp_resource_tool import ReadMcpResourceTool
from harnessOS.openharness.tools.remote_trigger_tool import RemoteTriggerTool
from harnessOS.openharness.tools.send_message_tool import SendMessageTool
from harnessOS.openharness.tools.skill_tool import SkillTool
from harnessOS.openharness.tools.sleep_tool import SleepTool
from harnessOS.openharness.tools.task_create_tool import TaskCreateTool
from harnessOS.openharness.tools.task_get_tool import TaskGetTool
from harnessOS.openharness.tools.task_list_tool import TaskListTool
from harnessOS.openharness.tools.task_output_tool import TaskOutputTool
from harnessOS.openharness.tools.task_stop_tool import TaskStopTool
from harnessOS.openharness.tools.task_update_tool import TaskUpdateTool
from harnessOS.openharness.tools.team_create_tool import TeamCreateTool
from harnessOS.openharness.tools.team_delete_tool import TeamDeleteTool
from harnessOS.openharness.tools.todo_write_tool import TodoWriteTool
from harnessOS.openharness.tools.tool_search_tool import ToolSearchTool
from harnessOS.openharness.tools.web_fetch_tool import WebFetchTool
from harnessOS.openharness.tools.web_search_tool import WebSearchTool


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
