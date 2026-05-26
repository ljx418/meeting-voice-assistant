import type { WorkflowInstanceSummary, WorkflowStatus, WorkflowSummary, WorkflowVersionSummary } from "../api/types.js";

export interface WorkflowHeaderProps {
  workflows: WorkflowSummary[];
  versions: WorkflowVersionSummary[];
  instances: WorkflowInstanceSummary[];
  status: WorkflowStatus;
  activeTopTab?: "workflows" | "nodes" | "agents" | "logs";
  selectedWorkflowId: string;
  selectedVersionId: string;
  selectedInstanceId: string;
  onTopTabChange?: (value: "workflows" | "nodes" | "agents" | "logs") => void;
  onWorkflowChange: (value: string) => void;
  onVersionChange: (value: string) => void;
  onInstanceChange: (value: string) => void;
}

export function WorkflowHeader({
  workflows,
  versions,
  instances,
  status,
  activeTopTab = "workflows",
  selectedWorkflowId,
  selectedVersionId,
  selectedInstanceId,
  onTopTabChange,
  onWorkflowChange,
  onVersionChange,
  onInstanceChange,
}: WorkflowHeaderProps) {
  const selectedWorkflow = workflows.find((workflow) => workflow.workflow_template_id === selectedWorkflowId);
  const selectedVersion = versions.find((version) => version.workflow_version_id === selectedVersionId);
  const topTabs: Array<["workflows" | "nodes" | "agents" | "logs", string]> = [
    ["workflows", "工作流"],
    ["nodes", "节点"],
    ["agents", "Agent"],
    ["logs", "日志"],
  ];
  return (
    <header className="console-header">
      <div className="brand-block">
        <span className="brand-mark">↗</span>
        <div>
          <strong>HarnessOS Workflow Studio</strong>
          <div className="muted">本地知识工作流 · Proposal-first</div>
        </div>
      </div>
      <nav className="top-mode-tabs" aria-label="顶层导航">
        {topTabs.map(([value, label]) => (
          <button
            aria-selected={activeTopTab === value}
            className={activeTopTab === value ? "active" : ""}
            data-testid={`top-tab-${value}`}
            key={value}
            role="tab"
            type="button"
            onClick={() => onTopTabChange?.(value)}
          >
            {label}
          </button>
        ))}
      </nav>
      <div className="workflow-title-block">
        <strong>{selectedWorkflow?.name || "技术分享资料递归总结工作流"}</strong>
        <span>{selectedVersion?.version || "Draft rev. 2"}</span>
      </div>
      <label className="toolbar-field sr-field">
        工作流
        <select data-testid="workflow-selector" value={selectedWorkflowId} onChange={(event) => onWorkflowChange(event.target.value)}>
          {workflows.map((workflow) => (
            <option key={workflow.workflow_template_id} value={workflow.workflow_template_id}>
              {workflow.name}
            </option>
          ))}
        </select>
      </label>
      <label className="toolbar-field sr-field">
        版本
        <select data-testid="workflow-version-selector" value={selectedVersionId} onChange={(event) => onVersionChange(event.target.value)}>
          {versions.map((version) => (
            <option key={version.workflow_version_id} value={version.workflow_version_id}>
              {version.version}
            </option>
          ))}
        </select>
      </label>
      <label className="toolbar-field sr-field">
        实例
        <select data-testid="workflow-instance-selector" value={selectedInstanceId} onChange={(event) => onInstanceChange(event.target.value)}>
          {instances.map((instance) => (
            <option key={instance.workflow_instance_id} value={instance.workflow_instance_id}>
              {instance.workflow_instance_id}
            </option>
          ))}
        </select>
      </label>
      <span className="status status-compact" data-testid="workflow-status">草稿 · {status.status}</span>
      <div className="header-actions" aria-label="工作流操作">
        <button type="button" disabled title="V4.0 当前只支持受治理 proposal 和用户确认路径，完整草稿保存是后续能力。">保存草稿（后续）</button>
        <button type="button" disabled title="运行测试必须走用户确认的 V4.1 本地工作流路径；顶部快捷入口是后续能力。">调试运行（后续）</button>
        <button type="button" disabled title="发布必须走 Patch apply 后的 governed publish path；顶部快捷发布是后续能力。">发布版本（后续）</button>
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
