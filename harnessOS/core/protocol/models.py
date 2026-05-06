"""Core v1.5 protocol objects.

These models are transport-neutral and intentionally separate from the older
apps.gateway protocol types. They are the object vocabulary shared by CLI,
HTTP/SSE, stdio, Web, and future bot clients.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


def new_core_id(prefix: str) -> str:
    """Create a compact identifier for a Core object."""
    return f"{prefix}_{uuid4().hex[:12]}"


class CoreObject(BaseModel):
    """Base object fields shared by Core records."""

    app_id: str = "default"
    project_id: Optional[str] = None
    workspace_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SessionRecord(CoreObject):
    """Client/user runtime context."""

    session_id: str = Field(default_factory=lambda: new_core_id("sess"))
    client_type: str = "unknown"
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    status: str = "active"
    capabilities: Dict[str, Any] = Field(default_factory=dict)


class ThreadRecord(CoreObject):
    """Project or task context across turns."""

    thread_id: str = Field(default_factory=lambda: new_core_id("thread"))
    session_id: str
    domain: Optional[str] = None
    title: str = ""
    goal: str = ""
    status: str = "active"


class TurnRecord(CoreObject):
    """One user input and execution lifecycle."""

    turn_id: str = Field(default_factory=lambda: new_core_id("turn"))
    session_id: str
    thread_id: str
    input: str
    state: str = "started"
    trace_id: Optional[str] = None
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


class ItemRecord(CoreObject):
    """Fine-grained event or content item inside a turn."""

    item_id: str = Field(default_factory=lambda: new_core_id("item"))
    session_id: str
    thread_id: str
    turn_id: str
    item_type: str
    role: Optional[str] = None
    content: Dict[str, Any] = Field(default_factory=dict)
    status: str = "created"
    parent_item_id: Optional[str] = None


class JobRecord(CoreObject):
    """Long-running workflow execution."""

    job_id: str = Field(default_factory=lambda: new_core_id("job"))
    workflow_id: str
    domain: Optional[str] = None
    session_id: Optional[str] = None
    thread_id: Optional[str] = None
    turn_id: Optional[str] = None
    status: str = "queued"
    progress: float = 0.0
    trace_id: Optional[str] = None
    artifact_ids: List[str] = Field(default_factory=list)
    external_job_ref: Optional[str] = None
    parent_job_id: Optional[str] = None
    failure_context: Dict[str, Any] = Field(default_factory=dict)


class JobEventRecord(CoreObject):
    """State transition or progress event for a Core job."""

    event_id: str = Field(default_factory=lambda: new_core_id("jobevt"))
    job_id: str
    event_type: str
    status: str
    progress: Optional[float] = None
    message: str = ""


class ArtifactRecord(CoreObject):
    """Output object visible through Core."""

    artifact_id: str = Field(default_factory=lambda: new_core_id("art"))
    domain: Optional[str] = None
    kind: str
    owner_session_id: Optional[str] = None
    owner_thread_id: Optional[str] = None
    owner_turn_id: Optional[str] = None
    uri: str
    name: str = ""
    mime: str = "application/octet-stream"
    parent_ids: List[str] = Field(default_factory=list)
    external_asset_uri: Optional[str] = None
    preview_uri: Optional[str] = None
    thumbnail_uri: Optional[str] = None


class ApprovalRecord(CoreObject):
    """Human decision record for risky actions."""

    approval_id: str = Field(default_factory=lambda: new_core_id("appr"))
    target_type: str
    target_id: str
    risk_class: str = "medium"
    reason: str = ""
    decision: str = "pending"
    reviewer: Optional[str] = None
    decided_at: Optional[datetime] = None


class TraceRecord(CoreObject):
    """Audit event for a turn, artifact, approval, or workflow operation."""

    record_id: str = Field(default_factory=lambda: new_core_id("trace_record"))
    trace_id: str
    session_id: Optional[str] = None
    turn_id: Optional[str] = None
    event_type: str
    status: str = "running"
    workflow_id: Optional[str] = None
    artifact_ids: List[str] = Field(default_factory=list)
    approval_ids: List[str] = Field(default_factory=list)
    input_summary: str = ""


class MemoryRecord(CoreObject):
    """Session or thread memory derived from turns and artifacts."""

    memory_id: str = Field(default_factory=lambda: new_core_id("mem"))
    session_id: str
    thread_id: Optional[str] = None
    source_turn_id: Optional[str] = None
    source_artifact_id: Optional[str] = None
    trace_id: Optional[str] = None
    scope: str = "session"
    kind: str = "summary"
    title: str = ""
    content: str = ""
    status: str = "active"
    refs: List[Dict[str, Any]] = Field(default_factory=list)


class RetryRecord(CoreObject):
    """Saved context for retrying a blocked or failed turn."""

    retry_id: str = Field(default_factory=lambda: new_core_id("retry"))
    source_turn_id: str
    session_id: str
    input: str
    domain: Optional[str] = None
    trace_id: Optional[str] = None
    approval_id: Optional[str] = None
    status: str = "pending_approval"
    workflow_id: Optional[str] = None
    failure_message: Optional[str] = None
    artifact_ids: List[str] = Field(default_factory=list)
    policy: Dict[str, Any] = Field(default_factory=dict)
    retried_at: Optional[datetime] = None
    retry_turn_id: Optional[str] = None
    retry_trace_id: Optional[str] = None


class ConnectorRecord(CoreObject):
    """MCP, native tool, or external system capability descriptor."""

    connector_id: str = Field(default_factory=lambda: new_core_id("conn"))
    kind: str
    domain: Optional[str] = None
    version: str = "0.1.0"
    health: str = "unknown"
    trust_level: str = "untrusted_local"
    execution_mode: str = "stub"
    capabilities: Dict[str, Any] = Field(default_factory=dict)
    config_ref: Optional[str] = None
    secret_ref: Optional[str] = None
    app_scope: List[str] = Field(default_factory=list)
    allowed_commands: List[str] = Field(default_factory=list)
    allowed_paths: List[str] = Field(default_factory=list)
    allowed_network_hosts: List[str] = Field(default_factory=list)
    network_policy: str = "none"
    tool_risk_defaults: Dict[str, Any] = Field(default_factory=dict)
    requires_approval_for: List[str] = Field(default_factory=list)
