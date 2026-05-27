import type { QualityStatus, WorkflowStatusName } from "../ui/base/BaseComponents.js";
import type { WorkflowNodeCardProps } from "../ui/workflow/WorkflowNodeCard.js";

export interface StudioNodeFixture extends WorkflowNodeCardProps {
  id: string;
  x: number;
  y: number;
}

export const v41WorkflowNodes: StudioNodeFixture[] = [
  {
    id: "folder_input",
    x: 0,
    y: 80,
    icon: "入",
    name: "文件夹输入",
    type: "Input",
    status: "completed",
    inputArtifact: "Desktop/技术分享",
    outputArtifact: "folder_ref",
    qualityStatus: "passed",
    attemptCount: 1,
  },
  {
    id: "folder_scan",
    x: 280,
    y: 80,
    icon: "扫",
    name: "递归文件扫描",
    type: "Tool",
    status: "completed",
    inputArtifact: "folder_ref",
    outputArtifact: "file_tree.json",
    qualityStatus: "passed",
    attemptCount: 1,
  },
  {
    id: "markdown_filter",
    x: 560,
    y: 80,
    icon: "滤",
    name: "Markdown 文件过滤",
    type: "Tool",
    status: "running",
    inputArtifact: "file_tree.json",
    outputArtifact: "md_file_list.json",
    qualityStatus: "running",
    attemptCount: 1,
  },
  {
    id: "markdown_parse",
    x: 840,
    y: 80,
    icon: "析",
    name: "Markdown 内容解析",
    type: "Tool",
    status: "pending",
    inputArtifact: "md_file_list.json",
    outputArtifact: "parsed_docs.json",
    qualityStatus: "pending",
    attemptCount: 1,
  },
  {
    id: "folder_group",
    x: 1120,
    y: 80,
    icon: "组",
    name: "子文件夹分组",
    type: "Tool",
    status: "pending",
    inputArtifact: "parsed_docs.json",
    outputArtifact: "grouped_docs.json",
    qualityStatus: "pending",
    attemptCount: 1,
  },
  {
    id: "folder_summary",
    x: 280,
    y: 300,
    icon: "子",
    name: "子文件夹总结 Agent",
    type: "Agent",
    status: "ghost",
    inputArtifact: "grouped_docs.json",
    outputArtifact: "folder_summaries/",
    qualityStatus: "pending",
    attemptCount: 0,
  },
  {
    id: "overview_summary",
    x: 560,
    y: 300,
    icon: "总",
    name: "总目录总结 Agent",
    type: "Agent",
    status: "ghost",
    inputArtifact: "folder_summaries/",
    outputArtifact: "总览总结.md",
    qualityStatus: "pending",
    attemptCount: 0,
  },
  {
    id: "quality_check",
    x: 840,
    y: 300,
    icon: "质",
    name: "质量检查 Agent",
    type: "Reviewer",
    status: "waiting_approval",
    inputArtifact: "总览总结.md",
    outputArtifact: "quality_report.json",
    qualityStatus: "warning",
    attemptCount: 1,
  },
  {
    id: "artifact_publish",
    x: 1120,
    y: 300,
    icon: "出",
    name: "输出总结文件",
    type: "Output",
    status: "pending",
    inputArtifact: "quality_report.json",
    outputArtifact: "output_package",
    qualityStatus: "pending",
    attemptCount: 0,
  },
];

export const v41WorkflowEdges = [
  ["folder_input", "folder_scan"],
  ["folder_scan", "markdown_filter"],
  ["markdown_filter", "markdown_parse"],
  ["markdown_parse", "folder_group"],
  ["folder_group", "folder_summary"],
  ["folder_summary", "overview_summary"],
  ["overview_summary", "quality_check"],
  ["quality_check", "artifact_publish"],
] as const;

export const nodeStatusOptions: WorkflowStatusName[] = ["ghost", "pending", "running", "completed", "failed", "waiting_approval", "stale"];
export const qualityStatusOptions: QualityStatus[] = ["pending", "running", "passed", "warning", "failed"];

export const artifactNames = ["AgentOS_总结.md", "前端低代码_总结.md", "项目复盘_总结.md", "总览总结.md", "quality_report.json"];
