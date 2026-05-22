"""Dev/local workflow template repository for V3.6-B."""

from __future__ import annotations

import copy
from dataclasses import dataclass
from datetime import datetime, timezone
from threading import RLock
from typing import Any, Protocol
from uuid import uuid4

from core.protocol.schemas.errors import ProtocolError
from core.workflows.models import (
    BusinessEvent,
    BusinessEventBinding,
    QualityEvaluation,
    StationRun,
    WorkflowContext,
    WorkflowDraft,
    WorkflowDraftStatus,
    WorkflowInstance,
    WorkflowPatch,
    WorkflowPatchActorType,
    WorkflowPatchOperation,
    WorkflowPatchStatus,
    WorkflowTemplate,
    WorkflowTemplateStatus,
    WorkflowVersion,
)


ScopeKey = tuple[str, str | None, str | None]
TemplateKey = tuple[str, str | None, str | None, str]

_FORBIDDEN_SCHEMA_KEYS = {
    "x",
    "y",
    "position",
    "canvas",
    "panel",
    "react_state",
    "component",
    "layout",
    "capability_token",
    "subscription_token",
    "authorization",
    "secret",
    "raw_trace_payload",
    "raw_connector_payload",
    "raw_artifact_content",
}

_PATCH_ALLOWED_FIELDS: dict[str, set[str]] = {
    WorkflowPatchOperation.ADD_STATION.value: {"station"},
    WorkflowPatchOperation.REMOVE_STATION.value: {"station_id"},
    WorkflowPatchOperation.UPDATE_STATION_PROMPT.value: {"station_id", "prompt_ref", "prompt_patch"},
    WorkflowPatchOperation.UPDATE_CONNECTOR.value: {"station_id", "connector_refs", "connector_patch"},
    WorkflowPatchOperation.UPDATE_ARTIFACT_CONTRACT.value: {"station_id", "contract_id", "contract_patch"},
    WorkflowPatchOperation.UPDATE_QUALITY_RULE.value: {"quality_contract_id", "quality_patch"},
    WorkflowPatchOperation.UPDATE_APPROVAL_POINT.value: {"station_id", "approval_required", "approval_policy"},
    WorkflowPatchOperation.UPDATE_EDGE.value: {"edge_id", "edge_patch"},
}

_PATCH_REQUIRED_FIELDS: dict[str, set[str]] = {
    WorkflowPatchOperation.ADD_STATION.value: {"station"},
    WorkflowPatchOperation.REMOVE_STATION.value: {"station_id"},
    WorkflowPatchOperation.UPDATE_STATION_PROMPT.value: {"station_id"},
    WorkflowPatchOperation.UPDATE_CONNECTOR.value: {"station_id"},
    WorkflowPatchOperation.UPDATE_ARTIFACT_CONTRACT.value: {"station_id", "contract_id", "contract_patch"},
    WorkflowPatchOperation.UPDATE_QUALITY_RULE.value: {"quality_contract_id", "quality_patch"},
    WorkflowPatchOperation.UPDATE_APPROVAL_POINT.value: {"station_id"},
    WorkflowPatchOperation.UPDATE_EDGE.value: {"edge_id", "edge_patch"},
}


class WorkflowStore(Protocol):
    """Repository-facing workflow storage interface."""

    def create_template(self, template_payload: dict[str, Any], *, scope: Any) -> tuple[WorkflowTemplate, WorkflowDraft]:
        ...

    def get_template(self, workflow_template_id: str, *, scope: Any) -> WorkflowTemplate:
        ...

    def list_templates(self, *, scope: Any, include_archived: bool = False) -> list[WorkflowTemplate]:
        ...

    def update_latest_draft(
        self,
        workflow_template_id: str,
        draft_payload: dict[str, Any],
        *,
        scope: Any,
        expected_revision: int | None = None,
    ) -> tuple[WorkflowDraft, bool]:
        ...

    def save_draft(
        self,
        workflow_draft_id: str,
        draft_payload: dict[str, Any],
        *,
        scope: Any,
        expected_revision: int | None = None,
    ) -> WorkflowDraft:
        ...

    def get_draft(self, workflow_draft_id: str, *, scope: Any) -> WorkflowDraft:
        ...

    def publish_template(
        self,
        workflow_template_id: str,
        *,
        version: str,
        scope: Any,
        expected_revision: int | None = None,
    ) -> tuple[WorkflowTemplate, WorkflowDraft, WorkflowVersion]:
        ...

    def archive_template(self, workflow_template_id: str, *, scope: Any) -> WorkflowTemplate:
        ...

    def get_version(self, workflow_version_id: str, *, scope: Any) -> WorkflowVersion:
        ...

    def get_version_by_template(self, workflow_template_id: str, version: str, *, scope: Any) -> WorkflowVersion:
        ...

    def list_versions(self, workflow_template_id: str, *, scope: Any) -> list[WorkflowVersion]:
        ...

    def create_instance(self, instance: WorkflowInstance, *, scope: Any) -> WorkflowInstance:
        ...

    def get_instance(self, workflow_instance_id: str, *, scope: Any) -> WorkflowInstance:
        ...

    def list_instances(self, *, scope: Any, status: str | None = None) -> list[WorkflowInstance]:
        ...

    def update_instance(self, instance: WorkflowInstance, *, scope: Any) -> WorkflowInstance:
        ...

    def create_station_run(self, station_run: StationRun, *, scope: Any) -> StationRun:
        ...

    def get_station_run(self, station_run_id: str, *, scope: Any) -> StationRun:
        ...

    def list_station_runs(self, workflow_instance_id: str, *, scope: Any) -> list[StationRun]:
        ...

    def update_station_run(self, station_run: StationRun, *, scope: Any) -> StationRun:
        ...

    def create_quality_evaluation(self, evaluation: QualityEvaluation, *, scope: Any) -> QualityEvaluation:
        ...

    def get_quality_evaluation(self, evaluation_id: str, *, scope: Any) -> QualityEvaluation:
        ...

    def list_quality_evaluations(
        self,
        *,
        scope: Any,
        workflow_instance_id: str | None = None,
        station_run_id: str | None = None,
    ) -> list[QualityEvaluation]:
        ...

    def update_quality_evaluation(self, evaluation: QualityEvaluation, *, scope: Any) -> QualityEvaluation:
        ...

    def get_or_create_context(self, workflow_instance_id: str, *, scope: Any) -> WorkflowContext:
        ...

    def update_context(
        self,
        context: WorkflowContext,
        *,
        scope: Any,
        expected_revision: int | None = None,
    ) -> WorkflowContext:
        ...

    def create_business_event_binding(self, binding: BusinessEventBinding, *, scope: Any) -> BusinessEventBinding:
        ...

    def list_business_event_bindings(
        self,
        *,
        scope: Any,
        workflow_instance_id: str,
        event_type: str | None = None,
    ) -> list[BusinessEventBinding]:
        ...

    def mark_business_event_applied(
        self,
        event_key: str,
        *,
        scope: Any,
        workflow_instance_id: str,
    ) -> bool:
        ...

    def apply_business_event_context(
        self,
        event_key: str,
        context: WorkflowContext,
        *,
        scope: Any,
    ) -> tuple[WorkflowContext, bool]:
        ...

    def propose_patch(self, patch: WorkflowPatch, *, scope: Any) -> WorkflowPatch:
        ...

    def get_patch(self, workflow_patch_id: str, *, scope: Any) -> WorkflowPatch:
        ...

    def list_patches(self, *, scope: Any, workflow_template_id: str | None = None, workflow_draft_id: str | None = None) -> list[WorkflowPatch]:
        ...

    def apply_patch(self, workflow_patch_id: str, *, scope: Any, actor_type: str) -> tuple[WorkflowPatch, WorkflowDraft, bool]:
        ...

    def reject_patch(self, workflow_patch_id: str, *, scope: Any, reason: str | None = None) -> tuple[WorkflowPatch, bool]:
        ...


