# Data Service Summary

## Positioning

- `data_service` is the upstream orchestration layer above `llmwiki` and `graphrag`.
- `llmwiki` focuses on compilation, readability, provenance, and local browsing.
- `graphrag` focuses on entity/relation indexing and graph-based reasoning.

## Ingest Policy

- Single user write: yes
- Shared extract/normalize: yes
- Distill before GraphRAG: yes
- Targets: llmwiki, graphrag

## Stages

- row
- extract
- normalize
- distill
- llmwiki_compile
- graphrag_index
- summary

## Artifact Layout

- row manifest: `/Users/Zhuanz/Desktop/workspace/知识库/workspace/row_manifest.json`
- raw: `/Users/Zhuanz/Desktop/workspace/知识库/workspace/llmwiki/raw`
- readable: `/Users/Zhuanz/Desktop/workspace/知识库/workspace/llmwiki/readable`
- normalized: `/Users/Zhuanz/Desktop/workspace/知识库/workspace/llmwiki/normalized`
- distill: `/Users/Zhuanz/Desktop/workspace/知识库/workspace/distill`
- distill sources: `/Users/Zhuanz/Desktop/workspace/知识库/workspace/distill/sources`
- distill units: `/Users/Zhuanz/Desktop/workspace/知识库/workspace/distill/units`
- distill manifest: `/Users/Zhuanz/Desktop/workspace/知识库/workspace/distill/manifest.json`
- distill schema: `/Users/Zhuanz/Desktop/workspace/知识库/workspace/distill/schema.json`
- llmwiki pages: `/Users/Zhuanz/Desktop/workspace/知识库/workspace/llmwiki/pages`
- graphrag input: `/Users/Zhuanz/Desktop/workspace/知识库/workspace/graphrag/input`
- graphrag state: `/Users/Zhuanz/Desktop/workspace/知识库/workspace/graphrag/state`
- graphrag execution owner: `app.graphrag`
- summary dir: `/Users/Zhuanz/Desktop/workspace/知识库/workspace/summary`
- summary.md: `/Users/Zhuanz/Desktop/workspace/知识库/workspace/summary/summary.md`
- summary.json: `/Users/Zhuanz/Desktop/workspace/知识库/workspace/summary/summary.json`
- quality feedback: `/Users/Zhuanz/Desktop/workspace/知识库/workspace/quality/feedback.jsonl`
- correction rules: `/Users/Zhuanz/Desktop/workspace/知识库/workspace/quality/correction_rules.json`

## Notes

- Users write data once; internal processing fans out after normalize/distill.
- LLMWiki consumes readable and distilled material for compilation and provenance.
- GraphRAG consumes distilled, high-information units rather than raw fulltext by default.
- GraphRAG execution owner: app.graphrag.
