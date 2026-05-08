import json
import asyncio

import pytest


@pytest.mark.asyncio
async def test_data_service_mcp_lists_quality_tools():
    pytest.importorskip("mcp")
    from data_service import mcp_stdio

    tools = await mcp_stdio.list_tools()

    assert {tool.name for tool in tools} >= {
        "knowledge_ingest",
        "knowledge_query",
        "knowledge_quality_summary",
        "knowledge_correction_plan",
        "knowledge_quality_feedback",
        "knowledge_correction_rules",
        "knowledge_review_correction_rule",
        "knowledge_ingest_v2",
        "knowledge_query_v2",
        "knowledge_quality_summary_v2",
        "knowledge_correction_plan_v2",
        "knowledge_quality_feedback_v2",
        "knowledge_correction_rules_v2",
        "knowledge_review_correction_rule_v2",
        "knowledge_workspace_create",
        "knowledge_workspace_list",
        "knowledge_workspace_describe",
        "knowledge_workspace_archive",
        "knowledge_source_import",
        "knowledge_source_list",
        "knowledge_source_remove",
        "knowledge_build_start",
        "knowledge_build_status",
        "knowledge_build_cancel",
    }


@pytest.mark.asyncio
async def test_data_service_mcp_workspace_lifecycle(monkeypatch, tmp_path):
    pytest.importorskip("mcp")
    from data_service import mcp_stdio

    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))

    created = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_workspace_create",
                {"name": "Project Knowledge", "owner": "harness", "tags": ["demo"]},
            )
        )[0].text
    )
    assert created["status"] == "ok"
    assert created["workspace_id"] == "project-knowledge"
    assert created["operation_id"] is None
    assert created["warnings"] == []
    assert created["data"]["capabilities"]["build"] is True

    listed = json.loads((await mcp_stdio.call_tool("knowledge_workspace_list", {"owner": "harness"}))[0].text)
    assert listed["data"]["items"][0]["workspace_id"] == "project-knowledge"

    described = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_workspace_describe",
                {"workspace_id": "project-knowledge"},
            )
        )[0].text
    )
    assert described["workspace_id"] == "project-knowledge"
    assert "layout" in described["data"]
    assert "engines" in described["data"]

    archived = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_workspace_archive",
                {"workspace_id": "project-knowledge", "reason": "test done"},
            )
        )[0].text
    )
    assert archived["data"]["workspace"]["status"] == "archived"

    archived_feedback = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_quality_feedback_v2",
                {
                    "workspace_id": "project-knowledge",
                    "target_type": "source",
                    "target_id": "x",
                    "action": "note",
                },
            )
        )[0].text
    )
    assert archived_feedback["status"] == "blocked"


@pytest.mark.asyncio
async def test_data_service_mcp_source_import_is_idempotent(monkeypatch, tmp_path):
    pytest.importorskip("mcp")
    from data_service import mcp_stdio

    root = tmp_path / "managed"
    source_root = tmp_path / "sources"
    source_root.mkdir()
    source_file = source_root / "note.md"
    source_file.write_text("# Note\n\nHarness MCP source.", encoding="utf-8")
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_SOURCE_ROOTS", str(source_root))

    created = json.loads((await mcp_stdio.call_tool("knowledge_workspace_create", {"name": "Import KB"}))[0].text)
    workspace_id = created["workspace_id"]

    first = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_source_import",
                {"workspace_id": workspace_id, "paths": [str(source_file)]},
            )
        )[0].text
    )
    assert first["status"] == "ok"
    assert first["data"]["sources"][0]["status"] == "imported"
    assert first["data"]["sources"][0]["sha256"]
    source_id = first["data"]["sources"][0]["source_id"]

    second = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_source_import",
                {"workspace_id": workspace_id, "paths": [str(source_file)]},
            )
        )[0].text
    )
    assert second["data"]["sources"][0]["status"] == "duplicate"
    assert second["data"]["sources"][0]["source_id"] == source_id

    listed = json.loads((await mcp_stdio.call_tool("knowledge_source_list", {"workspace_id": workspace_id}))[0].text)
    assert len(listed["data"]["items"]) == 1
    assert listed["data"]["items"][0]["source_id"] == source_id


