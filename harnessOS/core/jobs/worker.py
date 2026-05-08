"""In-process background worker for Core jobs."""

from __future__ import annotations

import asyncio
import inspect
from typing import Any, Awaitable, Callable, Dict, Optional

from core.apps import ScopeContext
from core.protocol import JobRecord
from core.services import CoreAppService

JobHandler = Callable[[JobRecord], Any]


class BackgroundJobWorker:
    """Small asyncio-backed worker for local-first long-running jobs.

    This is intentionally in-process for Roadmap Phase 3-C. It gives Core a
    real queued/running/completed/failed/cancelled lifecycle without committing
    to distributed queues or external workers.
    """

    def __init__(self, *, core_service: CoreAppService) -> None:
        self.core_service = core_service
        self._tasks: Dict[str, asyncio.Task[Any]] = {}

    def submit(
        self,
        *,
        workflow_id: str,
        handler: JobHandler,
        domain: Optional[str] = None,
        session_id: Optional[str] = None,
        thread_id: Optional[str] = None,
        turn_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        scope: Optional[ScopeContext] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> JobRecord:
        """Create a queued job and schedule it on the current event loop."""
        job = self.core_service.create_job(
            workflow_id=workflow_id,
            domain=domain,
            session_id=session_id,
            thread_id=thread_id,
            turn_id=turn_id,
            trace_id=trace_id,
            scope=scope,
            metadata=metadata,
        )
        self._tasks[job.job_id] = asyncio.create_task(self._run(job.job_id, handler))
        return job

    async def wait(self, job_id: str) -> JobRecord:
        """Wait for a scheduled job and return its latest record."""
        task = self._tasks.get(job_id)
        if task is not None:
            await task
        return self.core_service.get_job(job_id)

    def cancel(self, job_id: str, *, reason: Optional[str] = None) -> JobRecord:
        """Cancel a queued/running job and request task cancellation."""
        task = self._tasks.get(job_id)
        if task is not None and not task.done():
            task.cancel()
        return self.core_service.cancel_job(job_id, reason=reason)

    async def _run(self, job_id: str, handler: JobHandler) -> None:
        running = self.core_service.update_job(job_id=job_id, status="running", progress=0.0)
        try:
            result = handler(running)
            if inspect.isawaitable(result):
                result = await result
            metadata = result if isinstance(result, dict) else {}
            artifact_ids = metadata.get("artifact_ids") if isinstance(metadata.get("artifact_ids"), list) else []
            self.core_service.update_job(
                job_id=job_id,
                status="completed",
                progress=1.0,
                artifact_ids=[item for item in artifact_ids if isinstance(item, str)],
                metadata=metadata,
            )
        except asyncio.CancelledError:
            job = self.core_service.get_job(job_id)
            if job.status != "cancelled":
                self.core_service.cancel_job(job_id, reason="task cancelled")
        except Exception as exc:
            failure_context = {
                "error_type": type(exc).__name__,
                "message": str(exc),
            }
            self.core_service.update_job(
                job_id=job_id,
                status="failed",
                progress=1.0,
                failure_context=failure_context,
                metadata={
                    "failure_context": failure_context,
                },
            )
        finally:
            self._tasks.pop(job_id, None)
