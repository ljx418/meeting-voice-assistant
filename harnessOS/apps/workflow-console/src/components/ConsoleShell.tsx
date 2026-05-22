import { useEffect, useState, type DragEvent } from "react";
import type { AgentTalkFixture } from "../api/agentTalkTypes.js";
import { buildEdgeAddIntent, buildInspectorPromptIntent, buildNodeAddIntent, NODE_LIBRARY_FALLBACK_LABELS } from "../api/canvasPatchIntents.js";
import type {
  AgentTalkSession,
  AgentTalkInteractionState,
  AgentTalkSuggestion,
  AgentActionProposal,
  AgentActionHandoff,
  ApprovalSummary,
  CanvasPatchIntent,
  GovernanceReviewSummary,
  NodeCatalogItem,
  OperationEvidenceRecord,
  QualitySummary,
  WorkflowBoard,
  WorkflowContextSummary,
  WorkflowEvent,
  WorkflowInstanceSummary,
  WorkflowPatchDiff,
  WorkflowPatchProposal,
  WorkflowStatus,
  WorkflowSummary,
  WorkflowVersionSummary,
} from "../api/types.js";
import { AgentTalkShell } from "./AgentTalkShell.js";
import { ApprovalPanel } from "./ApprovalPanel.js";
import { ContextPanel } from "./ContextPanel.js";
import { EventFeed } from "./EventFeed.js";
import { GovernanceReviewPanel } from "./GovernanceReviewPanel.js";
import { QualityPanel } from "./QualityPanel.js";
import { StationBoard } from "./StationBoard.js";
import { WorkflowEditingPanel } from "./WorkflowEditingPanel.js";
import { WorkflowHeader } from "./WorkflowHeader.js";

export interface ConsoleShellProps {
  workflows: WorkflowSummary[];
  versions: WorkflowVersionSummary[];
  instances: WorkflowInstanceSummary[];
  selectedWorkflowId: string;
  selectedVersionId: string;
  selectedInstanceId: string;
  board: WorkflowBoard;
  nodeCatalog?: NodeCatalogItem[];
  status: WorkflowStatus;
  approvals?: ApprovalSummary[];
  quality?: QualitySummary[];
  context?: WorkflowContextSummary | null;
  events: WorkflowEvent[];
  patchProposal?: WorkflowPatchProposal;
  patchDiff?: WorkflowPatchDiff;
  highRiskPatchDiff?: WorkflowPatchDiff;
	  agentTalkFixture?: AgentTalkFixture;
	  agentSession?: AgentTalkSession;
	  agentInteractionState?: AgentTalkInteractionState | null;
	  agentSuggestions?: AgentTalkSuggestion[];
  agentActionProposals?: AgentActionProposal[];
  activeAgentHandoff?: AgentActionHandoff | null;
  operationEvidence?: OperationEvidenceRecord[];
  governanceReview?: GovernanceReviewSummary | null;
  modeLabel?: string;
  eventState?: "idle" | "connecting" | "connected" | "reconnecting" | "error" | "disconnected";
  onWorkflowChange: (value: string) => void;
  onVersionChange: (value: string) => void;
  onInstanceChange: (value: string) => void;
  onApprovalRespond?: (approvalId: string, decision: "approve" | "reject", reason?: string, handoff?: AgentActionHandoff | null) => Promise<void> | void;
  onSetBusinessValue?: (path: `business.${string}`, value: unknown, expectedRevision?: number, handoff?: AgentActionHandoff | null) => Promise<void> | void;
  onEmitBusinessEvent?: (
    eventType: `business.${string}`,
    payload?: Record<string, unknown>,
    binding?: { target_path: `context.business.${string}`; payload_path: `event.payload.${string}`; mode?: "set" },
    handoff?: AgentActionHandoff | null,
  ) => Promise<void> | void;
  onApplyPatch?: (patchId: string, handoff?: AgentActionHandoff | null) => Promise<void> | void;
  onRejectPatch?: (patchId: string, reason?: string, handoff?: AgentActionHandoff | null) => Promise<void> | void;
  onPublishVersion?: (version: string, expectedDraftRevision: number, handoff?: AgentActionHandoff | null) => Promise<void> | void;
  onProposeCanvasPatch?: (intent: CanvasPatchIntent) => Promise<void> | void;
  onSendAgentMessage?: (content: string) => Promise<void> | void;
  onDismissAgentSuggestion?: (suggestionId: string) => Promise<void> | void;
  onDismissAgentActionProposal?: (proposalId: string) => Promise<void> | void;
  onCreateAgentActionHandoff?: (proposal: AgentActionProposal, targetPanel: AgentActionHandoff["target_panel"]) => Promise<AgentActionHandoff> | AgentActionHandoff;
}

