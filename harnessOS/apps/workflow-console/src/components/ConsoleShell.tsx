import { useCallback, useEffect, useMemo, useState, type DragEvent } from "react";
import {
  Background,
  BackgroundVariant,
  BaseEdge,
  Controls,
  Handle,
  MarkerType,
  MiniMap,
  Position,
  ReactFlow,
  ReactFlowProvider,
  applyNodeChanges,
  getBezierPath,
  useOnViewportChange,
  useReactFlow,
  type Edge,
  type EdgeProps,
  type Node,
  type NodeChange,
  type NodeProps,
  type XYPosition,
} from "@xyflow/react";
import type { AgentTalkFixture } from "../api/agentTalkTypes.js";
import { buildEdgeAddIntent, buildInspectorPromptIntent, buildNodeAddIntent, NODE_LIBRARY_FALLBACK_LABELS } from "../api/canvasPatchIntents.js";
import type {
  AgentActionHandoff,
  AgentActionProposal,
  AgentTalkInteractionState,
  AgentTalkSession,
  AgentTalkSuggestion,
  ApprovalSummary,
  CanvasPatchIntent,
  FolderSummaryAuthorization,
  FolderSummaryProposal,
  FolderSummaryRun,
  FolderSummaryScanResult,
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
import { safeText } from "../api/redaction.js";
import { AgentTalkShell } from "./AgentTalkShell.js";
import { ApprovalPanel } from "./ApprovalPanel.js";
import { ContextPanel } from "./ContextPanel.js";
import { EventFeed } from "./EventFeed.js";
import { GovernanceReviewPanel } from "./GovernanceReviewPanel.js";
import { QualityPanel } from "./QualityPanel.js";
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
  folderSummaryProposal?: FolderSummaryProposal | null;
  folderSummaryAuthorization?: FolderSummaryAuthorization | null;
  folderSummaryScan?: FolderSummaryScanResult | null;
  folderSummaryRun?: FolderSummaryRun | null;
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
  onSendAgentMessage?: (content: string, context?: { selected_station_id?: string; selected_station_name?: string }) => Promise<void> | void;
  onDismissAgentSuggestion?: (suggestionId: string) => Promise<void> | void;
  onDismissAgentActionProposal?: (proposalId: string) => Promise<void> | void;
  onCreateAgentActionHandoff?: (proposal: AgentActionProposal, targetPanel: AgentActionHandoff["target_panel"]) => Promise<AgentActionHandoff> | AgentActionHandoff;
  onCreateFolderSummaryProposal?: (folderPath: string) => Promise<void> | void;
  onAuthorizeFolderSummaryRead?: (folderPath: string) => Promise<void> | void;
  onDebugFolderSummaryScan?: () => Promise<void> | void;
  onApplyFolderSummaryProposal?: (proposalId?: string) => Promise<void> | void;
  onPublishFolderSummaryProposal?: (proposalId?: string) => Promise<void> | void;
  onRunFolderSummaryWorkflow?: (proposalId?: string) => Promise<void> | void;
  onRerunFolderSummaryMarkdownParse?: () => Promise<void> | void;
  onCreateFolderSummaryAgentDebugProposal?: () => Promise<void> | void;
}

type RightTab = "agent" | "inspector" | "patch";
type BottomTab = "run" | "events" | "trace" | "artifacts" | "quality" | "approvals" | "context" | "patch" | "governance";
type TopTab = "workflows" | "nodes" | "agents" | "logs";
type FolderSummaryStage = "draft" | "review" | "apply" | "authorize" | "scan" | "publish" | "run" | "artifacts" | "quality" | "governance";

interface CanvasNodeData extends Record<string, unknown> {
  label: string;
  role: string;
  status: string;
  inputCount: number;
  outputCount: number;
  artifactName: string;
  attemptCount: number;
  qualityState: string;
  ghost?: boolean;
  selected?: boolean;
  onSelect?: (stationId: string) => void;
}

interface CanvasEdgeData extends Record<string, unknown> {
  label: string;
  onProposal?: (fromStationId: string, toStationId: string) => void;
}

