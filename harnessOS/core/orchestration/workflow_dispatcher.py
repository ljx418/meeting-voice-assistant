"""
Workflow dispatcher for harnessOS.

Dispatches tasks to the appropriate agent based on workflow definition.
"""

from typing import Any

from core.schemas import AgentType, AgentRequest, AgentResponse, WorkflowTask, ExecutionStatus


class WorkflowDispatcher:
    """
    Dispatches workflow tasks to appropriate agents.

    This is a placeholder implementation that will be expanded
    in Phase 2 with actual agent invocation logic.
    """

    def __init__(self):
        """Initialize the workflow dispatcher."""
        self._tasks: dict[str, WorkflowTask] = {}

    async def dispatch(self, task: WorkflowTask) -> AgentResponse:
        """
        Dispatch a workflow task to the appropriate agent.

        Args:
            task: The workflow task to dispatch

        Returns:
            Agent response with execution results
        """
        self._tasks[task.id] = task

        # Placeholder: In Phase 2, this will invoke the actual agent
        # For now, return a mock response
        return AgentResponse(
            request_id=task.id,
            agent_type=task.agent_type,
            messages=[],
            status=ExecutionStatus.COMPLETED,
            metadata={"message": "Workflow dispatcher placeholder - to be implemented in Phase 2"}
        )

    async def get_task_status(self, task_id: str) -> WorkflowTask | None:
        """
        Get the status of a workflow task.

        Args:
            task_id: The task ID to query

        Returns:
            The task if found, None otherwise
        """
        return self._tasks.get(task_id)

    def list_tasks(self) -> list[WorkflowTask]:
        """List all workflow tasks."""
        return list(self._tasks.values())
