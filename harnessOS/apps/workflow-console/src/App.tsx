import { ConsoleShell } from "./components/ConsoleShell.js";
import { useWorkflowConsoleData } from "./hooks/useWorkflowConsoleData.js";
import { WorkflowStudioLayout, type VisualAcceptanceState } from "./ui/layout/WorkflowStudioLayout.js";

function staticStudioState(): VisualAcceptanceState | null {
  if (typeof window === "undefined") return null;
  const state = new URLSearchParams(window.location.search).get("studio");
  if (
    state === "overview" ||
    state === "agent-draft-proposal" ||
    state === "folder-debug-scan" ||
    state === "running-board" ||
    state === "artifacts-quality" ||
    state === "governance-evidence"
  ) {
    return state;
  }
  return null;
}

export function App() {
  const studioState = staticStudioState();
  if (studioState) {
    return <WorkflowStudioLayout state={studioState} />;
  }
  const data = useWorkflowConsoleData();
  if (data.loading) {
    return <div className="console-state" data-testid="workflow-console-loading">正在连接真实工作流数据…</div>;
  }
  if (data.error) {
    return (
      <div className="console-state error-state" data-testid="workflow-console-error">
        <strong>真实数据连接失败</strong>
        <span>{data.error}</span>
      </div>
    );
  }
  if (data.empty || !data.board || !data.status) {
    return <div className="console-state" data-testid="workflow-console-empty">暂无可展示的工作流实例</div>;
  }
  return (
    <ConsoleShell
      workflows={data.workflows}
      versions={data.versions}
      instances={data.instances}
      selectedWorkflowId={data.selectedWorkflowId}
      selectedVersionId={data.selectedVersionId}
      selectedInstanceId={data.selectedInstanceId}
      board={data.board}
      nodeCatalog={data.nodeCatalog || []}
      status={data.status}
      approvals={data.approvals}
      quality={data.quality}
      context={data.context}
      events={data.mode === "demo" ? data.events : data.events}
      patchProposal={data.patchProposal}
      patchDiff={data.patchDiff}
      highRiskPatchDiff={data.highRiskPatchDiff}
	      agentTalkFixture={data.agentTalkFixture}
	      agentSession={data.agentSession}
	      agentInteractionState={data.agentInteractionState}
	      agentSuggestions={data.agentSuggestions}
      agentActionProposals={data.agentActionProposals}
      activeAgentHandoff={data.activeAgentHandoff}
      operationEvidence={data.operationEvidence}
      governanceReview={data.governanceReview}
      folderSummaryProposal={data.folderSummaryProposal}
      folderSummaryAuthorization={data.folderSummaryAuthorization}
      folderSummaryScan={data.folderSummaryScan}
      folderSummaryRun={data.folderSummaryRun}
      modeLabel={data.mode === "demo" ? "Demo / Fixture" : undefined}
      eventState={data.eventState}
      onWorkflowChange={data.setSelectedWorkflowId}
      onVersionChange={data.setSelectedVersionId}
      onInstanceChange={data.setSelectedInstanceId}
      onApprovalRespond={data.respondApproval}
      onSetBusinessValue={data.setBusinessContextValue}
      onEmitBusinessEvent={data.emitBusinessEvent}
      onApplyPatch={data.applyPatch}
      onRejectPatch={data.rejectPatch}
      onPublishVersion={data.publishWorkflowVersion}
      onProposeCanvasPatch={data.proposeCanvasPatch}
      onSendAgentMessage={data.sendAgentMessage}
      onDismissAgentSuggestion={data.dismissAgentSuggestion}
      onDismissAgentActionProposal={data.dismissAgentActionProposal}
      onCreateAgentActionHandoff={data.createAgentActionHandoff}
      onCreateFolderSummaryProposal={data.createFolderSummaryProposal}
      onAuthorizeFolderSummaryRead={data.authorizeFolderSummaryRead}
      onDebugFolderSummaryScan={data.debugFolderSummaryScan}
      onApplyFolderSummaryProposal={data.applyFolderSummaryProposal}
      onPublishFolderSummaryProposal={data.publishFolderSummaryProposal}
      onRunFolderSummaryWorkflow={data.runFolderSummaryWorkflow}
      onRerunFolderSummaryMarkdownParse={data.rerunFolderSummaryMarkdownParse}
      onCreateFolderSummaryAgentDebugProposal={data.createFolderSummaryAgentDebugProposal}
    />
  );
}