@pytest.mark.asyncio
async def test_data_service_mcp_source_import_rejects_disallowed_and_symlink(monkeypatch, tmp_path):
    pytest.importorskip("mcp")
    from data_service import mcp_stdio

    root = tmp_path / "managed"
    allowed = tmp_path / "allowed"
    outside = tmp_path / "outside"
    allowed.mkdir()
    outside.mkdir()
    outside_file = outside / "secret.md"
    outside_file.write_text("secret", encoding="utf-8")
    symlink = allowed / "escape.md"
    symlink.symlink_to(outside_file)
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_SOURCE_ROOTS", str(allowed))

    created = json.loads((await mcp_stdio.call_tool("knowledge_workspace_create", {"name": "Secure KB"}))[0].text)
    workspace_id = created["workspace_id"]

    outside_result = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_source_import",
                {"workspace_id": workspace_id, "paths": [str(outside_file)]},
            )
        )[0].text
    )
    assert outside_result["status"] == "blocked"
    assert "Source path is outside allowed roots" in outside_result["warnings"][0]

    symlink_result = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_source_import",
                {"workspace_id": workspace_id, "paths": [str(symlink)]},
            )
        )[0].text
    )
    assert symlink_result["status"] == "blocked"
    assert "Source path is outside allowed roots" in symlink_result["warnings"][0]


@pytest.mark.asyncio
async def test_data_service_mcp_build_operation_lifecycle(monkeypatch, tmp_path):
    pytest.importorskip("mcp")
    from data_service import mcp_stdio

    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(tmp_path / "managed"))
    source_root = tmp_path / "sources"
    source_root.mkdir()
    source_file = source_root / "build.md"
    source_file.write_text("# Build Note\n\nHarness build content.", encoding="utf-8")
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_SOURCE_ROOTS", str(source_root))
    created = json.loads((await mcp_stdio.call_tool("knowledge_workspace_create", {"name": "Build KB"}))[0].text)
    workspace_id = created["workspace_id"]
    await mcp_stdio.call_tool("knowledge_source_import", {"workspace_id": workspace_id, "paths": [str(source_file)]})

    started = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_build_start",
                {"workspace_id": workspace_id, "mode": "llmwiki_only"},
            )
        )[0].text
    )
    assert started["status"] == "queued"
    assert started["operation_id"]
    assert started["data"]["stage"] == "queued"
    operation_id = started["operation_id"]

    status = None
    for _ in range(80):
        status = json.loads(
            (
                await mcp_stdio.call_tool(
                    "knowledge_build_status",
                    {"workspace_id": workspace_id, "operation_id": operation_id},
                )
            )[0].text
        )
        if status["status"] in {"completed", "failed", "blocked"}:
            break
        await asyncio.sleep(0.05)
    assert status is not None
    assert status["status"] == "completed"
    assert status["data"]["stage"] == "completed"
    assert status["data"]["progress"] == 1.0
    assert status["data"]["retryable"] is False

    sources = json.loads((await mcp_stdio.call_tool("knowledge_source_list", {"workspace_id": workspace_id}))[0].text)
    assert sources["data"]["items"][0]["ingest_status"] == "built"

    completed_cancel = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_build_cancel",
                {"workspace_id": workspace_id, "operation_id": operation_id, "reason": "test"},
            )
        )[0].text
    )
    assert completed_cancel["status"] == "completed"
    assert completed_cancel["warnings"]


@pytest.mark.asyncio
async def test_data_service_mcp_build_cancel_queued_operation(monkeypatch, tmp_path):
    pytest.importorskip("mcp")
    from data_service import mcp_stdio

    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(tmp_path / "managed"))
    created = json.loads((await mcp_stdio.call_tool("knowledge_workspace_create", {"name": "Cancel KB"}))[0].text)
    workspace_id = created["workspace_id"]
    started = json.loads((await mcp_stdio.call_tool("knowledge_build_start", {"workspace_id": workspace_id}))[0].text)
    cancelled = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_build_cancel",
                {"workspace_id": workspace_id, "operation_id": started["operation_id"], "reason": "test"},
            )
        )[0].text
    )
    assert cancelled["status"] in {"cancelled", "blocked"}