export function ConsoleShell(props: ConsoleShellProps) {
  const nodeCatalog = props.nodeCatalog?.length ? props.nodeCatalog : fallbackCatalog();
  const hasFolderSummaryState = Boolean(props.folderSummaryProposal || props.folderSummaryAuthorization || props.folderSummaryScan || props.folderSummaryRun);
  const folderStage = deriveFolderSummaryStage(props.folderSummaryProposal, props.folderSummaryAuthorization, props.folderSummaryScan, props.folderSummaryRun);
  const folderCanvasStations = buildFolderSummaryCanvasStations(props.folderSummaryProposal, props.folderSummaryRun);
  const visibleCanvasStations = folderCanvasStations || projectStationsForV41Scenario(props.board.stations);
  const visibleBoard = { ...props.board, stations: visibleCanvasStations };
  const [nodeSearch, setNodeSearch] = useState("");
  const [topTab, setTopTab] = useState<TopTab>("workflows");
  const [rightTab, setRightTab] = useState<RightTab>(() => (hasFolderSummaryState ? "inspector" : "agent"));
  const [bottomTab, setBottomTab] = useState<BottomTab>(() => (props.folderSummaryRun ? "run" : "run"));
  const [leftCollapsed, setLeftCollapsed] = useState(false);
  const [rightCollapsed, setRightCollapsed] = useState(false);
  const [bottomCollapsed, setBottomCollapsed] = useState(false);
  const [selectedStationId, setSelectedStationId] = useState(props.board.stations[0]?.station.station_id || "");
  const [inspectorPrompt, setInspectorPrompt] = useState("");
  const [folderPath, setFolderPath] = useState("Desktop/技术分享");
  const [localGhostNodes, setLocalGhostNodes] = useState<Array<{ id: string; label: string; uiPosition?: XYPosition }>>([]);
  const [operationMessage, setOperationMessage] = useState("");
  const [activeHandoff, setActiveHandoff] = useState<AgentActionHandoff | null>(props.activeAgentHandoff || null);

  const selectedStation = visibleCanvasStations.find((station) => station.station.station_id === selectedStationId) || visibleCanvasStations[0] || props.board.stations[0];
  const selectedRun = selectedStation?.runs[0];
  const folderGhostNodes: Array<{ id: string; label: string; uiPosition?: XYPosition }> = [];
  const ghostNodes = [...localGhostNodes, ...folderGhostNodes];

  useEffect(() => {
    const incomingHandoff = props.activeAgentHandoff;
    if (!incomingHandoff) return;
    setActiveHandoff((current) => {
      if (current?.handoff_id && current.handoff_id !== "pending_handoff" && current.handoff_id !== incomingHandoff.handoff_id) {
        return current;
      }
      routeHandoff(incomingHandoff.target_panel);
      return incomingHandoff;
    });
  }, [props.activeAgentHandoff?.handoff_id, props.activeAgentHandoff?.target_panel]);

  useEffect(() => {
    if (hasFolderSummaryState && rightTab === "agent") {
      setRightTab("inspector");
    }
    if (props.folderSummaryRun) {
      setBottomTab("run");
    }
  }, [hasFolderSummaryState, props.folderSummaryRun?.workflow_instance_id, rightTab]);

  function routeHandoff(targetPanel: AgentActionHandoff["target_panel"]) {
    setBottomCollapsed(false);
    if (targetPanel === "editing_panel") {
      setRightTab("patch");
      setBottomTab("patch");
    }
    if (targetPanel === "approval_panel") setBottomTab("approvals");
    if (targetPanel === "context_panel") setBottomTab("context");
    if (targetPanel === "quality_panel") setBottomTab("quality");
    if (targetPanel === "artifact_panel") setBottomTab("artifacts");
  }

  async function createHandoff(proposal: AgentActionProposal, targetPanel: AgentActionHandoff["target_panel"]) {
    setActiveHandoff({
      handoff_id: "pending_handoff",
      proposal_id: proposal.proposal_id,
      workflow_instance_id: proposal.workflow_instance_id,
      workflow_template_id: proposal.workflow_template_id,
      target_panel: targetPanel,
      target_resource: {},
      suggested_form_prefill: {},
      expires_at: "",
      status: "blocked",
      inactive_reason: "等待 Agent handoff DTO 返回。",
      created_at: new Date().toISOString(),
      redaction_status: "redacted",
    });
    routeHandoff(targetPanel);
    const handoff = await props.onCreateAgentActionHandoff?.(proposal, targetPanel);
    if (handoff) {
      setActiveHandoff(handoff);
      setOperationMessage("来自 Agent 建议，已交接到对应面板，等待用户确认。");
      routeHandoff(handoff.target_panel);
    } else {
      routeHandoff(targetPanel);
    }
    return handoff;
  }

  async function proposeNodeAdd(nodeCatalogId: string, uiPosition?: XYPosition) {
    const item = nodeCatalog.find((candidate) => candidate.id === nodeCatalogId || candidate.node_template_id === nodeCatalogId);
    if (!item) return;
    setLocalGhostNodes((current) => [...current, { id: `ghost_${item.id}_${Date.now()}`, label: item.label, uiPosition }]);
    setOperationMessage("节点已进入待确认状态，正在生成 Patch。");
    setRightTab("patch");
    setBottomTab("patch");
    await props.onProposeCanvasPatch?.(buildNodeAddIntent(item, props.board.stations, props.selectedInstanceId));
  }

  async function proposeEdgeAdd(fromStationId: string, toStationId: string) {
    setOperationMessage("连线 Patch 已生成，Apply 前不会写入 WorkflowEdge。");
    setRightTab("patch");
    setBottomTab("patch");
    await props.onProposeCanvasPatch?.(buildEdgeAddIntent(fromStationId, toStationId, props.selectedInstanceId));
  }

  async function proposeInspectorPrompt() {
    if (!selectedStation || !inspectorPrompt.trim()) return;
    setOperationMessage("Inspector 修改已生成 Patch，等待用户确认。");
    setRightTab("patch");
    setBottomTab("patch");
    await props.onProposeCanvasPatch?.(buildInspectorPromptIntent(selectedStation.station.station_id, inspectorPrompt.trim(), props.selectedInstanceId));
  }

  function showFolderSummaryPatchReview() {
    setRightCollapsed(false);
    setRightTab("inspector");
    setBottomCollapsed(false);
    setBottomTab("patch");
    setOperationMessage("请在右侧查看工作流草案，确认后应用到草稿。");
  }

  function focusFolderSummaryStep(stage: FolderSummaryStage) {
    if (stage === "draft") {
      setRightCollapsed(false);
      setRightTab("agent");
      setBottomCollapsed(true);
      return;
    }
    if (stage === "review") {
      showFolderSummaryPatchReview();
      return;
    }
    if (stage === "apply" || stage === "authorize" || stage === "scan" || stage === "publish" || stage === "run") {
      setRightCollapsed(false);
      setRightTab("inspector");
      setBottomCollapsed(stage !== "run");
      setBottomTab(stage === "run" ? "run" : "patch");
      return;
    }
    setRightCollapsed(true);
    setBottomCollapsed(false);
    setBottomTab(stage);
  }

  async function runPrimaryFolderSummaryAction() {
    try {
      if (folderStage === "draft") {
        setRightCollapsed(false);
        setRightTab("agent");
        setBottomCollapsed(true);
        setOperationMessage("请在 Agent 助手中发送自然语言需求，系统只会生成草案。");
        return;
      }
      if (folderStage === "review") {
        showFolderSummaryPatchReview();
        return;
      }
      if (folderStage === "apply") {
        await props.onApplyFolderSummaryProposal?.(props.folderSummaryProposal?.proposal_id);
        return;
      }
      if (folderStage === "authorize") {
        await props.onAuthorizeFolderSummaryRead?.(folderPath);
        return;
      }
      if (folderStage === "scan") {
        await props.onDebugFolderSummaryScan?.();
        return;
      }
      if (folderStage === "publish") {
        await props.onPublishFolderSummaryProposal?.(props.folderSummaryProposal?.proposal_id);
        return;
      }
      if (folderStage === "run") {
        setBottomCollapsed(false);
        setBottomTab("run");
        await props.onRunFolderSummaryWorkflow?.(props.folderSummaryProposal?.proposal_id);
        return;
      }
      focusFolderSummaryStep(folderStage);
    } catch (caught) {
      setOperationMessage(caught instanceof Error ? caught.message : "操作失败，请检查当前步骤。");
    }
  }

  return (
    <div className="studio-shell" data-testid="workflow-console">
      <WorkflowHeader
        workflows={props.workflows}
        versions={props.versions}
        instances={props.instances}
        status={props.status}
        activeTopTab={topTab}
        displayWorkflowName="技术分享资料递归总结工作流"
        displayVersionLabel={folderHeaderVersionLabel(props.folderSummaryProposal)}
        scenarioStatusLabel={`${folderStageLabel(folderStage)} · ${props.status.status}`}
        primaryActionLabel={folderPrimaryActionLabel(folderStage)}
        secondaryActionLabel="查看结果"
        onPrimaryAction={() => void runPrimaryFolderSummaryAction()}
        onSecondaryAction={() => focusFolderSummaryStep(props.folderSummaryRun ? "artifacts" : "review")}
        selectedWorkflowId={props.selectedWorkflowId}
        selectedVersionId={props.selectedVersionId}
        selectedInstanceId={props.selectedInstanceId}
        onTopTabChange={(value) => {
          setTopTab(value);
          if (value === "workflows") {
            setLeftCollapsed(false);
            setRightCollapsed(false);
            setBottomCollapsed(false);
            setRightTab(hasFolderSummaryState ? "inspector" : "agent");
            setBottomTab(props.folderSummaryRun ? "run" : "events");
            return;
          }
          if (value === "nodes") {
            setLeftCollapsed(false);
            setRightCollapsed(false);
            setBottomCollapsed(true);
            setRightTab("inspector");
          }
          if (value === "agents") {
            setLeftCollapsed(true);
            setRightCollapsed(false);
            setBottomCollapsed(true);
            setRightTab("agent");
          }
          if (value === "logs") {
            setLeftCollapsed(true);
            setRightCollapsed(true);
            setBottomCollapsed(false);
            setBottomTab("events");
          }
        }}
        onWorkflowChange={props.onWorkflowChange}
        onVersionChange={props.onVersionChange}
        onInstanceChange={props.onInstanceChange}
      />
      <main className={`studio-main ${bottomCollapsed ? "bottom-is-collapsed" : ""} ${leftCollapsed ? "left-is-collapsed" : ""} ${rightCollapsed ? "right-is-collapsed" : ""}`}>
        <FolderSummaryStepper
          stage={folderStage}
          proposal={props.folderSummaryProposal}
          authorization={props.folderSummaryAuthorization}
          scan={props.folderSummaryScan}
          run={props.folderSummaryRun}
          onPrimary={() => void runPrimaryFolderSummaryAction()}
          onStepSelect={focusFolderSummaryStep}
        />
        {leftCollapsed ? (
          <CollapsedSideRail
            side="left"
            items={[{ id: "nodes", label: "节点库", title: "展开节点库" }]}
            onSelect={() => setLeftCollapsed(false)}
          />
        ) : (
          <NodeLibraryPanel
            catalog={nodeCatalog}
            nodeSearch={nodeSearch}
            operationMessage={operationMessage}
            onCollapse={() => setLeftCollapsed(true)}
            onCreateCustom={() => setOperationMessage("自定义节点编辑器属于后续能力；当前请从受控节点库生成 proposal。")}
            onNodeSelect={(nodeId) => void proposeNodeAdd(nodeId)}
            onSearch={setNodeSearch}
          />
        )}
        <WorkflowCanvas
          stations={visibleCanvasStations}
          ghostNodes={ghostNodes}
          scenarioEmpty={!hasFolderSummaryState}
          selectedStationId={selectedStation?.station.station_id}
          onEdgeProposal={proposeEdgeAdd}
          onNodeDrop={(nodeId, uiPosition) => void proposeNodeAdd(nodeId, uiPosition)}
          onSelectStation={(stationId) => {
            setSelectedStationId(stationId);
            setRightTab("inspector");
            setRightCollapsed(false);
          }}
        />
        {rightCollapsed ? (
          <CollapsedSideRail
            side="right"
            items={[
              { id: "agent", label: "助手", title: "展开 Agent 助手" },
              { id: "inspector", label: "配置", title: "展开节点配置" },
              { id: "patch", label: "Diff", title: "展开 Patch Diff" },
              { id: "run", label: "运行", title: "展开运行详情" },
              { id: "governance", label: "审计", title: "展开治理审计" },
            ]}
            onSelect={(id) => {
              setRightCollapsed(false);
              if (id === "run") {
                setRightTab("inspector");
                setBottomCollapsed(false);
                setBottomTab("run");
                return;
              }
              if (id === "governance") {
                setRightTab("patch");
                setBottomCollapsed(false);
                setBottomTab("governance");
                return;
              }
              setRightTab(id as RightTab);
            }}
          />
        ) : (
        <aside className="studio-right" aria-label="Agent 与节点配置">
          <div className="right-tabbar">
            <button className={rightTab === "agent" ? "active" : ""} type="button" onClick={() => setRightTab("agent")}>Agent 助手</button>
            <button className={rightTab === "inspector" ? "active" : ""} type="button" onClick={() => setRightTab("inspector")}>节点配置</button>
            <button className={rightTab === "patch" ? "active" : ""} type="button" onClick={() => setRightTab("patch")}>Patch Diff</button>
            <button type="button" onClick={() => { setBottomCollapsed(false); setBottomTab("run"); }}>运行详情</button>
            <button title="治理审计" type="button" onClick={() => { setBottomCollapsed(false); setBottomTab("governance"); }}>审计</button>
            <button className="panel-collapse-button" type="button" aria-label="收起右侧面板" onClick={() => setRightCollapsed(true)}>收起</button>
          </div>
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
              selectedStationId={selectedStation?.station.station_id}
              selectedStationName={selectedStation?.station.name}
              onSendMessage={props.onSendAgentMessage}
              onShowDiff={() => {
                setRightTab("patch");
                setBottomTab("patch");
              }}
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
          {rightTab === "inspector" ? (
            <FolderInputInspector
              folderPath={folderPath}
              inspectorPrompt={inspectorPrompt}
              selectedStationName={selectedStation?.station.name || "未选择节点"}
              selectedStationStatus={selectedStation?.status || selectedRun?.status || "pending"}
              authorization={props.folderSummaryAuthorization}
              scan={props.folderSummaryScan}
              proposal={props.folderSummaryProposal}
              run={props.folderSummaryRun}
              onApply={props.onApplyFolderSummaryProposal}
              onAuthorize={props.onAuthorizeFolderSummaryRead}
              onCreateProposal={props.onCreateFolderSummaryProposal}
              onDebugScan={props.onDebugFolderSummaryScan}
              onFolderPathChange={setFolderPath}
              onGeneratePromptPatch={proposeInspectorPrompt}
              onInspectorPromptChange={setInspectorPrompt}
              onPublish={props.onPublishFolderSummaryProposal}
              onRun={props.onRunFolderSummaryWorkflow}
              onRerun={props.onRerunFolderSummaryMarkdownParse}
              onAgentDebugFix={props.onCreateFolderSummaryAgentDebugProposal}
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
        </aside>
        )}
        {bottomCollapsed ? (
          <CollapsedBottomRail
            activeTab={bottomTab}
            onExpand={(tab) => {
              setBottomTab(tab);
              setBottomCollapsed(false);
            }}
          />
        ) : null}
      </main>
      {bottomCollapsed ? null : (
      <RunBottomPanel
        activeTab={bottomTab}
        approvals={props.approvals || props.board.approvals || []}
        board={visibleBoard}
        context={props.context}
        eventState={props.eventState}
        events={props.events}
        folderRun={props.folderSummaryRun}
        governanceReview={props.governanceReview}
        highRiskPatchDiff={props.highRiskPatchDiff}
        modeLabel={props.modeLabel}
        operationEvidence={props.operationEvidence || []}
        patchDiff={props.patchDiff}
        patchProposal={props.patchProposal}
        quality={props.quality || props.board.quality_evaluations || []}
        activeHandoff={activeHandoff}
        onApprovalRespond={props.onApprovalRespond}
        onEmitBusinessEvent={props.onEmitBusinessEvent}
        onSetBusinessValue={props.onSetBusinessValue}
        onApplyPatch={props.onApplyPatch}
        onPublishVersion={props.onPublishVersion}
        onRejectPatch={props.onRejectPatch}
        onTabChange={setBottomTab}
        onCollapse={() => setBottomCollapsed(true)}
      />
      )}
    </div>
  );
}

function CollapsedSideRail({
  items,
  onSelect,
  side,
}: {
  items: Array<{ id: string; label: string; title: string }>;
  onSelect: (id: string) => void;
  side: "left" | "right";
}) {
  return (
    <nav className={`collapsed-side-rail collapsed-side-rail-${side}`} aria-label={side === "left" ? "左侧收纳栏" : "右侧收纳栏"}>
      {items.map((item) => (
        <button data-testid={`rail-${side}-${item.id}`} key={item.id} title={item.title} type="button" onClick={() => onSelect(item.id)}>
          <span>{item.label}</span>
        </button>
      ))}
    </nav>
  );
}

function CollapsedBottomRail({ activeTab, onExpand }: { activeTab: BottomTab; onExpand: (tab: BottomTab) => void }) {
  const tabs: Array<[BottomTab, string]> = [
    ["run", "运行"],
    ["events", "事件"],
    ["trace", "Trace"],
    ["artifacts", "产物"],
    ["quality", "质量"],
    ["approvals", "审批"],
    ["patch", "Patch"],
    ["governance", "审计"],
  ];
  return (
    <nav className="collapsed-bottom-rail" aria-label="底部收纳栏">
      {tabs.map(([tab, label]) => (
        <button className={activeTab === tab ? "active" : ""} data-testid={`rail-bottom-${tab}`} key={tab} type="button" onClick={() => onExpand(tab)}>
          {label}
        </button>
      ))}
    </nav>
  );
}

function FolderSummaryStepper({
  authorization,
  onPrimary,
  onStepSelect,
  proposal,
  run,
  scan,
  stage,
}: {
  authorization?: FolderSummaryAuthorization | null;
  onPrimary: () => void;
  onStepSelect: (stage: FolderSummaryStage) => void;
  proposal?: FolderSummaryProposal | null;
  run?: FolderSummaryRun | null;
  scan?: FolderSummaryScanResult | null;
  stage: FolderSummaryStage;
}) {
  const steps: Array<{ id: FolderSummaryStage; label: string; detail: string; complete: boolean }> = [
    { id: "draft", label: "生成草案", detail: "Agent 只生成 proposal", complete: Boolean(proposal) },
    { id: "review", label: "查看 Diff", detail: "审查 9 节点计划", complete: Boolean(proposal && proposal.status !== "proposed") },
    { id: "apply", label: "应用草稿", detail: "用户确认写入草稿", complete: Boolean(proposal && proposal.status !== "proposed") },
    { id: "authorize", label: "授权读取", detail: authorization ? "已授权本地 fixture" : "等待用户授权", complete: Boolean(authorization) },
    { id: "scan", label: "调试扫描", detail: scan ? `${scan.markdown_file_count} 个 Markdown` : "只预览，不生成总结", complete: Boolean(scan) },
    { id: "publish", label: "发布版本", detail: "用户确认发布", complete: Boolean(proposal && ["published", "completed"].includes(proposal.status)) },
    { id: "run", label: "运行工作流", detail: run ? "WorkflowInstance 已创建" : "等待用户运行", complete: Boolean(run) },
    { id: "artifacts", label: "查看产物", detail: run ? `${run.artifacts.length} 个产物` : "等待运行完成", complete: Boolean(run?.artifacts.length) },
    { id: "quality", label: "质量检查", detail: run?.quality_report.status || "等待质量报告", complete: Boolean(run?.quality_report) },
    { id: "governance", label: "审计证据", detail: "证据已留痕", complete: Boolean(run?.operation_evidence?.length || run?.governance_review) },
  ];
  return (
    <section className="v41-stepper-card" aria-label="V4.1 本地知识工作流步骤" data-testid="v41-scenario-stepper">
      <div className="v41-stepper-head">
        <div>
          <span className="eyebrow">V4.1 Local Knowledge Workflow</span>
          <h2>Desktop/技术分享 递归总结</h2>
          <p>Agent 生成草案，用户确认后授权、发布并运行；浏览器只访问 BFF。</p>
        </div>
        <button className="primary" data-testid="v41-next-action" type="button" onClick={onPrimary}>{folderPrimaryActionLabel(stage)}</button>
      </div>
      <div className="v41-step-list">
        {steps.map((item) => (
          <button className={`${item.id === stage ? "active" : ""} ${item.complete ? "complete" : ""}`} data-testid={`v41-step-${item.id}`} key={item.id} type="button" onClick={() => onStepSelect(item.id)}>
            <span>{item.complete ? "✓" : steps.findIndex((step) => step.id === item.id) + 1}</span>
            <strong>{item.label}</strong>
            <small>{item.detail}</small>
          </button>
        ))}
      </div>
    </section>
  );
}

function NodeLibraryPanel({
  catalog,
  nodeSearch,
  operationMessage,
  onCollapse,
  onCreateCustom,
  onNodeSelect,
  onSearch,
}: {
  catalog: NodeCatalogItem[];
  nodeSearch: string;
  operationMessage: string;
  onCollapse: () => void;
  onCreateCustom: () => void;
  onNodeSelect: (nodeId: string) => void;
  onSearch: (value: string) => void;
}) {
  const [activeCategory, setActiveCategory] = useState("全部");
  const sections = useMemo(() => nodeSections(catalog, nodeSearch), [catalog, nodeSearch]);
  const visibleSections = activeCategory === "全部" ? sections : sections.filter((section) => section.title === activeCategory);
  const hasMatch = visibleSections.some((section) => section.nodes.length);
  const categories = ["全部", ...sections.map((section) => section.title)];
  const quickNodes = catalog
    .filter((node) => ["文件夹输入", "递归文件扫描", "Markdown 文件过滤", "子文件夹总结 Agent"].includes(node.label))
    .map((node) => ({ id: node.id, label: node.label, description: node.station_kind || "BFF 受控节点", badge: node.catalog_version }));
  return (
    <aside className="studio-left" aria-label="节点库">
      <div className="panel-title">
        <span className="eyebrow">Node Library</span>
        <div className="panel-title-row">
          <h2>节点库</h2>
          <button type="button" aria-label="收起节点库" onClick={onCollapse}>收起</button>
        </div>
        <p>拖拽节点到画布，从受控节点库生成 proposal，Apply 前不会修改草稿。</p>
      </div>
      <input className="node-search" aria-label="搜索节点" placeholder="搜索节点" value={nodeSearch} onChange={(event) => onSearch(event.currentTarget.value)} />
      {quickNodes.length && !nodeSearch ? (
        <div className="node-shortcut-strip" aria-label="受控节点快捷入口">
          {quickNodes.map((node) => (
            <button
              className="library-node library-node-compact"
              draggable
              key={node.id}
              type="button"
              onClick={() => onNodeSelect(node.id)}
              onDragStart={(event) => setNodeDragData(event, node.id)}
            >
              <span className="library-node-icon" aria-hidden="true">{nodeIcon(node.label)}</span>
              <span className="library-node-copy">
                <span>{node.label}</span>
                <small>{node.description}</small>
              </span>
              <em>{node.badge}</em>
            </button>
          ))}
        </div>
      ) : null}
      <div className="filter-tabs" aria-label="节点分类快捷入口">
        {categories.map((category) => (
          <button className={activeCategory === category ? "active" : ""} key={category} type="button" onClick={() => setActiveCategory(category)}>
            {category}
          </button>
        ))}
      </div>
      <button className="custom-node-button" type="button" onClick={onCreateCustom}>+ 自定义节点</button>
      {operationMessage ? <p className="operation-message node-operation-message">{operationMessage}</p> : null}
      {!hasMatch && nodeSearch ? <p className="operation-message node-empty-message">没有匹配节点，请调整搜索词。</p> : null}
      <div className="node-section-list">
        {visibleSections.map((section) => (
          <section className="node-category" key={section.title}>
            <strong>{section.title}</strong>
            {section.nodes.map((node) => (
              <button
                className="library-node"
                draggable
                key={node.id}
                type="button"
                onClick={() => onNodeSelect(node.id)}
                onDragStart={(event) => setNodeDragData(event, node.id)}
              >
                <span className="library-node-icon" aria-hidden="true">{nodeIcon(node.label)}</span>
                <span className="library-node-copy">
                  <span>{node.label}</span>
                  <small>{node.description}</small>
                </span>
                <em>{node.badge}</em>
              </button>
            ))}
          </section>
        ))}
      </div>
    </aside>
  );
}

function WorkflowCanvas({
  stations,
  ghostNodes,
  scenarioEmpty,
  selectedStationId,
  onEdgeProposal,
  onNodeDrop,
  onSelectStation,
}: {
  stations: WorkflowBoard["stations"];
  ghostNodes: Array<{ id: string; label: string; uiPosition?: XYPosition }>;
  scenarioEmpty: boolean;
  selectedStationId?: string;
  onEdgeProposal: (fromStationId: string, toStationId: string) => void;
  onNodeDrop: (nodeId: string, uiPosition?: XYPosition) => void;
  onSelectStation: (stationId: string) => void;
}) {
  const nodeTypes = useMemo(() => ({ workflowNode: WorkflowCanvasNode }), []);
  const edgeTypes = useMemo(() => ({ proposalEdge: ProposalEdge }), []);
  const [nodePositions, setNodePositions] = useState<Record<string, XYPosition>>({});
  const [zoom, setZoom] = useState(1);
  const [showMiniMap, setShowMiniMap] = useState(false);
  const flowNodes = useMemo<Node<CanvasNodeData>[]>(() => {
    const stationNodes = stations.map((station, index) => ({
      id: station.station.station_id,
      type: "workflowNode",
      position: nodePositions[station.station.station_id] || { x: 292 + (index % 3) * 194, y: 118 + Math.floor(index / 3) * 116 },
      data: {
        label: station.station.name || station.station.station_id,
        role: station.station.role || "station",
        status: station.status,
        inputCount: station.input_artifacts?.length || station.runs[0]?.input_artifacts?.length || 0,
        outputCount: station.output_artifacts?.length || station.runs[0]?.output_artifacts?.length || 0,
        artifactName: station.output_artifacts?.[0]?.name || station.runs[0]?.output_artifacts?.[0]?.name || "待生成",
        attemptCount: station.runs?.length || 0,
        qualityState: station.status === "failed" ? "需检查" : station.status === "completed" ? "通过" : "待评估",
        ghost: statusKey(station.status) === "pending-proposal",
        selected: selectedStationId === station.station.station_id,
        onSelect: onSelectStation,
      },
    }));
    const pendingNodes = ghostNodes.map((ghost, index) => ({
      id: ghost.id,
      type: "workflowNode",
      position: nodePositions[ghost.id] || ghost.uiPosition || { x: 292 + (index % 3) * 194, y: 118 + Math.floor(index / 3) * 116 },
      data: {
        label: ghost.label,
        role: "pending",
        status: "Pending Proposal",
        inputCount: 0,
        outputCount: 0,
        artifactName: "尚未写入草稿",
        attemptCount: 0,
        qualityState: "待确认",
        ghost: true,
        onSelect: undefined,
      },
    }));
    return [...stationNodes, ...pendingNodes];
  }, [ghostNodes, nodePositions, onSelectStation, selectedStationId, stations]);
  const flowEdges = useMemo<Edge<CanvasEdgeData>[]>(() => stations.slice(0, -1).map((station, index) => ({
    id: `${station.station.station_id}-${stations[index + 1].station.station_id}`,
    source: station.station.station_id,
    target: stations[index + 1].station.station_id,
    type: "proposalEdge",
    markerEnd: { type: MarkerType.ArrowClosed, color: "#2563eb" },
    data: {
      label: "生成连线 Patch",
      onProposal: onEdgeProposal,
    },
  })), [onEdgeProposal, stations]);
  const handleConnect = useCallback(({ source, target }: { source: string | null; target: string | null }) => {
    if (source && target) void onEdgeProposal(source, target);
  }, [onEdgeProposal]);
  const handleNodesChange = useCallback((changes: NodeChange<Node<CanvasNodeData>>[]) => {
    const nextNodes = applyNodeChanges(changes, flowNodes);
    setNodePositions((current) => {
      const next = { ...current };
      for (const node of nextNodes) {
        next[node.id] = node.position;
      }
      return next;
    });
  }, [flowNodes]);
  const supportsInteractiveCanvas = typeof window !== "undefined";

  return (
    <section className="studio-canvas" aria-label="工作流画布" data-testid="station-board">
      <header className="canvas-topbar">
        <div>
          <span className="eyebrow">Workflow Canvas</span>
          <h2>工作流画布</h2>
        </div>
        <div className="canvas-toolbar">
          <span data-testid="canvas-zoom-label">{Math.round(zoom * 100)}%</span>
          <span>拖拽节点 · 缩放画布 · proposal-only</span>
          {stations.length > 1 ? (
            <button
              className="edge-proposal-button stable-edge-proposal-button"
              data-testid="edge-proposal-button"
              type="button"
              onClick={() => onEdgeProposal(stations[stations.length - 2].station.station_id, stations[stations.length - 1].station.station_id)}
            >
              生成连线 Patch
            </button>
          ) : null}
        </div>
      </header>
      <div className="canvas-surface">
        {scenarioEmpty && flowNodes.length === 0 ? (
          <div className="canvas-empty-guide" data-testid="v41-scenario-empty">
            <span className="canvas-empty-icon">流</span>
            <h3>从一句话创建本地知识总结工作流</h3>
            <p>在右侧 Agent 助手输入需求后，画布会先出现 9 个待确认节点。Apply 前不会扫描文件夹，也不会修改草稿。</p>
            <ol>
              <li>读取 Desktop/技术分享</li>
              <li>递归扫描 Markdown 文件</li>
              <li>为每个子文件夹生成单独总结</li>
              <li>生成总览总结和质量报告</li>
            </ol>
          </div>
        ) : null}
        {supportsInteractiveCanvas ? (
          <ReactFlowProvider>
            <WorkflowFlow
              nodes={flowNodes}
              edges={flowEdges}
              nodeTypes={nodeTypes}
              edgeTypes={edgeTypes}
              showMiniMap={showMiniMap}
              onNodesChange={handleNodesChange}
              onConnect={handleConnect}
              onNodeDrop={onNodeDrop}
              onToggleMiniMap={() => setShowMiniMap((value) => !value)}
              onZoomChange={setZoom}
            />
          </ReactFlowProvider>
        ) : (
          <StaticCanvasFallback nodes={flowNodes} edges={flowEdges} />
        )}
      </div>
      <div className="canvas-footnote">
        <span>Projection fresh</span>
        <span>Draft read model</span>
        <span>画布当前只生成 proposal</span>
      </div>
      <div className="canvas-node-overview" aria-label="画布节点概览">
        <span>节点 {stations.length}</span>
        <span>待确认 {ghostNodes.length}</span>
      </div>
    </section>
  );
}

function WorkflowFlow({
  edgeTypes,
  edges,
  nodeTypes,
  nodes,
  onConnect,
  onNodeDrop,
  onNodesChange,
  onToggleMiniMap,
  onZoomChange,
  showMiniMap,
}: {
  edgeTypes: Record<string, typeof ProposalEdge>;
  edges: Edge<CanvasEdgeData>[];
  nodeTypes: Record<string, typeof WorkflowCanvasNode>;
  nodes: Node<CanvasNodeData>[];
  onConnect: ({ source, target }: { source: string | null; target: string | null }) => void;
  onNodeDrop: (nodeId: string, uiPosition?: XYPosition) => void;
  onNodesChange: (changes: NodeChange<Node<CanvasNodeData>>[]) => void;
  onToggleMiniMap: () => void;
  onZoomChange: (zoom: number) => void;
  showMiniMap: boolean;
}) {
  const flow = useReactFlow<Node<CanvasNodeData>, Edge<CanvasEdgeData>>();
  useOnViewportChange({ onChange: ({ zoom }) => onZoomChange(zoom) });
  const nodeSignature = nodes.map((node) => node.id).join("|");

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void flow.fitView({ padding: 0.22, duration: 0, maxZoom: 1.05 });
    }, 80);
    return () => window.clearTimeout(timer);
  }, [flow, nodeSignature]);

  function handleDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    const nodeId = event.dataTransfer.getData("application/x-harnessos-node");
    if (!nodeId) return;
    onNodeDrop(nodeId, flow.screenToFlowPosition({ x: event.clientX, y: event.clientY }));
  }

  return (
    <>
      <ReactFlow
        edges={edges}
        edgeTypes={edgeTypes}
        nodes={nodes}
        nodeTypes={nodeTypes}
        onConnect={onConnect}
        onDragOver={(event) => event.preventDefault()}
        onDrop={handleDrop}
        onNodesChange={onNodesChange}
        defaultViewport={{ x: 0, y: 0, zoom: 1 }}
        minZoom={0.45}
        maxZoom={1.6}
        proOptions={{ hideAttribution: true }}
      >
        <Background variant={BackgroundVariant.Dots} gap={24} size={1} />
        <Controls showInteractive={false} />
        {showMiniMap ? <MiniMap pannable zoomable /> : null}
      </ReactFlow>
      <div className="canvas-action-toolbar" aria-label="画布工具栏">
        <button data-testid="canvas-zoom-out" type="button" onClick={() => void flow.zoomOut()}>缩小</button>
        <button data-testid="canvas-zoom-in" type="button" onClick={() => void flow.zoomIn()}>放大</button>
        <button data-testid="canvas-fit-view" type="button" onClick={() => void flow.fitView({ padding: 0.18 })}>适配画布</button>
        <button type="button" onClick={() => void flow.setViewport({ x: 0, y: 0, zoom: 1 })}>重置视图</button>
        <button data-testid="canvas-minimap-toggle" type="button" onClick={onToggleMiniMap}>小地图</button>
      </div>
    </>
  );
}