export function ConsoleShell(props: ConsoleShellProps) {
  const defaultRun =
    props.board.stations.find((station) => station.station.station_id === "station_storyboard")?.runs[0]?.station_run_id ||
    props.board.stations[0]?.runs[0]?.station_run_id ||
    "";
  const [selectedRunId, setSelectedRunId] = useState(defaultRun);
  const isCompactInitial = typeof window !== "undefined" && window.matchMedia("(max-width: 720px)").matches;
  const [leftCollapsed, setLeftCollapsed] = useState(isCompactInitial);
  const [rightCollapsed, setRightCollapsed] = useState(isCompactInitial);
  const [rightTab, setRightTab] = useState<"agent" | "inspector" | "patch">("agent");
  const [bottomTab, setBottomTab] = useState<"events" | "trace" | "artifacts" | "quality" | "approvals" | "context" | "patch" | "governance">("events");
  const [ghostNodes, setGhostNodes] = useState<Array<{ id: string; label: string }>>([]);
  const [inspectorPrompt, setInspectorPrompt] = useState("");
  const [proposalMessage, setProposalMessage] = useState("");
  const [activeHandoff, setActiveHandoff] = useState<AgentActionHandoff | null>(props.activeAgentHandoff || null);
  const selectedStation = props.board.stations.find((station) => station.runs.some((run) => run.station_run_id === selectedRunId));
  const selectedRun = selectedStation?.runs.find((run) => run.station_run_id === selectedRunId);
  const artifacts = selectedRun?.output_artifacts || selectedStation?.output_artifacts || props.board.artifacts || [];
  const shellClass = ["console-shell", leftCollapsed ? "left-collapsed" : "", rightCollapsed ? "right-collapsed" : ""].join(" ");
  const nodeCatalog = props.nodeCatalog?.length ? props.nodeCatalog : [];

  useEffect(() => {
    const query = window.matchMedia("(max-width: 720px)");
    function syncCompact(event: MediaQueryList | MediaQueryListEvent) {
      if (event.matches) {
        setLeftCollapsed(true);
        setRightCollapsed(true);
      }
    }
    syncCompact(query);
    query.addEventListener("change", syncCompact);
    return () => query.removeEventListener("change", syncCompact);
  }, []);

  useEffect(() => {
    setInspectorPrompt("");
    setProposalMessage("");
  }, [selectedStation?.station.station_id]);

  useEffect(() => {
    if (!props.activeAgentHandoff) {
      return;
    }
    const incomingHandoff = props.activeAgentHandoff;
    setActiveHandoff((current) => {
      if (current?.handoff_id && current.handoff_id !== incomingHandoff.handoff_id) {
        return current;
      }
      routeHandoffToPanel(incomingHandoff.target_panel);
      return incomingHandoff;
    });
  }, [props.activeAgentHandoff?.handoff_id, props.activeAgentHandoff?.target_panel]);

  async function createHandoff(proposal: AgentActionProposal, targetPanel: AgentActionHandoff["target_panel"]) {
    routeHandoffToPanel(targetPanel);
    const handoff = await props.onCreateAgentActionHandoff?.(proposal, targetPanel);
    if (handoff) {
      setActiveHandoff(handoff);
      setProposalMessage("来自 Agent 建议，已交接到对应面板，等待用户确认。");
    }
    return handoff;
  }

  function routeHandoffToPanel(targetPanel: AgentActionHandoff["target_panel"]) {
    if (targetPanel === "editing_panel") {
      setRightTab("patch");
      setBottomTab("patch");
    }
    if (targetPanel === "approval_panel") {
      setBottomTab("approvals");
    }
    if (targetPanel === "context_panel") {
      setBottomTab("context");
    }
    if (targetPanel === "quality_panel") {
      setBottomTab("quality");
    }
    if (targetPanel === "artifact_panel") {
      setBottomTab("artifacts");
    }
  }

  async function proposeNodeAdd(nodeCatalogId: string) {
    const item = nodeCatalog.find((candidate) => candidate.id === nodeCatalogId || candidate.node_template_id === nodeCatalogId);
    if (!item) return;
    const ghostId = `ghost_${nodeCatalogId}_${Date.now()}`;
    setGhostNodes((current) => [...current, { id: ghostId, label: item.label }]);
    setProposalMessage("节点已进入待确认状态，正在生成 Patch。");
    setRightTab("patch");
    setBottomTab("patch");
    await props.onProposeCanvasPatch?.(buildNodeAddIntent(item, props.board.stations, props.selectedInstanceId));
  }

  function proposeNodeAddByName(name: string) {
    const item = nodeCatalog.find((candidate) => candidate.label === name);
    if (item) {
      void proposeNodeAdd(item.id);
    }
  }

  async function proposeEdgeAdd(fromStationId: string, toStationId: string) {
    setProposalMessage("连线 Patch 已生成，Apply 前不会写入 WorkflowEdge。");
    setRightTab("patch");
    setBottomTab("patch");
    await props.onProposeCanvasPatch?.(buildEdgeAddIntent(fromStationId, toStationId, props.selectedInstanceId));
  }

  async function proposeInspectorPrompt() {
    if (!selectedStation || !inspectorPrompt.trim()) return;
    setProposalMessage("Inspector 修改已生成 Patch，等待用户确认。");
    setRightTab("patch");
    setBottomTab("patch");
    await props.onProposeCanvasPatch?.(
      buildInspectorPromptIntent(selectedStation.station.station_id, inspectorPrompt.trim(), props.selectedInstanceId),
    );
  }

  return (
    <div className={shellClass} data-testid="workflow-console">
      <WorkflowHeader
        workflows={props.workflows}
        versions={props.versions}
        instances={props.instances}
        status={props.status}
        selectedWorkflowId={props.selectedWorkflowId}
        selectedVersionId={props.selectedVersionId}
        selectedInstanceId={props.selectedInstanceId}
        onWorkflowChange={props.onWorkflowChange}
        onVersionChange={props.onVersionChange}
        onInstanceChange={props.onInstanceChange}
      />
      <main className="console-content">
        <aside className="left-rail" aria-label="节点库">
          <button className="collapse-button" type="button" onClick={() => setLeftCollapsed((value) => !value)}>
            {leftCollapsed ? "展开节点库" : "折叠节点库"}
          </button>
          <div className="rail-content">
            <span className="eyebrow">Node Library</span>
            {props.modeLabel ? <span className="status">{props.modeLabel}</span> : null}
            <h2>节点库</h2>
            <p className="muted">拖拽节点到画布，快速搭建工作流</p>
            <input className="node-search" placeholder="搜索节点" aria-label="搜索节点" />
            <div className="filter-tabs">
              <span className="status">全部</span>
              <span className="status">常用</span>
              <span className="status">VideoStudio</span>
              <span className="status">自定义</span>
            </div>
            <button className="custom-node-button" type="button">+ 自定义节点</button>
            <div className="node-category">
              <strong>输入节点</strong>
              {nodeNamesForCategory(nodeCatalog, ["user_input", "file_input"], ["用户输入", "文件输入"]).map((name) => (
                <button className="library-node" draggable key={name} type="button" onClick={() => proposeNodeAddByName(name)} onDragStart={(event) => setNodeDragData(event, name, nodeCatalog)}><span>{name}</span><small>接收需求、文件或外部触发</small><em>常用</em></button>
              ))}
            </div>
            <div className="node-category">
              <strong>AI Agent 节点</strong>
              {nodeNamesForCategory(nodeCatalog, ["planner_agent", "script_writer_agent", "director_agent"], ["Planner Agent", "Script Writer Agent", "Director Agent"]).map((name) => (
                <button className="library-node" draggable key={name} type="button" onClick={() => proposeNodeAddByName(name)} onDragStart={(event) => setNodeDragData(event, name, nodeCatalog)}><span>{name}</span><small>编排推理、生成与审查任务</small><em>推荐</em></button>
              ))}
            </div>
            <div className="node-category">
              <strong>VideoStudio 推荐节点</strong>
              {nodeNamesForCategory(nodeCatalog, ["storyboard_generation", "character_consistency", "video_render", "publish_output"], ["分镜生成", "角色一致性检查", "视频渲染", "发布输出"]).map((name) => (
                <button className="library-node" draggable key={name} type="button" onClick={() => proposeNodeAddByName(name)} onDragStart={(event) => setNodeDragData(event, name, nodeCatalog)}><span>{name}</span><small>推荐 · 视频工作流</small><em>推荐</em></button>
              ))}
            </div>
            <div className="node-category">
              <strong>工具 / 连接器节点</strong>
              {nodeNamesForCategory(nodeCatalog, ["http_request", "mcp_tool", "video_render"], ["HTTP 请求", "MCP 工具", "视频渲染"]).map((name) => (
                <button className="library-node" draggable key={name} type="button" onClick={() => proposeNodeAddByName(name)} onDragStart={(event) => setNodeDragData(event, name, nodeCatalog)}><span>{name}</span><small>连接工具、模型或外部服务</small><em>高级</em></button>
              ))}
            </div>
            <div className="node-category">
              <strong>质量与治理节点</strong>
              {nodeNamesForCategory(nodeCatalog, ["quality_evaluation", "manual_approval"], ["质量评估", "人工审批"]).map((name) => (
                <button className="library-node" draggable key={name} type="button" onClick={() => proposeNodeAddByName(name)} onDragStart={(event) => setNodeDragData(event, name, nodeCatalog)}><span>{name}</span><small>治理、质量与审批控制</small><em>治理</em></button>
              ))}
            </div>
            <div className="node-category">
              <strong>控制流节点</strong>
              {nodeNamesForCategory(nodeCatalog, ["condition", "end"], ["条件判断", "结束节点"]).map((name) => (
                <button className="library-node" draggable key={name} type="button" onClick={() => proposeNodeAddByName(name)} onDragStart={(event) => setNodeDragData(event, name, nodeCatalog)}><span>{name}</span><small>控制流程方向与执行节奏</small><em>流程</em></button>
              ))}
            </div>
          </div>
        </aside>
        <StationBoard
          stations={props.board.stations}
          ghostNodes={ghostNodes}
          onEdgeProposal={proposeEdgeAdd}
          onNodeDrop={proposeNodeAdd}
          onSelectRun={setSelectedRunId}
        />
        <aside className="right-rail" aria-label="节点配置">
          <button className="collapse-button" type="button" onClick={() => setRightCollapsed((value) => !value)}>
            {rightCollapsed ? "展开检查器" : "折叠检查器"}
          </button>
          <div className="rail-content inspector-stack">
            <span className="eyebrow">Inspector</span>
            <div className="inspector-tabs">
              <button className={rightTab === "agent" ? "active" : ""} type="button" onClick={() => setRightTab("agent")}>Agent 助手</button>
              <button className={rightTab === "inspector" ? "active" : ""} type="button" onClick={() => setRightTab("inspector")}>节点配置</button>
              <button className={rightTab === "patch" ? "active" : ""} type="button" onClick={() => setRightTab("patch")}>Patch Diff</button>
            </div>
            {rightTab === "inspector" ? (
              <section className="panel selected-node">
                <h2>{selectedStation?.station.name || "未选择节点"}</h2>
                <p className="muted">{selectedRun?.status || "选择画布节点查看运行详情"}</p>
                <div className="inspector-form">
                  <label>节点名称<input disabled value={selectedStation?.station.name || ""} readOnly /></label>
                  <label>Agent 角色<input disabled value={selectedStation?.station.role || ""} readOnly /></label>
                  <label>输入合同<input disabled value={selectedRun?.input_artifacts?.[0]?.name || "待绑定"} readOnly /></label>
                  <label>输出合同<input disabled value={artifacts[0]?.name || "待生成"} readOnly /></label>
                  <label>质量规则<input disabled value="visual_consistency >= 0.8" readOnly /></label>
                  <label>
                    Prompt Patch
                    <textarea
                      data-testid="inspector-prompt-input"
                      onChange={(event) => setInspectorPrompt(event.target.value)}
                      placeholder="输入修改建议，点击生成 Patch 后才会调用 BFF"
                      value={inspectorPrompt}
                    />
                  </label>
                  <button data-testid="inspector-generate-patch-button" disabled={!selectedStation || !inspectorPrompt.trim()} type="button" onClick={proposeInspectorPrompt}>
                    生成 Patch
                  </button>
                  {proposalMessage ? <p className="operation-message">{proposalMessage}</p> : null}
                </div>
              </section>
            ) : null}
            {rightTab === "agent" ? (
              <AgentTalkShell
	                fixture={props.agentTalkFixture}
	                session={props.agentSession}
	                interactionState={props.agentInteractionState}
	                suggestions={props.agentSuggestions}
                actionProposals={props.agentActionProposals}
                board={props.board}
                context={props.context}
                events={props.events}
                selectedStationName={selectedStation?.station.name}
                onSendMessage={props.onSendAgentMessage}
                onShowDiff={() => setRightTab("patch")}
	                onNavigateToEditing={() => {
	                  setRightTab("patch");
	                  setBottomTab("patch");
	                }}
	                onNavigateToEvidenceReview={() => setBottomTab("governance")}
	                onCreateHandoff={createHandoff}
                onDismissSuggestion={props.onDismissAgentSuggestion}
                onDismissActionProposal={props.onDismissAgentActionProposal}
              />
            ) : null}
            {rightTab === "patch" && bottomTab !== "patch" && props.patchProposal && props.patchDiff ? (
              <WorkflowEditingPanel
                proposal={props.patchProposal}
                diff={props.patchDiff}
                highRiskDiff={props.highRiskPatchDiff}
                onApplyPatch={props.onApplyPatch}
                onRejectPatch={props.onRejectPatch}
                onPublishVersion={props.onPublishVersion}
                handoff={activeHandoff?.target_panel === "editing_panel" ? activeHandoff : null}
              />
            ) : null}
          </div>
        </aside>
      </main>
      <section className="bottom-run-panel" aria-label="运行观察区">
        <div className="bottom-tabs">
          {(["events", "trace", "artifacts", "quality", "approvals", "context", "patch", "governance"] as const).map((tab) => (
            <button className={bottomTab === tab ? "active" : ""} key={tab} type="button" onClick={() => setBottomTab(tab)}>
              {({ events: "事件", trace: "Trace", artifacts: "产物", quality: "质量", approvals: "审批", context: "上下文", patch: "Patch", governance: "治理审计" } as const)[tab]}
            </button>
          ))}
        </div>
        <div className="bottom-content">
          {bottomTab === "events" ? <EventFeed events={props.events} /> : null}
          {bottomTab === "trace" ? (
            <pre data-testid="trace-panel">{props.board.trace_summary?.summary || props.board.trace_summary?.trace_id || "redacted trace summary"}</pre>
          ) : null}
          {bottomTab === "artifacts" ? (
            <pre data-testid="artifact-panel">{artifacts.map((artifact) => artifact.name || artifact.artifact_id).join("\n")}</pre>
          ) : null}
          {bottomTab === "quality" ? <QualityPanel evaluations={props.quality || props.board.quality_evaluations || []} /> : null}
          {bottomTab === "approvals" ? (
            <ApprovalPanel
              approvals={props.approvals || props.board.approvals || []}
              handoff={activeHandoff?.target_panel === "approval_panel" ? activeHandoff : null}
              onRespond={props.onApprovalRespond}
            />
          ) : null}
          {bottomTab === "context" ? (
            <ContextPanel
              context={props.context || undefined}
              onEmitBusinessEvent={props.onEmitBusinessEvent}
              onSetBusinessValue={props.onSetBusinessValue}
              handoff={activeHandoff?.target_panel === "context_panel" ? activeHandoff : null}
            />
          ) : null}
          {bottomTab === "patch" && props.patchProposal && props.patchDiff ? (
            <WorkflowEditingPanel
              proposal={props.patchProposal}
              diff={props.patchDiff}
              highRiskDiff={props.highRiskPatchDiff}
              onApplyPatch={props.onApplyPatch}
              onRejectPatch={props.onRejectPatch}
              onPublishVersion={props.onPublishVersion}
              handoff={activeHandoff?.target_panel === "editing_panel" ? activeHandoff : null}
            />
          ) : null}
          {bottomTab === "governance" ? (
            <GovernanceReviewPanel evidence={props.operationEvidence || []} review={props.governanceReview} />
          ) : null}
        </div>
        <div className="run-status-strip" aria-label="运行状态">
          <span data-testid="event-connection-state">事件连接：{props.eventState || "idle"}</span>
          <span>只读 Console</span>
          <span>{props.modeLabel || "Real BFF"}</span>
        </div>
      </section>
    </div>
  );
}

function setNodeDragData(event: DragEvent<HTMLButtonElement>, label: string, catalog: NodeCatalogItem[] = []) {
  const item = catalog.find((candidate) => candidate.label === label);
  if (!item) return;
  event.dataTransfer.setData("application/x-harnessos-node", item.id);
  event.dataTransfer.effectAllowed = "copy";
}

function nodeNamesForCategory(catalog: NodeCatalogItem[], ids: string[], fallback: string[]): string[] {
  if (!catalog.length) {
    return fallback.filter((label) => NODE_LIBRARY_FALLBACK_LABELS.includes(label));
  }
  const labels = ids
    .map((id) => catalog.find((item) => item.id === id || item.node_template_id === id)?.label)
    .filter((label): label is string => Boolean(label));
  return labels.length ? labels : fallback.filter((label) => NODE_LIBRARY_FALLBACK_LABELS.includes(label));
}