@pytest.mark.asyncio
async def test_data_service_mcp_build_operations_queue_by_workspace(monkeypatch, tmp_path):
    pytest.importorskip("mcp")
    from data_service import mcp_stdio

    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(tmp_path / "managed"))
    source_root = tmp_path / "sources"
    source_root.mkdir()
    source_file = source_root / "queue.md"
    source_file.write_text("# Queue Note\n\nBuild queue fixture.", encoding="utf-8")
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_SOURCE_ROOTS", str(source_root))

    workspace_id = json.loads((await mcp_stdio.call_tool("knowledge_workspace_create", {"name": "Queue KB"}))[0].text)["workspace_id"]
    await mcp_stdio.call_tool("knowledge_source_import", {"workspace_id": workspace_id, "paths": [str(source_file)]})

    first = json.loads((await mcp_stdio.call_tool("knowledge_build_start", {"workspace_id": workspace_id, "mode": "llmwiki_only"}))[0].text)
    second = json.loads((await mcp_stdio.call_tool("knowledge_build_start", {"workspace_id": workspace_id, "mode": "llmwiki_only"}))[0].text)

    assert first["status"] == "queued"
    assert second["status"] == "queued"
    assert first["operation_id"] != second["operation_id"]

    final = {}
    for operation_id in (first["operation_id"], second["operation_id"]):
        for _ in range(100):
            status = json.loads(
                (
                    await mcp_stdio.call_tool(
                        "knowledge_build_status",
                        {"workspace_id": workspace_id, "operation_id": operation_id},
                    )
                )[0].text
            )
            if status["status"] in {"completed", "failed", "blocked", "cancelled"}:
                final[operation_id] = status
                break
            await asyncio.sleep(0.05)

    assert final[first["operation_id"]]["status"] == "completed"
    assert final[second["operation_id"]]["status"] == "completed"


@pytest.mark.asyncio
async def test_data_service_mcp_marks_interrupted_running_operation_retryable(monkeypatch, tmp_path):
    pytest.importorskip("mcp")
    from data_service import mcp_stdio

    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(tmp_path / "managed"))
    created = json.loads((await mcp_stdio.call_tool("knowledge_workspace_create", {"name": "Interrupted KB"}))[0].text)
    workspace_id = created["workspace_id"]
    workspace_path = tmp_path / "managed" / workspace_id
    operation_id = "op_interrupted"
    operation_path = workspace_path / "lifecycle" / "operations" / f"{operation_id}.json"
    operation_path.parent.mkdir(parents=True, exist_ok=True)
    operation_path.write_text(
        json.dumps(
            {
                "operation_id": operation_id,
                "workspace_id": workspace_id,
                "mode": "full",
                "status": "running",
                "stage": "distill",
                "progress": 0.25,
                "error": None,
                "retryable": True,
                "artifacts": [],
                "created_at": "2026-05-02T00:00:00Z",
                "updated_at": "2026-05-02T00:00:00Z",
            }
        ),
        encoding="utf-8",
    )

    started = json.loads((await mcp_stdio.call_tool("knowledge_build_start", {"workspace_id": workspace_id}))[0].text)
    assert started["status"] == "queued"

    interrupted = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_build_status",
                {"workspace_id": workspace_id, "operation_id": operation_id},
            )
        )[0].text
    )
    assert interrupted["status"] == "failed"
    assert interrupted["data"]["retryable"] is True
    assert interrupted["data"]["error"]["type"] == "server_interrupted"


@pytest.mark.asyncio
async def test_data_service_mcp_lifecycle_workspaces_are_isolated(monkeypatch, tmp_path):
    pytest.importorskip("mcp")
    from data_service import mcp_stdio

    root = tmp_path / "managed"
    source_root = tmp_path / "sources"
    source_root.mkdir()
    source_a = source_root / "a.md"
    source_a.write_text("A", encoding="utf-8")
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_SOURCE_ROOTS", str(source_root))

    workspace_a = json.loads((await mcp_stdio.call_tool("knowledge_workspace_create", {"name": "A"}))[0].text)["workspace_id"]
    workspace_b = json.loads((await mcp_stdio.call_tool("knowledge_workspace_create", {"name": "B"}))[0].text)["workspace_id"]
    await mcp_stdio.call_tool("knowledge_source_import", {"workspace_id": workspace_a, "paths": [str(source_a)]})

    sources_a = json.loads((await mcp_stdio.call_tool("knowledge_source_list", {"workspace_id": workspace_a}))[0].text)
    sources_b = json.loads((await mcp_stdio.call_tool("knowledge_source_list", {"workspace_id": workspace_b}))[0].text)

    assert len(sources_a["data"]["items"]) == 1
    assert sources_b["data"]["items"] == []