function StaticCanvasFallback({ nodes, edges }: { nodes: Node<CanvasNodeData>[]; edges: Edge<CanvasEdgeData>[] }) {
  return (
    <div className="canvas-static-flow" aria-label="静态画布预览">
      <svg className="canvas-static-edges" aria-hidden="true">
        {edges.map((edge) => {
          const sourceIndex = nodes.findIndex((node) => node.id === edge.source);
          const targetIndex = nodes.findIndex((node) => node.id === edge.target);
          if (sourceIndex < 0 || targetIndex < 0) return null;
          const x1 = 162 + sourceIndex * 210;
          const y1 = 86 + (sourceIndex % 2) * 86;
          const x2 = 42 + targetIndex * 210;
          const y2 = 86 + (targetIndex % 2) * 86;
          return <path d={`M ${x1} ${y1} C ${x1 + 52} ${y1}, ${x2 - 52} ${y2}, ${x2} ${y2}`} key={edge.id} />;
        })}
      </svg>
      <div className="canvas-static-nodes">
        {nodes.map((node) => (
          <StaticCanvasNode data={node.data} key={node.id} />
        ))}
      </div>
      <div className="canvas-static-edge-actions">
        {edges.map((edge) => (
          <button className="edge-proposal-button" data-testid="edge-proposal-button" key={edge.id} type="button">
            {edge.data?.label || "生成连线 Patch"}
          </button>
        ))}
      </div>
    </div>
  );
}

