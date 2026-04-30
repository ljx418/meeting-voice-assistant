"""CLI entrypoint for the shared data_service layer."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .models import GraphExecutionOwner, QueryMode
from .service import DataService


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="data_service", description="Shared ingest/query layer above llmwiki and graphrag")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest = subparsers.add_parser("ingest", help="Run a dual-engine ingest pipeline")
    ingest.add_argument("paths", nargs="+", help="File paths to ingest")
    ingest.add_argument("--workspace", required=True, help="Workspace directory")
    ingest.add_argument(
        "--graphrag-owner",
        choices=[owner.value for owner in GraphExecutionOwner],
        default=GraphExecutionOwner.APP_GRAPHRAG.value,
        help="Who executes GraphRAG indexing: local data_service or app.graphrag handoff",
    )

    summary = subparsers.add_parser("summary", help="Render workspace summary")
    summary.add_argument("--workspace", required=True, help="Workspace directory")

    distill = subparsers.add_parser("distill", help="Preview distill artifacts")
    distill.add_argument("--workspace", required=True, help="Workspace directory")
    distill.add_argument("--source-id", help="Optional source_id to inspect")
    distill.add_argument("--limit", type=int, default=20, help="Max sources/units to return")
    distill.add_argument("--kind", help="Optional unit kind filter")
    distill.add_argument("--min-importance", type=float, default=0.0, help="Minimum unit importance")
    distill.add_argument("--llm-enriched-only", action="store_true", help="Only return llm-enriched units")
    distill.add_argument("--authority", help="Optional authority filter, e.g. PRIMARY_DOC or SECONDARY_CHAT")
    distill.add_argument("--min-source-weight", type=float, default=0.0, help="Minimum source_weight")
    distill.add_argument("--min-source-density", type=float, default=0.0, help="Minimum source_density_score")

    boundary = subparsers.add_parser("boundary", help="Inspect current data_service vs graphrag boundary")
    boundary.add_argument("--workspace", required=True, help="Workspace directory")

    graphrag_execute = subparsers.add_parser("graphrag-execute", help="Run delegated app.graphrag execution for a workspace")
    graphrag_execute.add_argument("--workspace", required=True, help="Workspace directory")

    query = subparsers.add_parser("query", help="Query llmwiki, graphrag, or both")
    query.add_argument("query", help="Query text")
    query.add_argument("--workspace", required=True, help="Workspace directory")
    query.add_argument("--mode", choices=[mode.value for mode in QueryMode], default=QueryMode.HYBRID.value)
    query.add_argument("--top-k", type=int, default=8)

    return parser


def main() -> int:
    args = _build_parser().parse_args()
    service = DataService(Path(args.workspace))

    if args.command == "ingest":
        plan = service.build_ingest_plan(
            args.paths,
            graphrag_execution_owner=GraphExecutionOwner(args.graphrag_owner),
        )
        service.write_summary_files(plan)
        results = service.run_default_pipeline_and_refresh_summary(plan)
        print(json.dumps(
            {
                "workspace": str(service.workspace),
                "results": [
                    {"engine": result.engine, "status": result.status, "meta": result.meta}
                    for result in results
                ],
                "summary": str(service.layout.summary_md),
            },
            ensure_ascii=False,
            indent=2,
        ))
        return 0

    if args.command == "summary":
        plan = service.build_ingest_plan([])
        service.write_summary_files(plan)
        print(service.layout.summary_md.read_text(encoding="utf-8"))
        return 0

    if args.command == "distill":
        print(json.dumps(
            service.read_distill_bundle(
                source_id=getattr(args, "source_id", None),
                limit=getattr(args, "limit", 20),
                kind=getattr(args, "kind", None),
                min_importance=getattr(args, "min_importance", 0.0),
                llm_enriched_only=getattr(args, "llm_enriched_only", False),
                authority=getattr(args, "authority", None),
                min_source_weight=getattr(args, "min_source_weight", 0.0),
                min_source_density=getattr(args, "min_source_density", 0.0),
            ),
            ensure_ascii=False,
            indent=2,
        ))
        return 0

    if args.command == "boundary":
        print(json.dumps(service.read_boundary_audit(), ensure_ascii=False, indent=2))
        return 0

    if args.command == "graphrag-execute":
        print(json.dumps(service.run_graphrag_execution_request(), ensure_ascii=False, indent=2))
        return 0

    if args.command == "query":
        response = service.query(
            args.query,
            mode=QueryMode(args.mode),
            top_k=args.top_k,
        )
        print(json.dumps(
            {
                "mode": response.mode.value,
                "query": response.query,
                "answer": response.answer,
                "hits": [
                    {
                        "title": hit.title,
                        "snippet": hit.snippet,
                        "source": hit.source,
                        "score": hit.score,
                        "meta": hit.meta,
                    }
                    for hit in response.hits
                ],
                "engine_payloads": response.engine_payloads,
            },
            ensure_ascii=False,
            indent=2,
        ))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