@pytest.mark.asyncio
async def test_data_service_mcp_existing_tools_accept_workspace_id(monkeypatch, tmp_path):
    pytest.importorskip("mcp")
    from data_service import mcp_stdio

    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(tmp_path / "managed"))
    created = json.loads((await mcp_stdio.call_tool("knowledge_workspace_create", {"name": "Opaque ID KB"}))[0].text)
    workspace_id = created["workspace_id"]
    imported = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_source_import",
                {
                    "workspace_id": workspace_id,
                    "texts": [
                        {
                            "title": "Harness Note",
                            "content": "# Harness Note\n\nOpaque workspace id query content.",
                            "metadata": {"kind": "fixture"},
                        }
                    ],
                },
            )
        )[0].text
    )
    assert imported["data"]["sources"][0]["status"] == "imported"

    started = json.loads((await mcp_stdio.call_tool("knowledge_build_start", {"workspace_id": workspace_id, "mode": "llmwiki_only"}))[0].text)
    for _ in range(80):
        status = json.loads(
            (
                await mcp_stdio.call_tool(
                    "knowledge_build_status",
                    {"workspace_id": workspace_id, "operation_id": started["operation_id"]},
                )
            )[0].text
        )
        if status["status"] in {"completed", "failed", "blocked"}:
            break
        await asyncio.sleep(0.05)
    assert status["status"] == "completed"

    query = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_query",
                {"workspace_id": workspace_id, "query": "Opaque workspace", "mode": "llmwiki", "top_k": 3},
            )
        )[0].text
    )
    assert query["mode"] == "llmwiki"

    feedback = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_quality_feedback",
                {
                    "workspace_id": workspace_id,
                    "target_type": "source",
                    "target_id": imported["data"]["sources"][0]["source_id"],
                    "action": "note",
                    "reason": "workspace_id feedback path",
                },
            )
        )[0].text
    )
    assert feedback["workspace"].endswith(workspace_id)

    summary = json.loads((await mcp_stdio.call_tool("knowledge_quality_summary", {"workspace_id": workspace_id}))[0].text)
    assert summary["quality"]["manual_feedback"]["feedback_count"] == 1

    query_v2 = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_query_v2",
                {"workspace_id": workspace_id, "query": "Opaque workspace", "mode": "llmwiki", "top_k": 3},
            )
        )[0].text
    )
    assert query_v2["status"] == "ok"
    assert query_v2["workspace_id"] == workspace_id
    assert query_v2["data"]["mode"] == "llmwiki"

    feedback_v2 = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_quality_feedback_v2",
                {
                    "workspace_id": workspace_id,
                    "target_type": "source",
                    "target_id": imported["data"]["sources"][0]["source_id"],
                    "action": "note",
                    "reason": "v2 envelope feedback path",
                },
            )
        )[0].text
    )
    assert feedback_v2["status"] == "ok"
    assert feedback_v2["data"]["workspace"].endswith(workspace_id)

    summary_v2 = json.loads((await mcp_stdio.call_tool("knowledge_quality_summary_v2", {"workspace_id": workspace_id}))[0].text)
    assert summary_v2["status"] == "ok"
    assert summary_v2["data"]["quality"]["manual_feedback"]["feedback_count"] == 2


@pytest.mark.asyncio
async def test_data_service_mcp_lifecycle_unknown_ids_return_blocked(monkeypatch, tmp_path):
    pytest.importorskip("mcp")
    from data_service import mcp_stdio

    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(tmp_path / "managed"))
    workspace_id = json.loads((await mcp_stdio.call_tool("knowledge_workspace_create", {"name": "Blocked KB"}))[0].text)["workspace_id"]

    unknown_source = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_source_remove",
                {"workspace_id": workspace_id, "source_id": "missing"},
            )
        )[0].text
    )
    assert unknown_source["status"] == "blocked"
    assert "Unknown source_id" in unknown_source["warnings"][0]

    unknown_operation = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_build_status",
                {"workspace_id": workspace_id, "operation_id": "missing"},
            )
        )[0].text
    )
    assert unknown_operation["status"] == "blocked"
    assert "Unknown operation_id" in unknown_operation["warnings"][0]


