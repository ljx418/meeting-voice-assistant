import { artifactNames } from "../../fixtures/workflowStudioFixtures.js";
import { ArtifactCard, Button, EvidenceCard, Panel, QualityBadge, StatusBadge, Tabs } from "../base/BaseComponents.js";
import "./panels.css";

export function AgentAssistantPanel() {
  return (
    <Panel actions={<StatusBadge status="ghost" label="提案模式" />} className="studio-right-panel" title="画布助手">
      <div className="assistant-boundary">
        <strong>Agent 只生成建议，不会自动执行。</strong>
        <span>应用草稿、发布版本和运行工作流都需要用户确认。</span>
      </div>
      <div className="chat-stack">
        <div className="chat-message chat-message--user">
          帮我创建一个工作流，读取 Desktop/技术分享 文件夹，递归解析里面的 md 文件，并为每个子文件夹生成单独总结，最后生成总览总结。
        </div>
        <div className="chat-message chat-message--agent">我会先生成工作流草案和 Patch proposal，不会扫描、发布或运行。</div>
        <article className="proposal-card">
          <header>
            <strong>工作流草案</strong>
            <StatusBadge status="ghost" />
          </header>
          <p>包含 9 个节点、线性连接、Markdown-only 处理规则和质量检查。</p>
          <div className="proposal-card__actions">
            <Button variant="primary">查看 Diff</Button>
            <Button>前往编辑面板</Button>
            <Button variant="ghost">忽略</Button>
          </div>
        </article>
      </div>
      <label className="assistant-input">
        <span>输入需求</span>
        <textarea defaultValue="为什么这个文件夹没有生成总结？" />
      </label>
    </Panel>
  );
}

export function FolderInputInspector() {
  return (
    <Panel title="文件夹输入配置">
      <label className="field-stack">
        <span>文件夹路径</span>
        <input defaultValue="Desktop/技术分享" />
      </label>
      <div className="panel-actions">
        <Button variant="primary">授权读取</Button>
        <Button>调试扫描</Button>
      </div>
      <div className="scan-result">
        <strong>扫描结果</strong>
        <div className="metric-grid">
          <span>总文件数 6</span>
          <span>Markdown 5</span>
          <span>子文件夹 4</span>
          <span>未支持 1</span>
        </div>
        <p className="hos-muted">未支持/test.pdf · 空文件夹/</p>
      </div>
    </Panel>
  );
}

export function PatchDiffPanel() {
  return (
    <Panel title="Patch Diff">
      <ul className="clean-list">
        <li>新增 9 个 V4.1 工作流节点</li>
        <li>新增线性连接关系</li>
        <li>Apply 前不修改草稿</li>
        <li>运行和发布仍需用户确认</li>
      </ul>
      <Button variant="primary">应用到草稿</Button>
    </Panel>
  );
}

export function RunDetailPanel() {
  return (
    <Panel title="运行详情">
      <div className="hos-kv">
        <div>
          <strong>当前节点</strong>
          <span>Markdown 内容解析</span>
        </div>
        <div>
          <strong>输入</strong>
          <span className="hos-mono">md_file_list.json</span>
        </div>
        <div>
          <strong>输出</strong>
          <span className="hos-mono">parsed_docs.json</span>
        </div>
        <div>
          <strong>耗时</strong>
          <span>8.4s</span>
        </div>
        <div>
          <strong>attempt</strong>
          <span>1</span>
        </div>
      </div>
    </Panel>
  );
}

export function GovernanceEvidencePanel() {
  return (
    <Panel title="治理审计">
      <p className="hos-muted">治理审计只读，不执行操作。</p>
      <EvidenceCard handoffId="handoff_folder_001" operationType="workflow.folder_summary.apply" policyDecision="user_confirmed_only" proposalId="proposal_folder_001" redactionStatus="redacted" />
      <div className="panel-actions">
        <Button>查看详情</Button>
        <Button variant="ghost">复制证据 ID</Button>
        <Button variant="ghost">关闭</Button>
      </div>
    </Panel>
  );
}

export function RightPanelsGallery() {
  return (
    <main className="panel-gallery">
      <AgentAssistantPanel />
      <FolderInputInspector />
      <PatchDiffPanel />
      <RunDetailPanel />
      <GovernanceEvidencePanel />
    </main>
  );
}

export function EventsTab() {
  return <TabList items={["workflow.started", "station.completed", "artifact.created"]} />;
}

export function TraceTab() {
  return <TabList items={["trace_id: trace_v41_001", "correlation_id: corr_folder_summary", "duration: 42.8s"]} />;
}

export function ArtifactsTab() {
  return (
    <div className="bottom-tab-grid">
      {artifactNames.map((name) => (
        <ArtifactCard key={name} kind={name.endsWith(".json") ? "JSON" : "Markdown"} name={name} summary="包含内容概览、核心主题、关键知识点、重要文件列表和引用文件。" status={name.includes("quality") ? "warning" : "passed"} />
      ))}
    </div>
  );
}

export function QualityTab() {
  return (
    <div className="quality-tab">
      <QualityBadge status="warning" />
      <span>summary coverage 100%</span>
      <span>unsupported file: 未支持/test.pdf</span>
      <span>empty folder: 空文件夹</span>
    </div>
  );
}

export function ApprovalTab() {
  return <TabList items={["待确认操作：运行工作流", "用户确认后继续", "Agent 不执行运行操作"]} />;
}

export function PatchTab() {
  return <TabList items={["PatchDiff 摘要", "新增节点：9", "修改规则：Markdown-only", "等待用户确认"]} />;
}

export function EvidenceTab() {
  return <TabList items={["proposal -> handoff", "user_confirmed", "runtime result", "evidence record", "只读"]} />;
}

function TabList({ items }: { items: string[] }) {
  return (
    <ul className="clean-list">
      {items.map((item) => (
        <li key={item}>{item}</li>
      ))}
    </ul>
  );
}

export function BottomRunPanel({ activeTab = "artifacts" }: { activeTab?: string }) {
  const tabs = [
    { id: "events", label: "Events" },
    { id: "trace", label: "Trace" },
    { id: "artifacts", label: "Artifacts" },
    { id: "quality", label: "Quality" },
    { id: "approval", label: "Approval" },
    { id: "patch", label: "Patch" },
    { id: "evidence", label: "Evidence" },
  ];
  return (
    <Panel actions={<Tabs activeId={activeTab} items={tabs} />} className="bottom-run-panel" title="运行面板">
      {activeTab === "events" ? <EventsTab /> : null}
      {activeTab === "trace" ? <TraceTab /> : null}
      {activeTab === "artifacts" ? <ArtifactsTab /> : null}
      {activeTab === "quality" ? <QualityTab /> : null}
      {activeTab === "approval" ? <ApprovalTab /> : null}
      {activeTab === "patch" ? <PatchTab /> : null}
      {activeTab === "evidence" ? <EvidenceTab /> : null}
    </Panel>
  );
}
