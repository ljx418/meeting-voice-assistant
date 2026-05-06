from __future__ import annotations

import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from apps.gateway.approvals import ApprovalStore
from apps.gateway.artifacts import ArtifactRegistry
from apps.gateway.retries import RetryStore
from apps.gateway.storage import GatewaySessionStore


class SnapshotSession:
    session_id = "sess_persist"
    model = "fake-model"
    state = "idle"
    backend = "simple"
    interrupted = False
    agent = None
    bundle = None

    def __init__(self, stamp):
        self.created_at = stamp
        self.last_active_at = stamp


def test_approval_store_concurrent_requests_are_not_lost(tmp_path):
    store = ApprovalStore(tmp_path / "approvals")

    def create(index: int):
        return store.request(
            action="workspace.write",
            request_summary=f"request {index}",
            trace_id=f"trace_{index}",
        )

    with ThreadPoolExecutor(max_workers=8) as executor:
        records = list(executor.map(create, range(40)))

    index = json.loads((tmp_path / "approvals" / "index.json").read_text(encoding="utf-8"))
    assert len(index) == 40
    assert {record["approval_id"] for record in records} == {record["approval_id"] for record in index}


def test_retry_store_concurrent_policy_contexts_are_not_lost(tmp_path):
    store = RetryStore(tmp_path / "retries")

    def create(index: int):
        return store.create_policy_context(
            session_id="sess",
            turn_id=f"turn_{index}",
            user_input=f"请写入 file_{index}.txt",
            domain=None,
            trace_id=f"trace_{index}",
            approval_id=f"appr_{index}",
            policy={"requires_approval": True},
        )

    with ThreadPoolExecutor(max_workers=8) as executor:
        records = list(executor.map(create, range(40)))

    index = json.loads((tmp_path / "retries" / "index.json").read_text(encoding="utf-8"))
    assert len(index) == 40
    assert {record["retry_id"] for record in records} == {record["retry_id"] for record in index}


def test_retry_store_reserves_context_once(tmp_path):
    store = RetryStore(tmp_path / "retries")
    record = store.create_policy_context(
        session_id="sess",
        turn_id="turn",
        user_input="请写入 file.txt",
        domain=None,
        trace_id="trace",
        approval_id="appr",
        policy={"requires_approval": True},
    )

    reserved = store.mark_retrying(record["retry_id"])
    assert reserved["status"] == "retrying"

    try:
        store.mark_retrying(record["retry_id"])
    except Exception as exc:
        assert "not pending" in str(exc)
    else:
        raise AssertionError("retry context should only be reserved once")


def test_artifact_registry_concurrent_registers_are_not_lost(tmp_path):
    artifact_file = tmp_path / "source.txt"
    artifact_file.write_text("hello", encoding="utf-8")
    registry = ArtifactRegistry(tmp_path / "artifacts")

    def register(index: int):
        return registry.register_file(str(artifact_file), session_id=f"sess_{index}", kind="note")

    with ThreadPoolExecutor(max_workers=8) as executor:
        records = list(executor.map(register, range(40)))

    index = json.loads((tmp_path / "artifacts" / "index.json").read_text(encoding="utf-8"))
    assert len(index) == 40
    assert {record["artifact_id"] for record in records} == {record["artifact_id"] for record in index}


def test_session_snapshot_is_atomic_and_readable(tmp_path):
    from datetime import datetime

    store = GatewaySessionStore(tmp_path / "sessions")
    session = SnapshotSession(datetime.now())
    store.save_snapshot(session)

    snapshot = store.load_snapshot("sess_persist")
    assert snapshot["session_id"] == "sess_persist"
    assert snapshot["backend"] == "simple"


def test_session_snapshot_masks_agent_messages(tmp_path):
    from datetime import datetime

    store = GatewaySessionStore(tmp_path / "sessions")
    session = SnapshotSession(datetime.now())
    session.agent = type(
        "Agent",
        (),
        {"messages": [{"role": "user", "content": "secret sk-test-1234567890"}]},
    )()

    store.save_snapshot(session)
    snapshot_text = (tmp_path / "sessions" / "sess_persist" / "snapshot.json").read_text(encoding="utf-8")

    assert "sk-test-1234567890" not in snapshot_text
    assert "[REDACTED]" in snapshot_text


def test_session_store_rejects_path_traversal_session_id(tmp_path):
    store = GatewaySessionStore(tmp_path / "sessions")

    try:
        store.load_snapshot("../outside")
    except ValueError as exc:
        assert "Invalid session_id" in str(exc)
    else:
        raise AssertionError("path traversal session id should fail")
