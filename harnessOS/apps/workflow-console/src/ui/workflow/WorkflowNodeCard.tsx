import { QualityBadge, StatusBadge, type QualityStatus, type WorkflowStatusName } from "../base/BaseComponents.js";
import "./workflow-components.css";

export interface WorkflowNodeCardProps extends Record<string, unknown> {
  icon: string;
  name: string;
  type: string;
  status: WorkflowStatusName;
  inputArtifact: string;
  outputArtifact: string;
  qualityStatus: QualityStatus;
  attemptCount: number;
  selected?: boolean;
  errorSummary?: string;
}

export function WorkflowNodeCard({
  icon,
  name,
  type,
  status,
  inputArtifact,
  outputArtifact,
  qualityStatus,
  attemptCount,
  selected = false,
  errorSummary,
}: WorkflowNodeCardProps) {
  return (
    <article className={`workflow-node-card workflow-node-card--${status} ${selected ? "workflow-node-card--selected" : ""}`.trim()}>
      <span className="workflow-node-card__port workflow-node-card__port--input" aria-hidden="true" />
      <span className="workflow-node-card__port workflow-node-card__port--output" aria-hidden="true" />
      <header className="workflow-node-card__header">
        <span className="workflow-node-card__icon">{icon}</span>
        <div>
          <h3>{name}</h3>
          <p>{type}</p>
        </div>
        <StatusBadge status={status} />
      </header>
      <dl className="workflow-node-card__meta">
        <div>
          <dt>输入</dt>
          <dd>{inputArtifact}</dd>
        </div>
        <div>
          <dt>输出</dt>
          <dd>{outputArtifact}</dd>
        </div>
      </dl>
      <footer className="workflow-node-card__footer">
        <QualityBadge status={qualityStatus} />
        <span>attempt {attemptCount}</span>
      </footer>
      {errorSummary ? <p className="workflow-node-card__error">{errorSummary}</p> : null}
    </article>
  );
}

const DEFAULT_NODE = {
  icon: "文",
  name: "Markdown 内容解析",
  type: "Tool",
  inputArtifact: "md_file_list.json",
  outputArtifact: "parsed_docs.json",
  qualityStatus: "pending" as const,
  attemptCount: 1,
};

export function GhostNodeCard() {
  return <WorkflowNodeCard {...DEFAULT_NODE} icon="案" name="子文件夹总结 Agent" outputArtifact="folder_summaries/" qualityStatus="pending" status="ghost" type="Agent" />;
}

export function PendingNodeCard() {
  return <WorkflowNodeCard {...DEFAULT_NODE} status="pending" />;
}

export function RunningNodeCard() {
  return <WorkflowNodeCard {...DEFAULT_NODE} icon="扫" name="递归文件扫描" outputArtifact="file_tree.json" qualityStatus="running" status="running" />;
}

export function CompletedNodeCard() {
  return <WorkflowNodeCard {...DEFAULT_NODE} icon="输" name="输出总结文件" inputArtifact="quality_report.json" outputArtifact="output_package" qualityStatus="passed" status="completed" />;
}

export function FailedNodeCard() {
  return (
    <WorkflowNodeCard
      {...DEFAULT_NODE}
      attemptCount={2}
      errorSummary="解析失败：损坏 Markdown 文件需要用户确认后重跑。"
      qualityStatus="failed"
      selected
      status="failed"
    />
  );
}

export function WaitingApprovalNodeCard() {
  return <WorkflowNodeCard {...DEFAULT_NODE} icon="质" name="质量检查 Agent" inputArtifact="总览总结.md" outputArtifact="quality_report.json" qualityStatus="warning" status="waiting_approval" type="Reviewer" />;
}