function StaticCanvasNode({ data }: { data: CanvasNodeData }) {
  return (
    <button
      className={`canvas-node-card station-${statusKey(data.status)} ${data.selected ? "selected" : ""} ${data.ghost ? "ghost" : ""}`}
      data-testid={data.ghost ? "ghost-node" : "station-card"}
      type="button"
    >
      <CanvasNodeContents data={data} />
    </button>
  );
}

function WorkflowCanvasNode({ id, data }: NodeProps<Node<CanvasNodeData>>) {
  return (
    <button
      className={`canvas-node-card station-${statusKey(data.status)} ${data.selected ? "selected" : ""} ${data.ghost ? "ghost" : ""}`}
      data-testid={data.ghost ? "ghost-node" : "station-card"}
      type="button"
      onClick={() => data.onSelect?.(id)}
    >
      <Handle className="node-port node-port-in" type="target" position={Position.Left} />
      <CanvasNodeContents data={data} />
      <Handle className="node-port node-port-out" type="source" position={Position.Right} />
    </button>
  );
}

function CanvasNodeContents({ data }: { data: CanvasNodeData }) {
  return (
    <>
      <span className="canvas-node-head">
        <span className="canvas-node-icon" aria-hidden="true">{nodeIcon(data.label)}</span>
        <span className="node-type">{data.role}</span>
        <span className="status">{statusLabel(data.status)}</span>
      </span>
      <strong>{data.label}</strong>
      <span className="artifact-contract">输入 {data.inputCount} · 输出 {data.outputCount}</span>
      <span className="artifact-contract">{data.artifactName}</span>
      <span className="node-quality-row">
        <small>质量：{data.qualityState}</small>
        <small>attempt {data.attemptCount}</small>
      </span>
    </>
  );
}

