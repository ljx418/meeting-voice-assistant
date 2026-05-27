import type { ReactNode } from "react";

export type ButtonVariant = "primary" | "secondary" | "ghost" | "danger";

export interface ButtonProps {
  children: ReactNode;
  variant?: ButtonVariant;
  disabled?: boolean;
  loading?: boolean;
  onClick?: () => void;
  type?: "button" | "submit";
}

export function Button({ children, variant = "secondary", disabled = false, loading = false, onClick, type = "button" }: ButtonProps) {
  return (
    <button className={`hos-button hos-button--${variant}`} disabled={disabled || loading} onClick={onClick} type={type}>
      {loading ? "处理中" : null}
      {children}
    </button>
  );
}

export interface TabItem {
  id: string;
  label: string;
}

export interface TabsProps {
  items: TabItem[];
  activeId: string;
  onChange?: (id: string) => void;
}

export function Tabs({ items, activeId, onChange }: TabsProps) {
  return (
    <div className="hos-tabs" role="tablist">
      {items.map((item) => (
        <button key={item.id} aria-selected={item.id === activeId} className="hos-tab" onClick={() => onChange?.(item.id)} role="tab" type="button">
          {item.label}
        </button>
      ))}
    </div>
  );
}

export interface PanelProps {
  title: string;
  actions?: ReactNode;
  children: ReactNode;
  className?: string;
}

export function Panel({ title, actions, children, className = "" }: PanelProps) {
  return (
    <section className={`hos-panel ${className}`.trim()}>
      <div className="hos-panel__header">
        <h2 className="hos-panel__title">{title}</h2>
        {actions ? <div>{actions}</div> : null}
      </div>
      <div className="hos-panel__body">{children}</div>
    </section>
  );
}

export type WorkflowStatusName = "pending" | "running" | "completed" | "failed" | "waiting_approval" | "ghost" | "stale";

const STATUS_LABELS: Record<WorkflowStatusName, string> = {
  pending: "等待中",
  running: "运行中",
  completed: "已完成",
  failed: "失败",
  waiting_approval: "待确认",
  ghost: "草案",
  stale: "已过期",
};

export interface StatusBadgeProps {
  status: WorkflowStatusName;
  label?: string;
}

export function StatusBadge({ status, label }: StatusBadgeProps) {
  return <span className={`hos-badge hos-badge--${status}`}>{label || STATUS_LABELS[status]}</span>;
}

export type QualityStatus = "passed" | "warning" | "failed" | "pending" | "running";

const QUALITY_LABELS: Record<QualityStatus, string> = {
  passed: "质量通过",
  warning: "质量警告",
  failed: "质量失败",
  pending: "待检查",
  running: "检查中",
};

export interface QualityBadgeProps {
  status: QualityStatus;
  label?: string;
}

export function QualityBadge({ status, label }: QualityBadgeProps) {
  return <span className={`hos-quality-badge hos-quality-badge--${status}`}>{label || QUALITY_LABELS[status]}</span>;
}

export interface ArtifactCardProps {
  name: string;
  kind: string;
  summary: string;
  status?: QualityStatus;
}

export function ArtifactCard({ name, kind, summary, status = "passed" }: ArtifactCardProps) {
  return (
    <article className="hos-card">
      <strong>{name}</strong>
      <p className="hos-muted hos-mono">{kind}</p>
      <p>{summary}</p>
      <QualityBadge status={status} />
    </article>
  );
}

export interface EvidenceCardProps {
  proposalId: string;
  handoffId: string;
  operationType: string;
  policyDecision: string;
  redactionStatus: string;
}

export function EvidenceCard({ proposalId, handoffId, operationType, policyDecision, redactionStatus }: EvidenceCardProps) {
  return (
    <article className="hos-card hos-kv">
      <div>
        <strong>operation_type</strong>
        <span>{operationType}</span>
      </div>
      <div>
        <strong>proposal_id</strong>
        <span className="hos-mono">{proposalId}</span>
      </div>
      <div>
        <strong>handoff_id</strong>
        <span className="hos-mono">{handoffId}</span>
      </div>
      <div>
        <strong>policy_decision</strong>
        <span>{policyDecision}</span>
      </div>
      <div>
        <strong>redaction_status</strong>
        <span>{redactionStatus}</span>
      </div>
    </article>
  );
}

export interface StateBlockProps {
  title: string;
  message: string;
  action?: ReactNode;
}

export function EmptyState({ title, message, action }: StateBlockProps) {
  return (
    <div className="hos-card" role="status">
      <h3>{title}</h3>
      <p className="hos-muted">{message}</p>
      {action}
    </div>
  );
}

export function ErrorState({ title, message, action }: StateBlockProps) {
  return (
    <div className="hos-card" role="alert">
      <h3>{title}</h3>
      <p className="hos-muted">{message}</p>
      {action}
    </div>
  );
}
