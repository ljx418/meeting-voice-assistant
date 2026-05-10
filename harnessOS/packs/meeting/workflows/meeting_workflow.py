"""Standard Meeting Pack workflow entrypoint.

This module keeps the PhaseD directory contract while delegating to the
existing compatibility implementation until the workflow is split further.
"""

from packs.meeting.workflow import MeetingWorkflow

__all__ = ["MeetingWorkflow"]