function ProposalEdge(props: EdgeProps<Edge<CanvasEdgeData>>) {
  const [edgePath, labelX, labelY] = getBezierPath(props);
  const source = String(props.source);
  const target = String(props.target);
  return (
    <>
      <BaseEdge path={edgePath} markerEnd={props.markerEnd} style={{ stroke: "#2563eb", strokeWidth: 1.7 }} />
      <foreignObject width={118} height={38} x={labelX - 59} y={labelY - 19} requiredExtensions="http://www.w3.org/1999/xhtml">
        <button className="edge-proposal-button" type="button" onClick={() => props.data?.onProposal?.(source, target)}>
          {props.data?.label || "生成连线 Patch"}
        </button>
      </foreignObject>
    </>
  );
}

function FolderInputInspector(props: {
  folderPath: string;
  inspectorPrompt: string;
  selectedStationName: string;
  selectedStationStatus: string;
  authorization?: FolderSummaryAuthorization | null;
  scan?: FolderSummaryScanResult | null;
  proposal?: FolderSummaryProposal | null;
  run?: FolderSummaryRun | null;
  onFolderPathChange: (value: string) => void;
  onInspectorPromptChange: (value: string) => void;
  onGeneratePromptPatch: () => Promise<void> | void;
  onCreateProposal?: (folderPath: string) => Promise<void> | void;
  onAuthorize?: (folderPath: string) => Promise<void> | void;
  onDebugScan?: () => Promise<void> | void;
  onApply?: (proposalId?: string) => Promise<void> | void;
  onPublish?: (proposalId?: string) => Promise<void> | void;
  onRun?: (proposalId?: string) => Promise<void> | void;
  onRerun?: () => Promise<void> | void;
  onAgentDebugFix?: () => Promise<void> | void;
}) {
  return (
    <section className="inspector-panel" aria-label="本地文件夹总结" data-testid="folder-summary-panel">
      <div className="panel-title">
        <span className="eyebrow">Inspector</span>
        <h2>本地 Markdown 文件夹总结</h2>
        <p>当前节点：{props.selectedStationName || "文件夹输入"} · 状态：{props.selectedStationStatus}</p>
      </div>
      <label className="form-field">
        文件夹路径
        <input data-testid="folder-summary-path-input" value={props.folderPath} onChange={(event) => props.onFolderPathChange(event.currentTarget.value)} />
      </label>
      <div className="button-row action-grid">
        <button data-testid="folder-summary-create-proposal" type="button" onClick={() => void props.onCreateProposal?.(props.folderPath)}>生成工作流草案</button>
        <button data-testid="folder-summary-authorize" type="button" onClick={() => void props.onAuthorize?.(props.folderPath)}>授权读取</button>
        <button data-testid="folder-summary-debug-scan" disabled={!props.authorization} type="button" onClick={() => void props.onDebugScan?.()}>调试扫描</button>
        <button data-testid="folder-summary-apply" disabled={!props.proposal || props.proposal.status !== "proposed"} type="button" onClick={() => void props.onApply?.(props.proposal?.proposal_id)}>应用到草稿</button>
        <button data-testid="folder-summary-publish" disabled={!props.proposal || props.proposal.status !== "applied"} type="button" onClick={() => void props.onPublish?.(props.proposal?.proposal_id)}>发布版本</button>
        <button data-testid="folder-summary-run" disabled={!props.proposal || props.proposal.status !== "published" || !props.authorization} type="button" onClick={() => void props.onRun?.(props.proposal?.proposal_id)}>运行工作流</button>
        <button data-testid="folder-summary-rerun" disabled={!props.run || !props.run.nodes.some((node) => node.status === "failed")} type="button" onClick={() => void props.onRerun?.()}>重跑当前节点</button>
        <button data-testid="folder-summary-agent-debug-fix" disabled={!props.run} type="button" onClick={() => void props.onAgentDebugFix?.()}>Agent 生成修复 Proposal</button>
      </div>
      <label className="form-field">
        Prompt Patch
        <textarea
          data-testid="inspector-prompt-input"
          placeholder="输入修改建议，点击生成 Patch 后才会调用 BFF"
          value={props.inspectorPrompt}
          onChange={(event) => props.onInspectorPromptChange(event.currentTarget.value)}
        />
      </label>
      <button data-testid="inspector-generate-patch-button" disabled={!props.inspectorPrompt.trim()} type="button" onClick={() => void props.onGeneratePromptPatch()}>
        生成 Patch
      </button>
      {props.proposal ? <FolderProposalView proposal={props.proposal} /> : null}
      {props.authorization ? <p className="operation-message" data-testid="folder-summary-authorization">已授权：{props.authorization.resolved_path_label}</p> : null}
      {props.scan ? <FolderScanView scan={props.scan} /> : null}
      {props.run ? <FolderRunSummary run={props.run} /> : null}
    </section>
  );
}

