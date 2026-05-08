# Workspace Migration

This project was extracted from `meeting-voice-assistant` into `~/Desktop/workspace/data_service` and is now treated as an independent MCP-first Local Knowledge Governance Service.

Migrated into this workspace:
- standalone backend code under `backend/`
- project docs from `meeting-voice-assistant/docs/data_service/`
- architecture archive from `meeting-voice-assistant/docs/architecture/data-service/`
- Codex project memory under `.codex/memories/`

The service is the minimum separable unit for MCP / CLI / HTTP knowledge governance. Upstream apps must call the service boundary instead of reading or writing internal workspace artifacts.

Original memory was preserved as `.codex/memories/meeting_voice_assistant_stage_done.md`.
A project-local version for the new standalone service lives at `.codex/memories/data_service_stage_done.md`.
