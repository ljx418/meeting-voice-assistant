import type { WorkflowInstanceSummary, WorkflowStatus, WorkflowSummary, WorkflowVersionSummary } from "../api/types.js";

export interface WorkflowHeaderProps {
  workflows: WorkflowSummary[];
  versions: WorkflowVersionSummary[];
  instances: WorkflowInstanceSummary[];
  status: WorkflowStatus;
  selectedWorkflowId: string;
  selectedVersionId: string;
  selectedInstanceId: string;
  onWorkflowChange: (value: string) => void;
  onVersionChange: (value: string) => void;
  onInstanceChange: (value: string) => void;
}

export function WorkflowHeader({
  workflows,
  versions,
  instances,
  status,
  selectedWorkflowId,
  selectedVersionId,
  selectedInstanceId,
  onWorkflowChange,
  onVersionChange,
  onInstanceChange,
}: WorkflowHeaderProps) {
  return (
    <header className="console-header">
      <div className="brand-block">
        <span className="brand-mark">hOS</span>
        <div>
          <strong>harnessOS Workflow Studio</strong>
          <div className="muted">左右双折叠交互设计 · {status.workflow_instance_id}</div>
        </div>
      </div>
      <label className="toolbar-field">
        工作流{" "}
        <select value={selectedWorkflowId} onChange={(event) => onWorkflowChange(event.target.value)}>
          {workflows.map((workflow) => (
            <option key={workflow.workflow_template_id} value={workflow.workflow_template_id}>
              {workflow.name}
            </option>
          ))}
        </select>
      </label>
      <label className="toolbar-field">
        版本{" "}
        <select value={selectedVersionId} onChange={(event) => onVersionChange(event.target.value)}>
          {versions.map((version) => (
            <option key={version.workflow_version_id} value={version.workflow_version_id}>
              {version.version}
            </option>
          ))}
        </select>
      </label>
      <label className="toolbar-field">
        实例{" "}
        <select value={selectedInstanceId} onChange={(event) => onInstanceChange(event.target.value)}>
          {instances.map((instance) => (
            <option key={instance.workflow_instance_id} value={instance.workflow_instance_id}>
              {instance.workflow_instance_id}
            </option>
          ))}
        </select>
      </label>
      <span className="status">{status.status}</span>
      <div className="header-actions" aria-label="工作流操作">
        <button type="button" disabled>保存草稿</button>
        <button type="button" disabled>运行测试</button>
        <button type="button" disabled>发布版本</button>
        <label className="header-search">
          <span className="sr-only">搜索</span>
          <input placeholder="搜索" />
        </label>
        <button className="icon-button" type="button" aria-label="通知">铃</button>
        <span className="user-avatar" aria-label="用户头像">朱</span>
      </div>
    </header>
  );
}