function FolderProposalView({ proposal }: { proposal: FolderSummaryProposal }) {
  return (
    <div className="proposal-box" data-testid="folder-summary-proposal">
      <strong>工作流草案 · {proposal.status}</strong>
      <p>9 个逻辑节点已生成，Apply 前仅显示 pending proposal。</p>
      <ol>{proposal.nodes.map((node) => <li key={node.station_id}>{node.station_id} · {node.name} · {node.status}</li>)}</ol>
    </div>
  );
}

function FolderScanView({ scan }: { scan: FolderSummaryScanResult }) {
  return (
    <div className="scan-box" data-testid="folder-summary-scan-result">
      <strong>调试扫描结果</strong>
      <p>总文件：{scan.total_file_count} · Markdown：{scan.markdown_file_count} · 子文件夹：{scan.child_folder_count} · 未支持：{scan.unsupported_file_count}</p>
      <p>未支持文件：{scan.unsupported_files.join(", ") || "无"}</p>
      <p>空文件夹：{scan.empty_folders.join(", ") || "无"}</p>
    </div>
  );
}

function FolderRunSummary({ run }: { run: FolderSummaryRun }) {
  return (
    <div className="run-summary" data-testid="folder-summary-run-result">
      <strong>运行完成</strong>
      <p>WorkflowInstance：{run.workflow_instance_id}</p>
      <p>节点状态：{run.nodes.map((node) => `${node.station_id}:${node.status}`).join(", ")}</p>
      <p>产物列表：{run.artifacts.map((artifact) => artifact.name).join(", ")}</p>
      {run.nodes.some((node) => node.error) ? (
        <div data-testid="folder-summary-error-state">{run.nodes.filter((node) => node.error).map((node) => <p key={node.station_id}>{node.station_id}：{node.error}</p>)}</div>
      ) : null}
      <div data-testid="folder-summary-attempt-history">
        {run.nodes.map((node) => (
          <p key={node.station_id}>{node.station_id} attempts: {(node.attempts || []).map((attempt) => `${attempt.attempt}:${attempt.status}${attempt.error ? `:${attempt.error}` : ""}`).join(" | ")}</p>
        ))}
      </div>
    </div>
  );
}