@dataclass(frozen=True)
class WorkflowRepository:
    """Workflow template service facade over a workflow store."""

    store: WorkflowStore

    def create_template(self, template_payload: dict[str, Any], *, scope: Any) -> tuple[WorkflowTemplate, WorkflowDraft]:
        return self.store.create_template(template_payload, scope=scope)

    def get_template(self, workflow_template_id: str, *, scope: Any) -> WorkflowTemplate:
        return self.store.get_template(workflow_template_id, scope=scope)

    def list_templates(self, *, scope: Any, include_archived: bool = False) -> list[WorkflowTemplate]:
        return self.store.list_templates(scope=scope, include_archived=include_archived)

    def update_latest_draft(
        self,
        workflow_template_id: str,
        draft_payload: dict[str, Any],
        *,
        scope: Any,
        expected_revision: int | None = None,
    ) -> tuple[WorkflowDraft, bool]:
        return self.store.update_latest_draft(
            workflow_template_id,
            draft_payload,
            scope=scope,
            expected_revision=expected_revision,
        )

    def save_draft(
        self,
        workflow_draft_id: str,
        draft_payload: dict[str, Any],
        *,
        scope: Any,
        expected_revision: int | None = None,
    ) -> WorkflowDraft:
        return self.store.save_draft(
            workflow_draft_id,
            draft_payload,
            scope=scope,
            expected_revision=expected_revision,
        )

    def get_draft(self, workflow_draft_id: str, *, scope: Any) -> WorkflowDraft:
        return self.store.get_draft(workflow_draft_id, scope=scope)

    def publish_template(
        self,
        workflow_template_id: str,
        *,
        version: str,
        scope: Any,
        expected_revision: int | None = None,
    ) -> tuple[WorkflowTemplate, WorkflowDraft, WorkflowVersion]:
        return self.store.publish_template(
            workflow_template_id,
            version=version,
            scope=scope,
            expected_revision=expected_revision,
        )

    def archive_template(self, workflow_template_id: str, *, scope: Any) -> WorkflowTemplate:
        return self.store.archive_template(workflow_template_id, scope=scope)

    def get_version(self, workflow_version_id: str, *, scope: Any) -> WorkflowVersion:
        return self.store.get_version(workflow_version_id, scope=scope)

    def get_version_by_template(self, workflow_template_id: str, version: str, *, scope: Any) -> WorkflowVersion:
        return self.store.get_version_by_template(workflow_template_id, version, scope=scope)

    def list_versions(self, workflow_template_id: str, *, scope: Any) -> list[WorkflowVersion]:
        return self.store.list_versions(workflow_template_id, scope=scope)

    def create_instance(self, instance: WorkflowInstance, *, scope: Any) -> WorkflowInstance:
        return self.store.create_instance(instance, scope=scope)

    def get_instance(self, workflow_instance_id: str, *, scope: Any) -> WorkflowInstance:
        return self.store.get_instance(workflow_instance_id, scope=scope)

    def list_instances(self, *, scope: Any, status: str | None = None) -> list[WorkflowInstance]:
        return self.store.list_instances(scope=scope, status=status)

    def update_instance(self, instance: WorkflowInstance, *, scope: Any) -> WorkflowInstance:
        return self.store.update_instance(instance, scope=scope)

    def create_station_run(self, station_run: StationRun, *, scope: Any) -> StationRun:
        return self.store.create_station_run(station_run, scope=scope)

    def get_station_run(self, station_run_id: str, *, scope: Any) -> StationRun:
        return self.store.get_station_run(station_run_id, scope=scope)

    def list_station_runs(self, workflow_instance_id: str, *, scope: Any) -> list[StationRun]:
        return self.store.list_station_runs(workflow_instance_id, scope=scope)

    def update_station_run(self, station_run: StationRun, *, scope: Any) -> StationRun:
        return self.store.update_station_run(station_run, scope=scope)

    def create_quality_evaluation(self, evaluation: QualityEvaluation, *, scope: Any) -> QualityEvaluation:
        return self.store.create_quality_evaluation(evaluation, scope=scope)

    def get_quality_evaluation(self, evaluation_id: str, *, scope: Any) -> QualityEvaluation:
        return self.store.get_quality_evaluation(evaluation_id, scope=scope)

    def list_quality_evaluations(
        self,
        *,
        scope: Any,
        workflow_instance_id: str | None = None,
        station_run_id: str | None = None,
    ) -> list[QualityEvaluation]:
        return self.store.list_quality_evaluations(
            scope=scope,
            workflow_instance_id=workflow_instance_id,
            station_run_id=station_run_id,
        )

    def update_quality_evaluation(self, evaluation: QualityEvaluation, *, scope: Any) -> QualityEvaluation:
        return self.store.update_quality_evaluation(evaluation, scope=scope)

    def get_or_create_context(self, workflow_instance_id: str, *, scope: Any) -> WorkflowContext:
        return self.store.get_or_create_context(workflow_instance_id, scope=scope)

    def update_context(
        self,
        context: WorkflowContext,
        *,
        scope: Any,
        expected_revision: int | None = None,
    ) -> WorkflowContext:
        return self.store.update_context(context, scope=scope, expected_revision=expected_revision)

    def create_business_event_binding(self, binding: BusinessEventBinding, *, scope: Any) -> BusinessEventBinding:
        return self.store.create_business_event_binding(binding, scope=scope)

    def list_business_event_bindings(
        self,
        *,
        scope: Any,
        workflow_instance_id: str,
        event_type: str | None = None,
    ) -> list[BusinessEventBinding]:
        return self.store.list_business_event_bindings(
            scope=scope,
            workflow_instance_id=workflow_instance_id,
            event_type=event_type,
        )

    def mark_business_event_applied(
        self,
        event_key: str,
        *,
        scope: Any,
        workflow_instance_id: str,
    ) -> bool:
        return self.store.mark_business_event_applied(event_key, scope=scope, workflow_instance_id=workflow_instance_id)

    def apply_business_event_context(
        self,
        event_key: str,
        context: WorkflowContext,
        *,
        scope: Any,
    ) -> tuple[WorkflowContext, bool]:
        return self.store.apply_business_event_context(event_key, context, scope=scope)

    def propose_patch(self, patch: WorkflowPatch, *, scope: Any) -> WorkflowPatch:
        return self.store.propose_patch(patch, scope=scope)

    def get_patch(self, workflow_patch_id: str, *, scope: Any) -> WorkflowPatch:
        return self.store.get_patch(workflow_patch_id, scope=scope)

    def list_patches(self, *, scope: Any, workflow_template_id: str | None = None, workflow_draft_id: str | None = None) -> list[WorkflowPatch]:
        return self.store.list_patches(scope=scope, workflow_template_id=workflow_template_id, workflow_draft_id=workflow_draft_id)

    def apply_patch(self, workflow_patch_id: str, *, scope: Any, actor_type: str) -> tuple[WorkflowPatch, WorkflowDraft, bool]:
        return self.store.apply_patch(workflow_patch_id, scope=scope, actor_type=actor_type)

    def reject_patch(self, workflow_patch_id: str, *, scope: Any, reason: str | None = None) -> tuple[WorkflowPatch, bool]:
        return self.store.reject_patch(workflow_patch_id, scope=scope, reason=reason)


