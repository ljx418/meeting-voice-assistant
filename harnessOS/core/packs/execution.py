"""Domain Pack execution planning and deterministic stub execution."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from core.packs.registry import ALLOWED_WORKFLOW_NODE_TYPES, DomainPackManifest


@dataclass(frozen=True)
class PackExecutionPlan:
    """Validated execution plan built from one workflow template."""

    pack_name: str
    domain: str
    template_id: str
    status: str
    nodes: tuple[dict[str, Any], ...] = ()
    edges: tuple[dict[str, str], ...] = ()
    execution_order: tuple[str, ...] = ()
    missing_dependencies: tuple[str, ...] = ()
    blocked_reason: str = ""
    next_actions: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "pack_name": self.pack_name,
            "domain": self.domain,
            "template_id": self.template_id,
            "status": self.status,
            "nodes": [dict(node) for node in self.nodes],
            "edges": [dict(edge) for edge in self.edges],
            "execution_order": list(self.execution_order),
            "missing_dependencies": list(self.missing_dependencies),
            "blocked_reason": self.blocked_reason,
            "next_actions": list(self.next_actions),
        }


@dataclass(frozen=True)
class PackStubExecutionResult:
    """Deterministic stub execution result for one Pack execution plan."""

    status: str
    plan: PackExecutionPlan
    node_results: tuple[dict[str, Any], ...] = ()
    produced_outputs: dict[str, Any] = field(default_factory=dict)
    artifact_requests: tuple[dict[str, Any], ...] = ()
    blocked_reason: str = ""
    next_actions: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "plan": self.plan.to_dict(),
            "node_results": [dict(result) for result in self.node_results],
            "produced_outputs": dict(self.produced_outputs),
            "artifact_requests": [dict(request) for request in self.artifact_requests],
            "blocked_reason": self.blocked_reason,
            "next_actions": list(self.next_actions),
        }


def build_pack_execution_plan(
    manifest: DomainPackManifest,
    *,
    template_id: Optional[str] = None,
) -> PackExecutionPlan:
    """Build a validated DAG execution plan from a Pack workflow template."""
    resolved_template_id = template_id or _default_template_id(manifest)
    if not resolved_template_id:
        return PackExecutionPlan(
            pack_name=manifest.name,
            domain=manifest.domain,
            template_id="",
            status="blocked",
            missing_dependencies=("workflow_template",),
            blocked_reason="Pack does not declare workflow_templates.",
            next_actions=("Declare at least one workflow template.",),
        )
    template = manifest.workflow_templates.get(resolved_template_id)
    if not isinstance(template, dict):
        return PackExecutionPlan(
            pack_name=manifest.name,
            domain=manifest.domain,
            template_id=resolved_template_id,
            status="blocked",
            missing_dependencies=(f"workflow_template:{resolved_template_id}",),
            blocked_reason="Workflow template is not declared by the pack.",
            next_actions=(f"Declare workflow template {resolved_template_id}.",),
        )

    nodes = _normalize_nodes(template.get("nodes"))
    edges = _normalize_edges(template.get("edges"))
    missing = _validate_plan_dependencies(manifest, nodes, edges)
    execution_order = _topological_order(nodes, edges)
    if not execution_order:
        missing.append("workflow_template:cycle")
    if missing:
        return PackExecutionPlan(
            pack_name=manifest.name,
            domain=manifest.domain,
            template_id=resolved_template_id,
            status="blocked",
            nodes=tuple(nodes),
            edges=tuple(edges),
            missing_dependencies=tuple(missing),
            blocked_reason="Workflow template has missing or invalid dependencies.",
            next_actions=tuple(_next_action_for_missing(item) for item in missing),
        )

    nodes_by_id = {node["id"]: node for node in nodes}
    ordered_nodes = tuple(nodes_by_id[node_id] for node_id in execution_order)
    return PackExecutionPlan(
        pack_name=manifest.name,
        domain=manifest.domain,
        template_id=resolved_template_id,
        status="planned",
        nodes=ordered_nodes,
        edges=tuple(edges),
        execution_order=tuple(execution_order),
    )


def execute_pack_stub(
    manifest: DomainPackManifest,
    *,
    template_id: Optional[str] = None,
    inputs: Optional[dict[str, Any]] = None,
) -> PackStubExecutionResult:
    """Execute a workflow template with deterministic local stub results."""
    plan = build_pack_execution_plan(manifest, template_id=template_id)
    if plan.status != "planned":
        return PackStubExecutionResult(
            status="blocked",
            plan=plan,
            blocked_reason=plan.blocked_reason,
            next_actions=plan.next_actions,
        )

    produced_outputs: dict[str, Any] = dict(inputs or {})
    artifact_requests: list[dict[str, Any]] = []
    node_results: list[dict[str, Any]] = []
    produced_artifact_kinds: set[str] = set()
    for node in plan.nodes:
        node_id = str(node["id"])
        outputs = [item for item in node.get("outputs", []) if isinstance(item, str)]
        result_outputs = {
            output: _stub_output_value(plan.template_id, node_id, output)
            for output in outputs
        }
        produced_outputs.update(result_outputs)
        artifact_outputs = [
            output for output in outputs
            if output in manifest.artifact_kinds or output in manifest.artifact_schemas
        ]
        for kind in artifact_outputs:
            artifact_requests.append(
                {
                    "node_id": node_id,
                    "kind": kind,
                    "name": f"{plan.template_id}.{node_id}.{kind}.json",
                    "content": {
                        "pack_name": manifest.name,
                        "domain": manifest.domain,
                        "template_id": plan.template_id,
                        "node_id": node_id,
                        "kind": kind,
                        "value": result_outputs.get(kind),
                        "stubbed": True,
                    },
                    "parent_kinds": _artifact_parent_kinds(manifest, kind, produced_artifact_kinds),
                }
            )
            produced_artifact_kinds.add(kind)
        node_results.append(
            {
                "node_id": node_id,
                "status": "stubbed",
                "type": node.get("type"),
                "owner": node.get("owner"),
                "uses": node.get("uses"),
                "inputs": node.get("inputs", []),
                "outputs": result_outputs,
                "execution_deferred": _is_deferred_node(node),
            }
        )

    return PackStubExecutionResult(
        status="stubbed",
        plan=plan,
        node_results=tuple(node_results),
        produced_outputs=produced_outputs,
        artifact_requests=tuple(artifact_requests),
    )


def _default_template_id(manifest: DomainPackManifest) -> str:
    if not manifest.workflow_templates:
        return ""
    return sorted(manifest.workflow_templates)[0]


def _normalize_nodes(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    nodes: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        node_id = item.get("id")
        if not isinstance(node_id, str) or not node_id.strip():
            continue
        node = dict(item)
        node["inputs"] = [entry for entry in item.get("inputs", []) if isinstance(entry, str)]
        node["outputs"] = [entry for entry in item.get("outputs", []) if isinstance(entry, str)]
        nodes.append(node)
    return nodes


def _normalize_edges(value: Any) -> list[dict[str, str]]:
    if not isinstance(value, list):
        return []
    edges: list[dict[str, str]] = []
    for item in value:
        if (
            isinstance(item, list)
            and len(item) == 2
            and isinstance(item[0], str)
            and isinstance(item[1], str)
        ):
            edges.append({"source": item[0], "target": item[1]})
        elif isinstance(item, dict) and isinstance(item.get("source"), str) and isinstance(item.get("target"), str):
            edges.append({"source": item["source"], "target": item["target"]})
    return edges


def _validate_plan_dependencies(
    manifest: DomainPackManifest,
    nodes: list[dict[str, Any]],
    edges: list[dict[str, str]],
) -> list[str]:
    missing: list[str] = []
    node_ids = {str(node["id"]) for node in nodes}
    agent_ids = {agent.get("agent_id") for agent in manifest.agents}
    connector_ids = set(manifest.connectors)
    for edge in edges:
        if edge["source"] not in node_ids:
            missing.append(f"node:{edge['source']}")
        if edge["target"] not in node_ids:
            missing.append(f"node:{edge['target']}")
    for node in nodes:
        owner = node.get("owner")
        if isinstance(owner, str) and owner not in agent_ids:
            missing.append(f"agent:{owner}")
        uses = node.get("uses")
        node_type = node.get("type")
        if node_type not in ALLOWED_WORKFLOW_NODE_TYPES:
            missing.append(f"node_type:{node.get('id')}:{node_type}")
        if isinstance(uses, str) and node_type == "connector":
            connector_id = uses.split(".", 1)[0]
            if connector_id not in connector_ids:
                missing.append(f"connector:{connector_id}")
    return sorted(set(missing))


def _topological_order(nodes: list[dict[str, Any]], edges: list[dict[str, str]]) -> list[str]:
    node_ids = [str(node["id"]) for node in nodes]
    incoming = {node_id: 0 for node_id in node_ids}
    outgoing: dict[str, list[str]] = {node_id: [] for node_id in node_ids}
    for edge in edges:
        source = edge["source"]
        target = edge["target"]
        if source not in incoming or target not in incoming:
            continue
        incoming[target] += 1
        outgoing[source].append(target)
    ready = [node_id for node_id in node_ids if incoming[node_id] == 0]
    order: list[str] = []
    while ready:
        node_id = ready.pop(0)
        order.append(node_id)
        for target in outgoing[node_id]:
            incoming[target] -= 1
            if incoming[target] == 0:
                ready.append(target)
    if len(order) != len(node_ids):
        return []
    return order


def _artifact_parent_kinds(
    manifest: DomainPackManifest,
    kind: str,
    produced_artifact_kinds: set[str],
) -> list[str]:
    schema = manifest.artifact_schemas.get(kind)
    if not isinstance(schema, dict):
        return []
    parents = schema.get("parents")
    if not isinstance(parents, list):
        return []
    return [parent for parent in parents if isinstance(parent, str) and parent in produced_artifact_kinds]


def _stub_output_value(template_id: str, node_id: str, output: str) -> dict[str, str]:
    return {
        "template_id": template_id,
        "node_id": node_id,
        "output": output,
        "value": f"stub:{template_id}:{node_id}:{output}",
    }


def _is_deferred_node(node: dict[str, Any]) -> bool:
    return node.get("type") == "connector"


def _next_action_for_missing(dependency: str) -> str:
    if dependency.startswith("agent:"):
        return f"Declare agent {dependency.removeprefix('agent:')} in the pack manifest."
    if dependency.startswith("connector:"):
        return f"Declare connector {dependency.removeprefix('connector:')} in the pack manifest."
    if dependency.startswith("node:"):
        return f"Declare DAG node {dependency.removeprefix('node:')} or remove the invalid edge."
    if dependency.startswith("node_type:"):
        return f"Use one of the supported Pack workflow node types for {dependency}."
    if dependency == "workflow_template:cycle":
        return "Remove the DAG cycle from the workflow template."
    return f"Resolve {dependency}."