@pytest.mark.asyncio
async def test_data_service_mcp_quality_feedback_review_and_plan(tmp_path):
    pytest.importorskip("mcp")
    from data_service import mcp_stdio

    workspace = tmp_path / "workspace"
    feedback_content = await mcp_stdio.call_tool(
        "knowledge_quality_feedback",
        {
            "workspace": str(workspace),
            "target_type": "entity",
            "target_id": "old-topic",
            "action": "merge_suggest",
            "label": "Old Topic",
            "suggested_value": "Canonical Topic",
            "reason": "Agent 识别为同一 topic",
            "metadata": {"source": "mcp-test"},
        },
    )
    feedback = json.loads(feedback_content[0].text)
    assert feedback["target_type"] == "entity"
    assert feedback["metadata"]["source"] == "mcp-test"

    rules_content = await mcp_stdio.call_tool(
        "knowledge_correction_rules",
        {"workspace": str(workspace), "limit": 10},
    )
    rules = json.loads(rules_content[0].text)
    assert rules["total_count"] == 1
    rule_id = rules["items"][0]["rule_id"]

    review_content = await mcp_stdio.call_tool(
        "knowledge_review_correction_rule",
        {
            "workspace": str(workspace),
            "rule_id": rule_id,
            "status": "approved",
            "reviewer": "agent",
            "note": "受控批准",
        },
    )
    reviewed = json.loads(review_content[0].text)
    assert reviewed["rule"]["status"] == "approved"
    assert reviewed["correction_plan"]["source_rule_count"] == 1

    plan_content = await mcp_stdio.call_tool(
        "knowledge_correction_plan",
        {"workspace": str(workspace)},
    )
    plan = json.loads(plan_content[0].text)
    assert plan["source_rule_count"] == 1
    assert plan["summary"]["action_count"] == 1
    assert plan["actions"][0]["impact"]["summary"]["total_matches"] == 0

    summary_content = await mcp_stdio.call_tool(
        "knowledge_quality_summary",
        {"workspace": str(workspace)},
    )
    summary = json.loads(summary_content[0].text)
    assert summary["quality"]["manual_feedback"]["feedback_count"] == 1
    assert summary["quality"]["correction_rules"]["status_counts"]["approved"] == 1
    assert summary["quality_correction_plan"]["summary"]["action_count"] == 1


@pytest.mark.asyncio
async def test_data_service_mcp_rejects_unbounded_query_limits(tmp_path):
    pytest.importorskip("mcp")
    from data_service import mcp_stdio

    with pytest.raises(ValueError, match="top_k must be between 1 and 50"):
        await mcp_stdio.call_tool(
            "knowledge_query",
            {"workspace": str(tmp_path / "workspace"), "query": "test", "top_k": 1000000},
        )


@pytest.mark.asyncio
async def test_data_service_mcp_keeps_per_call_workspaces_isolated(tmp_path):
    pytest.importorskip("mcp")
    from data_service import mcp_stdio

    workspace_a = tmp_path / "workspace-a"
    workspace_b = tmp_path / "workspace-b"
    await mcp_stdio.call_tool(
        "knowledge_quality_feedback",
        {
            "workspace": str(workspace_a),
            "target_type": "entity",
            "target_id": "a",
            "action": "rename_suggest",
            "suggested_value": "A",
        },
    )

    summary_a = json.loads((await mcp_stdio.call_tool("knowledge_quality_summary", {"workspace": str(workspace_a)}))[0].text)
    summary_b = json.loads((await mcp_stdio.call_tool("knowledge_quality_summary", {"workspace": str(workspace_b)}))[0].text)

    assert summary_a["quality"]["manual_feedback"]["feedback_count"] == 1
    assert summary_b["quality"]["manual_feedback"]["feedback_count"] == 0