class InMemoryWorkflowStore:
    """Thread-safe in-memory workflow template store for dev/local V3.6-B."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._templates: dict[TemplateKey, WorkflowTemplate] = {}
        self._drafts: dict[str, WorkflowDraft] = {}
        self._draft_template_keys: dict[str, TemplateKey] = {}
        self._versions: dict[str, WorkflowVersion] = {}
        self._version_template_keys: dict[str, TemplateKey] = {}
        self._versions_by_template_and_name: dict[tuple[TemplateKey, str], str] = {}
        self._instances: dict[str, WorkflowInstance] = {}
        self._instance_scope_keys: dict[str, ScopeKey] = {}
        self._station_runs: dict[str, StationRun] = {}
        self._station_run_scope_keys: dict[str, ScopeKey] = {}
        self._station_runs_by_instance: dict[str, list[str]] = {}
        self._quality_evaluations: dict[str, QualityEvaluation] = {}
        self._quality_scope_keys: dict[str, ScopeKey] = {}
        self._contexts: dict[str, WorkflowContext] = {}
        self._context_scope_keys: dict[str, ScopeKey] = {}
        self._business_event_bindings: dict[str, BusinessEventBinding] = {}
        self._binding_scope_keys: dict[str, ScopeKey] = {}
        self._bindings_by_instance: dict[str, list[str]] = {}
        self._applied_business_events: set[tuple[ScopeKey, str, str]] = set()
        self._patches: dict[str, WorkflowPatch] = {}
        self._patch_scope_keys: dict[str, ScopeKey] = {}
        self._patches_by_draft: dict[str, list[str]] = {}

    def create_template(self, template_payload: dict[str, Any], *, scope: Any) -> tuple[WorkflowTemplate, WorkflowDraft]:
        with self._lock:
            template = _validate_template_payload(template_payload, scope=scope)
            key = _template_key(template)
            if key in self._templates:
                raise ProtocolError(
                    "WORKFLOW_TEMPLATE_ALREADY_EXISTS",
                    f"Workflow template already exists: {template.workflow_template_id}",
                    {"workflow_template_id": template.workflow_template_id},
                )
            draft_id = _new_id("wfd")
            template = template.model_copy(update={"latest_draft_id": draft_id})
            draft = WorkflowDraft(
                workflow_draft_id=draft_id,
                workflow_template_id=template.workflow_template_id,
                draft=template.model_dump(mode="json"),
                revision=1,
                status=WorkflowDraftStatus.EDITABLE,
            )
            self._templates[key] = template
            self._drafts[draft_id] = draft
            self._draft_template_keys[draft_id] = key
            return template.model_copy(deep=True), draft.model_copy(deep=True)

    def get_template(self, workflow_template_id: str, *, scope: Any) -> WorkflowTemplate:
        with self._lock:
            key = _key_from_scope(scope, workflow_template_id)
            template = self._templates.get(key)
            if template is None:
                raise _not_found("WORKFLOW_TEMPLATE_NOT_FOUND", workflow_template_id)
            return template.model_copy(deep=True)

    def list_templates(self, *, scope: Any, include_archived: bool = False) -> list[WorkflowTemplate]:
        with self._lock:
            scope_key = _scope_key(scope)
            templates = [
                template.model_copy(deep=True)
                for key, template in self._templates.items()
                if key[:3] == scope_key
                and (include_archived or template.status != WorkflowTemplateStatus.ARCHIVED)
            ]
            return sorted(templates, key=lambda item: item.workflow_template_id)

    def update_latest_draft(
        self,
        workflow_template_id: str,
        draft_payload: dict[str, Any],
        *,
        scope: Any,
        expected_revision: int | None = None,
    ) -> tuple[WorkflowDraft, bool]:
        with self._lock:
            key = _key_from_scope(scope, workflow_template_id)
            template = self._require_template(key)
            self._ensure_not_archived(template)
            latest_draft = self._require_draft(template.latest_draft_id)
            forked = False
            if latest_draft.status == WorkflowDraftStatus.PUBLISHED:
                latest_draft = WorkflowDraft(
                    workflow_draft_id=_new_id("wfd"),
                    workflow_template_id=template.workflow_template_id,
                    base_version=template.version,
                    base_version_id=template.latest_published_version_id,
                    draft=copy.deepcopy(latest_draft.draft),
                    revision=1,
                    status=WorkflowDraftStatus.EDITABLE,
                )
                self._drafts[latest_draft.workflow_draft_id] = latest_draft
                self._draft_template_keys[latest_draft.workflow_draft_id] = key
                template = template.model_copy(update={"latest_draft_id": latest_draft.workflow_draft_id})
                self._templates[key] = template
                forked = True
                expected_revision = None
            updated = self._save_draft_locked(latest_draft, draft_payload, key=key, scope=scope, expected_revision=expected_revision)
            return updated.model_copy(deep=True), forked

    def save_draft(
        self,
        workflow_draft_id: str,
        draft_payload: dict[str, Any],
        *,
        scope: Any,
        expected_revision: int | None = None,
    ) -> WorkflowDraft:
        with self._lock:
            draft = self._require_draft(workflow_draft_id)
            key = self._draft_template_keys[workflow_draft_id]
            if key[:3] != _scope_key(scope):
                raise ProtocolError("SCOPE_MISMATCH", "Workflow draft does not match requested scope.", {"resource": "workflow_draft_id"})
            return self._save_draft_locked(draft, draft_payload, key=key, scope=scope, expected_revision=expected_revision).model_copy(deep=True)

    def get_draft(self, workflow_draft_id: str, *, scope: Any) -> WorkflowDraft:
        with self._lock:
            draft = self._require_draft(workflow_draft_id)
            key = self._draft_template_keys.get(workflow_draft_id)
            if key is None:
                raise _not_found("WORKFLOW_DRAFT_NOT_FOUND", workflow_draft_id)
            if key[:3] != _scope_key(scope):
                raise ProtocolError("SCOPE_MISMATCH", "Workflow draft does not match requested scope.", {"resource": "workflow_draft_id"})
            return draft.model_copy(deep=True)

    def publish_template(
        self,
        workflow_template_id: str,
        *,
        version: str,
        scope: Any,
        expected_revision: int | None = None,
    ) -> tuple[WorkflowTemplate, WorkflowDraft, WorkflowVersion]:
        version = version.strip()
        if not version:
            raise ProtocolError("INVALID_PARAMS", "version is required", {"field": "version"})
        with self._lock:
            key = _key_from_scope(scope, workflow_template_id)
            template = self._require_template(key)
            self._ensure_not_archived(template)
            if (key, version) in self._versions_by_template_and_name:
                raise ProtocolError("WORKFLOW_VERSION_CONFLICT", f"Workflow version already exists: {version}", {"version": version})
            draft = self._require_draft(template.latest_draft_id)
            if draft.status != WorkflowDraftStatus.EDITABLE:
                raise ProtocolError("WORKFLOW_PUBLISHED_IMMUTABLE", "Published draft cannot be republished.", {"workflow_draft_id": draft.workflow_draft_id})
            _check_revision(draft, expected_revision)
            snapshot = copy.deepcopy(draft.draft)
            _validate_template_payload(snapshot, scope=scope)
            version_id = _new_id("wfv")
            version_record = WorkflowVersion(
                workflow_version_id=version_id,
                workflow_template_id=template.workflow_template_id,
                version=version,
                snapshot=snapshot,
            )
            published_draft = draft.model_copy(
                update={
                    "status": WorkflowDraftStatus.PUBLISHED,
                    "base_version": version,
                    "base_version_id": version_id,
                }
            )
            updated_template = template.model_copy(
                update={
                    "status": WorkflowTemplateStatus.PUBLISHED,
                    "version": version,
                    "latest_published_version_id": version_id,
                }
            )
            self._versions[version_id] = version_record
            self._version_template_keys[version_id] = key
            self._versions_by_template_and_name[(key, version)] = version_id
            self._drafts[draft.workflow_draft_id] = published_draft
            self._templates[key] = updated_template
            return (
                updated_template.model_copy(deep=True),
                published_draft.model_copy(deep=True),
                version_record.model_copy(deep=True),
            )

    def archive_template(self, workflow_template_id: str, *, scope: Any) -> WorkflowTemplate:
        with self._lock:
            key = _key_from_scope(scope, workflow_template_id)
            template = self._require_template(key)
            if template.status == WorkflowTemplateStatus.ARCHIVED:
                return template.model_copy(deep=True)
            archived = template.model_copy(update={"status": WorkflowTemplateStatus.ARCHIVED})
            self._templates[key] = archived
            return archived.model_copy(deep=True)

    def get_version(self, workflow_version_id: str, *, scope: Any) -> WorkflowVersion:
        with self._lock:
            version = self._versions.get(workflow_version_id)
            key = self._version_template_keys.get(workflow_version_id)
            if version is None or key is None:
                raise _not_found("WORKFLOW_VERSION_NOT_FOUND", workflow_version_id)
            if key[:3] != _scope_key(scope):
                raise ProtocolError("SCOPE_MISMATCH", "Workflow version does not match requested scope.", {"resource": "workflow_version_id"})
            return version.model_copy(deep=True)

    def get_version_by_template(self, workflow_template_id: str, version: str, *, scope: Any) -> WorkflowVersion:
        with self._lock:
            key = _key_from_scope(scope, workflow_template_id)
            self._require_template(key)
            version_id = self._versions_by_template_and_name.get((key, version))
            if version_id is None:
                raise _not_found("WORKFLOW_VERSION_NOT_FOUND", version)
            return self._versions[version_id].model_copy(deep=True)

    def list_versions(self, workflow_template_id: str, *, scope: Any) -> list[WorkflowVersion]:
        with self._lock:
            key = _key_from_scope(scope, workflow_template_id)
            self._require_template(key)
            versions = [
                version.model_copy(deep=True)
                for version_id, version in self._versions.items()
                if self._version_template_keys.get(version_id) == key
            ]
            return sorted(versions, key=lambda item: item.published_at.isoformat())

    def create_instance(self, instance: WorkflowInstance, *, scope: Any) -> WorkflowInstance:
        with self._lock:
            self._ensure_instance_scope(instance, scope)
            self._instances[instance.workflow_instance_id] = instance.model_copy(deep=True)
            self._instance_scope_keys[instance.workflow_instance_id] = _scope_key(scope)
            self._station_runs_by_instance.setdefault(instance.workflow_instance_id, [])
            return instance.model_copy(deep=True)

    def get_instance(self, workflow_instance_id: str, *, scope: Any) -> WorkflowInstance:
        with self._lock:
            instance = self._instances.get(workflow_instance_id)
            if instance is None:
                raise _not_found("WORKFLOW_INSTANCE_NOT_FOUND", workflow_instance_id)
            if self._instance_scope_keys.get(workflow_instance_id) != _scope_key(scope):
                raise ProtocolError("SCOPE_MISMATCH", "Workflow instance does not match requested scope.", {"resource": "workflow_instance_id"})
            return instance.model_copy(deep=True)

    def list_instances(self, *, scope: Any, status: str | None = None) -> list[WorkflowInstance]:
        with self._lock:
            scope_key = _scope_key(scope)
            instances = [
                instance.model_copy(deep=True)
                for instance_id, instance in self._instances.items()
                if self._instance_scope_keys.get(instance_id) == scope_key
                and (status is None or instance.status == status)
            ]
            return sorted(instances, key=lambda item: item.workflow_instance_id)

    def update_instance(self, instance: WorkflowInstance, *, scope: Any) -> WorkflowInstance:
        with self._lock:
            existing = self.get_instance(instance.workflow_instance_id, scope=scope)
            del existing
            self._ensure_instance_scope(instance, scope)
            self._instances[instance.workflow_instance_id] = instance.model_copy(deep=True)
            return instance.model_copy(deep=True)

    def create_station_run(self, station_run: StationRun, *, scope: Any) -> StationRun:
        with self._lock:
            self.get_instance(station_run.workflow_instance_id, scope=scope)
            self._station_runs[station_run.station_run_id] = station_run.model_copy(deep=True)
            self._station_run_scope_keys[station_run.station_run_id] = _scope_key(scope)
            runs = self._station_runs_by_instance.setdefault(station_run.workflow_instance_id, [])
            if station_run.station_run_id not in runs:
                runs.append(station_run.station_run_id)
            return station_run.model_copy(deep=True)

    def get_station_run(self, station_run_id: str, *, scope: Any) -> StationRun:
        with self._lock:
            station_run = self._station_runs.get(station_run_id)
            if station_run is None:
                raise _not_found("STATION_RUN_NOT_FOUND", station_run_id)
            if self._station_run_scope_keys.get(station_run_id) != _scope_key(scope):
                raise ProtocolError("SCOPE_MISMATCH", "Station run does not match requested scope.", {"resource": "station_run_id"})
            return station_run.model_copy(deep=True)

    def list_station_runs(self, workflow_instance_id: str, *, scope: Any) -> list[StationRun]:
        with self._lock:
            self.get_instance(workflow_instance_id, scope=scope)
            run_ids = self._station_runs_by_instance.get(workflow_instance_id, [])
            return [self._station_runs[run_id].model_copy(deep=True) for run_id in run_ids]

    def update_station_run(self, station_run: StationRun, *, scope: Any) -> StationRun:
        with self._lock:
            self.get_station_run(station_run.station_run_id, scope=scope)
            self._station_runs[station_run.station_run_id] = station_run.model_copy(deep=True)
            return station_run.model_copy(deep=True)

    def create_quality_evaluation(self, evaluation: QualityEvaluation, *, scope: Any) -> QualityEvaluation:
        with self._lock:
            self.get_instance(evaluation.workflow_instance_id, scope=scope)
            self.get_station_run(evaluation.station_run_id, scope=scope)
            self._quality_evaluations[evaluation.evaluation_id] = evaluation.model_copy(deep=True)
            self._quality_scope_keys[evaluation.evaluation_id] = _scope_key(scope)
            return evaluation.model_copy(deep=True)

    def get_quality_evaluation(self, evaluation_id: str, *, scope: Any) -> QualityEvaluation:
        with self._lock:
            evaluation = self._quality_evaluations.get(evaluation_id)
            if evaluation is None:
                raise _not_found("QUALITY_EVALUATION_NOT_FOUND", evaluation_id)
            if self._quality_scope_keys.get(evaluation_id) != _scope_key(scope):
                raise ProtocolError("SCOPE_MISMATCH", "Quality evaluation does not match requested scope.", {"resource": "evaluation_id"})
            return evaluation.model_copy(deep=True)

    def list_quality_evaluations(
        self,
        *,
        scope: Any,
        workflow_instance_id: str | None = None,
        station_run_id: str | None = None,
    ) -> list[QualityEvaluation]:
        with self._lock:
            scope_key = _scope_key(scope)
            evaluations = [
                evaluation.model_copy(deep=True)
                for evaluation_id, evaluation in self._quality_evaluations.items()
                if self._quality_scope_keys.get(evaluation_id) == scope_key
                and (workflow_instance_id is None or evaluation.workflow_instance_id == workflow_instance_id)
                and (station_run_id is None or evaluation.station_run_id == station_run_id)
            ]
            return sorted(evaluations, key=lambda item: item.created_at.isoformat())

    def update_quality_evaluation(self, evaluation: QualityEvaluation, *, scope: Any) -> QualityEvaluation:
        with self._lock:
            self.get_quality_evaluation(evaluation.evaluation_id, scope=scope)
            self._quality_evaluations[evaluation.evaluation_id] = evaluation.model_copy(deep=True)
            return evaluation.model_copy(deep=True)

    def get_or_create_context(self, workflow_instance_id: str, *, scope: Any) -> WorkflowContext:
        with self._lock:
            instance = self.get_instance(workflow_instance_id, scope=scope)
            context = self._contexts.get(workflow_instance_id)
            if context is None:
                context = WorkflowContext(
                    workflow_instance_id=workflow_instance_id,
                    app_id=instance.app_id,
                    project_id=instance.project_id,
                    workspace_id=instance.workspace_id,
                    system={},
                    business={},
                    runtime={},
                    metadata={},
                    revision=1,
                )
                self._contexts[workflow_instance_id] = context
                self._context_scope_keys[workflow_instance_id] = _scope_key(scope)
            if self._context_scope_keys.get(workflow_instance_id) != _scope_key(scope):
                raise ProtocolError("SCOPE_MISMATCH", "Workflow context does not match requested scope.", {"resource": "workflow_instance_id"})
            return context.model_copy(deep=True)

    def update_context(
        self,
        context: WorkflowContext,
        *,
        scope: Any,
        expected_revision: int | None = None,
    ) -> WorkflowContext:
        with self._lock:
            existing = self.get_or_create_context(context.workflow_instance_id, scope=scope)
            if expected_revision is not None and existing.revision != expected_revision:
                raise ProtocolError(
                    "WORKFLOW_CONTEXT_CONFLICT",
                    "Workflow context revision does not match expected revision.",
                    {
                        "expected_revision": expected_revision,
                        "actual_revision": existing.revision,
                    },
                )
            updated = context.model_copy(
                update={
                    "revision": existing.revision + 1,
                    "updated_at": _now_utc(),
                },
                deep=True,
            )
            self._contexts[context.workflow_instance_id] = updated
            self._context_scope_keys[context.workflow_instance_id] = _scope_key(scope)
            return updated.model_copy(deep=True)

    def create_business_event_binding(self, binding: BusinessEventBinding, *, scope: Any) -> BusinessEventBinding:
        with self._lock:
            self.get_instance(binding.workflow_instance_id, scope=scope)
            if binding.binding_id in self._business_event_bindings:
                raise ProtocolError(
                    "BUSINESS_EVENT_BINDING_INVALID",
                    "Business event binding id already exists.",
                    {"binding_id": binding.binding_id, "reason": "duplicate_binding_id"},
                )
            self._business_event_bindings[binding.binding_id] = binding.model_copy(deep=True)
            self._binding_scope_keys[binding.binding_id] = _scope_key(scope)
            binding_ids = self._bindings_by_instance.setdefault(binding.workflow_instance_id, [])
            if binding.binding_id not in binding_ids:
                binding_ids.append(binding.binding_id)
            return binding.model_copy(deep=True)

    def list_business_event_bindings(
        self,
        *,
        scope: Any,
        workflow_instance_id: str,
        event_type: str | None = None,
    ) -> list[BusinessEventBinding]:
        with self._lock:
            self.get_instance(workflow_instance_id, scope=scope)
            scope_key = _scope_key(scope)
            bindings = [
                self._business_event_bindings[binding_id].model_copy(deep=True)
                for binding_id in self._bindings_by_instance.get(workflow_instance_id, [])
                if self._binding_scope_keys.get(binding_id) == scope_key
                and (event_type is None or self._business_event_bindings[binding_id].event_type == event_type)
            ]
            return sorted(bindings, key=lambda item: item.binding_id)

    def mark_business_event_applied(
        self,
        event_key: str,
        *,
        scope: Any,
        workflow_instance_id: str,
    ) -> bool:
        with self._lock:
            self.get_instance(workflow_instance_id, scope=scope)
            key = (_scope_key(scope), workflow_instance_id, event_key)
            if key in self._applied_business_events:
                return False
            self._applied_business_events.add(key)
            return True

    def apply_business_event_context(
        self,
        event_key: str,
        context: WorkflowContext,
        *,
        scope: Any,
    ) -> tuple[WorkflowContext, bool]:
        with self._lock:
            existing = self.get_or_create_context(context.workflow_instance_id, scope=scope)
            key = (_scope_key(scope), context.workflow_instance_id, event_key)
            if key in self._applied_business_events:
                return existing.model_copy(deep=True), False
            updated = context.model_copy(
                update={
                    "revision": existing.revision + 1,
                    "updated_at": _now_utc(),
                },
                deep=True,
            )
            self._contexts[context.workflow_instance_id] = updated
            self._context_scope_keys[context.workflow_instance_id] = _scope_key(scope)
            self._applied_business_events.add(key)
            return updated.model_copy(deep=True), True

    def propose_patch(self, patch: WorkflowPatch, *, scope: Any) -> WorkflowPatch:
        with self._lock:
            key = _key_from_scope(scope, patch.workflow_template_id)
            template = self._require_template(key)
            self._ensure_not_archived(template)
            draft = self._require_draft(patch.workflow_draft_id)
            if self._draft_template_keys.get(draft.workflow_draft_id) != key:
                raise ProtocolError("SCOPE_MISMATCH", "Workflow patch draft does not match requested scope.", {"resource": "workflow_draft_id"})
            if draft.status != WorkflowDraftStatus.EDITABLE:
                raise ProtocolError("WORKFLOW_PUBLISHED_IMMUTABLE", "Published draft cannot be patched.", {"workflow_draft_id": draft.workflow_draft_id})
            if patch.base_revision != draft.revision:
                raise ProtocolError(
                    "WORKFLOW_PATCH_CONFLICT",
                    "Workflow patch base revision does not match draft revision.",
                    {"base_revision": patch.base_revision, "actual_revision": draft.revision},
                )
            _validate_patch_payload(patch.operation, patch.payload)
            self._patches[patch.workflow_patch_id] = patch.model_copy(deep=True)
            self._patch_scope_keys[patch.workflow_patch_id] = _scope_key(scope)
            patch_ids = self._patches_by_draft.setdefault(patch.workflow_draft_id, [])
            if patch.workflow_patch_id not in patch_ids:
                patch_ids.append(patch.workflow_patch_id)
            return patch.model_copy(deep=True)

    def get_patch(self, workflow_patch_id: str, *, scope: Any) -> WorkflowPatch:
        with self._lock:
            patch = self._patches.get(workflow_patch_id)
            if patch is None:
                raise _not_found("WORKFLOW_PATCH_NOT_FOUND", workflow_patch_id)
            if self._patch_scope_keys.get(workflow_patch_id) != _scope_key(scope):
                raise ProtocolError("SCOPE_MISMATCH", "Workflow patch does not match requested scope.", {"resource": "workflow_patch_id"})
            return patch.model_copy(deep=True)

    def list_patches(self, *, scope: Any, workflow_template_id: str | None = None, workflow_draft_id: str | None = None) -> list[WorkflowPatch]:
        with self._lock:
            scope_key = _scope_key(scope)
            patches: list[WorkflowPatch] = []
            for patch_id, patch in self._patches.items():
                if self._patch_scope_keys.get(patch_id) != scope_key:
                    continue
                if workflow_template_id is not None and patch.workflow_template_id != workflow_template_id:
                    continue
                if workflow_draft_id is not None and patch.workflow_draft_id != workflow_draft_id:
                    continue
                patches.append(patch.model_copy(deep=True))
            return sorted(patches, key=lambda item: (item.created_at, item.workflow_patch_id), reverse=True)

    def apply_patch(self, workflow_patch_id: str, *, scope: Any, actor_type: str) -> tuple[WorkflowPatch, WorkflowDraft, bool]:
        with self._lock:
            patch = self.get_patch(workflow_patch_id, scope=scope)
            if actor_type == WorkflowPatchActorType.AGENT.value:
                raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "Agent actor cannot apply workflow patches.", {"actor_type": actor_type})
            if patch.status == WorkflowPatchStatus.APPLIED:
                return patch.model_copy(deep=True), self._require_draft(patch.workflow_draft_id).model_copy(deep=True), True
            if patch.status == WorkflowPatchStatus.REJECTED:
                raise ProtocolError("WORKFLOW_PATCH_CONFLICT", "Rejected workflow patch cannot be applied.", {"status": patch.status})
            key = _key_from_scope(scope, patch.workflow_template_id)
            template = self._require_template(key)
            self._ensure_not_archived(template)
            draft = self._require_draft(patch.workflow_draft_id)
            if self._draft_template_keys.get(draft.workflow_draft_id) != key:
                raise ProtocolError("SCOPE_MISMATCH", "Workflow patch draft does not match requested scope.", {"resource": "workflow_draft_id"})
            if draft.status != WorkflowDraftStatus.EDITABLE:
                raise ProtocolError("WORKFLOW_PUBLISHED_IMMUTABLE", "Published draft cannot be patched.", {"workflow_draft_id": draft.workflow_draft_id})
            if draft.revision != patch.base_revision:
                raise ProtocolError(
                    "WORKFLOW_PATCH_CONFLICT",
                    "Workflow patch is stale and cannot be applied without rebase.",
                    {"base_revision": patch.base_revision, "actual_revision": draft.revision},
                )
            next_payload = _apply_patch_to_template_payload(draft.draft, patch.operation, patch.payload)
            try:
                validated = _validate_template_payload(next_payload, scope=scope)
            except ProtocolError as exc:
                raise ProtocolError("WORKFLOW_PATCH_INVALID", str(exc), exc.data) from exc
            next_revision = draft.revision + 1
            updated_draft = draft.model_copy(
                update={
                    "draft": validated.model_dump(mode="json"),
                    "revision": next_revision,
                    "updated_at": _now_utc(),
                },
                deep=True,
            )
            applied_patch = patch.model_copy(
                update={
                    "status": WorkflowPatchStatus.APPLIED,
                    "applied_revision": patch.base_revision,
                    "resulting_draft_revision": next_revision,
                    "updated_at": _now_utc(),
                },
                deep=True,
            )
            self._drafts[draft.workflow_draft_id] = updated_draft
            self._patches[workflow_patch_id] = applied_patch
            return applied_patch.model_copy(deep=True), updated_draft.model_copy(deep=True), False

    def reject_patch(self, workflow_patch_id: str, *, scope: Any, reason: str | None = None) -> tuple[WorkflowPatch, bool]:
        with self._lock:
            patch = self.get_patch(workflow_patch_id, scope=scope)
            if patch.status == WorkflowPatchStatus.REJECTED:
                return patch.model_copy(deep=True), True
            if patch.status == WorkflowPatchStatus.APPLIED:
                raise ProtocolError("WORKFLOW_PATCH_CONFLICT", "Applied workflow patch cannot be rejected.", {"status": patch.status})
            rejected = patch.model_copy(
                update={
                    "status": WorkflowPatchStatus.REJECTED,
                    "rejected_reason": reason,
                    "updated_at": _now_utc(),
                },
                deep=True,
            )
            self._patches[workflow_patch_id] = rejected
            return rejected.model_copy(deep=True), False

    def _save_draft_locked(
        self,
        draft: WorkflowDraft,
        draft_payload: dict[str, Any],
        *,
        key: TemplateKey,
        scope: Any,
        expected_revision: int | None,
    ) -> WorkflowDraft:
        if draft.status != WorkflowDraftStatus.EDITABLE:
            raise ProtocolError("WORKFLOW_PUBLISHED_IMMUTABLE", "Published draft cannot be edited.", {"workflow_draft_id": draft.workflow_draft_id})
        _check_revision(draft, expected_revision)
        validated = _validate_template_payload(draft_payload, scope=scope)
        if validated.workflow_template_id != draft.workflow_template_id:
            raise ProtocolError("WORKFLOW_SCHEMA_INVALID", "Draft template id cannot change.", {"workflow_template_id": draft.workflow_template_id})
        updated_draft = draft.model_copy(update={"draft": validated.model_dump(mode="json"), "revision": draft.revision + 1})
        self._drafts[draft.workflow_draft_id] = updated_draft
        return updated_draft

    def _require_template(self, key: TemplateKey) -> WorkflowTemplate:
        template = self._templates.get(key)
        if template is None:
            raise _not_found("WORKFLOW_TEMPLATE_NOT_FOUND", key[3])
        return template

    def _require_draft(self, workflow_draft_id: str | None) -> WorkflowDraft:
        if workflow_draft_id is None:
            raise ProtocolError("WORKFLOW_DRAFT_NOT_FOUND", "Workflow draft not found.", {"workflow_draft_id": None})
        draft = self._drafts.get(workflow_draft_id)
        if draft is None:
            raise _not_found("WORKFLOW_DRAFT_NOT_FOUND", workflow_draft_id)
        return draft

    def _ensure_not_archived(self, template: WorkflowTemplate) -> None:
        if template.status == WorkflowTemplateStatus.ARCHIVED:
            raise ProtocolError(
                "WORKFLOW_TEMPLATE_ARCHIVED",
                f"Workflow template is archived: {template.workflow_template_id}",
                {"workflow_template_id": template.workflow_template_id},
            )

    def _ensure_instance_scope(self, instance: WorkflowInstance, scope: Any) -> None:
        scope_key = _scope_key(scope)
        if (instance.app_id, instance.project_id, instance.workspace_id) != scope_key:
            raise ProtocolError("SCOPE_MISMATCH", "Workflow instance does not match requested scope.", {"resource": "workflow_instance_id"})


def _validate_template_payload(payload: dict[str, Any], *, scope: Any) -> WorkflowTemplate:
    if not isinstance(payload, dict):
        raise ProtocolError("WORKFLOW_SCHEMA_INVALID", "Workflow template payload must be an object.", {"reason": "invalid_payload"})
    _reject_forbidden_keys(payload)
    _reject_duplicate_station_artifact_contract_ids(payload)
    normalized = copy.deepcopy(payload)
    normalized["app_id"] = _scope_key(scope)[0]
    normalized["project_id"] = _scope_key(scope)[1]
    normalized["workspace_id"] = _scope_key(scope)[2]
    try:
        return WorkflowTemplate.model_validate(normalized)
    except Exception as exc:
        raise ProtocolError("WORKFLOW_SCHEMA_INVALID", str(exc), {"reason": "schema_validation_failed"}) from exc


def _reject_duplicate_station_artifact_contract_ids(payload: dict[str, Any]) -> None:
    stations = payload.get("stations")
    if not isinstance(stations, list):
        return
    for station in stations:
        if not isinstance(station, dict):
            continue
        contract_ids: list[str] = []
        for key in ("input_contracts", "output_contracts"):
            contracts = station.get(key)
            if not isinstance(contracts, list):
                continue
            for contract in contracts:
                if isinstance(contract, dict) and isinstance(contract.get("contract_id"), str):
                    contract_ids.append(contract["contract_id"])
        duplicates = sorted({contract_id for contract_id in contract_ids if contract_ids.count(contract_id) > 1})
        if duplicates:
            raise ProtocolError(
                "WORKFLOW_ARTIFACT_CONTRACT_INVALID",
                "Artifact contract_id must be unique within a station.",
                {
                    "station_id": station.get("station_id"),
                    "contract_ids": duplicates,
                },
            )


def _reject_forbidden_keys(value: Any) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = str(key).lower().replace("-", "_")
            if normalized in _FORBIDDEN_SCHEMA_KEYS or normalized.endswith("_token") or normalized.endswith("_secret"):
                raise ProtocolError("WORKFLOW_SCHEMA_INVALID", "Workflow schema contains forbidden field.", {"field": str(key)})
            _reject_forbidden_keys(item)
    elif isinstance(value, list):
        for item in value:
            _reject_forbidden_keys(item)


def _validate_patch_payload(operation: WorkflowPatchOperation | str, payload: dict[str, Any]) -> None:
    operation_value = str(operation.value if isinstance(operation, WorkflowPatchOperation) else operation)
    if not isinstance(payload, dict):
        raise ProtocolError("WORKFLOW_PATCH_INVALID", "Workflow patch payload must be an object.", {"operation": operation_value})
    allowed = _PATCH_ALLOWED_FIELDS.get(operation_value)
    required = _PATCH_REQUIRED_FIELDS.get(operation_value)
    if allowed is None or required is None:
        raise ProtocolError("WORKFLOW_PATCH_INVALID", "Unsupported workflow patch operation.", {"operation": operation_value})
    unknown = sorted(set(payload) - allowed)
    if unknown:
        raise ProtocolError("WORKFLOW_PATCH_INVALID", "Workflow patch payload contains unknown fields.", {"fields": unknown, "operation": operation_value})
    missing = sorted(field for field in required if field not in payload)
    if missing:
        raise ProtocolError("WORKFLOW_PATCH_INVALID", "Workflow patch payload is missing required fields.", {"fields": missing, "operation": operation_value})
    _reject_forbidden_keys(payload)


def _apply_patch_to_template_payload(draft_payload: dict[str, Any], operation: WorkflowPatchOperation | str, payload: dict[str, Any]) -> dict[str, Any]:
    _validate_patch_payload(operation, payload)
    operation_value = str(operation.value if isinstance(operation, WorkflowPatchOperation) else operation)
    next_payload = copy.deepcopy(draft_payload)
    stations = next_payload.setdefault("stations", [])
    edges = next_payload.setdefault("edges", [])
    quality_contracts = next_payload.setdefault("quality_contracts", [])
    if operation_value == WorkflowPatchOperation.ADD_STATION.value:
        station = copy.deepcopy(payload["station"])
        station_id = station.get("station_id") if isinstance(station, dict) else None
        if not isinstance(station_id, str) or not station_id:
            raise ProtocolError("WORKFLOW_PATCH_INVALID", "add_station requires station.station_id.", {"operation": operation_value})
        if any(station.get("station_id") == station_id for station in stations if isinstance(station, dict)):
            raise ProtocolError("WORKFLOW_PATCH_INVALID", "Station already exists.", {"station_id": station_id})
        stations.append(station)
        return next_payload
    if operation_value == WorkflowPatchOperation.REMOVE_STATION.value:
        station_id = str(payload["station_id"])
        if any(edge.get("from_station_id") == station_id or edge.get("to_station_id") == station_id for edge in edges if isinstance(edge, dict)):
            raise ProtocolError("WORKFLOW_PATCH_INVALID", "Cannot remove station referenced by workflow edge.", {"station_id": station_id})
        if not any(station.get("station_id") == station_id for station in stations if isinstance(station, dict)):
            raise ProtocolError("STATION_NOT_FOUND", "Station not found.", {"station_id": station_id})
        next_payload["stations"] = [station for station in stations if not (isinstance(station, dict) and station.get("station_id") == station_id)]
        return next_payload
    if operation_value in {
        WorkflowPatchOperation.UPDATE_STATION_PROMPT.value,
        WorkflowPatchOperation.UPDATE_CONNECTOR.value,
        WorkflowPatchOperation.UPDATE_ARTIFACT_CONTRACT.value,
        WorkflowPatchOperation.UPDATE_APPROVAL_POINT.value,
    }:
        station = _find_station(stations, str(payload["station_id"]))
        if operation_value == WorkflowPatchOperation.UPDATE_STATION_PROMPT.value:
            metadata = dict(station.get("metadata") or {})
            if "prompt_ref" in payload:
                metadata["prompt_ref"] = payload["prompt_ref"]
            if "prompt_patch" in payload:
                metadata["prompt_patch"] = payload["prompt_patch"]
            station["metadata"] = metadata
        elif operation_value == WorkflowPatchOperation.UPDATE_CONNECTOR.value:
            if "connector_refs" in payload:
                connector_refs = payload["connector_refs"]
                if not isinstance(connector_refs, list) or not all(isinstance(item, str) for item in connector_refs):
                    raise ProtocolError("WORKFLOW_PATCH_INVALID", "connector_refs must be a string list.", {"field": "connector_refs"})
                station["connector_refs"] = connector_refs
            if "connector_patch" in payload:
                metadata = dict(station.get("metadata") or {})
                metadata["connector_patch"] = payload["connector_patch"]
                station["metadata"] = metadata
        elif operation_value == WorkflowPatchOperation.UPDATE_ARTIFACT_CONTRACT.value:
            _update_artifact_contract(station, str(payload["contract_id"]), payload["contract_patch"])
        else:
            if "approval_required" in payload:
                if not isinstance(payload["approval_required"], bool):
                    raise ProtocolError("WORKFLOW_PATCH_INVALID", "approval_required must be a boolean.", {"field": "approval_required"})
                station["approval_required"] = payload["approval_required"]
            if "approval_policy" in payload:
                metadata = dict(station.get("metadata") or {})
                metadata["approval_policy"] = payload["approval_policy"]
                station["metadata"] = metadata
        return next_payload
    if operation_value == WorkflowPatchOperation.UPDATE_QUALITY_RULE.value:
        quality_contract = _find_quality_contract(quality_contracts, str(payload["quality_contract_id"]))
        patch = payload["quality_patch"]
        if not isinstance(patch, dict):
            raise ProtocolError("WORKFLOW_PATCH_INVALID", "quality_patch must be an object.", {"field": "quality_patch"})
        quality_contract.update(copy.deepcopy(patch))
        return next_payload
    if operation_value == WorkflowPatchOperation.UPDATE_EDGE.value:
        edge_patch = payload["edge_patch"]
        if not isinstance(edge_patch, dict):
            raise ProtocolError("WORKFLOW_PATCH_INVALID", "edge_patch must be an object.", {"field": "edge_patch"})
        station_ids = {station.get("station_id") for station in stations if isinstance(station, dict)}
        edge_id = str(payload["edge_id"])
        action = edge_patch.get("action", "update")
        if action not in {"add", "remove", "update"}:
            raise ProtocolError("WORKFLOW_PATCH_INVALID", "edge_patch.action must be add, remove, or update.", {"action": action})
        if action == "add":
            new_edge = copy.deepcopy(edge_patch)
            new_edge.pop("action", None)
            new_edge.setdefault("edge_id", edge_id)
            if new_edge.get("edge_id") != edge_id:
                raise ProtocolError("WORKFLOW_PATCH_INVALID", "edge_id must match edge_patch.edge_id.", {"edge_id": edge_id})
            if new_edge.get("from_station_id") not in station_ids or new_edge.get("to_station_id") not in station_ids:
                raise ProtocolError("WORKFLOW_PATCH_INVALID", "Workflow edge references missing station.", {"edge_id": edge_id})
            if new_edge.get("from_station_id") == new_edge.get("to_station_id"):
                raise ProtocolError("WORKFLOW_PATCH_INVALID", "Workflow edge cannot be a self-loop.", {"edge_id": edge_id})
            if any(
                edge.get("edge_id") == edge_id
                or (edge.get("from_station_id") == new_edge.get("from_station_id") and edge.get("to_station_id") == new_edge.get("to_station_id"))
                for edge in edges
                if isinstance(edge, dict)
            ):
                raise ProtocolError("WORKFLOW_PATCH_INVALID", "Workflow edge already exists.", {"edge_id": edge_id})
            edges.append(new_edge)
            return next_payload
        edge = _find_edge(edges, edge_id)
        if action == "remove":
            next_payload["edges"] = [item for item in edges if not (isinstance(item, dict) and item.get("edge_id") == edge_id)]
            return next_payload
        patch = copy.deepcopy(edge_patch)
        patch.pop("action", None)
        edge.update(patch)
        if edge.get("from_station_id") not in station_ids or edge.get("to_station_id") not in station_ids:
            raise ProtocolError("WORKFLOW_PATCH_INVALID", "Updated edge references missing station.", {"edge_id": edge.get("edge_id")})
        if edge.get("from_station_id") == edge.get("to_station_id"):
            raise ProtocolError("WORKFLOW_PATCH_INVALID", "Workflow edge cannot be a self-loop.", {"edge_id": edge.get("edge_id")})
        return next_payload
    raise ProtocolError("WORKFLOW_PATCH_INVALID", "Unsupported workflow patch operation.", {"operation": operation_value})


def _find_station(stations: list[Any], station_id: str) -> dict[str, Any]:
    for station in stations:
        if isinstance(station, dict) and station.get("station_id") == station_id:
            return station
    raise ProtocolError("STATION_NOT_FOUND", "Station not found.", {"station_id": station_id})


def _find_edge(edges: list[Any], edge_id: str) -> dict[str, Any]:
    for edge in edges:
        if isinstance(edge, dict) and edge.get("edge_id") == edge_id:
            return edge
    raise ProtocolError("WORKFLOW_PATCH_INVALID", "Workflow edge not found.", {"edge_id": edge_id})


def _find_quality_contract(quality_contracts: list[Any], contract_id: str) -> dict[str, Any]:
    for contract in quality_contracts:
        if isinstance(contract, dict) and contract.get("contract_id") == contract_id:
            return contract
    raise ProtocolError("WORKFLOW_PATCH_INVALID", "Quality contract not found.", {"quality_contract_id": contract_id})


def _update_artifact_contract(station: dict[str, Any], contract_id: str, contract_patch: Any) -> None:
    if not isinstance(contract_patch, dict):
        raise ProtocolError("WORKFLOW_PATCH_INVALID", "contract_patch must be an object.", {"field": "contract_patch"})
    for key in ("input_contracts", "output_contracts"):
        contracts = station.get(key)
        if not isinstance(contracts, list):
            continue
        for contract in contracts:
            if isinstance(contract, dict) and contract.get("contract_id") == contract_id:
                contract.update(copy.deepcopy(contract_patch))
                return
    raise ProtocolError("WORKFLOW_ARTIFACT_CONTRACT_MISSING", "Artifact contract not found.", {"contract_id": contract_id})


def _check_revision(draft: WorkflowDraft, expected_revision: int | None) -> None:
    if expected_revision is not None and expected_revision != draft.revision:
        raise ProtocolError(
            "WORKFLOW_DRAFT_CONFLICT",
            "Workflow draft revision conflict.",
            {"expected_revision": expected_revision, "actual_revision": draft.revision},
        )


def _scope_key(scope: Any) -> ScopeKey:
    return (str(scope.app_id), getattr(scope, "project_id", None), getattr(scope, "workspace_id", None))


def _template_key(template: WorkflowTemplate) -> TemplateKey:
    return (template.app_id, template.project_id, template.workspace_id, template.workflow_template_id)


def _key_from_scope(scope: Any, workflow_template_id: str) -> TemplateKey:
    app_id, project_id, workspace_id = _scope_key(scope)
    return (app_id, project_id, workspace_id, workflow_template_id)


def _not_found(code: str, identifier: str) -> ProtocolError:
    return ProtocolError(code, f"Workflow resource not found: {identifier}", {"id": identifier})


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)
