import { v41WorkflowNodes } from "../../fixtures/workflowStudioFixtures.js";
import { Button, Panel, StatusBadge, Tabs } from "../base/BaseComponents.js";
import { AgentAssistantPanel, BottomRunPanel, FolderInputInspector, GovernanceEvidencePanel } from "../panels/RightPanels.js";
import { WorkflowCanvas } from "../workflow/WorkflowCanvas.js";
import "./workflow-studio-layout.css";

export type VisualAcceptanceState = "overview" | "agent-draft-proposal" | "folder-debug-scan" | "running-board" | "artifacts-quality" | "governance-evidence";

export interface WorkflowStudioLayoutProps {
  state?: VisualAcceptanceState;
}

export function WorkflowStudioLayout({ state = "overview" }: WorkflowStudioLayoutProps) {
  const rightPanel = state === "folder-debug-scan" ? <FolderInputInspector /> : state === "governance-evidence" ? <GovernanceEvidencePanel /> : <AgentAssistantPanel />;
  const bottomTab = state === "governance-evidence" ? "evidence" : state === "artifacts-quality" ? "quality" : state === "running-board" ? "events" : "artifacts";
  const canvasMode = state === "agent-draft-proposal" ? "proposal" : state === "running-board" ? "running" : "overview";

  return (
    <div className="workflow-studio-layout" data-testid="workflow-studio-layout">
      <TopBar />
      <LeftNodeLibrary />
      <main className="workflow-studio-layout__canvas">
        <div className="canvas-status-strip">
          <span>V4.1 本地知识总结工作流</span>
          <StatusBadge status={state === "agent-draft-proposal" ? "ghost" : "running"} label={stateLabel(state)} />
        </div>
        <WorkflowCanvas mode={canvasMode} />
      </main>
      <aside className="workflow-studio-layout__right">{rightPanel}</aside>
      <section className="workflow-studio-layout__bottom">
        <BottomRunPanel activeTab={bottomTab} />
      </section>
    </div>
  );
}

function TopBar() {
  return (
    <header className="studio-topbar">
      <div>
        <strong>HarnessOS Workflow Studio</strong>
        <span>技术分享资料递归总结工作流</span>
      </div>
      <Tabs
        activeId="workflow"
        items={[
          { id: "workflow", label: "工作流" },
          { id: "nodes", label: "节点" },
          { id: "agent", label: "Agent" },
          { id: "logs", label: "日志" },
        ]}
      />
      <div className="studio-topbar__actions">
        <Button>保存草稿</Button>
        <Button variant="primary">发布版本</Button>
        <Button variant="secondary">运行工作流</Button>
      </div>
    </header>
  );
}

function LeftNodeLibrary() {
  return (
    <aside className="left-node-library">
      <Panel title="节点库">
        <div className="node-library-search">搜索节点</div>
        <div className="node-library-categories">
          {["输入节点", "文件处理节点", "AI Agent 节点", "质量治理节点", "审批节点", "输出节点"].map((category) => (
            <span key={category}>{category}</span>
          ))}
        </div>
        <div className="node-library-list">
          {v41WorkflowNodes.map((node) => (
            <article key={node.id} className="node-library-item">
              <span>{node.icon}</span>
              <div>
                <strong>{node.name}</strong>
                <p>{node.type}</p>
              </div>
            </article>
          ))}
        </div>
      </Panel>
    </aside>
  );
}

function stateLabel(state: VisualAcceptanceState) {
  switch (state) {
    case "agent-draft-proposal":
      return "草案提案";
    case "folder-debug-scan":
      return "调试扫描";
    case "running-board":
      return "运行中";
    case "artifacts-quality":
      return "产物与质量";
    case "governance-evidence":
      return "治理审计";
    default:
      return "工作台概览";
  }
}
