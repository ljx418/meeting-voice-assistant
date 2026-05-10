# Phase 5-C Connector Execution Runtime

## Current Implementation Scope

Phase 5-C now has a minimal connector execution runtime in harnessOS.

Implemented:

- Connector job lifecycle RPC:
  - `connector.submit`
  - `connector.poll`
  - `connector.cancel`
  - `connector.collect`
- Core job/event integration:
  - submit creates a Core `JobRecord`
  - lifecycle events are written through `job.queued`, `job.running`, `job.completed`, `job.cancelled`
  - collect returns Core artifacts and lineage
- Artifact governance:
  - connector outputs are written under the gateway artifact root
  - outputs are registered through `ArtifactRegistry`
  - Core artifact records are created through `CoreAppService`
- Lightweight acceptance connector:
  - `data_service_mcp` supports contract-stub execution for declared tools
  - `funasr_mcp` supports contract-stub execution for declared FunASR MCP tools
  - `defer=true` allows a running job to be cancelled for lifecycle acceptance
- Gated real MCP stdio execution:
  - `HARNESS_DATA_SERVICE_MCP_EXECUTION=stdio` enables stdio MCP tool calls for `data_service_mcp`
  - multi-step Knowledge acceptance uses a persistent MCP stdio session so data_service build queue state survives `knowledge_build_start -> knowledge_build_status`
  - default local/CI behavior remains contract-stub mode
  - MCP `content[].text` JSON is decoded and written into governed connector result artifacts

## External MCP Sources

The Phase 5-C MCP execution path must treat the adjacent `meeting-voice-assistant` project as the source of truth for two domain connectors:

- Meeting / ASR: `funasr_mcp` starts `python3 -m funasr_service.mcp_stdio` under `/Users/Zhuanz/Desktop/workspace/voice_service` and calls the existing FunASR HTTP service through MCP tools.
- Knowledge: `data_service_mcp` starts `python3 -m data_service.mcp_stdio` under `/Users/Zhuanz/Desktop/workspace/data_service/backend` and follows `/Users/Zhuanz/Desktop/workspace/data_service/docs/MCP-EXTERNAL-AGENT-GUIDE.md`.

Knowledge workflows must use the documented lifecycle tools and v2 envelope tools instead of writing GraphRAG, llmwiki, source, or quality directories directly.

## Explicit Boundary

This phase now has gated stdio execution paths for both `data_service_mcp` and `funasr_mcp`. They are not enabled by default. Historical local end-to-end acceptance against the real adjacent data_service server and the real FunASR HTTP service has passed, but current repository-local regression still depends on those adjacent services being started when the explicit real-audio acceptance tests are executed. Phase 5-D uses these connector execution paths from the Meeting and Knowledge workflows when explicitly enabled.

The default `data_service_mcp` and `funasr_mcp` execution paths are still contract-stub mode:

- it validates connector/tool availability against the registered connector descriptor
- it records a governed connector job
- it writes a structured connector result artifact
- it marks execution as deferred when connector health is `contract_stub`

Phase 5-D MCP stdio execution increments now covered in code:

- spawn and manage `funasr_service.mcp_stdio`
- initialize MCP session
- call tools through MCP protocol
- map MCP tool results into connector job events and artifacts
- keep real execution behind `HARNESS_FUNASR_MCP_EXECUTION=stdio`
- route Meeting workflow transcription through `funasr_mcp.funasr_recognize_file`
- register a governed transcript artifact with `connector_id`, connector job id, upstream connector result artifact id, and transcription mode metadata
- pass connector result artifacts through `parent_artifact_ids` so cross-domain lineage can connect Meeting transcript/minutes to Knowledge source/build/query artifacts

## Acceptance Coverage

Current acceptance criteria covered:

- submit -> poll -> collect lifecycle works for a lightweight connector
- connector execution writes Core job/events
- connector execution produces artifact records
- collect returns artifact lineage
- cancel transitions a deferred running job to a terminal state
- Remote ComfyUI not configured does not block default gateway tests
- Gated data_service stdio execution can call a MCP `tools/call` path and persist the decoded envelope in a connector result artifact
- Real data_service MCP lifecycle acceptance passed through persistent stdio session:
  `create -> import -> build -> poll -> query_v2 -> feedback_v2 -> correction_rules_v2 -> review_v2 -> correction_plan_v2 -> archive`
- Real FunASR MCP smoke passed through stdio:
  `funasr_health -> funasr_recognize_file`
- Real cross-domain acceptance passed:
  `audio -> funasr_mcp transcript -> meeting minutes -> data_service_mcp import/build/query`

## Phase 5-D Acceptance Evidence

Real local validation on 2026-05-05:

- FunASR service: started real adjacent `funasr_service.main` on `127.0.0.1:8001`; the adjacent `venv312` did not contain `funasr`, so the service was started with system `python3`.
- FunASR MCP smoke: `scripts/e2e_funasr_mcp_validation.py` returned `status=ok`, connector job `job_db4b4114eab3`, artifact `art_5f24f94bfbdc`.
- Data Service MCP smoke: `scripts/e2e_data_service_mcp_validation.py` returned `status=ok`, workspace `harnessos-real-data-service-phase5d`, operation `op_7df6de70eb14`.
- Cross-domain smoke: `scripts/e2e_meeting_to_knowledge_mcp_validation.py` returned `status=ok`, session `sess_333527af725f`, meeting session `meeting_cceef461`, workspace `harnessos-meeting-knowledge-phase5d-retry`, artifact lineage count `33`.
- During real cross-domain validation, the Meeting workflow exposed a real gap: text-analysis/minutes mode did not always produce a transcript artifact. The fix writes a governed FunASR transcript artifact before Knowledge import, so transcript lineage does not depend on the external Meeting MCP output shape.

Recommended next implementation slice:

1. Keep contract-stub as the default fallback for local development and CI.
2. Use `scripts/e2e_funasr_mcp_validation.py` for real `funasr_health -> funasr_recognize_file` smoke.
3. Use `scripts/e2e_data_service_mcp_validation.py` for real data_service lifecycle smoke.
4. Use `scripts/e2e_meeting_to_knowledge_mcp_validation.py` for Phase 5-D cross-domain workflow acceptance.
5. Keep Remote ComfyUI deferred until a remote execution environment is available.

## Data Service Phase 4 Acceptance Conclusion

Based on the data_service developer report, data_service Phase 4 is accepted as **implemented and internally validated**:

- MCP baseline: `14 passed`
- Data Service/API/MCP baseline: `74 passed, 14 skipped`
- LLMWiki baseline: `34 passed`
- lifecycle tools, v2 envelope tools, compatibility tools, build queue, path safety, archived workspace semantics, `blocked` error contract, and opaque `workspace_id` workflow are all in scope and reported implemented.

External Harness status is **accepted** as of 2026-05-02 local validation:

- Command path: `HARNESS_DATA_SERVICE_MCP_EXECUTION=stdio` with `HARNESS_DATA_SERVICE_MCP_COMMAND=venv312/bin/python`.
- Managed workspace root: `/tmp/harnessos-data-service-workspaces`.
- Real run: `HarnessOSRealDataServiceAcceptance4`.
- Result: `status=ok`, `workspace_id=harnessosrealdataserviceacceptance4`, `operation_id=op_fb639a7aee3c`, `warnings=[]`.
- Covered tools: `knowledge_workspace_create`, `knowledge_source_import`, `knowledge_build_start`, repeated `knowledge_build_status`, `knowledge_query_v2`, `knowledge_quality_feedback_v2`, `knowledge_correction_rules_v2`, `knowledge_review_correction_rule_v2`, `knowledge_correction_plan_v2`, `knowledge_workspace_archive`.

Environment note: the adjacent data_service virtualenv must have `backend/requirements.txt` installed. Earlier real runs failed at build time with missing `numpy` and `pandas`; installing the full requirements resolved the blocker.
