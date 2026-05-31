# data_service V1.7

Status: ResearchNotebook source preview backend contract enablement.

V1.7 opens the minimal target HTTP source-level preview contract needed by ResearchNotebook V1.1-B:

- `GET /api/workspaces/{workspace_id}/capabilities`
- `GET /api/workspaces/{workspace_id}/sources/{source_id}/preview`

It does not add compatibility `/api/v1/knowledge/*` routes, MCP tools, CLI commands, DocumentUnit, EvidenceSpan, precise citation backjump, multi-format ingestion, assessment, or source trace integration claims.

See `research-notebook-source-preview-contract.md`.
