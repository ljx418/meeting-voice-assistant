import { Background, Controls, MiniMap, ReactFlow, type Edge, type Node, type NodeProps } from "@xyflow/react";
import { useMemo } from "react";
import { v41WorkflowEdges, v41WorkflowNodes } from "../../fixtures/workflowStudioFixtures.js";
import { WorkflowNodeCard, type WorkflowNodeCardProps } from "./WorkflowNodeCard.js";
import "./workflow-canvas.css";

export type StudioFlowNode = Node<WorkflowNodeCardProps, "workflowNode">;

function StudioNode(props: NodeProps<StudioFlowNode>) {
  return <WorkflowNodeCard {...props.data} selected={props.selected} />;
}

const nodeTypes = {
  workflowNode: StudioNode,
};

export interface WorkflowCanvasProps {
  mode?: "overview" | "proposal" | "running" | "failed";
}

export function WorkflowCanvas({ mode = "overview" }: WorkflowCanvasProps) {
  const nodes = useMemo<StudioFlowNode[]>(
    () =>
      v41WorkflowNodes.map((node, index) => ({
        id: node.id,
        type: "workflowNode",
        position: { x: node.x, y: node.y },
        selected: index === 0,
        data: {
          ...node,
          status: mode === "proposal" && index > 4 ? "ghost" : mode === "running" && index === 3 ? "running" : node.status,
          qualityStatus: mode === "running" && index === 3 ? "running" : node.qualityStatus,
        },
      })),
    [mode],
  );

  const edges = useMemo<Edge[]>(
    () =>
      v41WorkflowEdges.map(([source, target], index) => ({
        id: `${source}-${target}`,
        source,
        target,
        animated: mode === "running" && index === 2,
        className: mode === "proposal" && index > 3 ? "workflow-edge--proposal" : undefined,
      })),
    [mode],
  );

  return (
    <div className="workflow-canvas" data-testid="component-workflow-canvas">
      <ReactFlow edges={edges} fitView nodeTypes={nodeTypes} nodes={nodes} nodesDraggable panOnDrag proOptions={{ hideAttribution: true }}>
        <Background color="var(--hos-border-default)" gap={24} size={1.4} />
        <MiniMap nodeColor="var(--hos-accent-blue)" pannable zoomable />
        <Controls showInteractive={false} />
      </ReactFlow>
    </div>
  );
}
