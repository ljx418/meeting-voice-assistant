"""Default concrete adapters for llmwiki and graphrag."""

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.llmwiki.config import LLMWikiConfig
from app.llmwiki.engine import WikiEngine

from .adapters import AdapterResult
from .models import DistilledUnit, DistilledUnitKind, EngineTarget, GraphExecutionOwner, IngestPlan


class LLMWikiEngineAdapter:
    """Run llmwiki compilation using the existing WikiEngine."""

    def compile(self, plan: IngestPlan, units: List[DistilledUnit]) -> AdapterResult:
        from .service import DataService

        contract_payload = DataService(plan.workspace).build_llmwiki_handoff(plan, units)
        contract_path = plan.layout.llmwiki_state_dir / "input_contract.json"
        contract_path.write_text(json.dumps(contract_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        config = LLMWikiConfig(
            workspace_path=plan.workspace,
            vault_path=plan.layout.raw_dir,
            db_path=plan.layout.llmwiki_state_dir / "llmwiki.db",
            markdown_output_dir=plan.layout.llmwiki_pages_dir,
            normalized_output_dir=plan.layout.normalized_dir,
            readable_docs_dir=plan.layout.readable_dir,
            summary_path=plan.layout.summary_md,
        )
        engine = WikiEngine(config)
        result = engine.ingest([source.path for source in plan.sources])
        return AdapterResult(
            engine=EngineTarget.LLMWIKI.value,
            status="success" if result.get("failed", 0) == 0 else "partial",
            artifacts=result.get("pages", []) + [str(contract_path)],
            meta={
                "sources": result.get("sources", []),
                "success": result.get("success", 0),
                "failed": result.get("failed", 0),
                "skipped": result.get("skipped", 0),
                "distilled_unit_count": len(units),
                "input_contract_version": contract_payload["contract_version"],
                "quality_plan_apply": {
                    "status": "skipped",
                    "reason": "quality_plan_is_applied_at_read_time",
                },
            },
        )


class GraphRAGWorkspaceAdapter:
    """Stage distilled inputs and delegate graph state creation to app.graphrag."""

    DISTILLED_BUNDLE_NAME = "distilled_units.jsonl"
    STAGING_DB_NAME = "graphrag.db"

    def __init__(self, *, execution_owner: GraphExecutionOwner = GraphExecutionOwner.APP_GRAPHRAG):
        self.execution_owner = execution_owner

    def index(self, plan: IngestPlan, units: List[DistilledUnit]) -> AdapterResult:
        staged_files, contract_payload, filtered_units = self._stage_inputs(plan, units)
        owner_path = self._write_execution_owner_record(
            plan,
            contract_payload=contract_payload,
            runtime_status="prepared",
        )
        staged_files.append(str(owner_path))

        if self.execution_owner == GraphExecutionOwner.APP_GRAPHRAG:
            request_path = self._write_execution_request(plan, contract_payload, filtered_units, staged_files)
            staged_files.append(str(request_path))
            self._write_execution_owner_record(
                plan,
                contract_payload=contract_payload,
                runtime_status="delegated",
                request_path=request_path,
            )
            auto_result = self._maybe_run_app_graphrag(request_path)
            if auto_result.get("status") == "completed":
                self._write_execution_owner_record(
                    plan,
                    contract_payload=contract_payload,
                    runtime_status="indexed_via_app_graphrag",
                    request_path=request_path,
                    state_db=plan.layout.graphrag_state_dir / self.STAGING_DB_NAME,
                )
                staged_files.append(str(plan.layout.graphrag_state_dir / self.STAGING_DB_NAME))
                return AdapterResult(
                    engine=EngineTarget.GRAPHRAG.value,
                    status="indexed",
                    artifacts=staged_files,
                    meta={
                        "source_count": len(plan.sources),
                        "distilled_unit_count": len(filtered_units),
                        "input_dir": str(plan.layout.graphrag_input_dir),
                        "input_contract_version": contract_payload["contract_version"],
                        "execution_owner": self.execution_owner.value,
                        "execution_mode": "app_graphrag",
                        "execution_result": auto_result,
                    },
                )
            return AdapterResult(
                engine=EngineTarget.GRAPHRAG.value,
                status="delegated",
                artifacts=staged_files,
                meta={
                    "source_count": len(plan.sources),
                    "distilled_unit_count": len(filtered_units),
                    "input_dir": str(plan.layout.graphrag_input_dir),
                    "input_contract_version": contract_payload["contract_version"],
                    "execution_owner": self.execution_owner.value,
                    "execution_request": str(request_path),
                    "execution_result": auto_result,
                },
            )

        from app.graphrag.service import materialize_workspace_graph_state

        graph_stats = materialize_workspace_graph_state(
            plan.workspace,
            contract_payload,
            execution_owner=self.execution_owner.value,
        )
        db_path = plan.layout.graphrag_state_dir / self.STAGING_DB_NAME
        staged_files.append(str(db_path))
        self._write_execution_owner_record(
            plan,
            contract_payload=contract_payload,
            runtime_status="indexed",
            state_db=db_path,
        )

        return AdapterResult(
            engine=EngineTarget.GRAPHRAG.value,
            status="indexed",
            artifacts=staged_files,
            meta={
                "source_count": len(plan.sources),
                "distilled_unit_count": len(filtered_units),
                "input_dir": str(plan.layout.graphrag_input_dir),
                "state_db": str(db_path),
                "input_contract_version": contract_payload["contract_version"],
                "execution_owner": self.execution_owner.value,
                **{key: value for key, value in graph_stats.items() if key != "source"},
            },
        )

    def _stage_inputs(self, plan: IngestPlan, units: List[DistilledUnit]) -> Tuple[List[str], Dict[str, Any], List[DistilledUnit]]:
        from .service import DataService

        plan.layout.ensure_directories()
        staged_files: List[str] = []
        contract_payload = DataService(plan.workspace).build_graphrag_handoff(plan, units)
        contract_path = plan.layout.graphrag_cache_dir / "input_contract.json"
        contract_path.write_text(json.dumps(contract_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        staged_files.append(str(contract_path))
        contract_units = contract_payload["units"]
        allowed_unit_ids = {item["unit_id"] for item in contract_units}
        filtered_units = [unit for unit in units if unit.unit_id in allowed_unit_ids]

        bundle_path = plan.layout.graphrag_input_dir / self.DISTILLED_BUNDLE_NAME
        bundle_lines = [json.dumps(item, ensure_ascii=False) for item in contract_units]
        bundle_path.write_text("\n".join(bundle_lines) + ("\n" if bundle_lines else ""), encoding="utf-8")
        staged_files.append(str(bundle_path))

        grouped_units: Dict[str, List[DistilledUnit]] = defaultdict(list)
        for unit in filtered_units:
            grouped_units[unit.source_id].append(unit)

        for source in plan.sources:
            source_units = grouped_units.get(source.source_id or "", [])
            source_slug = (source.source_id or Path(source.path).stem).replace("/", "_")
            source_path = plan.layout.graphrag_input_dir / f"{source_slug}.md"
            body = [
                f"# Distilled Source {source_slug}",
                "",
                f"- original_path: {source.path}",
                f"- source_weight: {source.meta.get('source_weight', '1.0')}",
                f"- density_score: {source.meta.get('source_density_score', '1.0')}",
                f"- title_flags: {source.meta.get('title_flags', '')}",
                "",
            ]
            for unit in source_units:
                kind = unit.kind.value if hasattr(unit.kind, "value") else str(unit.kind)
                body.extend([f"## {kind}", "", unit.text, ""])
            source_path.write_text("\n".join(body), encoding="utf-8")
            staged_files.append(str(source_path))

        manifest_path = plan.layout.graphrag_cache_dir / "index_manifest.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "workspace": str(plan.workspace),
                    "input_dir": str(plan.layout.graphrag_input_dir),
                    "staged_files": staged_files,
                    "source_count": len(plan.sources),
                    "distilled_unit_count": len(filtered_units),
                    "status": "prepared",
                    "execution_owner": self.execution_owner.value,
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        staged_files.append(str(manifest_path))
        return staged_files, contract_payload, filtered_units

    def _write_execution_owner_record(
        self,
        plan: IngestPlan,
        *,
        contract_payload: Dict[str, Any],
        runtime_status: str,
        request_path: Optional[Path] = None,
        state_db: Optional[Path] = None,
    ) -> Path:
        owner_path = plan.layout.graphrag_execution_owner
        owner_path.write_text(
            json.dumps(
                {
                    "execution_owner": self.execution_owner.value,
                    "status": runtime_status,
                    "contract_version": contract_payload["contract_version"],
                    "workspace": str(plan.workspace),
                    "request_path": str(request_path) if request_path else None,
                    "state_db": str(state_db) if state_db else None,
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        return owner_path

    def _write_execution_request(
        self,
        plan: IngestPlan,
        contract_payload: Dict[str, Any],
        filtered_units: List[DistilledUnit],
        staged_files: List[str],
    ) -> Path:
        request_path = plan.layout.graphrag_execution_request
        request_path.write_text(
            json.dumps(
                {
                    "execution_owner": self.execution_owner.value,
                    "workspace": str(plan.workspace),
                    "contract_version": contract_payload["contract_version"],
                    "input_contract_path": str(plan.layout.graphrag_cache_dir / "input_contract.json"),
                    "input_bundle_path": str(plan.layout.graphrag_input_dir / self.DISTILLED_BUNDLE_NAME),
                    "state_db_path": str(plan.layout.graphrag_state_dir / self.STAGING_DB_NAME),
                    "source_count": len(plan.sources),
                    "distilled_unit_count": len(filtered_units),
                    "staged_files": staged_files,
                    "status": "ready_for_app_graphrag_runner",
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        return request_path

    def _maybe_run_app_graphrag(self, request_path: Path) -> Dict[str, Any]:
        try:
            from app.graphrag.service import run_data_service_execution_request

            return run_data_service_execution_request(request_path)
        except Exception as exc:
            return {
                "status": "failed",
                "reason": "app_graphrag_runner_exception",
                "request_path": str(request_path),
                "error": str(exc),
            }