function RunBottomPanel(props: {
  activeTab: BottomTab;
  activeHandoff: AgentActionHandoff | null;
  approvals: ApprovalSummary[];
  board: WorkflowBoard;
  context?: WorkflowContextSummary | null;
  events: WorkflowEvent[];
  eventState?: string;
  folderRun?: FolderSummaryRun | null;
  governanceReview?: GovernanceReviewSummary | null;
  highRiskPatchDiff?: WorkflowPatchDiff;
  modeLabel?: string;
  operationEvidence: OperationEvidenceRecord[];
  patchDiff?: WorkflowPatchDiff;
  patchProposal?: WorkflowPatchProposal;
  quality: QualitySummary[];
  onApprovalRespond?: ConsoleShellProps["onApprovalRespond"];
  onApplyPatch?: ConsoleShellProps["onApplyPatch"];
  onEmitBusinessEvent?: ConsoleShellProps["onEmitBusinessEvent"];
  onPublishVersion?: ConsoleShellProps["onPublishVersion"];
  onRejectPatch?: ConsoleShellProps["onRejectPatch"];
  onSetBusinessValue?: ConsoleShellProps["onSetBusinessValue"];
  onTabChange: (tab: BottomTab) => void;
  onCollapse: () => void;
}) {
  const tabs: Array<[BottomTab, string]> = [
    ["run", "运行看板"],
    ["events", "事件"],
    ["trace", "Trace"],
    ["artifacts", "产物"],
    ["quality", "质量"],
    ["approvals", "审批"],
    ["context", "上下文"],
    ["patch", "Patch"],
    ["governance", "治理审计"],
  ];
  return (
    <section className="bottom-run-panel" aria-label="运行观察区">
      <div className="bottom-tabs">
        {tabs.map(([tab, label]) => <button className={props.activeTab === tab ? "active" : ""} key={tab} type="button" onClick={() => props.onTabChange(tab)}>{label}</button>)}
        <button className="panel-collapse-button" type="button" aria-label="收起运行面板" onClick={props.onCollapse}>收起</button>
      </div>
      <div className="bottom-content">
        {props.activeTab === "run" ? <RunBoard board={props.board} run={props.folderRun} /> : null}
        {props.activeTab === "events" ? <EventFeed events={props.events} /> : null}
        {props.activeTab === "trace" ? <pre data-testid="trace-panel">{safeText(props.board.trace_summary?.summary || props.board.trace_summary?.trace_id || "redacted trace summary")}</pre> : null}
        {props.activeTab === "artifacts" ? <ArtifactPanel board={props.board} run={props.folderRun} /> : null}
        {props.activeTab === "quality" ? <><QualityPanel evaluations={props.quality} />{props.folderRun ? <FolderSummaryQuality run={props.folderRun} /> : null}</> : null}
        {props.activeTab === "approvals" ? <ApprovalPanel approvals={props.approvals} handoff={props.activeHandoff?.target_panel === "approval_panel" ? props.activeHandoff : null} onRespond={props.onApprovalRespond} /> : null}
        {props.activeTab === "context" ? <ContextPanel context={props.context || undefined} handoff={props.activeHandoff?.target_panel === "context_panel" ? props.activeHandoff : null} onEmitBusinessEvent={props.onEmitBusinessEvent} onSetBusinessValue={props.onSetBusinessValue} /> : null}
        {props.activeTab === "patch" && props.patchProposal && props.patchDiff ? (
          <WorkflowEditingPanel proposal={props.patchProposal} diff={props.patchDiff} highRiskDiff={props.highRiskPatchDiff} onApplyPatch={props.onApplyPatch} onRejectPatch={props.onRejectPatch} onPublishVersion={props.onPublishVersion} handoff={props.activeHandoff?.target_panel === "editing_panel" ? props.activeHandoff : null} />
        ) : null}
        {props.activeTab === "governance" ? <GovernanceReviewPanel evidence={props.operationEvidence} review={props.governanceReview} /> : null}
      </div>
      <div className="run-status-strip">
        <span data-testid="event-connection-state">事件连接：{props.eventState || "idle"}</span>
        <span>Proposal-first Console</span>
        <span>{props.modeLabel || "Real BFF"}</span>
      </div>
    </section>
  );
}

function RunBoard({ board, run }: { board: WorkflowBoard; run?: FolderSummaryRun | null }) {
  const items = run?.nodes.map((node) => ({
    id: node.station_id,
    name: node.name,
    status: node.status,
    detail: (node.attempts || []).map((attempt) => `${attempt.attempt}:${attempt.status}`).join(" | ") || "attempt 1",
    error: node.error,
  })) || board.stations.map((station) => ({
    id: station.station.station_id,
    name: station.station.name,
    status: station.runs[0]?.status || station.status,
    detail: station.output_artifacts?.map((artifact) => artifact.name || artifact.artifact_id).join(", ") || "等待输出",
    error: undefined,
  }));
  return (
    <div className="run-board-panel" data-testid="run-board-panel">
      <div className="panel-heading-row">
        <div>
          <span className="eyebrow">Run Board</span>
          <h3>运行看板</h3>
        </div>
        <span className="status">{run ? "WorkflowInstance 已创建" : "等待运行"}</span>
      </div>
      <div className="run-board-grid" data-testid="folder-summary-run-board">
        {items.map((item) => (
          <article className={`run-board-item run-board-item-${item.status}`} key={item.id}>
            <strong>{item.name}</strong>
            <span>{item.id}:{item.status}</span>
            <small>{item.detail}</small>
            {item.error ? <em>{item.error}</em> : null}
          </article>
        ))}
      </div>
    </div>
  );
}

function ArtifactPanel({ board, run }: { board: WorkflowBoard; run?: FolderSummaryRun | null }) {
  const boardArtifacts = board.artifacts || [];
  return (
    <div className="artifact-panel" data-testid="artifact-panel">
      <pre>{boardArtifacts.map((artifact) => safeText(artifact.name || artifact.artifact_id)).join("\n")}</pre>
      {run ? (
        <div className="folder-summary-artifacts" data-testid="folder-summary-artifacts">
          <strong>生成产物</strong>
          {run.artifacts.map((artifact) => (
            <details key={artifact.artifact_id} open>
              <summary>{artifact.name}</summary>
              <pre>{safeText(artifact.content)}</pre>
            </details>
          ))}
        </div>
      ) : null}
    </div>
  );
}

function FolderSummaryQuality({ run }: { run: FolderSummaryRun }) {
  return (
    <div className="folder-summary-quality" data-testid="folder-summary-quality">
      <strong>V4.1 质量报告</strong>
      <p>状态：{run.quality_report.status}</p>
      <p>覆盖：{run.quality_report.summary_coverage.generated_summary_count}/{run.quality_report.summary_coverage.expected_folder_count}</p>
      <p>未支持文件：{run.quality_report.unsupported_files.join(", ") || "无"}</p>
      <p>空文件夹：{run.quality_report.empty_folders.join(", ") || "无"}</p>
    </div>
  );
}

function nodeSections(catalog: NodeCatalogItem[], search: string) {
  const normalizedSearch = search.trim().toLowerCase();
  const categories = [
    { title: "输入节点", ids: ["folder_input", "file_input"], fallback: ["文件夹输入"], description: "授权读取本地文件夹路径", badge: "V4.1" },
    { title: "文件处理节点", ids: ["folder_scan", "markdown_filter", "markdown_parse", "folder_group"], fallback: ["递归文件扫描", "Markdown 文件过滤", "Markdown 内容解析", "子文件夹分组"], description: "扫描、过滤、解析和分组 Markdown 文件", badge: "文件" },
    { title: "AI Agent 节点", ids: ["per_folder_summary", "overview_summary", "planner_agent"], fallback: ["子文件夹总结 Agent", "总目录总结 Agent", "Planner Agent"], description: "生成子文件夹总结和总览总结", badge: "Agent" },
    { title: "质量治理节点", ids: ["quality_check", "quality_evaluation", "character_consistency"], fallback: ["质量检查 Agent", "质量评估", "角色一致性检查"], description: "检查覆盖率、未支持文件和空文件夹", badge: "治理" },
    { title: "审批节点", ids: ["manual_approval", "approval_point"], fallback: ["人工审批"], description: "保留人工确认点，Agent 不会自动执行", badge: "审批" },
    { title: "输出节点", ids: ["artifact_publish", "publish_output", "end"], fallback: ["输出总结文件", "发布输出", "结束节点"], description: "发布总结 Markdown、文件清单和质量报告", badge: "输出" },
  ];
  const usedIds = new Set<string>();
  const groupedSections = categories.map((category) => {
    const labels = catalog.filter(
      (item) => category.ids.includes(item.id) || category.ids.includes(item.node_template_id) || category.fallback.includes(item.label),
    );
    labels.forEach((item) => {
      usedIds.add(item.id);
      usedIds.add(item.node_template_id);
      usedIds.add(item.label);
    });
    const nodes = labels.length
      ? labels.map((item) => ({ id: item.id, label: item.label, description: category.description, badge: category.badge }))
      : category.fallback.filter((label) => NODE_LIBRARY_FALLBACK_LABELS.includes(label)).map((label) => ({ id: label, label, description: category.description, badge: category.badge }));
    return { ...category, nodes: nodes.filter((node) => (normalizedSearch ? node.label.toLowerCase().includes(normalizedSearch) : true)) };
  });
  const additionalNodes = catalog
    .filter((item) => !usedIds.has(item.id) && !usedIds.has(item.node_template_id) && !usedIds.has(item.label))
    .map((item) => ({ id: item.id, label: item.label, description: item.station_kind || "BFF 受控节点", badge: item.catalog_version }))
    .filter((node) => (normalizedSearch ? node.label.toLowerCase().includes(normalizedSearch) : true));
  return additionalNodes.length
    ? [...groupedSections, { title: "更多受控节点", ids: [], fallback: [], description: "来自 BFF controlled catalog", badge: "BFF", nodes: additionalNodes }]
    : groupedSections;
}

