import type { EdgeAddIntent, InspectorUpdateIntent, NodeAddIntent, NodeCatalogItem, StationBoardSummary } from "./types.js";

export const NODE_LIBRARY_FALLBACK_LABELS = [
  "文件夹输入",
  "递归文件扫描",
  "Markdown 文件过滤",
  "Markdown 内容解析",
  "子文件夹分组",
  "子文件夹总结 Agent",
  "总目录总结 Agent",
  "质量检查 Agent",
  "输出总结文件",
  "Planner Agent",
  "Script Writer Agent",
  "Director Agent",
  "分镜生成",
  "角色一致性检查",
  "视频渲染",
  "质量评估",
  "人工审批",
  "发布输出",
  "HTTP 请求",
  "MCP 工具",
  "条件判断",
  "结束节点",
];

export function buildNodeAddIntent(
  item: NodeCatalogItem,
  existingStations: StationBoardSummary[],
  workflowInstanceId?: string,
): NodeAddIntent {
  const baseId = item.id.replace(/[^a-z0-9_]/gi, "_").toLowerCase();
  const stationId = uniqueStationId(`station_${baseId}`, existingStations);
  return {
    source: "canvas",
    intent_type: "node_add",
    operation: "add_station",
    workflow_instance_id: workflowInstanceId,
    payload: {
      station: {
        station_id: stationId,
        name: item.label,
        role: item.station_kind,
        skill_refs: item.allowed_skill_refs,
        connector_refs: item.allowed_connector_refs,
        metadata: {
          node_catalog_id: item.id,
          node_label: item.label,
          catalog_id: item.catalog_id,
          catalog_version: item.catalog_version,
          node_template_id: item.node_template_id,
          station_kind: item.station_kind,
          schema_version: item.schema_version,
          allowed_skill_refs: item.allowed_skill_refs,
          allowed_connector_refs: item.allowed_connector_refs,
          allowed_artifact_kinds: item.allowed_artifact_kinds,
          allowed_quality_rules: item.allowed_quality_rules,
          allowed_approval_policies: item.allowed_approval_policies,
        },
      },
    },
  };
}

export function buildEdgeAddIntent(fromStationId: string, toStationId: string, workflowInstanceId?: string): EdgeAddIntent {
  return {
    source: "canvas",
    intent_type: "edge_add",
    operation: "update_edge",
    workflow_instance_id: workflowInstanceId,
    payload: {
      edge_id: `edge_${fromStationId}_to_${toStationId}`,
      edge_patch: {
        action: "add",
        from_station_id: fromStationId,
        to_station_id: toStationId,
      },
    },
  };
}

export function buildInspectorPromptIntent(
  stationId: string,
  promptPatch: string,
  workflowInstanceId?: string,
): InspectorUpdateIntent {
  return {
    source: "inspector",
    intent_type: "inspector_update",
    operation: "update_station_prompt",
    workflow_instance_id: workflowInstanceId,
    payload: {
      station_id: stationId,
      prompt_patch: promptPatch,
    },
  };
}

function uniqueStationId(baseId: string, existingStations: StationBoardSummary[]): string {
  const existingIds = new Set(existingStations.map((station) => station.station.station_id));
  if (!existingIds.has(baseId)) return baseId;
  let index = 2;
  while (existingIds.has(`${baseId}_${index}`)) index += 1;
  return `${baseId}_${index}`;
}