function fallbackCatalog(): NodeCatalogItem[] {
  return NODE_LIBRARY_FALLBACK_LABELS.map((label) => ({
    id: label,
    label,
    description: label,
    catalog_id: "fallback",
    catalog_version: "local",
    node_template_id: label,
    station_kind: "agent",
    schema_version: "v1",
    allowed_skill_refs: [],
    allowed_connector_refs: [],
    allowed_artifact_kinds: [],
    allowed_quality_rules: [],
    allowed_approval_policies: [],
  }));
}

function setNodeDragData(event: DragEvent<HTMLButtonElement>, nodeId: string) {
  event.dataTransfer.setData("application/x-harnessos-node", nodeId);
  event.dataTransfer.effectAllowed = "copy";
}

function statusLabel(status: string): string {
  const normalized = statusKey(status);
  if (status === "warning") return "WARNING";
  if (normalized === "completed") return "DONE";
  if (normalized === "queued") return "待执行";
  if (normalized === "pending-proposal") return "Pending Proposal";
  return status;
}

function statusKey(status: string): string {
  return status.trim().toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") || "unknown";
}

function deriveFolderSummaryStage(
  proposal?: FolderSummaryProposal | null,
  authorization?: FolderSummaryAuthorization | null,
  scan?: FolderSummaryScanResult | null,
  run?: FolderSummaryRun | null,
): FolderSummaryStage {
  if (run?.quality_report) return "artifacts";
  if (proposal?.status === "published") return "run";
  if (proposal?.status === "applied" && scan) return "publish";
  if (proposal?.status === "applied" && authorization) return "scan";
  if (proposal?.status === "applied") return "authorize";
  if (proposal?.status === "proposed") return "review";
  return "draft";
}

function folderPrimaryActionLabel(stage: FolderSummaryStage): string {
  const labels: Record<FolderSummaryStage, string> = {
    draft: "让 Agent 生成草案",
    review: "查看 Diff",
    apply: "应用到草稿",
    authorize: "授权读取",
    scan: "调试扫描",
    publish: "发布版本",
    run: "运行工作流",
    artifacts: "查看产物",
    quality: "查看质量",
    governance: "查看审计",
  };
  return labels[stage];
}

function folderStageLabel(stage: FolderSummaryStage): string {
  const labels: Record<FolderSummaryStage, string> = {
    draft: "等待生成草案",
    review: "草案待审查",
    apply: "等待应用草稿",
    authorize: "等待授权读取",
    scan: "等待调试扫描",
    publish: "等待发布版本",
    run: "等待运行",
    artifacts: "运行完成",
    quality: "质量报告可查看",
    governance: "证据链已记录",
  };
  return labels[stage];
}

function folderHeaderVersionLabel(proposal?: FolderSummaryProposal | null): string {
  if (!proposal) return "V4.1 MVP · Proposal-first";
  return `Draft rev. ${proposal.draft_revision} · ${proposal.status}`;
}

function buildFolderSummaryCanvasStations(proposal?: FolderSummaryProposal | null, run?: FolderSummaryRun | null): WorkflowBoard["stations"] | null {
  const sourceNodes = run?.nodes.length
    ? run.nodes.map((node) => ({
        station_id: node.station_id,
        name: node.name,
        status: node.status,
        attempts: node.attempts || [],
        error: node.error,
      }))
    : proposal?.nodes.map((node) => ({
        station_id: node.station_id,
        name: node.name,
        status: proposal.status === "proposed" ? "pending_proposal" : proposal.status === "applied" ? "draft_ready" : proposal.status,
        attempts: [],
        error: null,
      }));
  if (!sourceNodes?.length) return null;
  return sourceNodes.map((node) => ({
    station: {
      station_id: node.station_id,
      name: node.name,
      role: folderNodeRole(node.station_id),
    },
    status: node.status,
    runs: node.attempts.length
      ? node.attempts.map((attempt) => ({
          station_run_id: attempt.attempt_id,
          station_id: node.station_id,
          status: attempt.status,
          output_artifacts: [],
        }))
      : [],
    input_artifacts: [],
    output_artifacts: folderNodeOutput(node.station_id),
  }));
}

function projectStationsForV41Scenario(stations: WorkflowBoard["stations"]): WorkflowBoard["stations"] {
  const labels = V41_FOLDER_SUMMARY_NODES;
  return stations.map((station, index) => {
    const planned = labels[index] || labels[labels.length - 1];
    const shouldProjectName = isLegacyFixtureStationName(station.station.name || "");
    return {
      ...station,
      station: {
        ...station.station,
        name: shouldProjectName ? planned.name : station.station.name,
        role: shouldProjectName ? planned.role : station.station.role || planned.role,
      },
      output_artifacts: station.output_artifacts?.length ? station.output_artifacts : folderNodeOutput(planned.station_id),
    };
  });
}

function isLegacyFixtureStationName(name: string): boolean {
  return ["Collect Input", "Transform Input", "Human Gate", "用户输入", "分镜生成", "分镜生成 Agent"].includes(name);
}

const V41_FOLDER_SUMMARY_NODES = [
  { station_id: "folder_input", name: "文件夹输入", role: "Input" },
  { station_id: "folder_scan", name: "递归文件扫描", role: "Tool" },
  { station_id: "markdown_filter", name: "Markdown 文件过滤", role: "Tool" },
  { station_id: "markdown_parse", name: "Markdown 内容解析", role: "Tool" },
  { station_id: "folder_group", name: "子文件夹分组", role: "Tool" },
  { station_id: "per_folder_summary", name: "子文件夹总结 Agent", role: "Agent" },
  { station_id: "overview_summary", name: "总目录总结 Agent", role: "Agent" },
  { station_id: "quality_check", name: "质量检查 Agent", role: "Reviewer" },
  { station_id: "artifact_publish", name: "输出总结文件", role: "Output" },
];

function folderNodeRole(stationId: string): string {
  if (stationId === "folder_input") return "Input";
  if (["folder_scan", "markdown_filter", "markdown_parse", "folder_group"].includes(stationId)) return "Tool";
  if (["per_folder_summary", "overview_summary"].includes(stationId)) return "Agent";
  if (stationId === "quality_check") return "Reviewer";
  if (stationId === "artifact_publish") return "Output";
  return "Station";
}

function folderNodeOutput(stationId: string): Array<{ artifact_id: string; name: string }> {
  const outputs: Record<string, string> = {
    folder_input: "folder_ref",
    folder_scan: "file_tree.json",
    markdown_filter: "md_file_list.json",
    markdown_parse: "parsed_docs.json",
    folder_group: "grouped_docs.json",
    per_folder_summary: "子文件夹总结",
    overview_summary: "总览总结.md",
    quality_check: "quality_report.json",
    artifact_publish: "output_package",
  };
  return [{ artifact_id: `${stationId}_out`, name: outputs[stationId] || "待生成" }];
}

function nodeIcon(label: string): string {
  if (label.includes("文件夹")) return "夹";
  if (label.includes("扫描")) return "扫";
  if (label.includes("过滤")) return "滤";
  if (label.includes("解析")) return "析";
  if (label.includes("分组")) return "组";
  if (label.includes("总结") || label.includes("Agent")) return "智";
  if (label.includes("质量")) return "质";
  if (label.includes("审批")) return "审";
  if (label.includes("输出") || label.includes("发布")) return "出";
  return "节";
}
